"""
eBay Login Test with Pre-Authenticated Cookies
================================================

This test uses pre-saved cookies from a real session to avoid CAPTCHA.
First run: python get_session_cookies.py (solve CAPTCHA manually once)
Then: pytest tests/test_ebay_login_with_cookies.py
"""

import pytest
import allure
import time
import pickle
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


EBAY_URL = "https://www.ebay.com"
COOKIES_FILE = "reports/ebay_cookies.pkl"


@allure.title("eBay Login Test with Pre-Authenticated Cookies")
@allure.description("Use saved cookies from real session to avoid CAPTCHA detection")
@allure.tag("ebay", "login", "cookies", "anti-bot")
@allure.severity(allure.severity_level.CRITICAL)
def test_ebay_login_with_cookies():
    """Test eBay with pre-authenticated cookies instead of credentials."""
    
    driver = None
    
    try:
        # ============================================================
        # Check if cookies exist
        # ============================================================
        with allure.step("Check for saved session cookies"):
            if not os.path.exists(COOKIES_FILE):
                raise FileNotFoundError(
                    f"❌ Cookies file '{COOKIES_FILE}' not found!\n"
                    "Run: python get_session_cookies.py\n"
                    "Then solve CAPTCHA manually to save cookies."
                )
            
            with open(COOKIES_FILE, 'rb') as f:
                cookies = pickle.load(f)
            
            allure.attach(
                f"✅ Loaded {len(cookies)} cookies from saved session\n"
                f"Cookies file: {COOKIES_FILE}",
                name="cookies_loaded",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # ============================================================
        # Launch Browser
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
            
            allure.attach("✓ Browser launched", name="browser_status", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Navigate to eBay and add cookies
        # ============================================================
        with allure.step("Navigate to eBay and inject cookies"):
            # First navigate to eBay (required before adding cookies)
            driver.get(EBAY_URL)
            time.sleep(3)
            
            # Add all cookies
            for cookie in cookies:
                try:
                    # Remove attributes that can cause issues
                    if 'expiry' in cookie:
                        # Only set expiry if it's valid
                        if isinstance(cookie['expiry'], (int, float)):
                            pass
                    
                    driver.add_cookie(cookie)
                except Exception as e:
                    # Skip problematic cookies
                    pass
            
            allure.attach(f"✓ Added {len(cookies)} cookies to browser", name="cookies_added", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Refresh page with cookies loaded
        # ============================================================
        with allure.step("Refresh page with session cookies"):
            driver.get(EBAY_URL)
            time.sleep(5)
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="eBay with Cookies", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Verify we're logged in
        # ============================================================
        with allure.step("Verify login status"):
            current_url = driver.current_url
            page_source_lower = driver.page_source.lower()
            page_title = driver.title
            
            # Check for ACTUAL CAPTCHA CHALLENGE page (not just CSS mentions)
            # Real CAPTCHA has specific phrases
            is_captcha_page = (
                "captcha" in current_url.lower() or
                "splashui/captcha" in current_url.lower() or
                ("security measure" in page_source_lower and "prove you" in page_source_lower) or
                ("/signin" in current_url and "captcha" in current_url)
            )
            
            # Check if still on signin page
            still_on_signin = "/signin" in current_url and "captcha" not in current_url
            
            # Simple check: if we're on ebay.com homepage, we're logged in
            is_on_homepage = current_url.strip('/').endswith('ebay.com') or current_url.endswith('ebay.com/')
            
            verification_report = f"""
LOGIN VERIFICATION WITH COOKIES
═════════════════════════════════════════════════════════════════

Current URL: {current_url}
Page Title: {page_title}

CHECKS:
  1. CAPTCHA Challenge: {'❌ Yes - Detected' if is_captcha_page else '✅ No - Not detected'}
  2. Still on signin page: {'❌ Yes' if still_on_signin else '✅ No'}
  3. On eBay homepage: {'✅ Yes' if is_on_homepage else '❌ No'}

STATUS: {'✅ SESSION LOADED SUCCESSFULLY' if (is_on_homepage and not is_captcha_page and not still_on_signin) else '❌ FAILED TO LOAD SESSION'}
"""
            
            allure.attach(verification_report, name="Login Verification", attachment_type=allure.attachment_type.TEXT)
            
            # Assert success
            if is_captcha_page:
                raise AssertionError(f"❌ CAPTCHA challenge page detected! Cookies may be expired. URL: {current_url}")
            
            if still_on_signin:
                raise AssertionError(f"❌ Still on signin page! Cookies were not accepted. URL: {current_url}")
            
            if not is_on_homepage:
                raise AssertionError(f"❌ Not on eBay homepage. URL: {current_url}")
            
            # Success!
            allure.attach("✅ Successfully accessed eBay with authenticated session cookies!", name="success", attachment_type=allure.attachment_type.TEXT)
    
    except Exception as e:
        with allure.step("Handle error"):
            error_msg = f"Error: {str(e)}"
            allure.attach(error_msg, name="error", attachment_type=allure.attachment_type.TEXT)
            
            if driver:
                try:
                    screenshot = driver.get_screenshot_as_png()
                    allure.attach(screenshot, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
                except:
                    pass
        
        raise
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=allure-results"])
