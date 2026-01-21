"""
Automation Test Store - Login Flow Tests
=========================================

Test suite for Automation Test Store login functionality.
Includes a reusable login flow function that can be imported and used in other tests.

Environment Variables Required:
    - ATS_URL: Automation Test Store URL (default: https://automationteststore.com/)
    - ATS_TEST_USER_NAME: Test user's login name
    - ATS_TEST_PASSWORD: Test user's password
"""

import os

import pytest
import allure

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest, get_logger, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    click_login_or_register_link,
    verify_account_login_page,
    enter_username_from_env_ats,
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
    verify_page_title,
)


logger = get_logger(__name__)


def execute_login_flow(driver):
    """
    Execute complete login flow for Automation Test Store.
    
    This function orchestrates the full login process from homepage navigation
    to successful login verification. It can be reused across different test scenarios.
    
    Flow:
        1. Navigate to Automation Test Store homepage
        2. Verify page title
        3. Click "Login or register" link
        4. Verify Account Login page loaded
        5. Enter username from environment variable
        6. Enter password from environment variable
        7. Click Login submit button
        8. Verify login success with welcome message
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        dict: Results dictionary containing:
            - welcome_message (str): The welcome message text displayed after login
            - username (str): The username that was used for login
            - ats_url (str): The Automation Test Store URL that was accessed
            
    Raises:
        AssertionError: If any step validation fails
        ValueError: If required environment variables are not set
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
        SmartAssert.contains(
            welcome_message, "Welcome back",
            "Welcome message contains greeting",
            "Missing 'Welcome back'"
        )
        SmartAssert.contains(
            welcome_message, username_from_env,
            "Welcome message contains username",
            "Missing username"
        )
    
    return {
        "welcome_message": welcome_message,
        "username": username_from_env,
        "ats_url": ats_url
    }


class TestAutomationTestStoreLogin(BaseSeleniumTest):
    """
    Test suite for Automation Test Store login functionality.
    
    This test class validates the complete login flow including:
    - Homepage navigation and verification
    - Login page navigation
    - Credential entry from environment variables
    - Successful login verification with welcome message
    """
    
    @allure.title("Verify Automation Test Store Login Flow")
    @allure.description("Complete end-to-end test of login functionality from homepage to successful authentication")
    @allure.tag("automationteststore", "login", "authentication", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_verify_automation_test_store_homepage(self):
        """
        Execute and verify complete login flow for Automation Test Store.
        
        This test validates the entire login journey:
            1. Navigate to homepage and verify page title
            2. Navigate to login page
            3. Enter credentials from environment variables
            4. Submit login form
            5. Verify successful login with welcome message
            
        Expected Results:
            - All navigation steps complete successfully
            - Login form accepts credentials
            - Welcome message displays with correct username
        """
        result = execute_login_flow(self.driver)
        step_aware_loggerInfo(
            f"✓ Login flow completed successfully for user: {result['username']}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
