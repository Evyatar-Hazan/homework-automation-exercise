"""
Verification Steps
==================

צעדי בדיקה וויריפיקציה.
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.core import get_logger
from automation.utils.smart_locator_finder import SmartLocatorFinder

logger = get_logger(__name__)


@allure.step("Verify eBay homepage")
def verify_ebay_homepage(driver) -> bool:
    """
    Verify that we are on eBay homepage.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if on homepage, raises AssertionError otherwise
    """
    logger.info("ASSERT: Verifying eBay homepage")
    
    current_url = driver.current_url
    page_title = driver.title
    
    # Check URL
    is_homepage = (
        current_url.endswith("ebay.com/") or 
        current_url.endswith("ebay.com") or
        "ebay.com" in current_url
    )
    
    # Check title
    has_ebay_title = "eBay" in page_title
    
    verification_report = f"""
        EBAY HOMEPAGE VERIFICATION
        ═══════════════════════════════════════════════════════════

        Current URL: {current_url}
        Page Title: {page_title}

        CHECKS:
        ✓ URL is eBay: {is_homepage}
        ✓ Title contains 'eBay': {has_ebay_title}

        STATUS: {'✅ PASSED' if (is_homepage and has_ebay_title) else '❌ FAILED'}
        """
    
    allure.attach(
        verification_report,
        name="homepage_verification",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"Verification Report:\n{verification_report}")
    
    # Assert
    assert is_homepage, f"Not on eBay homepage. URL: {current_url}"
    assert has_ebay_title, f"Page title doesn't contain 'eBay': {page_title}"
    
    logger.info("✓ Homepage verification passed")
    return True


@allure.step("Verify page title")
def verify_page_title(driver, expected_text: str) -> bool:
    """
    Verify that page title contains expected text.
    Logs which strategy successfully found the element to Allure.
    
    Args:
        driver: Selenium WebDriver instance
        expected_text: Expected text in title
    
    Returns:
        True if verification passes, raises AssertionError otherwise
    """
    logger.info(f"ASSERT: Verifying page title contains '{expected_text}'")
    
    # STRATEGY 1: Primary - Use driver.title (from <title> HTML tag)
    page_title = driver.title
    logger.info(f"[1/2] driver.title: '{page_title}'")
    
    if expected_text in page_title:
        logger.info(f"✅ Passed with driver.title")
        # Log to Allure which strategy worked
        allure.attach(
            f"✅ Strategy: driver.title\n✅ Content: {page_title}",
            name="which_strategy_found_element",
            attachment_type=allure.attachment_type.TEXT
        )
        return True
    
    # STRATEGY 2: Fallback - Use JSON locators via SmartLocatorFinder
    logger.info(f"[2/2] Trying JSON locators...")
    
    smart_finder = SmartLocatorFinder(driver, timeout_sec=5)
    title_element = smart_finder.find_element_by_id("page_title")
    
    if title_element:
        page_title = title_element.text.strip()
        logger.info(f"Found: '{page_title}'")
        assert expected_text in page_title, \
            f"Expected '{expected_text}' in '{page_title}'"
        logger.info(f"✅ Passed")
        # Log to Allure which strategy worked
        allure.attach(
            f"✅ Strategy: JSON locators\n✅ Content: {page_title}",
            name="which_strategy_found_element",
            attachment_type=allure.attachment_type.TEXT
        )
        return True
    
    # Both strategies failed
    raise AssertionError(
        f"Could not verify title contains '{expected_text}'"
    )


@allure.step("Verify page URL")
def verify_page_url(driver, expected_url_part: str) -> bool:
    """
    Verify that current URL contains expected text.
    
    Args:
        driver: Selenium WebDriver instance
        expected_url_part: Expected text in URL
    
    Returns:
        True if found, raises AssertionError otherwise
    """
    logger.info(f"ASSERT: Verifying URL contains '{expected_url_part}'")
    
    current_url = driver.current_url
    
    assert expected_url_part in current_url, \
        f"Expected '{expected_url_part}' in URL '{current_url}'"
    
    allure.attach(
        f"✓ URL contains '{expected_url_part}': {current_url}",
        name="url_verification",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ URL verification passed: {current_url}")
    return True


@allure.step("Verify element is visible")
def verify_element_visible(driver, by: By, value: str, element_name: str = "element", timeout: int = 10) -> bool:
    """
    Verify that an element is visible on the page.
    
    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator type
        value: Locator value
        element_name: Human-readable element name
        timeout: Max wait time in seconds
    
    Returns:
        True if element is visible
    
    Raises:
        TimeoutException: If element not found or not visible
    """
    logger.info(f"ASSERT: Verifying {element_name} is visible")
    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located((by, value)))
    
    allure.attach(
        f"✓ Element {element_name} is visible",
        name="element_visibility",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Element {element_name} is visible")
    return True
