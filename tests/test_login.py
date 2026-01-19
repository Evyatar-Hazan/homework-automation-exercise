import pytest
import allure
from selenium.webdriver.common.by import By
import time

from automation.core import BaseSeleniumTest, get_logger
from automation.steps import (
    navigate_to_ebay,
    verify_ebay_homepage,
    verify_page_title,
    verify_element_visible,
    take_screenshot,
    log_success_message,
    click_element_smart,
    type_email_from_env,
)
from automation.pages.ebay_login_page import EbayLoginLocators

logger = get_logger(__name__)


class TestLogin(BaseSeleniumTest):
    """Test suite for eBay login and homepage verification."""
    
    @allure.title("Verify eBay Sign In Navigation")
    @allure.description("Navigate to eBay, click Sign In button, and verify login page loads")
    @allure.tag("ebay", "login", "homepage", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_open_ebay_homepage(self):
        """
        Test: Navigate to eBay, verify homepage, click Sign In, verify login page.
        
        Steps:
        1. Navigate to eBay homepage
        2. Verify page title
        3. Verify eBay homepage loaded correctly
        4. Take screenshot of homepage
        5. Click Sign In button with SmartLocator
        6. Wait for login page to load
        7. Verify login page heading is visible
        8. Take screenshot of login page
        9. Log success
        """
        
        # Step 1: Navigate to eBay
        navigate_to_ebay(self.driver, url="https://www.ebay.com")
        
        # Step 2: Verify page title
        verify_page_title(self.driver, "eBay")
        
        # Step 3: Verify homepage
        verify_ebay_homepage(self.driver)
        
        # Step 4: Take screenshot of homepage
        take_screenshot(self.driver, self.take_screenshot, name="eBay Homepage")
        
        # Step 5: Click Sign In button using SmartLocator (with fallback locators)
        time.sleep(1)  # Wait for page to fully load
        click_element_smart(
            self.driver,
            EbayLoginLocators.SIGN_IN_BUTTON,
            element_name="Sign In Button"
        )
        
        # Step 6: Wait for login page to load
        time.sleep(2)
        
        # Step 7: Verify the login page heading is visible
        verify_element_visible(
            self.driver,
            By.ID,
            "greeting-msg",
            element_name="Login Page Heading (Sign in to your account)",
            timeout=10
        )
        
        # Step 8: Type email from TEST_EMAIL environment variable
        type_email_from_env(
            self.driver,
            By.ID,
            "userid",
            env_var_name="EBAY_TEST_EMAIL",
            element_name="Email/Username field"
        )
        
        # Step 9: Take screenshot of login page with email entered
        take_screenshot(self.driver, self.take_screenshot, name="Login Page - Email Entered")
        
        # Step 10: Click Continue button
        click_element_smart(
            self.driver,
            EbayLoginLocators.CONTINUE_BUTTON,
            element_name="Continue Button"
        )
        
        # Step 11: Wait for password page to load
        time.sleep(2)
        
        # Step 12: Take screenshot of password page
        take_screenshot(self.driver, self.take_screenshot, name="Password Page - Loaded")
        
        # Step 13: Log success
        log_success_message("eBay Sign In Test", "✅ Successfully entered email and clicked Continue button!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

