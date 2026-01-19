"""
eBay Login Test with Pre-Authenticated Cookies
================================================

This test uses pre-saved cookies from a real session to avoid CAPTCHA.
First run: python get_session_cookies.py (solve CAPTCHA manually once)
Then: pytest tests/test_ebay_login_with_cookies.py

שימוש בתשתית משותפת:
- BaseSeleniumTest מטפל ב-Browser setup/teardown
- Browser launch עם anti-bot protection
- Cleanup automatic
"""

import pytest
import allure
import time
import pickle
import os
from selenium.webdriver.common.by import By

from automation.core import BaseSeleniumTest, get_logger

logger = get_logger(__name__)

EBAY_URL = "https://www.ebay.com"
COOKIES_FILE = "reports/ebay_cookies.pkl"


class TestEBayLoginWithCookies(BaseSeleniumTest):
    """Test eBay login using pre-authenticated cookies."""
    
    @allure.title("eBay Login Test with Pre-Authenticated Cookies")
    @allure.description("Use saved cookies from real session to avoid CAPTCHA detection")
    @allure.tag("ebay", "login", "cookies", "anti-bot")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ebay_login_with_cookies(self):
        """Test eBay with pre-authenticated cookies instead of credentials."""
        
        # ============================================================
        # Step 1: Check if cookies exist
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
            
            logger.info(f"✅ Loaded {len(cookies)} cookies from saved session")
            
            allure.attach(
                f"✅ Loaded {len(cookies)} cookies from saved session\n"
                f"Cookies file: {COOKIES_FILE}",
                name="cookies_loaded",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # ============================================================
        # Step 2: Navigate to eBay and add cookies
        # ============================================================
        with allure.step("Navigate to eBay and inject cookies"):
            # First navigate to eBay (required before adding cookies)
            self.navigate_to(EBAY_URL)
            
            # Add all cookies
            self.add_cookies(cookies)
            
            logger.info(f"✓ Added {len(cookies)} cookies to browser")
            allure.attach(
                f"✓ Added {len(cookies)} cookies to browser",
                name="cookies_added",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # ============================================================
        # Step 3: Refresh page with cookies loaded
        # ============================================================
        with allure.step("Refresh page with session cookies"):
            self.refresh_page()
            
            self.take_screenshot("eBay with Cookies")
        
        # ============================================================
        # Step 4: Verify we're logged in
        # ============================================================
        with allure.step("Verify login status"):
            current_url = self.get_current_url()
            page_source_lower = self.get_page_source().lower()
            page_title = self.get_page_title()
            
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
            
            logger.info(f"Verification Report:\n{verification_report}")
            
            # Assert success
            if is_captcha_page:
                raise AssertionError(f"❌ CAPTCHA challenge page detected! Cookies may be expired. URL: {current_url}")
            
            if still_on_signin:
                raise AssertionError(f"❌ Still on signin page! Cookies were not accepted. URL: {current_url}")
            
            if not is_on_homepage:
                raise AssertionError(f"❌ Not on eBay homepage. URL: {current_url}")
            
            # Success!
            logger.info("✅ Successfully accessed eBay with authenticated session cookies!")
            allure.attach(
                "✅ Successfully accessed eBay with authenticated session cookies!",
                name="success",
                attachment_type=allure.attachment_type.TEXT
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=allure-results"])
