# Browser Matrix Parallel Execution Guide

## Overview

The browser matrix feature enables running tests in parallel across multiple browser versions and types. Each test runs with a different browser configuration, in isolated environments, with their own WebDriver sessions and reports.

**Key Capability:** Run 5 tests × 3 browser configs = 15 test runs, all in parallel with `-n` workers.

---

## Quick Start

### 1️⃣ Run Tests on Same Browser (Parallel Only)

```bash
# Run tests with 4 workers on Chrome 127 (from .env)
pytest tests/ -n 4 -v
```

**Result:** 4 worker processes, each with its own Chrome 127 instance, tests distributed across workers.

---

### 2️⃣ Run Tests on Multiple Browsers (Matrix Parallel)

```bash
# Run tests on 3 browsers with 2 parallel workers
pytest tests/test_browser_matrix.py -n 2 --browser-matrix="chrome:127,chrome:128,firefox:121"
```

**Result:**
- Test runs 3 times (once per browser)
- Each run distributed across 2 workers
- Reports in: `automation/reports/20260120_112942_matrix_chrome_127-chrome_128-firefox_121/`

---

## How It Works

### Infrastructure Config (From .env)
```env
USE_GRID=false
GRID_URL=http://localhost:4444/wd/hub
BROWSER_NAME=chrome
BROWSER_VERSION=127
```

### Browser Matrix Parametrization

When you use `--browser-matrix`:

1. **Parse**: `"chrome:127,chrome:128,firefox:121"` → List of `BrowserConfig` objects
2. **Generate Tests**: For each config, create a parametrized test variant
3. **Override Env**: Each variant gets unique `BROWSER_NAME` and `BROWSER_VERSION`
4. **Execute**: All variants run in parallel with pytest-xdist

### Example Execution Flow

```
pytest tests/test_browser_matrix.py -n 2 --browser-matrix="chrome:127,chrome:128"
│
├─ Collect & Parametrize
│  ├─ test_browser_matrix_demo[chrome_127-None]
│  └─ test_browser_matrix_demo[chrome_128-None]
│
├─ Worker 0 (gw0)
│  └─ chrome_127 test
│     ├─ Set BROWSER_NAME=chrome, BROWSER_VERSION=127
│     ├─ Initialize Chrome 127 driver
│     ├─ Run test
│     └─ Close driver
│
└─ Worker 1 (gw1)
   └─ chrome_128 test
      ├─ Set BROWSER_NAME=chrome, BROWSER_VERSION=128
      ├─ Initialize Chrome 128 driver
      ├─ Run test
      └─ Close driver
```

---

## Browser Matrix Command Line

### Syntax

```bash
pytest [TEST_FILES] -n [WORKERS] --browser-matrix="browser:version,browser:version,..."
```

### Parameters

- **TEST_FILES**: Tests to run (only tests using `browser_config` fixture are parametrized)
- **-n WORKERS**: Number of parallel workers (pytest-xdist)
- **--browser-matrix**: Comma-separated `browser:version` pairs

### Examples

```bash
# Chrome only - 2 versions in parallel with 2 workers
pytest tests/test_browser_matrix.py -n 2 --browser-matrix="chrome:127,chrome:128"

# All browsers - 3 browsers × 5 tests with 3 workers
pytest tests/test_browser_matrix.py -n 3 --browser-matrix="chrome:127,firefox:121,edge:127"

# Browser matrix without parallelism (sequential)
pytest tests/test_browser_matrix.py --browser-matrix="chrome:127,chrome:128,firefox:121"

# Mix: 2 Chrome versions + Firefox with 4 workers
pytest tests/test_browser_matrix.py -n 4 --browser-matrix="chrome:127,chrome:128,firefox:121"
```

---

## Available Browsers

From `automation/config/browsers.yaml`:

### Chrome
- `chrome:127`
- `chrome:128`
- `chrome:latest`

### Firefox
- `firefox:121`
- `firefox:122`
- `firefox:latest`

### Edge
- `edge:127`
- `edge:128`

---

## How to Use in Your Tests

### Option 1: Fixture in Test (Simple)

```python
import pytest
from automation.core import BaseSeleniumTest

class MyTests(BaseSeleniumTest):
    @pytest.mark.parametrize("dummy", [None])  # Required for browser_config
    def test_login(self, browser_config, dummy):
        """Test that runs on each browser in matrix."""
        self.driver.get("https://example.com")
        # Test code...
```

### Option 2: Fixture Not Used (Regular Tests)

```python
class MyTests(BaseSeleniumTest):
    def test_login(self):
        """Regular test - NOT parametrized by matrix.
        Still uses default browser from .env
        """
        self.driver.get("https://example.com")
        # Test code...
```

**Only tests that explicitly use the `browser_config` fixture are parametrized.**

### Option 3: Access Current Config

```python
class MyTests(BaseSeleniumTest):
    @pytest.mark.parametrize("dummy", [None])
    def test_login(self, browser_config, dummy):
        """Access the current browser config."""
        if browser_config:
            print(f"Running on: {browser_config}")
            # Output: Running on: chrome:127
        
        # Browser is already configured by fixture
        self.driver.get("https://example.com")
```

---

## Report Organization

Each run gets its own timestamped directory:

```
automation/reports/
├─ 20260120_112912/                              # No matrix
├─ 20260120_112942_matrix_chrome_127-chrome_128/ # Matrix run
│  ├─ 20260120_112942_matrix_chrome_127-chrome_128_gw0/
│  │  ├─ allure-results/
│  │  ├─ screenshots/
│  │  ├─ automation.log
│  │  └─ allure-report/
│  │
│  └─ 20260120_112942_matrix_chrome_127-chrome_128_gw1/
│     ├─ allure-results/
│     ├─ screenshots/
│     ├─ automation.log
│     └─ allure-report/
```

**Benefits:**
- Each worker/browser combo has isolated reports
- Allure results don't conflict
- Screenshots/logs organized per browser
- Easy to compare results across browsers

---

## Implementation Details

### New Files Created

#### `automation/utils/browser_matrix.py`
- `BrowserConfig` class: Represents single browser:version pair
- `BrowserMatrix` class: Utilities for parsing/validating matrices
- Functions:
  - `parse_matrix_string()`: Parse CLI format
  - `validate_against_browsers_yaml()`: Verify config exists
  - `generate_parametrize_ids()`: Create pytest IDs
  - `get_env_overrides()`: Environment variables for each config

#### `tests/test_browser_matrix.py`
- Demo test showing browser matrix functionality
- Example of using `browser_config` fixture
- Can be run with different matrix configurations

### Modified Files

#### `conftest.py`
- `pytest_addoption()`: Adds `--browser-matrix` CLI option
- `pytest_generate_tests()`: Parametrizes tests with browser configs
- `browser_config` fixture: Manages environment variable overrides
- `pytest_configure()`: Includes matrix info in report path

---

## Performance Considerations

### Scaling Rules

For optimal performance with `-n` workers:

```
Total Test Runs = Number of Tests × Number of Matrix Configs

Example:
- 5 tests × 3 browser configs = 15 test runs
- With -n 4 workers: ~4 runs per worker (balanced)
- Estimated time: 1 run time (if parallelization is perfect)
```

### Recommended -n Values

| Matrix Size | Recommended Workers | Notes |
|------------|-------------------|-------|
| No matrix (1 browser) | 4-8 | Per available CPU cores |
| 2 browsers | 2-4 | 2 browsers × 2 workers = 4 parallel |
| 3 browsers | 2-3 | 3 × 2 = 6 or 3 × 3 = 9 parallel |
| 4+ browsers | 2-4 | Keep total parallel tasks ≤ CPU cores |

### Example Timing

```
Scenario: 5 tests × 3 browser configs = 15 total runs

NO MATRIX (single browser):
  - 1 test = 5 seconds
  - -n 1: 25 seconds
  - -n 2: 13 seconds (2× speedup)
  - -n 4: ~7 seconds (3.5× speedup)

WITH MATRIX (3 browsers):
  - 1 test on 1 browser = 5 seconds
  - Sequential (no -n): 75 seconds (15 runs × 5 sec)
  - -n 2: ~38 seconds (7-8 runs per worker)
  - -n 3: ~25 seconds (5 runs per worker)
  - -n 4: ~19 seconds (3-4 runs per worker)
  - -n 5: ~15 seconds (3 runs per worker)
```

---

## Troubleshooting

### Error: Invalid browser configuration

```
Invalid browser matrix format: 'chrome:99'
```

**Solution:** Use version from browsers.yaml (127, 128, 121, 122, etc.)

```bash
# ✅ Correct
pytest tests/ --browser-matrix="chrome:127,firefox:121"

# ❌ Wrong - no version 99
pytest tests/ --browser-matrix="chrome:99"
```

### Error: Function uses no argument 'browser_config'

```
In test_login: function uses no argument 'browser_config'
```

**Solution:** Add `browser_config` fixture if you want matrix parametrization:

```python
# ✅ With matrix parametrization
def test_login(self, browser_config, dummy):
    pass

# ✅ Without matrix (uses default browser from .env)
def test_login(self):
    pass
```

### Test not parametrized

**Issue:** `--browser-matrix` set but test only runs once

**Solution:** Test must use `browser_config` fixture:

```python
@pytest.mark.parametrize("dummy", [None])  # Dummy param helper
def test_login(self, browser_config, dummy):  # Add browser_config
    pass
```

---

## Advanced Usage

### Running Tests on Grid with Matrix

```bash
# Matrix on Selenium Grid
USE_GRID=true GRID_URL=http://localhost:4444/wd/hub \
  pytest tests/ -n 4 --browser-matrix="chrome:127,firefox:121"
```

Each test run will:
1. Request browser from Grid
2. Use specified version
3. Run in parallel

### Custom Test Selection

```bash
# Only run specific tests in matrix
pytest tests/test_browser_matrix.py::TestBrowserMatrix::test_browser_matrix_demo \
  -n 2 --browser-matrix="chrome:127,chrome:128"

# With markers
pytest tests/ -m smoke -n 2 --browser-matrix="chrome:127,firefox:121"
```

### Environment Variable Inspection

Each test can inspect its current browser config:

```python
def test_login(self, browser_config, dummy):
    if browser_config:
        browser_name = browser_config.browser_name  # "chrome"
        version = browser_config.browser_version      # "127"
        display = browser_config.display_name         # "chrome:127"
        print(f"Running on {display}")
```

---

## Summary

✅ **Same Browser Parallel:** `pytest tests/ -n 4`
- 4 workers, same browser, tests distributed

✅ **Different Browsers Parallel:** `pytest tests/ -n 2 --browser-matrix="chrome:127,chrome:128,firefox:121"`
- 3 browser configs × 2 workers = 6 parallel runs
- Each test runs 3 times (once per browser)
- Reports include browser info in path

✅ **No Test Code Changes:**
- Infrastructure-level configuration
- Tests use infrastructure automatically
- Just add optional `browser_config` fixture if needed

✅ **Per-Worker Isolation:**
- Each worker gets isolated WebDriver
- Each matrix variant gets isolated environment
- Each run gets isolated report directory

---

## More Resources

- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)
- [Selenium Grid Documentation](https://www.selenium.dev/documentation/grid/)
- [Allure Report Documentation](https://docs.qameta.io/allure/)
- Project: `automation/utils/browser_matrix.py`
- Demo: `tests/test_browser_matrix.py`
