"""
Element Interaction Steps
=========================

צעדי עבודה עם אלמנטים בעמוד.
"""

import os
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.core import get_logger
from automation.utils.smart_locator_finder import SmartLocatorFinder

logger = get_logger(__name__)


@allure.step("Click element")
def click_element(driver, by: By, value: str, element_name: str = "element") -> bool:
    """
    Click element with human-like delays.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value
        element_name: Human-readable element name
    
    Returns:
        True if successful, raises exception otherwise
    """
    logger.info(f"ACTION: Clicking {element_name} ({by}={value})")
    
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((by, value)))
    
    time.sleep(0.3)  # Human-like delay before click
    element.click()
    time.sleep(0.5)  # Human-like delay after click
    
    allure.attach(
        f"✓ Clicked {element_name}",
        name="click_action",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully clicked {element_name}")
    return True


@allure.step("Type text")
def type_text(driver, by: By, value: str, text: str, element_name: str = "field") -> bool:
    """
    Type text in field with human-like speed.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value
        text: Text to type
        element_name: Human-readable field name
    
    Returns:
        True if successful, raises exception otherwise
    """
    logger.info(f"ACTION: Typing '{text}' in {element_name}")
    
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((by, value)))
    
    element.clear()
    time.sleep(0.2)
    
    # Type with human-like speed
    for char in text:
        element.send_keys(char)
        time.sleep(0.05)
    
    allure.attach(
        f"✓ Typed '{text}' in {element_name}",
        name="type_action",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully typed in {element_name}")
    return True


@allure.step("Type email from ENV variable")
def type_email_from_env(driver, by: By, value: str, env_var_name: str = "TEST_EMAIL", element_name: str = "email field") -> bool:
    """
    Type email address from environment variable into field.
    
    This step reads the email from an environment variable and types it
    into the specified field with human-like speed.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value (XPath, CSS, ID, etc.)
        env_var_name: Name of environment variable containing email (default: TEST_EMAIL)
        element_name: Human-readable field name
    
    Returns:
        True if successful, raises exception if email not in ENV
    
    Raises:
        ValueError: If environment variable is not set
    
    Example:
        type_email_from_env(driver, By.ID, "userid", env_var_name="TEST_EMAIL")
    """
    # Get email from environment variable
    email = os.environ.get(env_var_name)
    
    if not email:
        error_msg = f"❌ Environment variable '{env_var_name}' not set! Please set it before running the test."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"ACTION: Typing email from ENV variable '{env_var_name}' into {element_name}")
    logger.info(f"Email: {email[:3]}***{email[-3:]} (masked for security)")
    
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((by, value)))
    
    # Clear the field first
    element.clear()
    time.sleep(0.2)
    
    # Type email with human-like speed
    for char in email:
        element.send_keys(char)
        time.sleep(0.05)
    
    allure.attach(
        f"✓ Typed email from {env_var_name} into {element_name}\nEmail: {email[:3]}***{email[-3:]}",
        name="type_email_action",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully typed email into {element_name}")
    return True


@allure.step("Click element using SmartLocator")
def click_element_smart(driver, locators_list, element_name: str = "element") -> bool:
    """
    Click element using SmartLocator with fallback locators.
    
    SmartLocator tries each locator in the list until one works,
    with intelligent fallback if primary locator fails.
    
    Args:
        driver: Selenium WebDriver instance
        locators_list: List of tuples [(by_type, selector), ...]
                      Example: [("xpath", "//a[contains(...)]"), 
                               ("css", "a.signin"), ...]
        element_name: Human-readable element name
    
    Returns:
        True if successful, raises exception otherwise
    
    Example:
        from automation.pages.ebay_login_page import EbayLoginLocators
        click_element_smart(driver, EbayLoginLocators.SIGN_IN_BUTTON, "Sign In")
    """
    logger.info(f"ACTION: Clicking {element_name} using SmartLocator")
    
    try:
        # Use SmartLocatorFinder to find and click the element
        finder = SmartLocatorFinder(driver)
        element = finder.find_element(locators_list)
        
        time.sleep(0.3)  # Human-like delay before click
        element.click()
        time.sleep(0.5)  # Human-like delay after click
        
        allure.attach(
            f"✓ Clicked {element_name} using SmartLocator",
            name="smart_click_action",
            attachment_type=allure.attachment_type.TEXT
        )
        
        logger.info(f"✓ Successfully clicked {element_name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to click {element_name}: {str(e)}")
        allure.attach(
            f"✗ Failed to click {element_name}: {str(e)}",
            name="smart_click_error",
            attachment_type=allure.attachment_type.TEXT
        )
        raise
