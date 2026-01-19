"""
Navigation Steps
================

צעדי ניווט בין עמודים.
"""

import allure
import time
from automation.core import get_logger

logger = get_logger(__name__)


@allure.step("Navigate to eBay homepage")
def navigate_to_ebay(driver, url: str = "https://www.ebay.com"):
    """
    Navigate to eBay homepage.
    
    Args:
        driver: Selenium WebDriver instance
        url: URL to navigate to (default: eBay homepage)
    
    Returns:
        Current URL
    """
    logger.info(f"ACTION: Navigating to {url}")
    driver.get(url)
    time.sleep(3)
    
    current_url = driver.current_url
    
    allure.attach(
        f"✓ Navigated to {current_url}",
        name="navigation",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully navigated to {current_url}")
    return current_url
