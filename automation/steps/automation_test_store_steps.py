"""
Automation Test Store Steps
============================

צעדים נפרדים וחוזרים להשימוש בהם בבדיקות שונות של Automation Test Store.

כל פונקציה כאן היא "step" שיכולה להיות בשימוש חוזר בכמה בדיקות שונות.
"""

import allure
import time
from automation.core import get_logger

logger = get_logger(__name__)


@allure.step("Navigate to Automation Test Store homepage")
def navigate_to_automation_test_store(driver, url: str = "https://automationteststore.com/"):
    """
    Navigate to Automation Test Store homepage.
    
    Args:
        driver: Selenium WebDriver instance
        url: URL to navigate to (default: Automation Test Store homepage)
    
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


@allure.step("Verify Automation Test Store homepage")
def verify_automation_test_store_homepage(driver) -> bool:
    """
    Verify that we are on Automation Test Store homepage.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if on homepage, raises AssertionError otherwise
    """
    logger.info("ASSERT: Verifying Automation Test Store homepage")
    
    current_url = driver.current_url
    page_title = driver.title
    
    # Check URL
    is_homepage = (
        current_url.endswith("automationteststore.com/") or 
        current_url.endswith("automationteststore.com") or
        "automationteststore.com" in current_url
    )
    
    # Check title
    has_correct_title = "practice" in page_title.lower() or "automation" in page_title.lower()
    
    verification_report = f"""
        AUTOMATION TEST STORE HOMEPAGE VERIFICATION
        ═════════════════════════════════════════════════════════════

        Current URL: {current_url}
        Page Title: {page_title}

        CHECKS:
        ✓ URL is Automation Test Store: {is_homepage}
        ✓ Title is relevant: {has_correct_title}

        STATUS: {'✅ PASSED' if (is_homepage and has_correct_title) else '❌ FAILED'}
        """
    
    allure.attach(
        verification_report,
        name="homepage_verification",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(verification_report)
    
    assert is_homepage, f"Expected to be on automationteststore.com, but got {current_url}"
    assert has_correct_title, f"Page title '{page_title}' doesn't match expected title"
    
    return True


@allure.step("Click Login or Register link")
def click_login_or_register_link(driver):
    """
    Click the "Login or register" link on the homepage.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if successful
    """
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
    
    logger.info("ACTION: Clicking 'Login or register' link")
    
    smart_locator = SmartLocatorFinder(driver)
    smart_locator.click_element(
        AutomationTestStoreLoginLocators.LOGIN_OR_REGISTER_LINK,
        description="Login or register link"
    )
    
    time.sleep(2)  # Wait for page to load
    
    logger.info("✓ Successfully clicked 'Login or register' link")
    return True


@allure.step("Verify Account Login page")
def verify_account_login_page(driver) -> bool:
    """
    Verify that we are on the Account Login page.
    Checks for the "Account Login" heading and URL.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if on login page, raises AssertionError otherwise
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
    
    logger.info("ASSERT: Verifying Account Login page")
    
    current_url = driver.current_url
    
    # Check URL contains login
    has_login_url = "account/login" in current_url.lower() or "login" in current_url.lower()
    
    # Check for Account Login heading
    try:
        wait = WebDriverWait(driver, 10)
        heading = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING[0][1]
            ))
        )
        has_login_heading = heading is not None
    except Exception as e:
        logger.warning(f"Could not find Account Login heading: {e}")
        has_login_heading = False
    
    verification_report = f"""
        ACCOUNT LOGIN PAGE VERIFICATION
        ═════════════════════════════════════════════════════════════

        Current URL: {current_url}

        CHECKS:
        ✓ URL contains 'login': {has_login_url}
        ✓ 'Account Login' heading visible: {has_login_heading}

        STATUS: {'✅ PASSED' if (has_login_url and has_login_heading) else '❌ FAILED'}
        """
    
    allure.attach(
        verification_report,
        name="login_page_verification",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(verification_report)
    
    assert has_login_url, f"Expected login URL, but got {current_url}"
    assert has_login_heading, "Account Login heading not found on page"
    
    return True


@allure.step("Enter username from ATS_TEST_USER_NAME environment variable")
def enter_username_from_env_ats(driver, env_var_name: str = "ATS_TEST_USER_NAME"):
    """
    Enter username/login name from environment variable into the login form.
    Uses ATS_TEST_USER_NAME instead of email for Automation Test Store.
    
    Args:
        driver: Selenium WebDriver instance
        env_var_name: Name of environment variable containing username (default: ATS_TEST_USER_NAME)
    
    Returns:
        Username that was entered
    
    Raises:
        ValueError: If environment variable is not set
    """
    import os
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    # Get username from environment variable
    username = os.getenv(env_var_name)
    
    if not username:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    logger.info(f"ACTION: Entering username from {env_var_name} environment variable")
    
    # Wait for username field to be present
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(
        EC.presence_of_element_located((By.ID, "loginFrm_loginname"))
    )
    
    # Clear and type username
    username_field.clear()
    time.sleep(0.3)
    
    # Type username with human-like speed
    for char in username:
        username_field.send_keys(char)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    allure.attach(
        f"✓ Entered username: {username}",
        name="username_entry",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully entered username: {username}")
    return username


@allure.step("Enter email from ATS_TEST_EMAIL environment variable")
def enter_email_from_env_ats(driver, env_var_name: str = "ATS_TEST_EMAIL"):
    """
    Enter email address from environment variable into the login form.
    
    Args:
        driver: Selenium WebDriver instance
        env_var_name: Name of environment variable containing email (default: ATS_TEST_EMAIL)
    
    Returns:
        Email address that was entered
    
    Raises:
        ValueError: If environment variable is not set
    """
    import os
    from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    # Get email from environment variable
    email = os.getenv(env_var_name)
    
    if not email:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    logger.info(f"ACTION: Entering email from {env_var_name} environment variable")
    
    # Wait for email field to be present
    wait = WebDriverWait(driver, 10)
    email_field = wait.until(
        EC.presence_of_element_located((By.ID, "loginFrm_loginname"))
    )
    
    # Clear and type email
    email_field.clear()
    time.sleep(0.3)
    
    # Type email with human-like speed
    for char in email:
        email_field.send_keys(char)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    allure.attach(
        f"✓ Entered email: {email}",
        name="email_entry",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully entered email: {email}")
    return email


@allure.step("Enter password from ATS_TEST_PASSWORD environment variable")
def enter_password_from_env_ats(driver, env_var_name: str = "ATS_TEST_PASSWORD"):
    """
    Enter password from environment variable into the login form.
    
    Args:
        driver: Selenium WebDriver instance
        env_var_name: Name of environment variable containing password (default: ATS_TEST_PASSWORD)
    
    Returns:
        Password that was entered (masked for security)
    
    Raises:
        ValueError: If environment variable is not set
    """
    import os
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    # Get password from environment variable
    password = os.getenv(env_var_name)
    
    if not password:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    logger.info(f"ACTION: Entering password from {env_var_name} environment variable")
    
    # Wait for password field to be present
    wait = WebDriverWait(driver, 10)
    password_field = wait.until(
        EC.presence_of_element_located((By.ID, "loginFrm_password"))
    )
    
    # Clear and type password
    password_field.clear()
    time.sleep(0.3)
    
    # Type password with human-like speed
    for char in password:
        password_field.send_keys(char)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    allure.attach(
        f"✓ Entered password (masked)",
        name="password_entry",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Successfully entered password from {env_var_name}")
    return password


@allure.step("Click Login Submit button")
def click_login_button(driver):
    """
    Click the Login submit button on the login form.
    Uses specific title attribute to distinguish from Continue button.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        None
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    
    logger.info("ACTION: Clicking Login submit button")
    
    wait = WebDriverWait(driver, 10)
    smart_locator = SmartLocatorFinder(driver)
    
    # Define locators for login button - with title="Login" to distinguish from Continue button
    locators = [
        ("xpath", "//button[@type='submit' and @title='Login']"),
        ("xpath", "//button[@type='submit' and contains(@class, 'btn-orange') and contains(., 'Login')]"),
        ("css", "button[type='submit'][title='Login']"),
    ]
    
    login_button = smart_locator.find_element(
        locators,
        "Login Submit Button"
    )
    
    # Wait for button to be clickable
    wait.until(EC.element_to_be_clickable(login_button))
    time.sleep(0.5)
    
    logger.info("✓ Clicking Login button")
    login_button.click()
    time.sleep(2)  # Wait for login processing
    
    allure.attach(
        "✓ Clicked Login submit button",
        name="login_button_click",
        attachment_type=allure.attachment_type.TEXT
    )


@allure.step("Verify login success with welcome message")
def verify_login_success(driver, username_from_env: str = "Evyatar"):
    """
    Verify successful login by checking for welcome message.
    
    Args:
        driver: Selenium WebDriver instance
        username_from_env: Expected username to appear in welcome message (default: "Evyatar")
    
    Returns:
        The welcome message text
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    
    logger.info(f"ACTION: Verifying login success - expecting welcome message with '{username_from_env}'")
    
    wait = WebDriverWait(driver, 10)
    smart_locator = SmartLocatorFinder(driver)
    
    # First, let's check the current page title and URL to see where we are
    current_url = driver.current_url
    page_title = driver.title
    logger.info(f"Current URL after login: {current_url}")
    logger.info(f"Current page title: {page_title}")
    
    # Get page source for debugging
    page_source = driver.page_source
    
    # Check if welcome message is in the page
    if "Welcome back" in page_source:
        logger.info("✓ 'Welcome back' found in page source")
    else:
        logger.warning("⚠ 'Welcome back' NOT found in page source")
        logger.info(f"Page source length: {len(page_source)}")
    
    # Define locators for welcome message
    locators = [
        ("xpath", "//div[contains(text(), 'Welcome back')]"),
        ("css", "div.menu_text"),
        ("xpath", "//div[@class='menu_text']"),
    ]
    
    try:
        welcome_element = smart_locator.find_element(
            locators,
            "Welcome Message"
        )
        
        time.sleep(1)
        
        welcome_text = welcome_element.text
        logger.info(f"✓ Found welcome message: '{welcome_text}'")
        
        # Verify username is in welcome message
        if username_from_env in welcome_text:
            logger.info(f"✓ Username '{username_from_env}' found in welcome message")
            allure.attach(
                f"✓ Login Successful!\n✓ Welcome message: '{welcome_text}'",
                name="login_success_verification",
                attachment_type=allure.attachment_type.TEXT
            )
            return welcome_text
        else:
            logger.warning(f"⚠ Username '{username_from_env}' not found in welcome message: '{welcome_text}'")
            allure.attach(
                f"⚠ Warning: Username not found in message: '{welcome_text}'",
                name="login_success_warning",
                attachment_type=allure.attachment_type.TEXT
            )
            return welcome_text
            
    except Exception as e:
        logger.error(f"✗ Failed to find welcome message: {str(e)}")
        
        # Save page source for debugging
        import os
        debug_dir = "/home/evyatar/Desktop/Projects/HomeworkAutomationExercise/automation-project1/automation/reports/debug"
        os.makedirs(debug_dir, exist_ok=True)
        debug_file = os.path.join(debug_dir, f"page_source_{int(time.time())}.html")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(page_source)
        logger.info(f"✓ Page source saved to {debug_file}")
        
        allure.attach(
            f"✗ Login verification failed: {str(e)}\n\nPage source saved for debugging",
            name="login_verification_error",
            attachment_type=allure.attachment_type.TEXT
        )
        raise
