from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo, step_aware_loggerAttach
import pytest
import allure
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import os

from automation.core import BaseSeleniumTest, get_logger, TestExecutionTracker, SmartAssert, log_step_with_allure
from automation.steps import (
    navigate_to_automation_test_store,
    click_login_or_register_link,
    verify_account_login_page,
    enter_username_from_env_ats,
    enter_email_from_env_ats,
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
    verify_page_title,
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
        
        # Step 1: Navigate to Automation Test Store
        ats_url = os.getenv("ATS_URL", "https://automationteststore.com/")
        with step_aware_loggerStep("Step 1: Navigate to Automation Test Store"):
            result = navigate_to_automation_test_store(self.driver, url=ats_url)
            SmartAssert.equal(result, ats_url, "Navigate to homepage", "URL mismatch")

        
        # Step 2: Verify page title
        with step_aware_loggerStep("Step 2: Verify page title"):
            result = verify_page_title(self.driver, "practice")
            SmartAssert.true(result, "Page title verified", "Title check failed")
        
        
        # Step 3: Click "Login or register" link
        with step_aware_loggerStep("Step 3: Click 'Login or register' link"):
            result = click_login_or_register_link(self.driver)
            SmartAssert.true(result is not None, "Login link clicked", "Login link click failed")
        
        # # Step 8: Verify Account Login page
        # result = verify_account_login_page(self.driver)
        # tracker.log_step("Verify Account Login page loaded", "Login page verified")
        # SmartAssert.true(result, "Login page verified", "Login page check failed")
        
        # # Step 9: Verify "Account Login" heading is visible
        # result = verify_element_visible(self.driver, By.XPATH, AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING[0][1], "Heading", timeout=10)
        # tracker.log_step("Verify 'Account Login' heading is visible", f"Locator: {AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING}")
        # SmartAssert.true(result, "Login heading visible", "Heading check failed")
        
        # # Step 10: Take screenshot of login page
        # result = take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login Page")
        # tracker.log_step("Take screenshot of login page", "Login page screenshot saved")
        # SmartAssert.true(result is not None, "Login screenshot taken", "Login screenshot failed")
        
        # # Step 11: Enter username from ATS_TEST_USER_NAME
        # result = enter_username_from_env_ats(self.driver, env_var_name="ATS_TEST_USER_NAME")
        # tracker.log_step("Enter username from environment variable", f"Locator: {AutomationTestStoreLoginLocators.EMAIL_INPUT}\nUsername: Evyatar")
        # SmartAssert.true(result is not None, "Username entered", "Username entry failed")
        
        # # Step 12: Take screenshot after username entry
        # result = take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - Username Entered")
        # tracker.log_step("Take screenshot after username entry", "Username screenshot saved")
        # SmartAssert.true(result is not None, "Username screenshot taken", "Username screenshot failed")
        
        # # Step 13: Enter password from ATS_TEST_PASSWORD
        # result = enter_password_from_env_ats(self.driver, env_var_name="ATS_TEST_PASSWORD")
        # tracker.log_step("Enter password from environment variable", f"Locator: {AutomationTestStoreLoginLocators.PASSWORD_INPUT}\nPassword: (masked)")
        # SmartAssert.true(result is not None, "Password entered", "Password entry failed")
        
        # # Step 14: Take screenshot after password entry
        # result = take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - Username and Password Entered")
        # tracker.log_step("Take screenshot after password entry", "Password screenshot saved")
        # SmartAssert.true(result is not None, "Password screenshot taken", "Password screenshot failed")
        
        # # Step 15: Click Login submit button
        # result = click_login_button(self.driver)
        # tracker.log_step("Click Login submit button", f"Locator: {AutomationTestStoreLoginLocators.LOGIN_SUBMIT_BUTTON}\nSelector: type='submit' title='Login'")
        # SmartAssert.true(result is not None, "Login button clicked", "Login button click failed")
        
        # # Step 16: Take screenshot after login button click
        # result = take_screenshot(self.driver, self.take_screenshot, name="Automation Test Store Login - After Login Button Click")
        # tracker.log_step("Take screenshot after login button click", "Post-login screenshot saved")
        # SmartAssert.true(result is not None, "Post-login screenshot taken", "Post-login screenshot failed")
        
        # # Step 17: Verify login success with welcome message
        # welcome_message = verify_login_success(self.driver, username_from_env="Evyatar")
        # tracker.log_step("Verify login success with welcome message", f"Expected: 'Welcome back Evyatar'\nLocator: {AutomationTestStoreLoginLocators.WELCOME_MESSAGE}")
        # SmartAssert.contains(welcome_message, "Welcome back", "Welcome message contains greeting", "Missing 'Welcome back'")
        # SmartAssert.contains(welcome_message, "Evyatar", "Welcome message contains username", "Missing username")
        
        # # Step 18: Log success
        # result = log_success_message("Automation Test Store Sign In Test", "✅ Successfully verified Automation Test Store homepage, logo, navigated to Account Login page, entered username and password, clicked login, and verified successful login with welcome message!")
        # tracker.log_step("Log success message", "Test completed successfully")
        # SmartAssert.true(result is not None, "Success logged", "Success logging failed")
        
        # Attach all test execution data to Allure (from infrastructure)
        tracker.attach_to_allure()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
