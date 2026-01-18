# Smart Locator Architecture

## System Design

```
┌─────────────────────────────────────────────────────────┐
│                    TEST LAYER                           │
│  test_ebay_login_smart_locators.py                      │
│                                                          │
│  @allure.feature("eBay Login")                           │
│  def test_ebay_login_with_smart_locators():             │
│      page = EbayLoginPage(driver)                       │
│      page.click_sign_in()      # Simple API             │
│      page.enter_email(email)                            │
│      page.click_continue()                              │
│      page.enter_password(pwd)                           │
│      assert page.is_on_ebay_home()                      │
│                                                          │
│  ✅ Clean, readable, no technical details              │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│               PAGE OBJECT LAYER                         │
│  automation/pages/ebay_login_page.py                    │
│                                                          │
│  class EbayLoginPage:                                   │
│      def __init__(self, driver):                        │
│          self.finder = SmartLocatorFinder(driver)       │
│                                                          │
│      def click_sign_in(self):                           │
│          self.finder.click_element(                     │
│              EbayLoginLocators.SIGN_IN_BUTTON,          │
│              description="Sign In button"               │
│          )                                              │
│                                                          │
│      def enter_email(self, email):                      │
│          self.finder.type_text(                         │
│              EbayLoginLocators.EMAIL_INPUT,             │
│              text=email,                                │
│              human_like=True                            │
│          )                                              │
│                                                          │
│  class EbayLoginLocators:                               │
│      SIGN_IN_BUTTON = [                                 │
│          ("xpath", "//a[contains(text(), 'Sign in')]"), │
│          ("xpath", "//a[@href and contains(...)]"),     │
│          ("css", "a[data-test-id='topnav-signin']"),    │
│      ]                                                  │
│      EMAIL_INPUT = [...] # 4 alternatives              │
│      PASSWORD_INPUT = [...] # 4 alternatives           │
│      SIGNIN_BUTTON = [...] # 4 alternatives            │
│                                                          │
│  ✅ Defines all locator alternatives                   │
│  ✅ Clean method API                                   │
│  ✅ Locators organized by element                      │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│           SMART LOCATOR FINDER LAYER                    │
│  automation/utils/smart_locator_finder.py               │
│                                                          │
│  class SmartLocatorFinder:                              │
│                                                          │
│  def find_element(locators, description, timeout=10):   │
│      for attempt_num, (by, selector) in enumerate(...):│
│          try:                                           │
│              element = WebDriverWait(...).until(...)    │
│              # Log success                             │
│              allure.attach(f"✅ Attempt {attempt_num}")  │
│              return element                            │
│          except TimeoutException:                       │
│              # Try next locator                        │
│              pass                                       │
│      # All failed                                       │
│      self._take_screenshot(description)                │
│      raise TimeoutError(f"Element {description}...")   │
│                                                          │
│  def click_element(locators, description):              │
│      element = self.find_element(...)                  │
│      # Pre-click delay (human-like)                    │
│      sleep(0.5)                                         │
│      try:                                               │
│          element.click()                                │
│      except:                                            │
│          # Fallback to JS click                        │
│          self.driver.execute_script(...)               │
│      sleep(1.0)  # Post-click delay                    │
│                                                          │
│  def type_text(locators, text, human_like=True):       │
│      element = self.find_element(...)                  │
│      element.clear()                                    │
│      if human_like:                                     │
│          for char in text:                             │
│              element.send_keys(char)                   │
│              sleep(0.05)  # Per-character delay        │
│      else:                                              │
│          element.send_keys(text)                       │
│                                                          │
│  def _take_screenshot(self, name):                      │
│      path = f"reports/screenshots/{name}.png"          │
│      self.driver.save_screenshot(path)                 │
│      allure.attach_file(path, ...)                     │
│                                                          │
│  ✅ Fallback loop tries all locators                   │
│  ✅ Detailed logging (attempt N/M)                     │
│  ✅ Screenshots on failure                             │
│  ✅ Human-like delays                                  │
│  ✅ Allure integration                                 │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              SELENIUM WEBDRIVER                         │
│  undetected-chromedriver + selenium.webdriver           │
│                                                          │
│  - Browser control                                      │
│  - Element finding                                      │
│  - Click/type actions                                  │
│  - Screenshot capture                                  │
└─────────────────────────────────────────────────────────┘
```

## Execution Flow

### Click with Fallback Example

```
page.click_sign_in()
    ↓
page.finder.click_element(
    locators=[
        ("xpath", "//a[contains(text(), 'Sign in')]"),
        ("xpath", "//a[@href and contains(...)]"),
        ("css", "a[data-test-id='topnav-signin']"),
    ],
    description="Sign In button"
)
    ↓
SmartLocatorFinder.click_element():
    ↓
    Pre-click delay (0.5s)
    ↓
    find_element(locators=[...]):
        ↓
        Attempt 1: Try ("xpath", "//a[contains(text(), 'Sign in')]")
            ↓
            WebDriverWait(10s).until(EC.presence_of_element_located(...))
            ↓ FAIL? (TimeoutException)
            ↓
        Attempt 2: Try ("xpath", "//a[@href and contains(...)]")
            ↓
            WebDriverWait(10s).until(EC.presence_of_element_located(...))
            ↓ FAIL? (NoSuchElementException)
            ↓
        Attempt 3: Try ("css", "a[data-test-id='topnav-signin']")
            ↓
            WebDriverWait(10s).until(EC.presence_of_element_located(...))
            ↓ SUCCESS! ✅
            ↓
            allure.attach("✅ SUCCESS: attempt 3/3")
            return element
    ↓
    element.click()  (or JS click if fails)
    ↓
    Post-click delay (1.0s)
    ↓
    allure.attach("✅ Clicked Sign In button")
    ↓
test continues to next step
```

### Type with Fallback Example

```
page.enter_email("user@example.com")
    ↓
page.finder.type_text(
    locators=[
        ("id", "userid"),
        ("name", "userid"),
        ("xpath", "//input[@id='userid']"),
        ("xpath", "//input[@type='email']"),
    ],
    text="user@example.com",
    human_like=True
)
    ↓
SmartLocatorFinder.type_text():
    ↓
    find_element() → returns input element
    ↓
    element.clear()
    ↓
    For each character in "user@example.com":
        ↓
        element.send_keys(char)  # Send single character
        sleep(0.05)  # 50ms delay
    ↓
    allure.attach("✅ Typed: user@example.com (28 chars)")
    ↓
test continues
```

## Logging Structure

### Allure Attachments

```
Test: test_ebay_login_with_smart_locators
├── Step 1: Navigate to eBay
│   ├── Attachment: navigate_log
│   └── Screenshot: step1.png
├── Step 2: Click Sign In
│   ├── Attachment: ✅ SUCCESS: attempt 1/3 - xpath matched
│   └── Screenshot: step2.png
├── Step 3: Enter Email
│   ├── Attachment: ✅ Typed: user@example.com (28 chars)
│   └── Screenshot: step3.png
├── Step 4: Click Continue
│   ├── Attachment: ✅ SUCCESS: attempt 2/3 - xpath fallback worked
│   └── Screenshot: step4.png
├── Step 5: Enter Password
│   ├── Attachment: ✅ Typed: ••••• (11 chars)
│   └── Screenshot: step5.png
├── Step 6: Submit
│   ├── Attachment: ✅ SUCCESS: attempt 1/4 - id matched
│   └── Screenshot: step6.png
├── Step 7: Verify Result
│   ├── Attachment: ✅ Home page loaded
│   └── Screenshot: step7.png
└── Test Result: PASSED ✅ (54.90s)
```

## Error Scenario

```
page.click_sign_in()
    ↓
SmartLocatorFinder.click_element():
    ↓
    find_element():
        ↓
        Attempt 1 (10s): TIMEOUT
        ❌ TimeoutException
        ↓
        Attempt 2 (10s): NOT FOUND
        ❌ NoSuchElementException
        ↓
        Attempt 3 (10s): STALE
        ❌ StaleElementReferenceException
        ↓
        All attempts failed!
        ↓
        _take_screenshot("element_not_found_Sign In button")
        ↓
        Allure attachment: Failed_Sign_In_button.png
        ↓
        Raise TimeoutError with detailed log
        ↓

Test Result: FAILED ❌
Allure shows:
  - Which locators were tried (all 3)
  - Which attempt failed (which error, timeout, etc.)
  - Screenshot of page state when it failed
  - Full error log for debugging
```

## Data Flow

```
Input: page.click_sign_in()
    ↓
SmartLocatorFinder.click_element(
    locators=[tuple, tuple, tuple],
    description="Sign In button"
)
    ↓
Process:
    1. Loop through locators
    2. Try WebDriverWait with each
    3. Handle exceptions
    4. Log each attempt
    5. Return element or raise
    ↓
Output to Allure:
    - Attempt log: "attempt N/total"
    - Success/failure: "✅/❌"
    - Locator used: selector text
    - Screenshot: page state
    ↓
Test continues or fails
```

## Integration Points

### 1. Selenium WebDriver
- Provides element location
- Performs clicks/types
- Captures screenshots

### 2. Allure Pytest
- Attachments via `allure.attach()`
- Screenshot files
- Step decorators
- Test metadata

### 3. pytest
- Test execution
- Fixtures (driver)
- Session management

### 4. undetected-chromedriver
- Anti-bot bypassing
- Browser automation

## Component Reusability

SmartLocatorFinder can be used with ANY page:

```python
# Create new Page Object
class AmazonLoginPage:
    def __init__(self, driver):
        self.finder = SmartLocatorFinder(driver)
    
    SEARCH_BOX = [
        ("id", "twotabsearchtextbox"),
        ("name", "field-keywords"),
        ("xpath", "//input[@placeholder='Search Amazon']"),
    ]
    
    def search(self, query):
        self.finder.type_text(
            self.SEARCH_BOX,
            query,
            description="Amazon search box"
        )

# Same framework, different page
page = AmazonLoginPage(driver)
page.search("laptop")  # Fallbacks work automatically
```

## Performance Characteristics

| Scenario | Attempts | Time |
|----------|----------|------|
| First locator works | 1 | ~1s (with delays) |
| Second locator works | 2 | ~2s (with retries) |
| Third locator works | 3 | ~3s (with retries) |
| All fail (timeout 10s) | 3 | ~30s (3 × 10s) |
| Visible but not clickable | 1 | Fallback to JS click |

## Summary

```
┌─────────────────────────────────────┐
│    Clean Test Code                  │
│  page.click_sign_in()               │
└──────────────┬──────────────────────┘
               ↓ (no technical details)
┌─────────────────────────────────────┐
│  Page Object with Locators          │
│  EbayLoginLocators.SIGN_IN_BUTTON   │
└──────────────┬──────────────────────┘
               ↓ (clean API)
┌─────────────────────────────────────┐
│  SmartLocator with Fallbacks        │
│  Try 1, 2, 3... until success       │
│  Log each attempt                   │
│  Screenshot on failure              │
└──────────────┬──────────────────────┘
               ↓ (automatic retry)
┌─────────────────────────────────────┐
│  Selenium WebDriver                 │
│  Browser control                    │
└─────────────────────────────────────┘
```

✅ **Result: Robust, maintainable, enterprise-grade automation**
