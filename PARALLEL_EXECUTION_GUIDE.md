# Parallel Execution & Selenium Grid Integration

## ✅ What's New

Your automation framework now supports:

### 1. **Selenium Grid / Moon** 🌐
- Remote WebDriver execution via GRID_URL
- Support for both Selenium Grid Hub and Moon
- Capabilities management per browser/version
- Custom Grid URLs via environment variables

### 2. **Browser Matrix** 🔄
- Multiple browsers: Chrome, Firefox, Edge
- Multiple versions: 127, 128, latest (for Chrome/Edge)
- Parametrized test execution on all versions
- Per-version Capabilities management from `browsers.yaml`

### 3. **Parallel Execution** ⚡
- Built-in pytest-xdist integration (2-4 workers recommended)
- Each worker = isolated driver session (no sharing)
- Each worker = isolated report directory
- Per-worker Allure results + merged HTML report

### 4. **Isolated Reports** 📊
- Sequential run: Single directory `automation/reports/`
- Parallel run: Per-worker directories `automation/reports/runs/TIMESTAMP_workerN/`
- Automatic HTML report generation
- Merged report combines all workers

---

## 🚀 Quick Start Examples

### 1. Run Tests Locally (Default)

```bash
source venv/bin/activate

# Sequential execution on local browser
pytest tests/test_automation_test_store_login.py -v

# Parallel execution on local browser (2 workers)
pytest tests/test_automation_test_store_login.py -n 2 -v
```

**Result:** `automation/reports/allure-report.html`

---

### 2. Run Tests on Selenium Grid (Sequential)

```bash
# First, start Selenium Grid locally
docker run -d -p 4444:4444 -p 7900:7900 \
  --name selenium-hub \
  selenium/hub:4.15.0

docker run -d -p 5555:5555 \
  --shm-size=2gb \
  -e SE_EVENT_BUS_HOST=localhost \
  -e SE_EVENT_BUS_PUBLISH_PORT=4442 \
  -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 \
  --name chrome-node \
  selenium/node-chrome:4.15.0

# Then run tests
export GRID_URL=http://localhost:4444/wd/hub
export USE_GRID=true

pytest tests/test_automation_test_store_login.py -v

# View report
firefox automation/reports/allure-report.html
```

---

### 3. Run Tests on Grid with Parallel Workers

```bash
# Run with 4 parallel workers on Grid
export GRID_URL=http://localhost:4444/wd/hub
export USE_GRID=true

pytest tests/ -n 4 -v

# Result: 4 workers, each with isolated session
# Reports structure:
# automation/reports/
# ├── runs/
# │   └── 20250119_143022/
# │       ├── 20250119_143022_worker0/allure-results/
# │       ├── 20250119_143022_worker1/allure-results/
# │       ├── 20250119_143022_worker2/allure-results/
# │       └── 20250119_143022_worker3/allure-results/
# └── allure-report.html (MERGED)

firefox automation/reports/allure-report.html
```

---

### 4. Run Same Test on Multiple Browser Versions

```bash
# Start Grid with multiple browser versions
# (Make sure you have Docker containers for Chrome 127, 128, Firefox, etc.)

export GRID_URL=http://localhost:4444/wd/hub
export USE_GRID=true

# Run the grid integration test (parametrized by browser)
pytest tests/test_grid_integration.py::TestGridMultipleVersions -v

# Or run all grid tests
pytest tests/test_grid_integration.py -v
```

---

### 5. Using Browser Matrix in Tests

```python
from automation.core import BaseSeleniumTest

class TestWithMatrix(BaseSeleniumTest):
    USE_GRID = True
    BROWSER_NAME = "chrome"
    BROWSER_VERSION = "127"  # Supports: 127, 128, latest
    
    def test_login(self):
        self.navigate_to("https://automationteststore.com/")
        # Test runs on Chrome 127 on Grid
```

---

### 6. Manual Browser Matrix Configuration

Edit `automation/config/browsers.yaml` to add more versions:

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

## 📋 Configuration Files

### `.env` - Environment Variables

```ini
# Grid Settings
USE_GRID=true                                    # Enable/disable Grid
GRID_URL=http://localhost:4444/wd/hub          # Grid Hub URL

# Parallel Execution
PYTEST_WORKERS=2                                # Number of workers

# Browser Matrix
BROWSER_NAME=chrome                             # Browser: chrome, firefox, edge
BROWSER_VERSION=127                             # Version from matrix
```

### `automation/config/browsers.yaml` - Browser Matrix

Defines:
- Available browsers (chrome, firefox, edge)
- Available versions per browser
- Capabilities per version/platform
- Remote WebDriver configurations

---

## 🔍 Report Viewing

### Sequential Run Report
```bash
firefox automation/reports/allure-report.html
```

### Parallel Run Reports
```bash
# View merged report (all workers combined)
firefox automation/reports/allure-report.html

# View individual worker report
firefox automation/reports/runs/20250119_143022_worker0/report.html
```

---

## 🛠️ Troubleshooting

### Grid Connection Issues

```bash
# Check Grid is running
curl http://localhost:4444/status

# Check Grid URL in code
python -c "
from automation.core import GridDriverFactory
f = GridDriverFactory()
print(f'Grid URL: {f.grid_url}')
print(f'Reachable: {f.verify_grid_connectivity()}')
"
```

### Session Isolation

Each worker gets completely isolated:
- ✅ New driver instance
- ✅ New browser session
- ✅ Separate cookies/cache
- ✅ Independent report directory

Verify in logs:
```bash
# Check worker 0 logs
tail automation/reports/runs/20250119_143022_worker0/automation.log

# Should show Session ID like:
# [INFO] Grid driver created. Session ID: 12345abcde...
```

### Browser Version Not Found

```bash
# List available versions
python -c "
from automation.core import CapabilitiesManager
mgr = CapabilitiesManager()
for v in mgr.get_all_versions('chrome', 'remote'):
    print(f'  {v[\"version\"]}: {v[\"name\"]}')
"
```

---

## 📊 Real-World Examples

### Example 1: Parallel Login Tests on Grid

```bash
# Setup Grid (Chrome + Firefox nodes)
docker-compose up -d

# Run tests
export GRID_URL=http://localhost:4444/wd/hub
export USE_GRID=true

pytest tests/test_automation_test_store_login.py -n 4 -v

# Result: 4 parallel workers, all on Grid
# Each worker: isolated session, isolated report
# Final: merged HTML report
```

### Example 2: Matrix Testing (All Chrome Versions)

```bash
# Setup Grid with Chrome 127 + 128 nodes

# Create test class
class TestChromeMatrix(BaseSeleniumTest):
    USE_GRID = True
    
    @pytest.mark.parametrize("version", ["127", "128"])
    def test_login(self, version):
        self.BROWSER_VERSION = version
        # Test code...

# Run
pytest test_matrix.py -v
# Runs on Chrome 127, then Chrome 128
```

### Example 3: Parallel Matrix Testing

```bash
# Most powerful: Parallel + Matrix

# Run same tests on Chrome 127, 128, Firefox in parallel
export GRID_URL=http://localhost:4444/wd/hub
export USE_GRID=true

pytest tests/ -n auto -v
# -n auto = number of workers = number of CPU cores
# Each worker runs subset of tests on Grid
# Tests parametrized by browser version
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `automation/core/grid_driver_factory.py` | Grid/Moon driver factory |
| `automation/core/base_test.py` | Base test class with Grid support |
| `automation/config/browsers.yaml` | Browser matrix configuration |
| `conftest.py` | Pytest hooks for parallel execution & reports |
| `.env` | Environment variables (Grid URL, browser, etc) |
| `tests/test_grid_integration.py` | Grid integration examples |
| `GRID_INTEGRATION_GUIDE.md` | Detailed Grid usage guide |

---

## 🎯 Requirements Checklist

- ✅ **Selenium Grid / Moon Support**: Remote WebDriver via GRID_URL
- ✅ **Browser Matrix**: Chrome 127/128, Firefox, Edge with Capabilities per version
- ✅ **Session Isolation**: Each worker = separate driver, no sharing
- ✅ **Isolated Reports**: Per-worker directories + merged HTML report
- ✅ **Parallel Execution**: pytest-xdist with 2-4 workers recommended

---

## 📖 Next Steps

1. **Read the detailed guide**: `GRID_INTEGRATION_GUIDE.md`
2. **Review examples**: `tests/test_grid_integration.py`
3. **Customize matrix**: Edit `automation/config/browsers.yaml`
4. **Add Grid support to existing tests**: Set `USE_GRID = True` in test class
5. **Run parallel**: `pytest tests/ -n 4 --env USE_GRID=true`

---

## 🚀 That's It!

Your automation framework is now fully equipped for:
- Local browser automation
- Remote Selenium Grid execution
- Parallel testing with isolated sessions
- Multiple browser/version testing
- Professional HTML reporting with per-worker details

Happy testing! 🎉
