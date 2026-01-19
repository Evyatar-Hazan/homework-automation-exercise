"""
Automation Test Store Login Page Object
========================================

Page Object עם SmartLocator fallbacks לדף התחברות של Automation Test Store.

כל אלמנט מוגדר עם 2-3 לוקייטורים חלופיים:
- Primary locator (הדיוק הגבוה ביותר)
- Fallback 1 (חלופי)
- Fallback 2 (אם קיים)

בזמן ריצה, SmartLocatorFinder ינסה כל אחד בתורו.
"""

from typing import Optional, List, Tuple

from automation.utils.smart_locator_finder import SmartLocatorFinder


class AutomationTestStoreLoginLocators:
    """
    הגדרת כל הלוקייטורים לדף התחברות של Automation Test Store.
    
    פורמט: [(by_type, selector), (by_type, selector), ...]
    """
    
    # Account Button/Link (on homepage to access login)
    ACCOUNT_BUTTON = [
        ("xpath", "//div[@class='topBarAccount']"),
        ("css", ".topBarAccount"),
        ("xpath", "//a[contains(text(), 'Account')]"),
    ]
    
    # Login Button/Link
    LOGIN_BUTTON = [
        ("xpath", "//a[contains(text(), 'Login')]"),
        ("css", "a[href*='login']"),
        ("xpath", "//button[contains(text(), 'Login')]"),
    ]
    
    # Email Input Field
    EMAIL_INPUT = [
        ("id", "LoginFrm_loginname"),
        ("name", "loginname"),
        ("xpath", "//input[@id='LoginFrm_loginname']"),
    ]
    
    # Password Input Field
    PASSWORD_INPUT = [
        ("id", "LoginFrm_password"),
        ("name", "password"),
        ("xpath", "//input[@id='LoginFrm_password']"),
    ]
    
    # Login Submit Button
    LOGIN_SUBMIT_BUTTON = [
        ("css", "button[type='submit'].btn.btn-orange"),
        ("xpath", "//button[@type='submit' and contains(@class, 'btn-orange')]"),
        ("xpath", "//button[contains(text(), 'Login')]"),
        ("css", "button[type='submit']"),
    ]
    
    # Welcome Message (after login)
    WELCOME_MESSAGE = [
        ("css", "div.menu_text"),
        ("xpath", "//div[@class='menu_text']"),
        ("xpath", "//div[contains(text(), 'Welcome back')]"),
    ]
    
    # Logo/Homepage indicator for verification
    LOGO = [
        ("xpath", "//img[contains(@src, 'logo')]"),
        ("css", "img[alt*='automationteststore']"),
        ("xpath", "//a[@class='logo']"),
    ]
    
    # Login or Register Link (on homepage)
    LOGIN_OR_REGISTER_LINK = [
        ("xpath", "//a[contains(@href, 'rt=account/login')]"),
        ("xpath", "//a[contains(text(), 'Login or register')]"),
        ("css", "a[href*='account/login']"),
    ]
    
    # Account Login Heading (on login page)
    ACCOUNT_LOGIN_HEADING = [
        ("xpath", "//span[contains(text(), 'Account Login')]"),
        ("xpath", "//span[@class='maintext' and contains(text(), 'Account Login')]"),
        ("css", "span.maintext"),
    ]


class AutomationTestStoreLoginPage:
    """
    Automation Test Store Login Page with SmartLocator support.
    
    Attributes:
        driver: Selenium WebDriver instance
        locators: AutomationTestStoreLoginLocators instance with all locator definitions
        smart_locator: SmartLocatorFinder instance for intelligent element location
    """
    
    def __init__(self, driver):
        """
        Initialize the page object.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.locators = AutomationTestStoreLoginLocators()
        self.smart_locator = SmartLocatorFinder(driver)
    
    def is_on_homepage(self) -> bool:
        """
        Check if we are on Automation Test Store homepage.
        
        Returns:
            True if on homepage, False otherwise
        """
        try:
            return "automationteststore.com" in self.driver.current_url
        except Exception:
            return False
    
    def click_account_button(self):
        """
        Click the Account button to access login options.
        """
        self.smart_locator.click_element(
            AutomationTestStoreLoginLocators.ACCOUNT_BUTTON,
            element_name="Account Button"
        )
    
    def click_login_button(self):
        """
        Click the Login button/link.
        """
        self.smart_locator.click_element(
            AutomationTestStoreLoginLocators.LOGIN_BUTTON,
            element_name="Login Button"
        )
    
    def enter_email(self, email: str):
        """
        Enter email/username in the login form.
        
        Args:
            email: Email address or username
        """
        self.smart_locator.type_in_element(
            AutomationTestStoreLoginLocators.EMAIL_INPUT,
            email,
            element_name="Email/Username field"
        )
    
    def enter_password(self, password: str):
        """
        Enter password in the login form.
        
        Args:
            password: Password
        """
        self.smart_locator.type_in_element(
            AutomationTestStoreLoginLocators.PASSWORD_INPUT,
            password,
            element_name="Password field"
        )
    
    def click_login_submit(self):
        """
        Click the Login submit button.
        """
        self.smart_locator.click_element(
            AutomationTestStoreLoginLocators.LOGIN_SUBMIT_BUTTON,
            element_name="Login Submit Button"
        )
