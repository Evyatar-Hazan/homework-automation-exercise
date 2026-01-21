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
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
    verify_page_title,
    log_success_message,
)
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators

logger = get_logger(__name__)


def execute_login_flow(driver):
    """
    Execute full login flow for Automation Test Store.
    
    This function can be reused in different test scenarios.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        dict: Results containing welcome_message and other verification data
    """
    # Step 1: Navigate to Automation Test Store
    ats_url = os.getenv("ATS_URL", "https://automationteststore.com/")
    with step_aware_loggerStep("Step 1: Navigate to Automation Test Store"):
        result = navigate_to_automation_test_store(driver, url=ats_url)
        SmartAssert.equal(result, ats_url, "Navigate to homepage", "URL mismatch")
    
    # Step 2: Verify page title
    with step_aware_loggerStep("Step 2: Verify page title"):
        result = verify_page_title(driver, "practice")
        SmartAssert.true(result, "Page title verified", "Title check failed")
    
    # Step 3: Click "Login or register" link
    with step_aware_loggerStep("Step 3: Click 'Login or register' link"):
        result = click_login_or_register_link(driver)
        SmartAssert.true(result is not None, "Login link clicked", "Login link click failed")
    
    # Step 4: Verify Account Login page
    with step_aware_loggerStep("Step 4: Verify Account Login page"):
        result = verify_account_login_page(driver)
        SmartAssert.true(result, "Login page verified", "Login page check failed")

    # Step 5: Enter username from ATS_TEST_USER_NAME
    with step_aware_loggerStep("Step 5: Enter username from ATS_TEST_USER_NAME"):
        result = enter_username_from_env_ats(driver, env_var_name="ATS_TEST_USER_NAME")
        SmartAssert.true(result is not None, "Username entered", "Username entry failed")
    
    # Step 6: Enter password from ATS_TEST_PASSWORD
    with step_aware_loggerStep("Step 6: Enter password from ATS_TEST_PASSWORD"):
        result = enter_password_from_env_ats(driver, env_var_name="ATS_TEST_PASSWORD")
        SmartAssert.true(result is not None, "Password entered", "Password entry failed")
    
    # Step 7: Click Login submit button
    with step_aware_loggerStep("Step 7: Click Login submit button"):
        result = click_login_button(driver)
        SmartAssert.true(result is not None, "Login button clicked", "Login button click failed")
    
    # Step 8: Verify login success with welcome message
    with step_aware_loggerStep("Step 8: Verify login success with welcome message"):
        username_from_env = os.getenv("ATS_TEST_USER_NAME", "Evyatar")
        welcome_message = verify_login_success(driver, username_from_env=username_from_env)
        SmartAssert.contains(welcome_message, "Welcome back", "Welcome message contains greeting", "Missing 'Welcome back'")
        SmartAssert.contains(welcome_message, username_from_env, "Welcome message contains username", "Missing username")
    
    return {
        "welcome_message": welcome_message,
        "username": username_from_env,
        "ats_url": ats_url
    }


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
        result = execute_login_flow(self.driver)
        step_aware_loggerInfo(f"✓ Login flow completed successfully for user: {result['username']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
