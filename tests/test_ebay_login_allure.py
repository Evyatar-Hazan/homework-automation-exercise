"""
eBay Login Test with Allure Reports Integration
================================================

This test demonstrates:
- Opening eBay website
- Logging in with valid credentials
- Using undetected-chromedriver to bypass bot detection
- Allure Reports generation with detailed steps
- Screenshot attachment
- Human-like behavior (delays, interactions)

Test will generate allure-results/ directory with comprehensive reports.
"""

import pytest
import allure
import time
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


# ============================================================
# Test Credentials
# ============================================================

EBAY_URL = "https://www.ebay.com"
EMAIL = "EvayatarHazan3.14@gmail.com"
PASSWORD = "Eh123456"


# ============================================================
# Test Implementation
# ============================================================

@allure.title("eBay Login Test with Allure Reports")
@allure.description("Complete login flow to eBay with Allure reporting - Using undetected-chromedriver to bypass bot detection")
@allure.tag("ebay", "login", "critical", "undetected")
@allure.severity(allure.severity_level.CRITICAL)
def test_ebay_login_with_allure():
    """Test eBay login functionality with Allure reporting using undetected-chromedriver."""
    
    driver = None
    
    try:
        # ============================================================
        # Step 1: Launch Browser with undetected-chromedriver
        # ============================================================
        with allure.step("Launch undetected browser and navigate to eBay"):
            allure.attach(
                f"Test started at {datetime.now().isoformat()}\nUsing: undetected-chromedriver (bypasses bot detection)",
                name="test_start_time",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Launch undetected Chrome driver with STRONGER anti-detection options
            options = uc.ChromeOptions()
            
            # Core anti-detection arguments
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-setuid-sandbox")
            
            # Disable various detection methods
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-popup-blocking")
            
            # Browser capabilities
            options.add_argument("--start-maximized")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-resources")
            options.add_argument("--disable-preconnect")
            
            # Real user agents (rotate for less suspicion)
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            options.add_argument(f"user-agent={user_agents[0]}")
            
            # Increase timeouts for natural behavior
            driver = uc.Chrome(options=options, headless=False, version_main=None, suppress_welcome=True)
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            
            # Navigate to eBay
            driver.get(EBAY_URL)
            time.sleep(7)  # Longer wait for page load (human-like delay)
            
            allure.attach(f"Navigated to: {EBAY_URL}", name="navigation", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 2: Take homepage screenshot
        # ============================================================
        with allure.step("Capture eBay homepage"):
            time.sleep(2)  # Human-like delay
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="eBay Homepage", attachment_type=allure.attachment_type.PNG)
        
        # ============================================================
        # Step 3: Click Sign In
        # ============================================================
        with allure.step("Click Sign In button"):
            try:
                # Try to find and click Sign In button
                sign_in_selectors = [
                    ("xpath", "//a[contains(text(), 'Sign in')]"),
                    ("xpath", "//a[@class and contains(@href, 'signin')]"),
                    ("xpath", "//button[contains(text(), 'Sign in')]"),
                    ("xpath", "//div[@aria-label='Sign in']"),
                    ("xpath", "//a[contains(., 'Sign in')]"),
                    ("css selector", "a[href*='signin']"),
                ]
                
                sign_in_clicked = False
                for by, selector in sign_in_selectors:
                    try:
                        # Wait a bit before trying
                        time.sleep(1)
                        
                        elements = driver.find_elements(by, selector)
                        for element in elements:
                            if element.is_displayed():
                                # Human-like: move mouse to element first
                                actions = ActionChains(driver)
                                actions.move_to_element(element).pause(1).click().perform()
                                time.sleep(2)
                                allure.attach(f"✓ Clicked Sign In with selector: {selector}", name="click_result", attachment_type=allure.attachment_type.TEXT)
                                time.sleep(2)
                                sign_in_clicked = True
                                break
                    except:
                        continue
                    
                    if sign_in_clicked:
                        break
                
                if not sign_in_clicked:
                    allure.attach("⚠️  Sign In button not found with default selectors - may be already on login page", name="click_warning", attachment_type=allure.attachment_type.TEXT)
                
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name="After Sign In Click", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(f"Error clicking Sign In: {str(e)}", name="error", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 4: Enter Email
        # ============================================================
        with allure.step(f"Enter email: {EMAIL}"):
            try:
                # First, log what we see on the page
                page_html = driver.page_source
                
                # Check if we're on the right page
                if "userid" in page_html.lower() or "email" in page_html.lower():
                    allure.attach("✓ Email input field detected on page", name="page_analysis", attachment_type=allure.attachment_type.TEXT)
                else:
                    allure.attach("⚠️  Email input field NOT found on page - checking alternatives", name="page_analysis", attachment_type=allure.attachment_type.TEXT)
                
                email_selectors = [
                    ("id", "userid"),
                    ("name", "userid"),
                    ("xpath", "//input[@id='userid']"),
                    ("xpath", "//input[@type='email']"),
                    ("xpath", "//input[@aria-label*='email']"),
                    ("css selector", "input[type='email']"),
                    ("xpath", "//input[contains(@placeholder, 'email') or contains(@placeholder, 'Email')]"),
                ]
                
                email_field = None
                for by, selector in email_selectors:
                    try:
                        email_field = driver.find_element(by, selector)
                        if email_field.is_displayed():
                            # Mouse movement before click (human-like behavior)
                            action_chains = ActionChains(driver)
                            action_chains.move_to_element(email_field).click().perform()
                            time.sleep(1)
                            email_field.clear()
                            time.sleep(0.5)
                            
                            # Type email SLOWLY (character by character with delays)
                            for char in EMAIL:
                                email_field.send_keys(char)
                                time.sleep(0.05)  # Delay between characters
                            
                            allure.attach(f"✓ Email entered SLOWLY with selector: {selector}", name="email_input", attachment_type=allure.attachment_type.TEXT)
                            time.sleep(1.5)
                            break
                    except:
                        continue
                
                if not email_field:
                    allure.attach("❌ Email field not found with any selector", name="email_warning", attachment_type=allure.attachment_type.TEXT)
                
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name="After Email Entry", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(f"Error entering email: {str(e)}", name="error", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 5: Click Continue
        # ============================================================
        with allure.step("Click Continue button"):
            try:
                continue_selectors = [
                    ("id", "signin-continue-btn"),
                    ("xpath", "//button[contains(text(), 'Continue')]"),
                    ("xpath", "//button[@type='submit']"),
                    ("css selector", "button[type='submit']"),
                ]
                
                continue_clicked = False
                for by, selector in continue_selectors:
                    try:
                        time.sleep(1)
                        buttons = driver.find_elements(by, selector)
                        for button in buttons:
                            if button.is_displayed():
                                button.click()
                                allure.attach(f"✓ Continue clicked with selector: {selector}", name="continue_result", attachment_type=allure.attachment_type.TEXT)
                                time.sleep(4)
                                continue_clicked = True
                                break
                        if continue_clicked:
                            break
                    except:
                        continue
            except Exception as e:
                allure.attach(f"Error clicking Continue: {str(e)}", name="error", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 6: Enter Password
        # ============================================================
        with allure.step("Enter password"):
            try:
                password_selectors = [
                    ("id", "pass"),
                    ("name", "pass"),
                    ("xpath", "//input[@type='password']"),
                    ("xpath", "//input[@aria-label*='password']"),
                    ("css selector", "input[type='password']"),
                ]
                
                password_field = None
                for by, selector in password_selectors:
                    try:
                        password_field = driver.find_element(by, selector)
                        if password_field.is_displayed():
                            # Mouse movement before click (more human-like)
                            action_chains = ActionChains(driver)
                            action_chains.move_to_element(password_field).click().perform()
                            time.sleep(0.8)
                            password_field.clear()
                            time.sleep(0.5)
                            
                            # Type password SLOWLY (character by character with delays)
                            for char in PASSWORD:
                                password_field.send_keys(char)
                                time.sleep(0.1)  # Delay between characters
                            
                            allure.attach(f"✓ Password entered SLOWLY with selector: {selector}", name="password_input", attachment_type=allure.attachment_type.TEXT)
                            time.sleep(1.5)
                            break
                    except:
                        continue
                
                if not password_field:
                    allure.attach("Password field not found", name="password_warning", attachment_type=allure.attachment_type.TEXT)
                
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name="After Password Entry", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(f"Error entering password: {str(e)}", name="error", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 7: Submit Login - Click the actual Sign in button (ID: sgnBt)
        # ============================================================
        with allure.step("Submit login form"):
            try:
                # The actual button ID is 'sgnBt' (not signin-continue-btn)
                submit_btn = driver.find_element("id", "sgnBt")
                
                if submit_btn:
                    allure.attach("✓ Found actual Sign in button (ID: sgnBt)", name="submit_found", attachment_type=allure.attachment_type.TEXT)
                    
                    # Move mouse to button slowly (human-like)
                    action_chains = ActionChains(driver)
                    action_chains.move_to_element(submit_btn).perform()
                    time.sleep(1)
                    
                    # Scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                    time.sleep(1.5)
                    
                    # Click the button via JavaScript
                    driver.execute_script("arguments[0].click();", submit_btn)
                    allure.attach("✓ Clicked Sign in button (sgnBt)", name="submit_result", attachment_type=allure.attachment_type.TEXT)
                    
                    # Wait for page to load - be VERY patient (give eBay time to process)
                    driver.implicitly_wait(15)
                    time.sleep(15)  # Wait 15 seconds for redirect/CAPTCHA to appear
                    time.sleep(3)
                    # Wait for possible redirect or CAPTCHA
                    driver.implicitly_wait(10)
                    time.sleep(8)
                    
            except Exception as e:
                allure.attach(f"❌ Error clicking Sign in button: {str(e)}", name="submit_error", attachment_type=allure.attachment_type.TEXT)
        
        # ============================================================
        # Step 8: Verify Login Success - REAL VALIDATION
        # ============================================================
        with allure.step("Verify login success - Check if we're truly logged in"):
            time.sleep(2)
            current_url = driver.current_url
            page_title = driver.title
            page_source = driver.page_source
            
            allure.attach(
                f"Current URL: {current_url}\nPage Title: {page_title}",
                name="page_info_after_login",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Screenshot of final page
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, name="Final Page After Login", attachment_type=allure.attachment_type.PNG)
            
            # ============================================================
            # CHECK 1: Did we hit CAPTCHA/Anti-bot page?
            # ============================================================
            with allure.step("Check 1: Did we hit CAPTCHA or anti-bot page?"):
                # Check for ACTUAL CAPTCHA page (not just CSS mentions)
                hit_captcha = (
                    "splashui/captcha" in current_url.lower() or
                    "/signin" in current_url and "captcha" in current_url.lower() or
                    ("security measure" in page_source.lower() and "prove you" in page_source.lower())
                )
                
                captcha_report = f"""
CAPTCHA DETECTION
═════════════════════════════════════════════════════════════

Current URL: {current_url}
Page Title: {page_title}

CAPTCHA Challenge: {'❌ YES - DETECTED' if hit_captcha else '✅ NO - NOT DETECTED'}

This indicates: {'❌ BOT DETECTED - eBay recognized automation attempt' if hit_captcha else '✅ No bot detection'}
"""
                
                allure.attach(
                    captcha_report,
                    name="captcha_check",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # ============================================================
            # CHECK 2: Are we on eBay's main/account page? (not login page)
            # ============================================================
            with allure.step("Check 2: Are we on actual eBay account page (not login)?"):
                is_on_ebay_main = "ebay.com" in current_url.lower() and "signin" not in current_url.lower()
                
                # If we're still on signin page, login failed
                still_on_signin = "signin" in current_url.lower()
                
                page_location_report = f"""
PAGE LOCATION CHECK
═════════════════════════════════════════════════════════════

Current URL: {current_url}
Still on Sign-in page: {'❌ YES' if still_on_signin else '✅ NO'}
On eBay (not signin): {'✅ YES' if is_on_ebay_main else '❌ NO'}

This indicates: {'❌ Still stuck on login page - FAILED' if still_on_signin else '✅ Redirected from login page'}
"""
                
                allure.attach(
                    page_location_report,
                    name="page_location_check",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # ============================================================
            # FINAL VERDICT: Login successful or failed?
            # ============================================================
            with allure.step("Final Verdict: Did login succeed?"):
                # Login succeeded ONLY if:
                # 1. No CAPTCHA page
                # 2. Not on signin page anymore
                # 3. We're on ebay.com
                
                login_actually_succeeded = (
                    not hit_captcha and 
                    not still_on_signin and 
                    is_on_ebay_main
                )
                
                final_verdict = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                        🔐 FINAL LOGIN VERDICT                              ║
╚════════════════════════════════════════════════════════════════════════════╝

Credentials: {EMAIL}
Final URL: {current_url}
Page Title: {page_title}

VERIFICATION CHECKS:
  1. CAPTCHA Page: {'❌ YES - DETECTED' if hit_captcha else '✅ NO - NOT DETECTED'}
  2. Still on Login Page: {'❌ YES' if still_on_signin else '✅ NO'}
  3. On eBay Main Page: {'✅ YES' if is_on_ebay_main else '❌ NO'}

═════════════════════════════════════════════════════════════════════════════

RESULT: {'✅ LOGIN SUCCESSFUL' if login_actually_succeeded else '❌ LOGIN FAILED'}

Why:
{'✗ eBay detected automation and showed CAPTCHA' if hit_captcha else 
 '✗ Form submission failed - still on signin page' if still_on_signin else
 '✗ Could not reach eBay main page' if not is_on_ebay_main else
 '✅ Successfully authenticated to eBay!'}

═════════════════════════════════════════════════════════════════════════════
"""
                
                allure.attach(
                    final_verdict,
                    name="Final Login Verdict",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Fail the test if login didn't work
                if hit_captcha:
                    captcha_failure = f"""
❌ BOT DETECTED - CAPTCHA CHALLENGE
═════════════════════════════════════════════════════════════════════════════

eBay presented a CAPTCHA verification page instead of completing login.

What this means:
  ✗ Credentials may be correct BUT...
  ✗ eBay detected our automation attempt
  ✗ Form submission triggered bot detection
  ✗ Cannot proceed without human CAPTCHA solving

Current URL: {current_url}

SOLUTION OPTIONS:
  1. Use pre-authenticated session cookies (see test_ebay_login_with_cookies.py)
  2. Strengthen anti-detection measures in undetected-chromedriver
  3. Add manual CAPTCHA solving capability (2captcha, AntiCaptcha APIs)
  4. Use eBay's official testing sandbox environment

═════════════════════════════════════════════════════════════════════════════
"""
                    allure.attach(captcha_failure, name="CAPTCHA Failure", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(f"❌ Test FAILED - CAPTCHA detected. eBay identified bot detection. URL: {current_url}")
                
                if still_on_signin:
                    signin_failure = f"""
❌ FORM SUBMISSION FAILED
═════════════════════════════════════════════════════════════════════════════

Still on login page after submitting credentials. Form didn't process.

Current URL: {current_url}

Possible issues:
  - Credentials incorrect
  - Button not clicked properly
  - JavaScript didn't execute
  - Form validation failed

═════════════════════════════════════════════════════════════════════════════
"""
                    allure.attach(signin_failure, name="Submit Failure", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(f"❌ Test FAILED - Form submission didn't work. URL: {current_url}")
                
                if not is_on_ebay_main:
                    page_failure = f"""
❌ UNEXPECTED PAGE
═════════════════════════════════════════════════════════════════════════════

Didn't reach eBay main page after login attempt.

Current URL: {current_url}
Expected: ebay.com (without /signin)

═════════════════════════════════════════════════════════════════════════════
"""
                    allure.attach(page_failure, name="Page Failure", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(f"❌ Test FAILED - Unexpected page. URL: {current_url}")
    
    except Exception as e:
        # ============================================================
        # Error Handling
        # ============================================================
        with allure.step("Handle test error"):
            error_msg = f"Error: {str(e)}\nError Type: {type(e).__name__}"
            allure.attach(error_msg, name="error_details", attachment_type=allure.attachment_type.TEXT)
            
            if driver:
                try:
                    screenshot = driver.get_screenshot_as_png()
                    allure.attach(screenshot, name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
                except:
                    pass
        
        raise
    
    finally:
        # ============================================================
        # Cleanup
        # ============================================================
        with allure.step("Close browser and cleanup"):
            if driver:
                try:
                    driver.quit()
                except:
                    pass


if __name__ == "__main__":
    """
    Run the test with:
    pytest tests/test_ebay_login_allure.py -v --alluredir=allure-results
    """
    pytest.main([__file__, "-v", "--alluredir=allure-results"])
