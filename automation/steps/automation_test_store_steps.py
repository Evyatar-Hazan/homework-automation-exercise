"""
Automation Test Store Steps
============================

Reusable steps for Automation Test Store tests.

Each function here is a "step" that can be reused across multiple tests.
"""

import os
import allure
import time
from selenium.webdriver.common.by import By
from automation.core import get_logger, log_step_with_allure
from automation.core.logger import step_aware_loggerInfo, step_aware_loggerAttach
from automation.utils.smart_locator_finder import SmartLocatorFinder
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
from automation.pages.automation_test_store_cart_page import AutomationTestStoreCartLocators, AutomationTestStoreCommonLocators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




logger = get_logger(__name__)


def navigate_to_automation_test_store(driver, url: str = "https://automationteststore.com/"):
    """
    Navigate to Automation Test Store homepage.
    
    Args:
        driver: Selenium WebDriver instance
        url: URL to navigate to (default: Automation Test Store homepage)
    
    Returns:
        Current URL
    """
    step_aware_loggerInfo(f"Navigating to Automation Test Store - URL: {url}")
    
    driver.get(url)
    time.sleep(3)
    
    current_url = driver.current_url
    step_aware_loggerInfo(f"Successfully navigated to Automation Test Store - Final URL: {current_url}")
    
    return current_url

    """
    Verify that we are on Automation Test Store homepage.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if on homepage, raises AssertionError otherwise
    """
    step_aware_loggerInfo("ASSERT: Verifying Automation Test Store homepage")
    
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
    
    step_aware_loggerAttach(
        verification_report,
        name="homepage_verification",
        attachment_type=allure.attachment_type.TEXT
    )
    
    step_aware_loggerInfo(verification_report)
    
    assert is_homepage, f"Expected to be on automationteststore.com, but got {current_url}"
    assert has_correct_title, f"Page title '{page_title}' doesn't match expected title"
    
    return True


def click_login_or_register_link(driver):
    """
    Click the "Login or register" link on the homepage.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if successful
    """
    
    step_aware_loggerInfo("ACTION: Clicking 'Login or register' link")
    
    smart_locator = SmartLocatorFinder(driver)
    smart_locator.click_element(
        AutomationTestStoreLoginLocators.LOGIN_OR_REGISTER_LINK,
        description="Login or register link"
    )
    
    time.sleep(2)  # Wait for page to load

    step_aware_loggerInfo("✓ Successfully clicked 'Login or register' link")
    return True


def verify_account_login_page(driver) -> bool:
    """
    Verify that we are on the Account Login page.
    Checks for the "Account Login" heading and URL.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if on login page, raises AssertionError otherwise
    """
    
    step_aware_loggerInfo("ASSERT: Verifying Account Login page")
    
    current_url = driver.current_url
    
    # Check URL contains login
    has_login_url = "account/login" in current_url.lower() or "login" in current_url.lower()
    
    # Check for Account Login heading using SmartLocatorFinder
    try:
        smart_locator = SmartLocatorFinder(driver)
        heading = smart_locator.find_element(
            AutomationTestStoreLoginLocators.ACCOUNT_LOGIN_HEADING,
            description="Account Login heading"
        )
        has_login_heading = heading is not None
    except Exception as e:
        step_aware_loggerInfo(f"Could not find Account Login heading: {e}")
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
    
    
    step_aware_loggerInfo(verification_report)
    
    assert has_login_url, f"Expected login URL, but got {current_url}"
    assert has_login_heading, "Account Login heading not found on page"
    
    return True


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
        
    # Get username from environment variable
    username = os.getenv(env_var_name)
    
    if not username:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    step_aware_loggerInfo(f"ACTION: Entering username from {env_var_name} environment variable")
    
    # Use SmartLocatorFinder to find and enter username
    smart_locator = SmartLocatorFinder(driver)
    smart_locator.type_text(
        AutomationTestStoreCartLocators.USERNAME_INPUT,
        username,
        description="Username input field"
    )
    
    time.sleep(0.5)
    
    step_aware_loggerAttach(
        f"✓ Entered username: {username}",
        name="username_entry",
        attachment_type=allure.attachment_type.TEXT
    )
    
    step_aware_loggerInfo(f"✓ Successfully entered username: {username}")
    return username


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
    
    # Get email from environment variable
    email = os.getenv(env_var_name)
    
    if not email:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    step_aware_loggerInfo(f"ACTION: Entering email from {env_var_name} environment variable")
    
    # Use SmartLocatorFinder to find and enter email
    smart_locator = SmartLocatorFinder(driver)
    smart_locator.type_text(
        AutomationTestStoreCartLocators.USERNAME_INPUT,
        email,
        description="Email input field"
    )
    
    time.sleep(0.5)
    
    step_aware_loggerInfo(f"✓ Successfully entered email: {email}")
    return email


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
    
    # Get password from environment variable
    password = os.getenv(env_var_name)
    
    if not password:
        raise ValueError(f"Environment variable '{env_var_name}' not set. Please set it before running the test.")
    
    step_aware_loggerInfo(f"ACTION: Entering password from {env_var_name} environment variable")
    
    # Use SmartLocatorFinder to find and enter password
    smart_locator = SmartLocatorFinder(driver)
    smart_locator.type_text(
        AutomationTestStoreCartLocators.PASSWORD_INPUT,
        password,
        description="Password input field"
    )
    
    time.sleep(0.5)

    step_aware_loggerInfo(f"✓ Successfully entered password from {env_var_name}")
    return password


def click_login_button(driver) -> bool:
    """
    Click the Login submit button on the login form.
    Uses specific title attribute to distinguish from Continue button.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if button was clicked successfully
    """
    
    
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    
    step_aware_loggerInfo("ACTION: Clicking Login submit button")
    
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
    
    step_aware_loggerInfo("✓ Clicking Login button")
    login_button.click()
    time.sleep(2)  # Wait for login processing
    
    step_aware_loggerAttach(
        "✓ Clicked Login submit button",
        name="login_button_click",
        attachment_type=allure.attachment_type.TEXT
    )
    
    return True


def verify_login_success(driver, username_from_env: str = "Evyatar"):
    """
    Verify successful login by checking for welcome message.
    
    Args:
        driver: Selenium WebDriver instance
        username_from_env: Expected username to appear in welcome message (default: "Evyatar")
    
    Returns:
        The welcome message text
    """
        
    step_aware_loggerInfo(f"ACTION: Verifying login success - expecting welcome message with '{username_from_env}'")
    
    wait = WebDriverWait(driver, 10)
    smart_locator = SmartLocatorFinder(driver)
    
    # First, let's check the current page title and URL to see where we are
    current_url = driver.current_url
    page_title = driver.title
    step_aware_loggerInfo(f"Current URL after login: {current_url}")
    step_aware_loggerInfo(f"Current page title: {page_title}")
    
    # Get page source for debugging
    page_source = driver.page_source
    
    # Check if welcome message is in the page
    if "Welcome back" in page_source:
        step_aware_loggerInfo("✓ 'Welcome back' found in page source")
    else:
        step_aware_loggerInfo("⚠ 'Welcome back' NOT found in page source")
        step_aware_loggerInfo(f"Page source length: {len(page_source)}")
    
    try:
        welcome_element = smart_locator.find_element(
            AutomationTestStoreLoginLocators.WELCOME_MESSAGE,
            "Welcome Message"
        )
        
        time.sleep(1)
        
        welcome_text = welcome_element.text
        step_aware_loggerInfo(f"✓ Found welcome message: '{welcome_text}'")
        
        # Verify username is in welcome message
        if username_from_env in welcome_text:
            step_aware_loggerInfo(f"✓ Username '{username_from_env}' found in welcome message")
            step_aware_loggerAttach(
                f"✓ Login Successful!\n✓ Welcome message: '{welcome_text}'",
                name="login_success_verification",
                attachment_type=allure.attachment_type.TEXT
            )
            return welcome_text
        else:
            step_aware_loggerInfo(f"⚠ Username '{username_from_env}' not found in welcome message: '{welcome_text}'")
            step_aware_loggerAttach(
                f"⚠ Warning: Username not found in message: '{welcome_text}'",
                name="login_success_warning",
                attachment_type=allure.attachment_type.TEXT
            )
            return welcome_text
            
    except Exception as e:
        step_aware_loggerInfo(f"✗ Failed to find welcome message: {str(e)}")
        
        # Save page source for debugging
        import os
        debug_dir = "/home/evyatar/Desktop/Projects/HomeworkAutomationExercise/automation-project1/automation/reports/debug"
        os.makedirs(debug_dir, exist_ok=True)
        debug_file = os.path.join(debug_dir, f"page_source_{int(time.time())}.html")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(page_source)
        step_aware_loggerInfo(f"✓ Page source saved to {debug_file}")
        
        step_aware_loggerAttach(
            f"✗ Login verification failed: {str(e)}\n\nPage source saved for debugging",
            name="login_verification_error",
            attachment_type=allure.attachment_type.TEXT
        )
        raise


# ============================================================================
# SEARCH AND PRICE FILTER FUNCTIONS
# ============================================================================

def search_items_by_query(driver, query: str) -> bool:
    """
    Search for items on Automation Test Store using the search input.
    
    Args:
        driver: Selenium WebDriver instance
        query: Search query string
    
    Returns:
        True if search was performed successfully
    """
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators
    
    step_aware_loggerInfo(f"ACTION: Searching for items with query: '{query}'")
    
    smart_locator = SmartLocatorFinder(driver)
    
    # Find and fill the search input
    search_input = smart_locator.find_element(
        AutomationTestStoreSearchLocators.SEARCH_INPUT,
        description="Search input field"
    )
    
    search_input.clear()
    search_input.send_keys(query)
    
    time.sleep(1)
    
    # Submit search
    try:
        search_button = smart_locator.find_element(
            AutomationTestStoreSearchLocators.SEARCH_BUTTON,
            description="Search button"
        )
        search_button.click()
    except Exception as e:
        step_aware_loggerInfo(f"Could not find search button, trying Enter key: {e}")
        search_input.send_keys("\n")
    
    time.sleep(2)  # Wait for search results to load
    
    step_aware_loggerInfo(f"✓ Search performed with query: '{query}'")
    
    return True


def apply_price_filter(driver, min_price: float = None, max_price: float = None) -> bool:
    """
    Apply price filter on the search page.
    
    Args:
        driver: Selenium WebDriver instance
        min_price: Minimum price (optional)
        max_price: Maximum price (optional)
    
    Returns:
        True if filter was applied successfully
    """
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators
    
    step_aware_loggerInfo(f"ACTION: Applying price filter (min: {min_price}, max: {max_price})")
    
    smart_locator = SmartLocatorFinder(driver)
    
    # Apply minimum price if provided
    if min_price is not None:
        try:
            min_input = smart_locator.find_element(
                AutomationTestStoreSearchLocators.PRICE_MIN_INPUT,
                description="Minimum price input"
            )
            min_input.clear()
            min_input.send_keys(str(int(min_price)))
            step_aware_loggerInfo(f"✓ Set minimum price to {min_price}")
        except Exception as e:
            step_aware_loggerInfo(f"Could not set minimum price: {e}")
    
    # Apply maximum price if provided
    if max_price is not None:
        try:
            max_input = smart_locator.find_element(
                AutomationTestStoreSearchLocators.PRICE_MAX_INPUT,
                description="Maximum price input"
            )
            max_input.clear()
            max_input.send_keys(str(int(max_price)))
            step_aware_loggerInfo(f"✓ Set maximum price to {max_price}")
        except Exception as e:
            step_aware_loggerInfo(f"Could not set maximum price: {e}")
    
    # Try to apply filter
    try:
        apply_button = smart_locator.find_element(
            AutomationTestStoreSearchLocators.FILTER_APPLY_BUTTON,
            description="Filter apply button"
        )
        apply_button.click()
        time.sleep(2)
        step_aware_loggerInfo("✓ Filter applied successfully")
    except Exception as e:
        step_aware_loggerInfo(f"No apply button found, filter may be auto-applied: {e}")
    
    step_aware_loggerAttach(
        f"Price Filter Applied\nMin: {min_price}\nMax: {max_price}",
        name="price_filter",
        attachment_type=allure.attachment_type.TEXT
    )
    
    return True


def extract_product_links_with_prices(driver, limit: int = 5, in_stock_only: bool = True) -> list:
    """
    Extract product links and their prices from the current search results page.
    Optionally filters by stock status (presence of 'Add to Cart' button/icon).
    
    Args:
        driver: Selenium WebDriver instance
        limit: Maximum number of products to extract
        in_stock_only: If True, only return products that are in stock (default: True)
    
    Returns:
        List of tuples: [(product_url, product_price), ...]
    """
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators
    
    
    step_aware_loggerInfo(f"ACTION: Extracting product links (limit: {limit}, in_stock_only: {in_stock_only})")
    
    products = []
    
    try:
        # Find all product items on current page
        product_items = driver.find_elements(
            By.XPATH,
            AutomationTestStoreSearchLocators.PRODUCT_ITEMS_CONTAINER[0][1]
        )
        
        step_aware_loggerInfo(f"Found {len(product_items)} product items on current page")
        
        for item in product_items[:limit]:
            try:
                # Extract product link
                product_link_element = item.find_element(
                    By.XPATH,
                    AutomationTestStoreSearchLocators.PRODUCT_LINK[0][1]
                )
                product_url = product_link_element.get_attribute("href")
                
                # Validate URL
                if not product_url or "product_id=" not in product_url:
                    step_aware_loggerInfo(f"Invalid product URL: {product_url}")
                    continue
                
                # Check if product is in stock (if required)
                if in_stock_only:
                    try:
                        # Look for the 'Add to Cart' button/icon within the pricetag div
                        # The presence of fa-cart-plus icon indicates the item is in stock
                        pricetag_div = item.find_element(
                            By.XPATH,
                            ".//div[contains(@class, 'pricetag')]"
                        )
                        cart_icon = pricetag_div.find_element(
                            By.XPATH,
                            ".//i[contains(@class, 'fa-cart-plus')]"
                        )
                        # If we found the cart icon, item is in stock
                        is_in_stock = True
                        step_aware_loggerInfo(f"✓ Product is in stock (cart icon found): {product_url}")
                    except Exception as e:
                        # Cart icon not found - item is out of stock
                        is_in_stock = False
                        step_aware_loggerInfo(f"✗ Product is OUT OF STOCK (no cart icon): {product_url}")
                    
                    # Skip this product if not in stock
                    if not is_in_stock:
                        continue
                
                # Extract product price
                price = None
                try:
                    price_element = item.find_element(
                        By.XPATH,
                        AutomationTestStoreSearchLocators.PRODUCT_PRICE[0][1]
                    )
                    price_text = price_element.text.strip()
                    step_aware_loggerInfo(f"Price text found: {price_text}")
                    # Parse price (remove currency symbols and whitespace)
                    price_str = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                    if price_str:
                        price = float(price_str)
                except Exception as e:
                    step_aware_loggerInfo(f"Could not extract price for {product_url}: {e}")
                    price = None
                
                products.append((product_url, price))
                step_aware_loggerInfo(f"✓ Extracted: {product_url} - Price: {price}")
                
            except Exception as e:
                step_aware_loggerInfo(f"Could not extract product info: {e}")
                continue
        
        step_aware_loggerInfo(f"✓ Extracted {len(products)} products from current page (in_stock_only: {in_stock_only})")
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Error extracting product links: {e}")
        step_aware_loggerAttach(
            f"Error extracting products: {str(e)}",
            name="extraction_error",
            attachment_type=allure.attachment_type.TEXT
        )
    
    return products


def has_next_page(driver) -> bool:
    """
    Check if there's a next page in pagination.
    Scrolls to bottom to find pagination controls.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if next page exists and is clickable, False otherwise
    """
    from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators
    
    
    
    
    step_aware_loggerInfo("ASSERT: Checking if next page exists")
    
    try:
        # Scroll to bottom to find pagination
        step_aware_loggerInfo("Scrolling to bottom to find pagination controls")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        wait = WebDriverWait(driver, 5)
        next_button = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                AutomationTestStoreSearchLocators.NEXT_PAGE_BUTTON[0][1]
            ))
        )
        
        # Check if button is enabled (not disabled)
        is_enabled = "disabled" not in next_button.get_attribute("class").lower()
        
        step_aware_loggerInfo(f"Next page exists: {is_enabled}")
        return is_enabled
        
    except Exception as e:
        step_aware_loggerInfo(f"Next page button not found or not available: {e}")
        return False


def click_next_page(driver) -> bool:
    """
    Click the next page button in pagination.
    Scrolls to bottom to find and click the pagination button.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if next page was clicked successfully
    """
    from automation.utils.smart_locator_finder import SmartLocatorFinder
    from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators
    
    step_aware_loggerInfo("ACTION: Clicking next page button")
    
    smart_locator = SmartLocatorFinder(driver)
    
    try:
        # Scroll to bottom to ensure pagination is visible
        step_aware_loggerInfo("Scrolling to bottom to find next page button")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        next_button = smart_locator.find_element(
            AutomationTestStoreSearchLocators.NEXT_PAGE_BUTTON,
            description="Next page button"
        )
        
        next_button.click()
        time.sleep(2)  # Wait for next page to load
        
        step_aware_loggerInfo("✓ Next page clicked successfully")
        return True
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Could not click next page: {e}")
        return False


def search_items_by_name_under_price(driver, query: str, max_price: float, limit: int = 5, in_stock_only: bool = True) -> list:
    """
    Search for items by name and filter by maximum price with pagination support.
    
    This function handles the extraction of products across multiple pages,
    filtering by price, and collecting results until the limit is reached or
    no more pages are available.
    
    Args:
        driver: Selenium WebDriver instance
        max_price: Maximum price filter (filters results in code)
        limit: Maximum number of products to collect (default: 5)
        in_stock_only: If True, only return products that are in stock (default: True)
    
    Returns:
        list: List of product URLs matching criteria, up to 'limit' items
    """
    step_aware_loggerInfo(f"ACTION: Collecting products under ${max_price}, limit {limit}, in_stock_only: {in_stock_only}")
    
    # Check if there are no search results
    page_source = driver.page_source
    if "There is no product that matches the search criteria" in page_source:
        step_aware_loggerInfo("⚠ No products found matching the search criteria - returning empty list")
        step_aware_loggerAttach(
            "No products found matching the search criteria",
            name="no_search_results",
            attachment_type=allure.attachment_type.TEXT
        )
        return []
    
    product_urls = []
    page_num = 1
    max_pages = 20  # Safety limit
    
    while len(product_urls) < limit and page_num <= max_pages:
        step_aware_loggerInfo(f"Processing page {page_num}...")
        
        # Extract products from current page
        products = extract_product_links_with_prices(
            driver,
            limit=50,  # Get all products from page
            in_stock_only=in_stock_only
        )
        
        step_aware_loggerInfo(f"Found {len(products)} products on page {page_num}")
        
        # Filter by price and add to results
        for url, price in products:
            if len(product_urls) >= limit:
                break
                
            if price is not None and price <= max_price:
                product_urls.append(url)
                step_aware_loggerInfo(f"✓ Added product #{len(product_urls)} at ${price}")
            else:
                price_display = f"${price}" if price is not None else "N/A"
                step_aware_loggerInfo(f"✗ Product price {price_display} exceeds max ${max_price}, skipping")
        
        # Check if we have enough results
        if len(product_urls) >= limit:
            step_aware_loggerInfo(f"✓ Reached limit of {limit} items")
            break
        
        # Check if next page exists
        if has_next_page(driver):
            step_aware_loggerInfo(f"Need more products ({len(product_urls)}/{limit}), moving to page {page_num + 1}...")
            if click_next_page(driver):
                page_num += 1
            else:
                step_aware_loggerInfo("Failed to click next page, stopping")
                break
        else:
            step_aware_loggerInfo(f"No more pages available, found {len(product_urls)}/{limit} items")
            break
    
    step_aware_loggerInfo(f"✓ Collection completed: {len(product_urls)} products found")
    
    return product_urls


def search_items_by_name_under_price(driver, query: str, max_price: float, limit: int = 5, in_stock_only: bool = True) -> list:
    """
    Search for items by name and filter by maximum price and stock status.
    Returns up to 'limit' product URLs where price <= max_price and item is in stock.
    
    Handles pagination: if fewer than 'limit' items are found on current page,
    continues to next page if available until reaching the limit or running out of pages.
    
    Args:
        driver: Selenium WebDriver instance
        query: Search query string
        max_price: Maximum price filter (filters results in code, not via UI)
        limit: Number of items to return (default: 5)
        in_stock_only: If True, only return products that are in stock (default: True)
    
    Returns:
        List of product URLs (strings) with price <= max_price and in stock, up to 'limit' items
        Returns fewer items if not enough found, returns empty list if none found
    """
    step_aware_loggerInfo(f"ACTION: Search items by name '{query}' under price ${max_price}, in_stock_only: {in_stock_only}, limit {limit}")
    
    # Perform search without price filter UI
    search_items_by_query(driver, query)
    
    time.sleep(2)
    
    result_urls = []
    page_num = 1
    max_pages = 20  # Safety limit to avoid infinite loops
    
    while len(result_urls) < limit and page_num <= max_pages:
        step_aware_loggerInfo(f"Processing page {page_num}...")
        
        # Extract products from current page with stock filter
        # Request more than needed from page to account for price filtering
        products = extract_product_links_with_prices(
            driver, 
            limit=50,  # Get all products from page
            in_stock_only=in_stock_only
        )
        
        step_aware_loggerInfo(f"Found {len(products)} products on page {page_num}")
        
        # Filter by price and add to results
        for url, price in products:
            if len(result_urls) >= limit:
                break
                
            if price is not None and price <= max_price:
                result_urls.append(url)
                step_aware_loggerInfo(f"✓ Added product #{len(result_urls)} with price ${price}: {url}")
            else:
                price_display = f"${price}" if price is not None else "N/A"
                step_aware_loggerInfo(f"✗ Product price {price_display} exceeds max ${max_price}, skipping")
        
        # Check if we have enough results
        if len(result_urls) >= limit:
            step_aware_loggerInfo(f"✓ Reached limit of {limit} items")
            break
        
        # Check if next page exists
        if has_next_page(driver):
            step_aware_loggerInfo(f"Need more products ({len(result_urls)}/{limit}), moving to page {page_num + 1}...")
            if click_next_page(driver):
                page_num += 1
            else:
                step_aware_loggerInfo("Failed to click next page, stopping")
                break
        else:
            step_aware_loggerInfo(f"No more pages available, found {len(result_urls)}/{limit} items in total")
            break
    
    # Attach results to Allure
    results_report = f"""
SEARCH RESULTS SUMMARY
══════════════════════════════════════════════════════
Query: {query}
Max Price: ${max_price}
In Stock Only: {in_stock_only}
Limit Requested: {limit}
Results Found: {len(result_urls)}
Pages Scanned: {page_num}

PRODUCT URLS:
"""
    
    for i, url in enumerate(result_urls, 1):
        results_report += f"\n{i}. {url}"
    
    if len(result_urls) == 0:
        results_report += "\n(No products found matching criteria)"
    
    step_aware_loggerAttach(
        results_report,
        name="search_results_summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    step_aware_loggerInfo(f"✓ Search completed: {len(result_urls)} products found for '{query}' under ${max_price}")
    
    return result_urls


# ============================================================================
# LOGIN FUNCTION
# ============================================================================

@allure.step("Perform Automation Test Store login")
def perform_automation_test_store_login(driver) -> bool:
    """
    Perform complete login flow for Automation Test Store.
    
    Requires environment variables:
    - ATS_TEST_USER_NAME: Username/Email for login
    - ATS_TEST_PASSWORD: Password for login
    
    Steps:
    1. Navigate to homepage
    2. Click "Login or register" link
    3. Verify login page loaded
    4. Enter username from environment variable
    5. Enter password from environment variable
    6. Click Login button
    7. Verify login success
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if login was successful
    
    Raises:
        ValueError: If environment variables are not set
        AssertionError: If login fails
    """
    from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
    
    
    import os
    
    logger.info("ACTION: Performing Automation Test Store login")
    
    # Navigate to homepage
    logger.info("ACTION: Navigating to Automation Test Store")
    driver.get("https://automationteststore.com/")
    time.sleep(3)
    
    smart_locator = SmartLocatorFinder(driver)
    
    # Click "Login or register" link
    logger.info("ACTION: Clicking 'Login or register' link")
    try:
        smart_locator.click_element(
            AutomationTestStoreLoginLocators.LOGIN_OR_REGISTER_LINK,
            description="Login or register link"
        )
        time.sleep(2)
    except Exception as e:
        logger.error(f"✗ Failed to click login link: {e}")
        raise
    
    # Enter username from environment variable
    logger.info("ACTION: Entering username from ATS_TEST_USER_NAME environment variable")
    username = os.getenv("ATS_TEST_USER_NAME")
    if not username:
        raise ValueError("Environment variable 'ATS_TEST_USER_NAME' not set")
    
    try:
        smart_locator.type_text(
            AutomationTestStoreCartLocators.USERNAME_INPUT,
            username,
            description="Username input field"
        )
        time.sleep(0.5)
        logger.info(f"✓ Entered username: {username}")
    except Exception as e:
        logger.error(f"✗ Failed to enter username: {e}")
        raise
    
    # Enter password from environment variable
    logger.info("ACTION: Entering password from ATS_TEST_PASSWORD environment variable")
    password = os.getenv("ATS_TEST_PASSWORD")
    if not password:
        raise ValueError("Environment variable 'ATS_TEST_PASSWORD' not set")
    
    try:
        smart_locator.type_text(
            AutomationTestStoreCartLocators.PASSWORD_INPUT,
            password,
            description="Password input field"
        )
        time.sleep(0.5)
        logger.info(f"✓ Entered password (masked)")
    except Exception as e:
        logger.error(f"✗ Failed to enter password: {e}")
        raise
    
    # Click Login button
    logger.info("ACTION: Clicking Login button")
    try:
        smart_locator.click_element(
            AutomationTestStoreCartLocators.LOGIN_SUBMIT_BUTTON,
            description="Login submit button"
        )
        time.sleep(2)
        logger.info("✓ Clicked Login button")
    except Exception as e:
        logger.error(f"✗ Failed to click login button: {e}")
        raise
    
    # Verify login success
    logger.info("ACTION: Verifying login success")
    try:
        # Wait for welcome message to appear using SmartLocatorFinder
        welcome = smart_locator.find_element(
            AutomationTestStoreCartLocators.WELCOME_MESSAGE,
            description="Welcome message"
        )
        logger.info("✓ Login successful - welcome message found")
        
        allure.attach(
            "✓ Login Successful!\n✓ Welcome message found",
            name="login_success",
            attachment_type=allure.attachment_type.TEXT
        )
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Login verification failed: {e}")
        raise


# ============================================================================
# CART MANAGEMENT STEPS
# ============================================================================


def navigate_to_product_page(driver, product_url: str, take_screenshot_func=None) -> bool:
    """
    Navigate to a specific product page.
    
    Args:
        driver: Selenium WebDriver instance
        product_url: Full URL of the product page
        take_screenshot_func: Optional screenshot function
    
    Returns:
        True if navigation successful
    """
    step_aware_loggerInfo(f"Navigating to product page: {product_url}")
    
    try:
        driver.get(product_url)
        time.sleep(2)
        
        step_aware_loggerInfo(f"✓ Successfully navigated to product page")
        return True
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Failed to navigate to product page: {e}")
        raise


def select_product_variants(driver, take_screenshot_func=None) -> dict:
    """
    Select random variants (size, color, quantity) if available on product page.
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Optional screenshot function
    
    Returns:
        Dictionary with selected variants, or empty dict if none available
    """
    from selenium.webdriver.support.ui import Select
    
    step_aware_loggerInfo("Looking for product variants to select")
    
    selected_variants = {}
    
    try:
        # Find all select elements using SmartLocator
        select_elements = driver.find_elements(*AutomationTestStoreCartLocators.SELECT_ELEMENTS[0])
        step_aware_loggerInfo(f"Found {len(select_elements)} select elements")
        
        for idx, select_elem in enumerate(select_elements):
            try:
                # Get select label/name
                select_name = select_elem.get_attribute("name") or f"option_{idx}"
                
                # Get all available options (excluding disabled)
                select = Select(select_elem)
                options = [opt for opt in select.options if opt.get_attribute("disabled") is None and opt.text.strip()]
                
                if len(options) > 1:  # Skip if only one option (usually placeholder)
                    # Select random option
                    import random
                    random_option = random.choice(options[1:] if options[0].text.strip().lower() in ['select', 'choose', '---'] else options)
                    select.select_by_value(random_option.get_attribute("value"))
                    
                    selected_variants[select_name] = random_option.text.strip()
                    step_aware_loggerInfo(f"✓ Selected '{selected_variants[select_name]}' for {select_name}")
                    
                    # Small delay between selections
                    time.sleep(0.3)
                    
            except Exception as e:
                step_aware_loggerInfo(f"✗ Error selecting from {select_name}: {str(e)[:50]}")
                continue
        
        # Find quantity input if available using SmartLocator
        try:
            quantity_inputs = driver.find_elements(*AutomationTestStoreCartLocators.QUANTITY_INPUT[0])
            if quantity_inputs:
                qty_input = quantity_inputs[0]
                # Select random quantity between 1 and 3
                import random
                random_qty = random.randint(1, 3)
                qty_input.clear()
                qty_input.send_keys(str(random_qty))
                selected_variants["quantity"] = str(random_qty)
                step_aware_loggerInfo(f"✓ Set quantity to {random_qty}")
        except Exception as e:
            pass
        
        # Find radio buttons for size/color if no select elements using SmartLocator
        if not select_elements:
            try:
                radio_buttons = driver.find_elements(*AutomationTestStoreCartLocators.RADIO_BUTTONS[0])
                if radio_buttons:
                    # Get unique names (groups)
                    radio_groups = {}
                    for radio in radio_buttons:
                        group_name = radio.get_attribute("name")
                        if group_name not in radio_groups:
                            radio_groups[group_name] = []
                        radio_groups[group_name].append(radio)
                    
                    # Select one from each group
                    import random
                    for group_name, radios in radio_groups.items():
                        available_radios = [r for r in radios if r.get_attribute("disabled") is None]
                        if available_radios:
                            selected_radio = random.choice(available_radios)
                            selected_radio.click()
                            
                            # Get the value or label
                            value = selected_radio.get_attribute("value") or selected_radio.text
                            selected_variants[group_name] = value
                            step_aware_loggerInfo(f"✓ Selected radio button '{value}' for {group_name}")
                            time.sleep(0.3)
            except Exception as e:
                pass
        
    except Exception as e:
        step_aware_loggerInfo(f"Error finding variants: {str(e)}")
    
    if not selected_variants:
        step_aware_loggerInfo("No variants found (simple product)")
    
    return selected_variants


def click_add_to_cart_button(driver, take_screenshot_func=None) -> bool:
    """
    Find and click the 'Add to Cart' button on product page.
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Optional screenshot function
    
    Returns:
        True if button clicked successfully
        
    Raises:
        Exception if button not found
    """
    step_aware_loggerInfo("Looking for 'Add to Cart' button")
    
    # Use SmartLocatorFinder with the ADD_TO_CART_BUTTON locators
    smart_locator = SmartLocatorFinder(driver)
    
    try:
        smart_locator.click_element(
            AutomationTestStoreCartLocators.ADD_TO_CART_BUTTON,
            description="Add to Cart button"
        )
        time.sleep(2)
        
        step_aware_loggerInfo("✓ Successfully clicked 'Add to Cart' button")
        return True
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Could not find 'Add to Cart' button: {e}")
        raise Exception("Could not find 'Add to Cart' button")


def navigate_back_to_previous_page(driver) -> bool:
    """
    Navigate back to previous page using browser history.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if navigation successful
    """
    step_aware_loggerInfo("Navigating back to previous page")
    
    try:
        driver.execute_script("window.history.back();")
        time.sleep(2)
        
        step_aware_loggerInfo("✓ Successfully navigated back")
        return True
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Failed to navigate back: {e}")
        raise


def navigate_to_cart_page(driver) -> bool:
    """
    Navigate to the shopping cart page.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if navigation successful
    """
    step_aware_loggerInfo("Navigating to cart page")
    
    try:
        cart_url = "https://automationteststore.com/index.php?rt=checkout/cart"
        driver.get(cart_url)
        time.sleep(2)
        
        if "cart" in driver.current_url.lower():
            step_aware_loggerInfo("✓ Successfully navigated to cart page")
            return True
        else:
            step_aware_loggerInfo("⚠ Navigated but URL doesn't contain 'cart'")
            return False
            
    except Exception as e:
        step_aware_loggerInfo(f"✗ Failed to navigate to cart page: {e}")
        raise


def get_cart_total(driver) -> float:
    """
    Extract the total amount from the shopping cart page.
    
    Parses the cart page to find the total amount (including shipping).
    The function looks for the "Total:" row in the cart summary table.
    
    Args:
        driver: Selenium WebDriver instance (must be on cart page)
    
    Returns:
        float: Total cart amount in USD
        
    Raises:
        Exception: If total amount cannot be found or parsed
    """
    step_aware_loggerInfo("Extracting cart total from page")
    
    try:
        # Use SmartLocatorFinder to find cart total
        smart_locator = SmartLocatorFinder(driver)
        
        element = smart_locator.find_element(
            AutomationTestStoreCartLocators.CART_TOTAL,
            description="Cart total"
        )
        
        # Scroll to the element to ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        cart_total_text = element.text.strip()
        
        if not cart_total_text:
            raise Exception("Cart total element found but text is empty")
        
        step_aware_loggerInfo(f"Found cart total text: {cart_total_text}")
        
        # Extract numeric value from total text (e.g., "$227.84" -> 227.84)
        total_str = ''.join(filter(lambda x: x.isdigit() or x == '.', cart_total_text))
        
        if not total_str:
            raise Exception(f"Could not parse numeric value from: {cart_total_text}")
        
        actual_total = float(total_str)
        step_aware_loggerInfo(f"✓ Parsed cart total: ${actual_total:.2f}")
        
        return actual_total
        
    except Exception as e:
        step_aware_loggerInfo(f"✗ Failed to extract cart total: {e}")
        raise