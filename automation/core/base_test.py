"""
Base Test Class - Foundation for All Selenium Tests
====================================================

קובץ תשתית מרכזי שכל טסט של Selenium יורש ממנו.

תכונות:
✓ Anti-bot protection (undetected-chromedriver)
✓ Browser launch with optimized options
✓ Allure reporting integration
✓ Auto cleanup
✓ Error handling & screenshots
✓ Human-like delays
✓ Logging

שימוש:
    from automation.core.base_test import BaseSeleniumTest
    
    class TestEBay(BaseSeleniumTest):
        def test_login(self):
            self.driver.get("https://www.ebay.com")
            # Test code here
            # Cleanup happens automatically!
"""

import time
import os
from typing import Optional
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure

from automation.core.logger import get_logger

logger = get_logger(__name__)


class TestExecutionTracker:
    """
    Tracks test execution steps and generates detailed reports.
    Used by all tests to log steps with timing and locator information.
    """
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.steps = []
        self.start_time = datetime.now()
        self.step_number = 1
    
    def log_step(self, name: str, details: str = ""):
        """Log a single step with optional details."""
        step_info = {
            "number": self.step_number,
            "name": name,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.steps.append(step_info)
        self.step_number += 1
    
    def get_formatted_report(self) -> str:
        """Generate formatted step report."""
        report = "📋 TEST EXECUTION STEPS - DETAILED BREAKDOWN\n"
        report += "=" * 80 + "\n\n"
        
        for step in self.steps:
            num = step["number"]
            name = step["name"]
            details = step["details"]
            
            report += f"┌─ STEP {num}: {name}\n"
            if details:
                for line in details.split("\n"):
                    if line.strip():
                        report += f"│  {line}\n"
            report += f"└─ ✅ Completed\n\n"
        
        return report
    
    def attach_to_allure(self):
        """Attach step report and timing to Allure."""
        # Steps report
        steps_report = self.get_formatted_report()
        allure.attach(steps_report, name="📋 Test Steps Execution Report", 
                     attachment_type=allure.attachment_type.TEXT)
        
        # Timing report
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        timing_report = f"""Test Execution Timing Report
=====================================
Test Name:     {self.test_name}
Start Time:    {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
End Time:      {end_time.strftime("%Y-%m-%d %H:%M:%S")}
Duration:      {duration:.2f} seconds
Steps Count:   {len(self.steps)}
====================================="""
        
        allure.attach(timing_report, name="⏱️ Test Timing Report", 
                     attachment_type=allure.attachment_type.TEXT)
        
        # Add as parameters
        allure.dynamic.parameter("⏱️ Start Time", self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        allure.dynamic.parameter("⏱️ Duration", f"{duration:.2f} seconds")
        allure.dynamic.parameter("📊 Steps Count", str(len(self.steps)))


class BaseSeleniumTest:
    """
    Base class for all Selenium-based tests.
    
    Automatically handles:
    - Browser initialization with anti-bot options
    - Cleanup
    - Screenshot on error
    - Allure integration
    """
    
    # ===================================================================
    # Configuration - Override in subclass if needed
    # ===================================================================
    HEADLESS = False  # Set True to run headless
    PAGE_LOAD_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # ===================================================================
    # Lifecycle Methods
    # ===================================================================
    
    def setup_method(self):
        """
        Called before each test.
        Initializes browser with anti-bot protection.
        """
        logger.info("=" * 80)
        logger.info("TEST SETUP: Initializing browser")
        logger.info("=" * 80)
        
        self.driver = self._create_driver()
        
        logger.info("✓ Browser initialized successfully")
        
        with allure.step("Browser Initialization"):
            allure.attach(
                "✓ Browser launched with anti-bot protection",
                name="browser_init",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def teardown_method(self, request):
        """
        Called after each test.
        Cleans up browser and handles errors.
        """
        logger.info("=" * 80)
        logger.info("TEST TEARDOWN: Closing browser")
        logger.info("=" * 80)
        
        try:
            # If test failed, take screenshot
            if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
                self._take_screenshot_on_error()
        except:
            pass
        
        # Cleanup
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✓ Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
    
    # ===================================================================
    # Anti-Bot Browser Creation
    # ===================================================================
    
    def _create_driver(self):
        """
        Create undetected ChromeDriver with anti-bot options.
        
        Returns:
            Undetected Chrome WebDriver instance
        """
        logger.info("Creating undetected ChromeDriver with anti-bot options...")
        
        import tempfile
        import os
        
        options = uc.ChromeOptions()
        
        # ===== Create User Profile Directory =====
        profile_dir = tempfile.mkdtemp(prefix="ebay_bot_")
        logger.info(f"Using Chrome profile directory: {profile_dir}")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        # ===== Anti-Bot Options =====
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # Additional anti-detection options
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-sync")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-preconnect")
        options.add_argument("--enable-automation=false")
        
        # Disable password manager and other popups
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-translate")
        
        # Window size
        if not self.HEADLESS:
            options.add_argument("--start-maximized")
        
        # User agent
        options.add_argument(f"user-agent={self.USER_AGENT}")
        
        # ===== Chrome Options for Stability =====
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        # ===== Create Driver =====
        try:
            driver = uc.Chrome(
                options=options,
                headless=self.HEADLESS,
                version_main=None,
                suppress_welcome=True
            )
            
            # Set timeouts
            driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
            driver.implicitly_wait(self.IMPLICIT_WAIT)
            
            # Add JavaScript to hide webdriver and masquerade as real browser
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    Object.defineProperty(navigator, 'chrome', {
                        get: () => ({runtime: {}}),
                    });
                    window.chrome = {
                        runtime: {},
                    };
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """
            })
            
            logger.info("✓ UndetectedChromeDriver created successfully")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise
    
    # ===================================================================
    # Utility Methods - Common for All Tests
    # ===================================================================
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element to be visible.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Max wait time in seconds
            
        Returns:
            WebElement if found
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_element_clickable(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element to be clickable.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Max wait time in seconds
            
        Returns:
            WebElement if found and clickable
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def click_element(self, by: By, value: str, delay_before: float = 0.3, delay_after: float = 0.5):
        """
        Click element with human-like delays.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            delay_before: Delay before click (seconds)
            delay_after: Delay after click (seconds)
        """
        time.sleep(delay_before)
        element = self.wait_for_element_clickable(by, value)
        element.click()
        time.sleep(delay_after)
    
    def type_text(self, by: By, value: str, text: str, clear_first: bool = True, delay: float = 0.1):
        """
        Type text with human-like speed.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            text: Text to type
            clear_first: Clear field before typing
            delay: Delay between keystrokes (seconds)
        """
        element = self.wait_for_element(by, value)
        
        if clear_first:
            element.clear()
            time.sleep(0.2)
        
        for char in text:
            element.send_keys(char)
            time.sleep(delay)
    
    def take_screenshot(self, name: str = "screenshot"):
        """
        Take screenshot and attach to Allure.
        
        Args:
            name: Screenshot name
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = f"automation/reports/screenshots/{filename}"
            
            os.makedirs("automation/reports/screenshots", exist_ok=True)
            
            screenshot = self.driver.get_screenshot_as_png()
            with open(filepath, 'wb') as f:
                f.write(screenshot)
            
            allure.attach(
                screenshot,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info(f"✓ Screenshot saved: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to take screenshot: {e}")
    
    def _take_screenshot_on_error(self):
        """Take screenshot when test fails."""
        try:
            self.take_screenshot("error_screenshot")
        except:
            pass
    
    def get_page_title(self) -> str:
        """Get current page title."""
        return self.driver.title
    
    def get_current_url(self) -> str:
        """Get current URL."""
        return self.driver.current_url
    
    def get_page_source(self) -> str:
        """Get page HTML source."""
        return self.driver.page_source
    
    def refresh_page(self):
        """Refresh current page."""
        self.driver.refresh()
        time.sleep(2)
    
    def navigate_to(self, url: str):
        """Navigate to URL."""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(3)  # Wait for page to load
    
    def navigate_to_url(self, env_var: str = "TEST_URL", default_url: str = None):
        """
        Navigate to URL from environment variable or default.
        
        Args:
            env_var: Environment variable name (default: TEST_URL)
            default_url: Fallback URL if env var not set
        """
        url = os.getenv(env_var, default_url)
        
        if not url:
            raise ValueError(
                f"URL not found! Set environment variable '{env_var}' "
                f"or provide default_url parameter"
            )
        
        logger.info(f"Navigating to URL from env '{env_var}': {url}")
        self.navigate_to(url)
    
    def human_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """
        Add human-like random delay.
        
        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    # ===================================================================
    # Cookies Management
    # ===================================================================
    
    def add_cookies(self, cookies: list):
        """
        Add cookies to browser.
        
        Args:
            cookies: List of cookie dictionaries
        """
        for cookie in cookies:
            try:
                # Remove 'expiry' if it causes issues
                if 'expiry' in cookie:
                    cookie_copy = cookie.copy()
                    cookie_copy['expiry'] = int(cookie['expiry'])
                    self.driver.add_cookie(cookie_copy)
                else:
                    self.driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Failed to add cookie: {e}")
    
    def get_cookies(self) -> list:
        """Get all cookies from browser."""
        return self.driver.get_cookies()
    
    def clear_cookies(self):
        """Clear all cookies."""
        self.driver.delete_all_cookies()
    
    # ===================================================================
    # Assertions & Verification
    # ===================================================================
    
    def assert_element_visible(self, by: By, value: str, timeout: int = 10):
        """Assert element is visible."""
        try:
            self.wait_for_element(by, value, timeout)
            logger.info(f"✓ Element found: {by}={value}")
        except Exception as e:
            logger.error(f"✗ Element not found: {by}={value}")
            raise
    
    def assert_element_not_visible(self, by: By, value: str, timeout: int = 3):
        """Assert element is not visible."""
        try:
            element = self.driver.find_element(by, value)
            if element.is_displayed():
                raise AssertionError(f"Element should not be visible: {by}={value}")
            logger.info(f"✓ Element not visible: {by}={value}")
        except:
            logger.info(f"✓ Element not found (as expected): {by}={value}")
    
    def assert_url_contains(self, expected_url: str):
        """Assert current URL contains expected text."""
        current_url = self.get_current_url()
        assert expected_url in current_url, f"Expected '{expected_url}' in URL '{current_url}'"
        logger.info(f"✓ URL contains: {expected_url}")
    
    def assert_page_title_contains(self, expected_title: str):
        """Assert page title contains expected text."""
        current_title = self.get_page_title()
        assert expected_title in current_title, f"Expected '{expected_title}' in title '{current_title}'"
        logger.info(f"✓ Page title contains: {expected_title}")
    
    # ===================================================================
    # Logging Helpers
    # ===================================================================
    
    def log_step(self, step_description: str):
        """Log test step."""
        logger.info(f"STEP: {step_description}")
    
    def log_assertion(self, assertion_description: str):
        """Log assertion."""
        logger.info(f"ASSERT: {assertion_description}")
    
    def log_action(self, action_description: str):
        """Log action."""
        logger.info(f"ACTION: {action_description}")
