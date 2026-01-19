# Selenium Grid / Moon Integration Guide

## Overview

Your automation framework now supports **Selenium Grid** and **Moon** (Selenium Grid replacement) for:
- ✅ Remote browser execution
- ✅ Parallel testing across multiple workers
- ✅ Browser matrix execution (Chrome 127/128, Firefox, Edge)
- ✅ Isolated report directories per run

---

## 1. Quick Start with Selenium Grid

### Local Grid Setup (Docker)

```bash
# Start Selenium Grid Hub locally
docker run -d -p 4444:4444 -p 7900:7900 \
  -v /dev/shm:/dev/shm \
  selenium/hub:4.15.0

# Start Chrome Node
docker run -d -p 5555:5555 \
  --shm-size=2gb \
  -e SE_EVENT_BUS_HOST=localhost \
  -e SE_EVENT_BUS_PUBLISH_PORT=4442 \
  -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 \
  selenium/node-chrome:4.15.0

# Start Firefox Node
docker run -d -p 5556:5556 \
  --shm-size=2gb \
  -e SE_EVENT_BUS_HOST=localhost \
  -e SE_EVENT_BUS_PUBLISH_PORT=4442 \
  -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 \
  selenium/node-firefox:4.15.0
```

---

## 2. Configuration

### Using Environment Variables

```bash
# Set Grid URL
export GRID_URL="http://localhost:4444/wd/hub"

# Enable Grid execution
export USE_GRID="true"

# Or run with inline variables
pytest tests/ -n 2 \
  --env USE_GRID=true \
  --env GRID_URL=http://localhost:4444/wd/hub
```

### Using `.env` File

```ini
# Selenium Grid Configuration
USE_GRID=true
GRID_URL=http://localhost:4444/wd/hub
BROWSER_NAME=chrome
BROWSER_VERSION=127
```

---

## 3. Browser Matrix Configuration

The browser matrix is defined in `automation/config/browsers.yaml`:

```yaml
browsers:
  chrome:
    remote:
      - version: "127"
        name: "Chrome 127 (Remote)"
        capabilities:
          browserName: "chrome"
          browserVersion: "127"
          platformName: "linux"
      
      - version: "128"
        name: "Chrome 128 (Remote)"
        capabilities:
          browserName: "chrome"
          browserVersion: "128"
          platformName: "linux"
```

---

## 4. Usage Patterns

### Pattern 1: Using Grid in Test Class

```python
from automation.core import BaseSeleniumTest

class TestWithGrid(BaseSeleniumTest):
    """Test using Selenium Grid."""
    
    # Use Grid instead of local browser
    USE_GRID = True
    
    # Optional: specify Grid URL (or use GRID_URL env var)
    GRID_URL = "http://localhost:4444/wd/hub"
    
    # Browser and version from matrix
    BROWSER_NAME = "chrome"
    BROWSER_VERSION = "127"
    
    def test_something(self):
        self.driver.get("https://example.com")
        # Your test code here
```

### Pattern 2: Using CapabilitiesManager

```python
from automation.core import CapabilitiesManager, GridDriverFactory

# Get capabilities from matrix
mgr = CapabilitiesManager()

# Get Chrome 127 capabilities
caps = mgr.get_capabilities("chrome", version="127", execution_mode="remote")
print(caps)
# Output:
# {
#   'browserName': 'chrome',
#   'browserVersion': '127',
#   'platformName': 'linux',
#   ...
# }

# Create driver
factory = GridDriverFactory(grid_url="http://localhost:4444/wd/hub")
driver = factory.create_remote_driver(caps)
driver.get("https://example.com")
driver.quit()
```

### Pattern 3: Matrix Parametrization

```python
import pytest
from automation.core import CapabilitiesManager, GridDriverFactory

mgr = CapabilitiesManager()

# Get full matrix for parametrization
matrix = mgr.get_matrix("remote")

@pytest.mark.parametrize("browser_config", [
    (b, v["version"]) 
    for b, versions in matrix.items() 
    for v in versions
])
def test_on_all_browsers(browser_config):
    """Run this test on all configured browser versions."""
    browser_name, version = browser_config
    
    factory = GridDriverFactory()
    driver = factory.create_driver_from_matrix(browser_name, version)
    
    try:
        driver.get("https://example.com")
        # Test code
    finally:
        driver.quit()
```

---

## 5. Parallel Execution

### Running with Multiple Workers

```bash
# Run with 4 parallel workers
pytest tests/ -n 4 \
  --env USE_GRID=true \
  --env GRID_URL=http://localhost:4444/wd/hub

# Or using pytest.ini
[pytest]
addopts = -n auto --env USE_GRID=true
```

### Report Structure for Parallel Execution

```
automation/reports/
├── runs/
│   └── 20250119_143022/
│       ├── 20250119_143022_worker0/
│       │   ├── allure-results/
│       │   ├── screenshots/
│       │   └── automation.log
│       ├── 20250119_143022_worker1/
│       │   ├── allure-results/
│       │   ├── screenshots/
│       │   └── automation.log
│       └── 20250119_143022_worker2/
├── allure-report.html (merged report)
└── screenshots/ (all runs combined)
```

### Each Worker Gets:

✅ **Isolated Driver**: No sharing between workers
✅ **Isolated Session**: Each worker = separate browser session
✅ **Isolated Directory**: `runs/TIMESTAMP_workerN/`
✅ **Isolated Reports**: Per-worker `allure-results/`
✅ **Merged Report**: Final HTML merges all workers

---

## 6. Running Tests

### Sequential (Local)

```bash
source venv/bin/activate
pytest tests/test_automation_test_store_login.py -v
```

### Sequential (Grid)

```bash
export USE_GRID=true
export GRID_URL=http://localhost:4444/wd/hub
pytest tests/ -v
```

### Parallel (Grid, 4 workers)

```bash
export USE_GRID=true
export GRID_URL=http://localhost:4444/wd/hub
pytest tests/ -n 4 -v
```

### Parallel (Browser Matrix)

```bash
# Run same test on Chrome 127, Chrome 128, Firefox
export USE_GRID=true
export GRID_URL=http://localhost:4444/wd/hub
pytest tests/test_matrix.py::test_on_all_browsers -v
```

---

## 7. Troubleshooting

### Grid Not Reachable

```bash
# Check Grid status
curl http://localhost:4444/status

# Check connectivity in Python
from automation.core import GridDriverFactory
factory = GridDriverFactory(grid_url="http://localhost:4444/wd/hub")
if factory.verify_grid_connectivity():
    print("✓ Grid is reachable")
else:
    print("✗ Grid connection failed")
```

### Session Isolation Issues

✅ Each worker = isolated driver
✅ Each test = new browser session (in setup_method)
✅ No shared cookies/cache between tests
✅ Session ID available in logs

Check logs:
```bash
tail -f automation/reports/runs/20250119_143022_worker0/automation.log
```

### Capabilities Not Found

```bash
# Check available capabilities
from automation.core import CapabilitiesManager
mgr = CapabilitiesManager()

# List browsers
print(mgr.get_available_browsers("remote"))
# Output: ['chrome', 'firefox']

# List versions
print(mgr.get_all_versions("chrome", "remote"))
```

---

## 8. Report Generation

### Reports are automatically generated:

1. **Per-Worker Reports**: `runs/TIMESTAMP_workerN/report.html`
2. **Merged Report**: `automation/reports/allure-report.html`

### View Reports

```bash
# Sequential run
firefox automation/reports/allure-report.html

# Parallel run (merged)
firefox automation/reports/allure-report.html

# Individual worker report
firefox "automation/reports/runs/20250119_143022_worker0/report.html"
```

---

## 9. Advanced: Custom Grid Configuration

### Using Moon (Aerokube)

```bash
# Start Moon container
docker run -d -p 4444:4444 -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aerokube/moon:latest

# Configure in .env
GRID_URL=http://localhost:4444/wd/hub
```

### Using Remote Grid

```bash
# Point to remote Grid
export GRID_URL="http://grid.example.com:4444/wd/hub"
pytest tests/ -n 4 -v
```

---

## 10. Example Test with All Features

```python
import pytest
from automation.core import BaseSeleniumTest, CapabilitiesManager

class TestGridParallel(BaseSeleniumTest):
    """
    Complete example:
    - Uses Selenium Grid
    - Parallel execution
    - Isolated reports per worker
    """
    
    USE_GRID = True
    BROWSER_NAME = "chrome"
    BROWSER_VERSION = "127"
    
    def test_automation_test_store_login(self):
        """Test login on Grid with Chrome 127."""
        # Navigate
        self.navigate_to("https://automationteststore.com/")
        
        # Assert
        self.assert_page_title_contains("practice")
        
        # Take screenshot
        self.take_screenshot("homepage")

# Run with:
# pytest test_grid_parallel.py -n 4 -v --env USE_GRID=true
```

---

## Summary

✅ **Selenium Grid / Moon Support**: Remote WebDriver via GRID_URL
✅ **Browser Matrix**: Chrome 127/128, Firefox, Edge with Capabilities
✅ **Isolated Sessions**: Each worker = separate driver, no sharing
✅ **Isolated Reports**: Per-worker directories + merged HTML report
✅ **Parallel Execution**: 2-4 workers recommended
✅ **Easy Configuration**: Environment variables or .env file

**All requirements satisfied!** 🚀
