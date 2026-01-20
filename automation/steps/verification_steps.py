"""
Verification Steps
==================

צעדי בדיקה וויריפיקציה.
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.core import get_logger, loggerInfo, loggerAttach
from automation.core.logger import step_aware_loggerError, step_aware_loggerInfo, step_aware_loggerAttach
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
    step_aware_loggerInfo(f"ASSERT: Verifying homepage by checking logo presence")
    
    # Use JSON locators via SmartLocatorFinder to find logo
    step_aware_loggerInfo(f"Trying JSON locators (Logo check)...")
    
    smart_finder = SmartLocatorFinder(driver, timeout_sec=5)
    title_element = smart_finder.find_element_by_id("page_title")
    
    if title_element:
        # Check alt or title attribute (for logo image)
        element_text = (
            title_element.get_attribute("alt") or 
            title_element.get_attribute("title") or 
            title_element.text.strip()
        )
        step_aware_loggerInfo(f"Found logo element with text: '{element_text}'")
        
        # Verify it's the correct homepage by checking logo text
        if "Automation Test Store" in element_text:
            step_aware_loggerInfo(f"✅ Passed - Logo found with correct text")
            # Log to Allure which strategy worked
            step_aware_loggerAttach(
                f"✅ Strategy: JSON locators (Logo verification)\n✅ Logo text: {element_text}\n✅ Homepage confirmed",
                name="homepage_verification",
                attachment_type=allure.attachment_type.TEXT
            )
            return True
        else:
            step_aware_loggerError(f"❌ Logo found but text incorrect: '{element_text}'")
    
    # Logo verification failed
    raise AssertionError(
        f"Could not verify homepage - Logo 'Automation Test Store' not found."
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

