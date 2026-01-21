"""
Utility Steps
=============

General utility and helper steps.
"""

import allure
import time
import os
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from automation.core import get_logger

logger = get_logger(__name__)


# =====================================================================
# Screenshot
# =====================================================================

@allure.step("Take screenshot")
def take_screenshot(driver, screenshot_func, name: str = "screenshot") -> str:
    """
    Take screenshot and attach to Allure.
    
    Args:
        driver: Selenium WebDriver instance
        screenshot_func: Function to call to take screenshot
        name: Screenshot name
    
    Returns:
        Path to screenshot file
    """
    logger.info(f"ACTION: Taking screenshot '{name}'")
    
    file_path = screenshot_func(name)
    
    logger.info(f"✓ Screenshot saved: {file_path}")
    return file_path


# =====================================================================
# Page Inspection
# =====================================================================

@allure.step("Get page title")
def get_page_title(driver) -> str:
    """
    Get current page title.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        Page title string
    """
    title = driver.title
    logger.info(f"Page title: {title}")
    return title


@allure.step("Get current URL")
def get_current_url(driver) -> str:
    """
    Get current page URL.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        Current URL string
    """
    url = driver.current_url
    logger.info(f"Current URL: {url}")
    return url


@allure.step("Get page source")
def get_page_source(driver) -> str:
    """
    Get current page HTML source.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        HTML source string
    """
    source = driver.page_source
    logger.info(f"Page source length: {len(source)} characters")
    return source


# =====================================================================
# Wait
# =====================================================================

@allure.step("Wait for element")
def wait_for_element_to_appear(driver, by: By, value: str, 
                                timeout: int = 10, element_name: str = "element") -> bool:
    """
    Wait for element to appear on page.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value
        timeout: Max wait time in seconds
        element_name: Human-readable element name
    
    Returns:
        True if element appears, raises TimeoutException otherwise
    """
    logger.info(f"ACTION: Waiting for {element_name} to appear (max {timeout}s)")
    
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.presence_of_element_located((by, value)))
    
    allure.attach(
        f"✓ Element {element_name} appeared",
        name="wait_action",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Element {element_name} appeared")
    return True


@allure.step("Wait for element to be clickable")
def wait_for_element_clickable(driver, by: By, value: str, 
                               timeout: int = 10, element_name: str = "element") -> bool:
    """
    Wait for element to be clickable.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value
        timeout: Max wait time in seconds
        element_name: Human-readable element name
    
    Returns:
        True if element is clickable, raises TimeoutException otherwise
    """
    logger.info(f"ACTION: Waiting for {element_name} to be clickable (max {timeout}s)")
    
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.element_to_be_clickable((by, value)))
    
    allure.attach(
        f"✓ Element {element_name} is clickable",
        name="wait_action",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Element {element_name} is clickable")
    return True


# =====================================================================
# Navigation Helpers
# =====================================================================

@allure.step("Refresh page")
def refresh_page(driver) -> str:
    """
    Refresh current page.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        Current URL after refresh
    """
    logger.info("ACTION: Refreshing page")
    driver.refresh()
    time.sleep(2)
    
    url = driver.current_url
    logger.info(f"✓ Page refreshed: {url}")
    return url


@allure.step("Human delay")
def human_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """
    Add human-like random delay.
    
    Args:
        min_seconds: Minimum delay
        max_seconds: Maximum delay
    """
    import random
    delay = random.uniform(min_seconds, max_seconds)
    logger.info(f"ACTION: Adding human delay {delay:.2f}s")
    time.sleep(delay)


# =====================================================================
# Success Message
# =====================================================================

@allure.step("Test completed successfully")
def log_success_message(test_name: str = "Test", success_message: str = None):
    """
    Log success message and attach to Allure.
    
    Args:
        test_name: Name of the test
        success_message: Custom success message (optional)
    
    Returns:
        True
    """
    if success_message is None:
        success_message = f"✅ {test_name} completed successfully!"
    
    allure.attach(
        success_message,
        name="success",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(success_message)
    return True


# Backward compatibility alias
test_success_message = log_success_message
