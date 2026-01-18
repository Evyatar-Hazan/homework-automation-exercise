#!/usr/bin/env python3
"""Debug script - check what's on eBay homepage with cookies."""

import pickle
import time
import undetected_chromedriver as uc

EBAY_URL = "https://www.ebay.com"
COOKIES_FILE = "reports/ebay_cookies.pkl"

# Load cookies
with open(COOKIES_FILE, 'rb') as f:
    cookies = pickle.load(f)

# Launch browser
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options, headless=False)

try:
    # Navigate and add cookies
    driver.get(EBAY_URL)
    time.sleep(2)
    
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    
    # Refresh with cookies
    driver.get(EBAY_URL)
    time.sleep(5)
    
    # Get page info
    current_url = driver.current_url
    page_source = driver.page_source.lower()
    page_title = driver.title
    
    print(f"\n📊 PAGE INFO:")
    print(f"URL: {current_url}")
    print(f"Title: {page_title}")
    print(f"Page length: {len(page_source)} chars")
    
    # Search for specific words
    print(f"\n🔍 WORD SEARCHES:")
    print(f"'captcha' in page: {'captcha' in page_source}")
    print(f"'security measure' in page: {'security measure' in page_source}")
    print(f"'prove you' in page: {'prove you' in page_source}")
    print(f"'signin' in page: {'signin' in page_source}")
    
    # Find where 'captcha' appears
    if 'captcha' in page_source:
        idx = page_source.find('captcha')
        print(f"\n'captcha' found at position {idx}")
        print(f"Context: ...{page_source[max(0, idx-50):idx+100]}...")
    
    # Get first 2000 chars
    print(f"\n📄 FIRST 2000 CHARS OF PAGE:")
    print(page_source[:2000])
    
finally:
    driver.quit()
