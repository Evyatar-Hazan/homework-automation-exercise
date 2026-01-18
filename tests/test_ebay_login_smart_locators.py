"""
eBay Login Test with Smart Locators
====================================

בדיקה המשתמשת בSmartLocatorFinder עם fallback locators.

כל אלמנט מוגדר עם לפחות 2 לוקייטורים חלופיים.
בזמן ריצה, אם הלוקייטור הראשוני נכשל, נסה את התחליף.

הלוגיקה טמונה בשכבת SmartLocatorFinder,
הבדיקה עצמה נקיה וקריאה.
"""

import pytest
import allure
import time
import os
import undetected_chromedriver as uc

from automation.pages.ebay_login_page import EbayLoginPage


EBAY_URL = "https://www.ebay.com"
EMAIL = os.getenv("EBAY_TEST_EMAIL", "")
PASSWORD = os.getenv("EBAY_TEST_PASSWORD", "")


@allure.title("eBay Login with Smart Locators")
@allure.description("Login to eBay using SmartLocatorFinder with fallback locators")
@allure.tag("ebay", "login", "smart-locators", "fallback")
@allure.severity(allure.severity_level.CRITICAL)
def test_ebay_login_with_smart_locators():
    """Test eBay login using SmartLocator fallback mechanism."""
    
    driver = None
    
    try:
        # ============================================================
        # Step 1: Launch Browser
        # ============================================================
        with allure.step("Launch undetected browser"):
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-gpu")
            
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")
            
            driver = uc.Chrome(options=options, headless=False, version_main=None, suppress_welcome=True)
            driver.set_page_load_timeout(30)
            
            # Initialize page object
            login_page = EbayLoginPage(driver, timeout_sec=10)
            
            allure.attach("✓ Browser launched", name="browser_init", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 2: Navigate to eBay
        # ============================================================
        with allure.step("Navigate to eBay homepage"):
            driver.get(EBAY_URL)
            time.sleep(5)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="Homepage", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 3: Click Sign In
        # ============================================================
        with allure.step("Click Sign In button"):
            login_page.click_sign_in()
            time.sleep(3)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="After Sign In Click", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 4: Wait for Email Field & Enter Email
        # ============================================================
        with allure.step(f"Enter email: {EMAIL}"):
            login_page.wait_for_email_field(timeout_sec=10)
            time.sleep(1)
            
            login_page.enter_email(EMAIL)
            time.sleep(1.5)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="After Email Entry", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 5: Click Continue
        # ============================================================
        with allure.step("Click Continue button"):
            login_page.click_continue()
            time.sleep(3)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="After Continue Click", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 6: Wait for Password Field & Enter Password
        # ============================================================
        with allure.step(f"Enter password"):
            login_page.wait_for_password_field(timeout_sec=10)
            time.sleep(1)
            
            login_page.enter_password(PASSWORD)
            time.sleep(1.5)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="After Password Entry", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 7: Submit Login
        # ============================================================
        with allure.step("Click Sign In submit button"):
            login_page.click_signin_submit()
            time.sleep(15)  # Wait for page load/redirect
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="After Submit", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 8: Verify Login Result
        # ============================================================
        with allure.step("Verify login result"):
            current_url = login_page.get_current_url()
            page_title = driver.title
            page_source = driver.page_source.lower()
            
            # Check login status
            is_captcha = login_page.is_on_captcha_page()
            is_login_page = login_page.is_on_login_page()
            is_home = login_page.is_on_ebay_home()
            
            verification_report = f"""
LOGIN VERIFICATION REPORT
═════════════════════════════════════════════════════════════════

Current URL: {current_url}
Page Title: {page_title}

Status Checks:
  ✓ On CAPTCHA page: {is_captcha}
  ✓ On Login page: {is_login_page}
  ✓ On eBay Home: {is_home}

Interpretation:
  {
    '❌ CAPTCHA detected - Bot detection triggered' if is_captcha else
    '❌ Still on login page - Credentials failed' if is_login_page else
    '✅ Successfully logged in - On eBay homepage' if is_home else
    '⚠️  Unexpected page state'
  }
"""
            
            allure.attach(
                verification_report,
                name="Verification Report",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Assert result
            if is_captcha:
                raise AssertionError(f"❌ CAPTCHA detected: {current_url}")
            
            if is_login_page:
                raise AssertionError(f"❌ Still on login page: {current_url}")
            
            assert is_home, f"❌ Not on eBay home: {current_url}"
    
    finally:
        with allure.step("Cleanup"):
            if driver:
                try:
                    driver.quit()
                except:
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=reports/allure-results"])
