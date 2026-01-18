"""
eBay Login Page Object
======================

Page Object עם SmartLocator fallbacks לדף התחברות של eBay.

כל אלמנט מוגדר עם 2-3 לוקייטורים חלופיים:
- Primary locator (הדיוק הגבוה ביותר)
- Fallback 1 (חלופי)
- Fallback 2 (אם קיים)

בזמן ריצה, SmartLocatorFinder ינסה כל אחד בתורו.
"""

from typing import Optional, List, Tuple

from automation.utils.smart_locator_finder import SmartLocatorFinder


class EbayLoginLocators:
    """
    הגדרת כל הלוקייטורים לדף התחברות.
    
    פורמט: [(by_type, selector), (by_type, selector), ...]
    """
    
    # Sign In Button (homepage)
    SIGN_IN_BUTTON = [
        ("xpath", "//a[contains(text(), 'Sign in')]"),
        ("xpath", "//a[@href and contains(@href, 'signin')]"),
        ("css", "a[data-test-id='topnav-signin']"),
    ]
    
    # Email Input Field
    EMAIL_INPUT = [
        ("id", "userid"),
        ("name", "userid"),
        ("xpath", "//input[@id='userid']"),
        ("xpath", "//input[@type='email' or contains(@placeholder, 'email')]"),
    ]
    
    # Continue Button (after email)
    CONTINUE_BUTTON = [
        ("id", "signin-continue-btn"),
        ("xpath", "//button[contains(text(), 'Continue')]"),
        ("css", "button[type='submit'][id*='continue']"),
    ]
    
    # Password Input Field
    PASSWORD_INPUT = [
        ("id", "pass"),
        ("name", "pass"),
        ("xpath", "//input[@id='pass']"),
        ("xpath", "//input[@type='password']"),
    ]
    
    # Sign In Button (bottom of form)
    SIGNIN_BUTTON = [
        ("id", "sgnBt"),  # Primary - actual button ID
        ("xpath", "//button[@id='sgnBt']"),
        ("xpath", "//button[contains(text(), 'Sign in')]"),
        ("css", "button[type='button'][id='sgnBt']"),
    ]


class EbayLoginPage:
    """
    Page Object עבור דף התחברות eBay.
    
    עוטף SmartLocatorFinder ומספק methods בעברית וברור.
    """
    
    def __init__(self, driver, timeout_sec: float = 10):
        """
        Initialize eBay Login Page.
        
        Args:
            driver: Selenium WebDriver instance
            timeout_sec: Default timeout for operations
        """
        self.driver = driver
        self.finder = SmartLocatorFinder(driver, timeout_sec=timeout_sec)
    
    def click_sign_in(self) -> None:
        """
        Click Sign In button on homepage.
        
        Raises:
            TimeoutError: If button not found
        """
        self.finder.click_element(
            EbayLoginLocators.SIGN_IN_BUTTON,
            description="Sign In button (homepage)"
        )
    
    def enter_email(self, email: str) -> None:
        """
        Enter email address.
        
        Args:
            email: Email to enter
        
        Raises:
            TimeoutError: If field not found
        """
        self.finder.type_text(
            EbayLoginLocators.EMAIL_INPUT,
            email,
            description="Email input field"
        )
    
    def click_continue(self) -> None:
        """
        Click Continue button after email.
        
        Raises:
            TimeoutError: If button not found
        """
        self.finder.click_element(
            EbayLoginLocators.CONTINUE_BUTTON,
            description="Continue button"
        )
    
    def enter_password(self, password: str) -> None:
        """
        Enter password.
        
        Args:
            password: Password to enter
        
        Raises:
            TimeoutError: If field not found
        """
        self.finder.type_text(
            EbayLoginLocators.PASSWORD_INPUT,
            password,
            description="Password input field"
        )
    
    def click_signin_submit(self) -> None:
        """
        Click Sign In submit button.
        
        Raises:
            TimeoutError: If button not found
        """
        self.finder.click_element(
            EbayLoginLocators.SIGNIN_BUTTON,
            description="Sign In submit button"
        )
    
    def wait_for_email_field(self, timeout_sec: Optional[float] = None) -> None:
        """
        Wait for email field to appear.
        
        Args:
            timeout_sec: Custom timeout
        """
        self.finder.wait_for_element(
            EbayLoginLocators.EMAIL_INPUT,
            description="Email input field",
            timeout_sec=timeout_sec,
            state="visible"
        )
    
    def wait_for_password_field(self, timeout_sec: Optional[float] = None) -> None:
        """
        Wait for password field to appear.
        
        Args:
            timeout_sec: Custom timeout
        """
        self.finder.wait_for_element(
            EbayLoginLocators.PASSWORD_INPUT,
            description="Password input field",
            timeout_sec=timeout_sec,
            state="visible"
        )
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.driver.current_url
    
    def is_on_captcha_page(self) -> bool:
        """Check if we're on CAPTCHA page."""
        url = self.get_current_url()
        return "captcha" in url.lower() or "security" in url.lower()
    
    def is_on_login_page(self) -> bool:
        """Check if we're still on login page."""
        url = self.get_current_url()
        return "signin" in url.lower()
    
    def is_on_ebay_home(self) -> bool:
        """Check if we're on eBay homepage."""
        url = self.get_current_url()
        return "ebay.com" in url and "signin" not in url.lower()
