# Test Automation Architecture

## Project Structure

```
automation-project1/
├── automation/
│   ├── core/
│   │   ├── base_test.py          ← BaseSeleniumTest (lifecycle, common methods)
│   │   └── __init__.py
│   ├── steps/                     ← Reusable test steps
│   │   ├── __init__.py            ← Central exports
│   │   ├── navigation_steps.py    ← navigate_to_ebay()
│   │   ├── verification_steps.py  ← verify_*() assertions
│   │   ├── element_steps.py       ← click_element(), type_text()
│   │   ├── utility_steps.py       ← helpers (screenshot, wait, etc.)
│   │   └── ebay_steps.py          ← re-exports
│   └── reports/                   ← Output directory (centralized)
│       ├── allure-results/        ← Allure JSON results
│       ├── screenshots/           ← Test screenshots
│       ├── allure-report.html     ← Allure HTML report
│       └── automation.log         ← Test logs
│
├── tests/
│   ├── test_login.py              ← Test suite using BaseSeleniumTest
│   └── conftest.py                ← Pytest fixtures & hooks
│
├── pytest.ini                      ← Pytest configuration
├── conftest.py                     ← Global configuration
└── requirements.txt                ← Dependencies
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Test Execution                        │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  pytest runs test (e.g., test_login.py)                 │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  BaseSeleniumTest.setup_method()                        │
│  - Creates undetected ChromeDriver                      │
│  - Initializes anti-bot protection                      │
│  - Sets implicit/page load timeouts                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Test calls reusable steps:                             │
│  - navigate_to_ebay()                                   │
│  - verify_page_title()                                  │
│  - take_screenshot()                                    │
│  - test_success_message()                               │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  BaseSeleniumTest.teardown_method()                     │
│  - Closes browser                                       │
│  - Takes error screenshots if needed                    │
│  - Cleans up resources                                  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Allure integration:                                    │
│  - Attaches screenshots                                 │
│  - Logs step details                                    │
│  - Generates report                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Output to automation/reports/                          │
│  - allure-report.html                                   │
│  - automation.log                                       │
│  - screenshots/                                         │
└─────────────────────────────────────────────────────────┘
```

## Step Categories

### Navigation Steps (navigation_steps.py)
```
navigate_to_ebay(driver, url)
  ├─ driver.get(url)
  ├─ wait 3 seconds (human-like)
  └─ return current_url
```

### Verification Steps (verification_steps.py)
```
verify_ebay_homepage(driver)
  ├─ Check URL contains "ebay.com"
  ├─ Check title contains "eBay"
  └─ Attach report to Allure

verify_page_title(driver, expected_text)
  ├─ Get page title
  ├─ Assert text in title
  └─ Attach to Allure

verify_page_url(driver, expected_text)
  ├─ Get current URL
  ├─ Assert text in URL
  └─ Attach to Allure
```

### Element Steps (element_steps.py)
```
click_element(driver, by, value, name)
  ├─ Wait 0.3s (pre-delay)
  ├─ Find element
  ├─ Click element
  └─ Wait 0.5s (post-delay)

type_text(driver, by, value, text, name)
  ├─ Find element
  ├─ Clear field
  ├─ Type character-by-character (0.05s each)
  └─ Wait 0.3s (post-delay)
```

### Utility Steps (utility_steps.py)
```
take_screenshot(driver, screenshot_func, name)
  └─ Save to automation/reports/screenshots/

get_page_title(driver) → str
get_current_url(driver) → str
get_page_source(driver) → str

wait_for_element_to_appear(driver, by, value, timeout)
wait_for_element_clickable(driver, by, value, timeout)

refresh_page(driver)
human_delay(min, max)
test_success_message(test_name, message)
```

## Key Features

### ✅ Anti-Bot Protection
- Undetected ChromeDriver
- Custom Chrome options:
  - `--disable-blink-features=AutomationControlled`
  - `--user-agent=Mozilla/5.0...`
  - `--disable-gpu`
  - `--no-sandbox`
  - etc.

### ✅ Human-Like Behavior
- Random delays between actions
- Character-by-character typing
- Pre/post-action delays
- Natural page load waits

### ✅ Test Reporting
- Allure step decorators
- Screenshots on failure
- Log attachment
- HTML report generation

### ✅ Centralized Output
- All reports → `automation/reports/`
- Screenshots in subdirectory
- Logs with timestamps
- Clean, organized structure

### ✅ Reusable Components
- All steps importable from `automation.steps`
- No duplicate code
- Easy to extend with new steps
- Backward compatible

## Adding New Tests

```python
from automation.core import BaseSeleniumTest
from automation.steps import navigate_to_ebay, verify_page_title

class TestNewFeature(BaseSeleniumTest):
    def test_something(self):
        navigate_to_ebay(self.driver)
        verify_page_title(self.driver, "eBay")
        # Your test logic here
        self.take_screenshot("final_state")
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_login.py

# Run with verbose output
pytest tests/test_login.py -v

# Generate Allure report
pytest tests/test_login.py --alluredir=automation/reports/allure-results

# View Allure report
allure serve automation/reports/allure-results
```

## Configuration Files

### pytest.ini
- Allure results directory: `automation/reports/allure-results`
- Screenshot directory: `automation/reports/screenshots`
- Default markers and options

### conftest.py
- Creates report directories
- Configures logging
- Session hooks for report generation

### automation/reports/conftest.py
- Allure report generation hook
- Runs after all tests complete

## Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_login.py
```
