"""
Smart Locator Finder for Selenium
==================================

מנגנון Locator חכם עם fallback הדרגתי עבור Selenium (undetected-chromedriver).

תכונות:
- לכל אלמנט: לפחות 2 לוקייטורים חלופיים
- בזמן ריצה: ניסיון בכל לוקייטור עד הצלחה
- Logging מלא: איזה נכשל, כמה ניסיונות, סקרינים בכשל
- Screenshots: בכל כשל סופי

דוגמה:
    finder = SmartLocatorFinder(driver)
    
    locators = [
        ("id", "userid"),
        ("name", "userid"),
        ("xpath", "//input[@type='email']"),
    ]
    
    element = finder.find_element(locators, description="Email field")
    finder.click_element(locators, description="Sign in button")
    finder.type_text(locators, "user@example.com", description="Email input")
"""

import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotVisibleException,
)

import allure


class SmartLocatorFinder:
    """
    Smart finder with fallback locators for Selenium.
    
    Attributes:
        driver: Selenium WebDriver
        timeout_sec: Default timeout (seconds)
        screenshot_dir: Where to save failure screenshots
    """
    
    def __init__(self, driver, timeout_sec: float = 10, screenshot_dir: str = None):
        """
        Initialize SmartLocatorFinder.
        
        Args:
            driver: Selenium WebDriver instance
            timeout_sec: Default timeout for operations
            screenshot_dir: Directory for failure screenshots
        """
        self.driver = driver
        self.timeout_sec = timeout_sec
        
        # Default to automation/reports/screenshots if not provided
        if screenshot_dir is None:
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            screenshot_dir = str(project_root / "automation" / "reports" / "screenshots")
        
        self.screenshot_dir = screenshot_dir
        
        # Create screenshot directory
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    def find_element(
        self,
        locators: List[Tuple[str, str]],
        description: Optional[str] = None,
        timeout_sec: Optional[float] = None,
        take_screenshot_on_failure: bool = True
    ) -> Optional[WebElement]:
        """
        Find element with fallback strategy.
        
        Args:
            locators: List of (by_type, selector) tuples
                     Examples: [("id", "btn"), ("xpath", "//button[@id='btn']")]
            description: Human-readable description (for logging)
            timeout_sec: Custom timeout (default from __init__)
            take_screenshot_on_failure: Take screenshot if all locators fail
        
        Returns:
            WebElement if found, None if all locators fail
        
        Raises:
            TimeoutError: If all locators fail
        """
        timeout_sec = timeout_sec or self.timeout_sec
        
        # Log attempt start
        element_desc = description or self._describe_locators(locators)
        allure.attach(
            f"🔍 Starting to find element: {element_desc}\n"
            f"Total locators to try: {len(locators)}",
            name=f"find_element_start",
            attachment_type=allure.attachment_type.TEXT
        )
        
        last_error = None
        errors_log = []
        
        for attempt_num, (by_type, selector) in enumerate(locators, 1):
            try:
                # Convert string by_type to Selenium By object
                by = self._convert_by_type(by_type)
                
                # Wait for element
                element = WebDriverWait(self.driver, timeout_sec).until(
                    EC.presence_of_element_located((by, selector))
                )
                
                # Log success
                success_msg = (
                    f"✅ SUCCESS: Found element on attempt {attempt_num}/{len(locators)}\n"
                    f"   Locator: {by_type}={selector}\n"
                    f"   Element: {element.tag_name} "
                    f"(visible: {self._is_visible(element)})\n"
                    f"   Time: {attempt_num * timeout_sec:.1f}s max waited"
                )
                
                allure.attach(
                    success_msg,
                    name=f"find_element_success_{attempt_num}",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                return element
            
            except TimeoutException as e:
                error_msg = f"Attempt {attempt_num}/{len(locators)}: TIMEOUT - {by_type}={selector}"
                errors_log.append(error_msg)
                last_error = e
            
            except NoSuchElementException as e:
                error_msg = f"Attempt {attempt_num}/{len(locators)}: NOT FOUND - {by_type}={selector}"
                errors_log.append(error_msg)
                last_error = e
            
            except Exception as e:
                error_msg = f"Attempt {attempt_num}/{len(locators)}: ERROR ({type(e).__name__}) - {by_type}={selector}"
                errors_log.append(error_msg)
                last_error = e
        
        # All locators failed - take screenshot and raise
        if take_screenshot_on_failure:
            self._take_screenshot(f"element_not_found_{element_desc}")
        
        # Build error report
        error_report = (
            f"❌ FAILED: Element not found after {len(locators)} attempts\n"
            f"Description: {element_desc}\n\n"
            f"Attempts:\n" +
            "\n".join(f"  {e}" for e in errors_log) +
            f"\n\nLast error: {last_error}"
        )
        
        allure.attach(
            error_report,
            name=f"find_element_failure",
            attachment_type=allure.attachment_type.TEXT
        )
        
        raise TimeoutError(error_report)
    
    def click_element(
        self,
        locators: List[Tuple[str, str]],
        description: Optional[str] = None,
        human_like: bool = True,
        delay_before: float = 0.5,
        delay_after: float = 1.0,
    ) -> None:
        """
        Click element with fallback locators.
        
        Args:
            locators: List of (by_type, selector) tuples
            description: Human-readable description
            human_like: Add human-like delays
            delay_before: Delay before click (seconds)
            delay_after: Delay after click (seconds)
        
        Raises:
            TimeoutError: If element not found after all locators
        """
        element_desc = description or self._describe_locators(locators)
        
        # Pre-click delay
        if human_like:
            time.sleep(delay_before)
        
        try:
            # Find element with fallback
            element = self.find_element(
                locators,
                description=description,
                take_screenshot_on_failure=True
            )
            
            # Try to click
            try:
                element.click()
            except Exception as e:
                # If normal click fails, try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
            
            click_msg = f"✅ Clicked: {element_desc}"
            allure.attach(click_msg, name="click_success", attachment_type=allure.attachment_type.TEXT)
            
            # Post-click delay
            if human_like:
                time.sleep(delay_after)
        
        except Exception as e:
            self._take_screenshot(f"click_failed_{element_desc}")
            error_msg = f"❌ Click failed for: {element_desc}\nError: {e}"
            allure.attach(error_msg, name="click_failure", attachment_type=allure.attachment_type.TEXT)
            raise
    
    def type_text(
        self,
        locators: List[Tuple[str, str]],
        text: str,
        description: Optional[str] = None,
        clear_first: bool = True,
        human_like: bool = True,
        char_delay: float = 0.05,
    ) -> None:
        """
        Type text into element with fallback locators.
        
        Args:
            locators: List of (by_type, selector) tuples
            text: Text to type
            description: Human-readable description
            clear_first: Clear field before typing
            human_like: Type character-by-character with delays
            char_delay: Delay between characters (seconds)
        
        Raises:
            TimeoutError: If element not found
        """
        element_desc = description or self._describe_locators(locators)
        
        try:
            # Find element
            element = self.find_element(
                locators,
                description=description,
                take_screenshot_on_failure=True
            )
            
            # Clear if requested
            if clear_first:
                element.clear()
                time.sleep(0.3)
            
            # Type text - human-like if enabled
            if human_like:
                for char in text:
                    element.send_keys(char)
                    time.sleep(char_delay)
            else:
                element.send_keys(text)
            
            type_msg = f"✅ Typed: {len(text)} characters into {element_desc}"
            allure.attach(type_msg, name="type_success", attachment_type=allure.attachment_type.TEXT)
        
        except Exception as e:
            self._take_screenshot(f"type_failed_{element_desc}")
            error_msg = f"❌ Type failed for: {element_desc}\nText: {text}\nError: {e}"
            allure.attach(error_msg, name="type_failure", attachment_type=allure.attachment_type.TEXT)
            raise
    
    def wait_for_element(
        self,
        locators: List[Tuple[str, str]],
        description: Optional[str] = None,
        timeout_sec: Optional[float] = None,
        state: str = "visible",
    ) -> WebElement:
        """
        Wait for element to reach a specific state.
        
        Args:
            locators: List of (by_type, selector) tuples
            description: Human-readable description
            timeout_sec: Custom timeout
            state: "visible", "present", or "clickable"
        
        Returns:
            WebElement once found
        
        Raises:
            TimeoutError: If timeout exceeded
        """
        timeout_sec = timeout_sec or self.timeout_sec
        element_desc = description or self._describe_locators(locators)
        
        for attempt_num, (by_type, selector) in enumerate(locators, 1):
            try:
                by = self._convert_by_type(by_type)
                
                if state == "visible":
                    element = WebDriverWait(self.driver, timeout_sec).until(
                        EC.visibility_of_element_located((by, selector))
                    )
                elif state == "clickable":
                    element = WebDriverWait(self.driver, timeout_sec).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                else:  # "present"
                    element = WebDriverWait(self.driver, timeout_sec).until(
                        EC.presence_of_element_located((by, selector))
                    )
                
                return element
            
            except TimeoutException:
                continue
        
        # All failed
        self._take_screenshot(f"wait_failed_{element_desc}")
        raise TimeoutError(f"Element not {state} after {timeout_sec}s: {element_desc}")
    
    def _convert_by_type(self, by_type: str) -> str:
        """Convert string to Selenium By constant."""
        by_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }
        return by_map.get(by_type.lower(), By.XPATH)
    
    def _is_visible(self, element: WebElement) -> bool:
        """Check if element is visible."""
        try:
            return element.is_displayed()
        except:
            return False
    
    def _describe_locators(self, locators: List[Tuple[str, str]]) -> str:
        """Create a description of all locators."""
        descs = [f"{by_type}={selector[:30]}" for by_type, selector in locators]
        return " | ".join(descs)
    
    def _take_screenshot(self, name: str) -> str:
        """
        Take screenshot on failure.
        
        Args:
            name: Screenshot name/description
        
        Returns:
            Path to saved screenshot
        """
        try:
            from pathlib import Path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{name}.png"
            filepath = Path(self.screenshot_dir) / filename
            
            self.driver.save_screenshot(str(filepath))
            
            # Attach to Allure
            allure.attach.file(
                str(filepath),
                name=f"screenshot_{name}",
                attachment_type=allure.attachment_type.PNG
            )
            
            return str(filepath)
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return ""


# Helper function for easier usage
def get_smart_finder(driver, timeout_sec: float = 10) -> SmartLocatorFinder:
    """Factory function to create SmartLocatorFinder."""
    return SmartLocatorFinder(driver, timeout_sec=timeout_sec)
