# 🚀 Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Directory Structure

```
automation-project1/
├── automation/               # Framework core
│   ├── core/               # Infrastructure (logger, retry, locator, driver, base_page)
│   ├── utils/              # Support functions (human_actions, random_utils)
│   ├── config/             # Configuration (YAML)
│   ├── data/               # Test data (JSON)
│   ├── pages/              # Page Objects (user-created)
│   └── __init__.py         # Package initialization
│
├── tests/                   # Test cases (user-created)
├── reports/                 # Output (logs, screenshots, traces, videos)
├── conftest.py             # Global pytest configuration
├── pytest.ini              # Pytest settings
├── requirements.txt        # Dependencies
├── README.md               # Full documentation
└── .gitignore              # Git ignore rules
```

## Creating a Page Object

**File: `automation/pages/my_page.py`**

```python
from automation.core import BasePage, SmartLocator, Locator, LocatorType

class MyPage(BasePage):
    """My application page."""
    
    # Define UI elements with fallback selectors
    LOGIN_BUTTON = SmartLocator(
        Locator(LocatorType.CSS, "#login", "Login button"),
        Locator(LocatorType.XPATH, "//button[@id='login']", "Login by XPath"),
    )
    
    EMAIL_INPUT = SmartLocator(
        Locator(LocatorType.CSS, "[type='email']", "Email input"),
    )
    
    # High-level business methods
    async def login(self, email: str, password: str) -> None:
        """Login with email and password."""
        await self.type(self.EMAIL_INPUT, email)
        await self.click(self.LOGIN_BUTTON)
        await self.wait_for_navigation()
```

## Writing a Test

**File: `tests/test_my_app.py`**

```python
import pytest
from automation.core import DriverFactory, BasePage, get_logger, AutomationLogger
from automation.pages.my_page import MyPage

logger = get_logger(__name__)

@pytest.fixture
async def setup_teardown():
    """Setup and teardown."""
    # Setup
    factory = DriverFactory()
    await factory.initialize()
    browser = await factory.create_browser()
    context = await factory.create_context(browser)
    page = await factory.create_page(context)
    
    # Create page object
    my_page = MyPage(BasePage(page))
    
    yield my_page
    
    # Teardown
    await factory.cleanup_page(page)
    await factory.cleanup_context(context)
    await factory.cleanup_browser(browser)
    await factory.cleanup()

@pytest.mark.asyncio
async def test_login(setup_teardown):
    """Test login."""
    my_page = setup_teardown
    
    await my_page.navigate("https://example.com/login")
    await my_page.login("user@example.com", "password123")
    
    # Verify
    current_url = await my_page.get_current_url()
    assert "dashboard" in current_url
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_my_app.py::test_login -v

# Run with detailed logging
pytest tests/ -v -s --log-cli-level=DEBUG

# Run with parallel execution (requires pytest-xdist)
pytest tests/ -n auto
```

## Configuration

**`automation/config/env.yaml`** - Modify these settings:

```yaml
headless: false              # Run browser visibly
trace: true                  # Record Playwright traces
video: false                 # Record videos
screenshot_on_failure: true

timeouts:
  page_load: 30
  element_visibility: 15
  element_interaction: 10

human_behavior:
  enabled: true              # Anti-bot delays
  typing_speed_min_ms: 20
  typing_speed_max_ms: 100
  click_delay_min_ms: 100
  click_delay_max_ms: 500
```

## Key Concepts

### SmartLocator
Define multiple fallback selectors for robustness:

```python
MY_ELEMENT = SmartLocator(
    Locator(LocatorType.CSS, "#element-id", "Primary selector"),
    Locator(LocatorType.XPATH, "//div[@class='element']", "Fallback 1"),
    Locator(LocatorType.TEXT, "text=Click Me", "Fallback 2"),
)
```

### BasePage Methods
- `find()` - Find element with fallback
- `click()` - Click with human delays
- `type()` - Character-by-character typing
- `fill()` - Fast input fill
- `wait_for_element()` - Wait for state
- `get_text()` - Get element text
- `get_attribute()` - Get attribute
- `scroll_to_element()` - Scroll into view
- `navigate()` - Go to URL
- `refresh()`, `go_back()`, `go_forward()`

### Automatic Features
✅ Retry with exponential backoff  
✅ Human-like behavior (delays, typing speed)  
✅ SmartLocator fallback  
✅ Comprehensive logging  
✅ Screenshots on failure  
✅ Playwright traces & video recording  

## Troubleshooting

### Playwright not installed
```bash
playwright install
```

### Import errors
Make sure you're in the project root and run:
```bash
pip install -r requirements.txt
python3 -c "from automation.core import BasePage; print('OK')"
```

### Test timeouts
Increase timeouts in `automation/config/env.yaml`:
```yaml
timeouts:
  element_visibility: 30  # Increase from 15
```

## Next Steps

1. Create your Page Objects in `automation/pages/`
2. Write tests in `tests/`
3. Run with `pytest tests/ -v`
4. Check logs in `reports/automation.log`
5. Review screenshots in `reports/screenshots/`

## Documentation

See `README.md` for complete architecture documentation.

---

**Happy testing! 🎉**
