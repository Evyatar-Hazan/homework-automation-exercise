#!/usr/bin/env python3
"""
Get eBay session cookies from a real browser login.
Run this once manually to establish a real session, then use cookies in tests.
"""

import pickle
import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

EBAY_URL = "https://www.ebay.com"
EMAIL = "EvayatarHazan3.14@gmail.com"
PASSWORD = "Eh123456"
REPORTS_DIR = "reports"
COOKIES_FILE = os.path.join(REPORTS_DIR, "ebay_cookies.pkl")

def get_fresh_cookies():
    """Open browser, login manually (with CAPTCHA if needed), save cookies."""
    
    # Create reports directory
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("🌐 Opening browser for manual login...")
    print(f"📧 Email: {EMAIL}")
    print("🔐 You'll need to complete the CAPTCHA manually")
    print("\nOnce you're logged in, the cookies will be saved.\n")
    
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    driver = uc.Chrome(options=options, headless=False)
    
    try:
        # Navigate to eBay
        driver.get(f"{EBAY_URL}/signin")
        
        # Wait for manual login (user solves CAPTCHA)
        print("⏳ Waiting for you to log in manually (complete CAPTCHA if shown)...")
        print("   Once logged in, the script will auto-save cookies.\n")
        
        # Check if we're logged in by looking for logout/account menu
        logged_in = False
        wait_time = 0
        max_wait = 600  # 10 minutes
        
        while wait_time < max_wait:
            try:
                # Check if we see account menu (sign of being logged in)
                current_url = driver.current_url
                page_source = driver.page_source
                
                # Look for logged-in indicators
                if ("account" in page_source.lower() and "my ebay" in page_source.lower()) or \
                   ("ebay.com/" in current_url and "signin" not in current_url and "captcha" not in current_url):
                    logged_in = True
                    break
                
                time.sleep(5)
                wait_time += 5
                print(f"⏳ Waiting... {wait_time}s / {max_wait}s")
            except:
                time.sleep(5)
                wait_time += 5
        
        if logged_in:
            print("\n✅ Logged in! Saving cookies...\n")
            
            # Get all cookies
            cookies = driver.get_cookies()
            
            # Save to file
            with open(COOKIES_FILE, 'wb') as f:
                pickle.dump(cookies, f)
            
            print(f"✅ Cookies saved to {COOKIES_FILE}")
            print(f"📊 Total cookies: {len(cookies)}")
            print("\nYou can now use these cookies in automated tests!")
            
            return True
        else:
            print(f"\n⏱️  Timeout after {max_wait} seconds")
            print("Script will still save current cookies if any exist.")
            
            cookies = driver.get_cookies()
            if cookies:
                with open(COOKIES_FILE, 'wb') as f:
                    pickle.dump(cookies, f)
                print(f"✅ Partial cookies saved ({len(cookies)} cookies)")
            
            return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = get_fresh_cookies()
    if success:
        print("\n🎉 Session cookies ready for automated tests!")
    else:
        print("\n⚠️  Login may not have completed. Try again.")
