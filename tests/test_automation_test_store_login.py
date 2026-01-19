import pytest
import allure
from selenium.webdriver.common.by import By
import time
from datetime import datetime

from automation.core import BaseSeleniumTest, get_logger, TestExecutionTracker
from automation.steps import (
    navigate_to_automation_test_store,
    verify_automation_test_store_homepage,
    click_login_or_register_link,
    verify_account_login_page,
    enter_username_from_env_ats,
    enter_email_from_env_ats,
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
    verify_page_title,
    verify_element_visible,
    take_screenshot,
    log_success_message,
)
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators

logger = get_logger(__name__)


class TestAutomationTestStoreLogin(BaseSeleniumTest):
    """Test suite for Automation Test Store login and homepage verification."""
    
    @allure.title("Verify Automation Test Store Sign In Navigation")
    @allure.description("Navigate to Automation Test Store, verify homepage loads, and navigate to login page")
    @allure.tag("automationteststore", "login", "homepage", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_verify_automation_test_store_homepage(self):
        """
        Test: Navigate to Automation Test Store, verify homepage, navigate to login, and enter credentials.
        
        Steps:
        1. Navigate to Automation Test Store homepage
        2. Verify page title
        3. Verify Automation Test Store homepage loaded correctly
        4. Take screenshot of homepage
        5. Verify logo is visible (Automation Test Store indicator)
        6. Take screenshot of logo area
        7. Click "Login or register" link
        8. Verify Account Login page loaded
        9. Verify "Account Login" heading is visible
        10. Take screenshot of login page
        11. Enter email from ATS_TEST_EMAIL environment variable
        12. Take screenshot after email entry
        13. Enter password from ATS_TEST_PASSWORD environment variable
        14. Take screenshot after password entry
        15. Click Login submit button
        16. Take screenshot after login button click
        17. Verify login success with welcome message
        18. Log success
        """
        
        # Initialize test execution tracker (from infrastructure)
        tracker = TestExecutionTracker("test_verify_automation_test_store_homepage")
        
        def log_step(name, details=""):
            """Log step using the infrastructure tracker."""
            tracker.log_step(name, details)
        
        # Step 1: Navigate to Automation Test Store
        log_step("Navigate to Automation Test Store", 
                 "URL: https://automationteststore.com/\nWait: 3 seconds")
        navigate_to_automation_test_store(self.driver, url="https://automationteststore.com/")
        
        # Step 2: Verify page title
        log_step("Verify page title", 
                 'Title should contain: "practice"')
        verify_page_title(self.driver, "practice")
        
        # Step 3: Verify homepage
        log_step("Verify Automation Test Store homepage loaded correctly")
        verify_automation_test_store_homepage(self.driver)
        
        # Step 4: Take screenshot of homepage
        log_step("Take screenshot of homepage")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Homepage")
        
        # Step 5: Verify logo is visible (using SmartLocator)
        log_step("Verify logo is visible",
                 f"Locator: {AutomationTestStoreLoginLocators.LOGO}")
        time.sleep(1)  # Wait for page to fully load
        verify_element_visible(
            self.driver,
            By.XPATH,
            AutomationTestStoreLoginLocators.LOGO[0][1],
            element_name="Automation Test Store Logo",
            timeout=10
        )
        
        # Step 6: Take screenshot with logo visible
        log_step("Take screenshot of logo area")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Logo - Verified")
        
        # Step 7: Click "Login or register" link
        log_step("Click 'Login or register' link",
                 f"Locator: {AutomationTestStoreLoginLocators.LOGIN_OR_REGISTER_LINK}")
        click_login_or_register_link(self.driver)
        
        # Step 8: Verify Account Login page
        log_step("Verify Account Login page loaded")
        verify_account_login_page(self.driver)
        
        # Step 9: Verify "Account Login" heading is visible
        log_step("Verify 'Account Login' heading is visible",
                 f"Locator: {AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING}")
        verify_element_visible(
            self.driver,
            By.XPATH,
            AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING[0][1],
            element_name="Account Login Heading",
            timeout=10
        )
        
        # Step 10: Take screenshot of login page
        log_step("Take screenshot of login page")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login Page")
        
        # Step 11: Enter username from ATS_TEST_USER_NAME environment variable
        log_step("Enter username from environment variable",
                 f"Locator: {AutomationTestStoreLoginLocators.EMAIL_INPUT}\nUsername: Evyatar")
        enter_username_from_env_ats(self.driver, env_var_name="ATS_TEST_USER_NAME")
        
        # Step 12: Take screenshot after username entry
        log_step("Take screenshot after username entry")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - Username Entered")
        
        # Step 13: Enter password from ATS_TEST_PASSWORD environment variable
        log_step("Enter password from environment variable",
                 f"Locator: {AutomationTestStoreLoginLocators.PASSWORD_INPUT}\nPassword: (masked)")
        enter_password_from_env_ats(self.driver, env_var_name="ATS_TEST_PASSWORD")
        
        # Step 14: Take screenshot after password entry
        log_step("Take screenshot after password entry")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - Username and Password Entered")
        
        # Step 15: Click Login submit button
        log_step("Click Login submit button",
                 f"Locator: {AutomationTestStoreLoginLocators.LOGIN_SUBMIT_BUTTON}\nSelector: type='submit' title='Login'")
        click_login_button(self.driver)
        
        # Step 16: Take screenshot after login button click
        log_step("Take screenshot after login button click")
        take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - After Login Button Click")
        
        # Step 17: Verify login success with welcome message
        log_step("Verify login success with welcome message",
                 f"Expected: 'Welcome back Evyatar'\nLocator: {AutomationTestStoreLoginLocators.WELCOME_MESSAGE}")
        verify_login_success(self.driver, username_from_env="Evyatar")
        
        # Step 18: Log success
        log_step("Log success message")
        log_success_message("Automation Test Store Sign In Test", "✅ Successfully verified Automation Test Store homepage, logo, navigated to Account Login page, entered username and password, clicked login, and verified successful login with welcome message!")
        
        # Attach all test execution data to Allure (from infrastructure)
        tracker.attach_to_allure()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
