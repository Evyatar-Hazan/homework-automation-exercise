"""
Automation Test Store Steps
============================

צעדים נפרדים וחוזרים להשימוש בהם בבדיקות שונות של Automation Test Store.

כל פונקציה כאן היא "step" שיכולה להיות בשימוש חוזר בכמה בדיקות שונות.
"""

import os
import allure
import time
from selenium.webdriver.common.by import By
from automation.core import get_logger, log_step_with_allure
from automation.core.logger import step_aware_loggerInfo, step_aware_loggerAttach
from automation.utils.smart_locator_finder import SmartLocatorFinder
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators



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
    
    step_aware_loggerAttach(
        f"✓ Entered username: {username}",
        name="username_entry",
        attachment_type=allure.attachment_type.TEXT
    )
    
    step_aware_loggerInfo(f"✓ Successfully entered username: {username}")
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


# ============================================================================
# SEARCH AND PRICE FILTER FUNCTIONS
# ============================================================================

@allure.step("Search for items by query")
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
    
    logger.info(f"ACTION: Searching for items with query: '{query}'")
    
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
        logger.warning(f"Could not find search button, trying Enter key: {e}")
        search_input.send_keys("\n")
    
    time.sleep(2)  # Wait for search results to load
    
    logger.info(f"✓ Search performed with query: '{query}'")
    
    allure.attach(
        f"Search Query: {query}",
        name="search_query",
        attachment_type=allure.attachment_type.TEXT
    )
    
    return True


@allure.step("Apply price filter")
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
    
    logger.info(f"ACTION: Applying price filter (min: {min_price}, max: {max_price})")
    
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
            logger.info(f"✓ Set minimum price to {min_price}")
        except Exception as e:
            logger.warning(f"Could not set minimum price: {e}")
    
    # Apply maximum price if provided
    if max_price is not None:
        try:
            max_input = smart_locator.find_element(
                AutomationTestStoreSearchLocators.PRICE_MAX_INPUT,
                description="Maximum price input"
            )
            max_input.clear()
            max_input.send_keys(str(int(max_price)))
            logger.info(f"✓ Set maximum price to {max_price}")
        except Exception as e:
            logger.warning(f"Could not set maximum price: {e}")
    
    # Try to apply filter
    try:
        apply_button = smart_locator.find_element(
            AutomationTestStoreSearchLocators.FILTER_APPLY_BUTTON,
            description="Filter apply button"
        )
        apply_button.click()
        time.sleep(2)
        logger.info("✓ Filter applied successfully")
    except Exception as e:
        logger.warning(f"No apply button found, filter may be auto-applied: {e}")
    
    allure.attach(
        f"Price Filter Applied\nMin: {min_price}\nMax: {max_price}",
        name="price_filter",
        attachment_type=allure.attachment_type.TEXT
    )
    
    return True


@allure.step("Extract product links with prices")
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
    
    
    logger.info(f"ACTION: Extracting product links (limit: {limit}, in_stock_only: {in_stock_only})")
    
    products = []
    
    try:
        # Find all product items on current page
        product_items = driver.find_elements(
            By.XPATH,
            AutomationTestStoreSearchLocators.PRODUCT_ITEMS_CONTAINER[0][1]
        )
        
        logger.info(f"Found {len(product_items)} product items on current page")
        
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
                    logger.warning(f"Invalid product URL: {product_url}")
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
                        logger.info(f"✓ Product is in stock (cart icon found): {product_url}")
                    except Exception as e:
                        # Cart icon not found - item is out of stock
                        is_in_stock = False
                        logger.info(f"✗ Product is OUT OF STOCK (no cart icon): {product_url}")
                    
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
                    logger.info(f"Price text found: {price_text}")
                    # Parse price (remove currency symbols and whitespace)
                    price_str = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                    if price_str:
                        price = float(price_str)
                except Exception as e:
                    logger.warning(f"Could not extract price for {product_url}: {e}")
                    price = None
                
                products.append((product_url, price))
                logger.info(f"✓ Extracted: {product_url} - Price: {price}")
                
            except Exception as e:
                logger.warning(f"Could not extract product info: {e}")
                continue
        
        logger.info(f"✓ Extracted {len(products)} products from current page (in_stock_only: {in_stock_only})")
        
    except Exception as e:
        logger.error(f"✗ Error extracting product links: {e}")
        allure.attach(
            f"Error extracting products: {str(e)}",
            name="extraction_error",
            attachment_type=allure.attachment_type.TEXT
        )
    
    return products


@allure.step("Check if next page exists")
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
    
    
    
    
    logger.info("ASSERT: Checking if next page exists")
    
    try:
        # Scroll to bottom to find pagination
        logger.info("Scrolling to bottom to find pagination controls")
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
        
        logger.info(f"Next page exists: {is_enabled}")
        return is_enabled
        
    except Exception as e:
        logger.info(f"Next page button not found or not available: {e}")
        return False


@allure.step("Click next page")
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
    
    logger.info("ACTION: Clicking next page button")
    
    smart_locator = SmartLocatorFinder(driver)
    
    try:
        # Scroll to bottom to ensure pagination is visible
        logger.info("Scrolling to bottom to find next page button")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        next_button = smart_locator.find_element(
            AutomationTestStoreSearchLocators.NEXT_PAGE_BUTTON,
            description="Next page button"
        )
        
        next_button.click()
        time.sleep(2)  # Wait for next page to load
        
        logger.info("✓ Next page clicked successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Could not click next page: {e}")
        return False


@allure.step("Search items by name under price")
def search_items_by_name_under_price(driver, query: str, max_price: float, limit: int = 5, in_stock_only: bool = True) -> list:
    """
    Search for items by name and filter by maximum price and stock status.
    Returns up to 'limit' product links where price <= max_price and item is in stock.
    
    Handles pagination: if fewer than 'limit' items are found on current page,
    continues to next page if available.
    
    Args:
        driver: Selenium WebDriver instance
        query: Search query string
        max_price: Maximum price filter
        limit: Number of items to return (default: 5)
        in_stock_only: If True, only return products that are in stock (default: True)
    
    Returns:
        List of product URLs (strings) with price <= max_price and in stock, up to 'limit' items
        Returns fewer items if not enough found, returns empty list if none found
    """
    logger.info(f"ACTION: Search items by name '{query}' under price {max_price}, in_stock_only: {in_stock_only}, limit {limit}")
    
    search_items_by_query(driver, query)
    apply_price_filter(driver, max_price=max_price)
    
    time.sleep(2)
    
    result_urls = []
    page_num = 1
    max_pages = 10  # Safety limit to avoid infinite loops
    
    while len(result_urls) < limit and page_num <= max_pages:
        logger.info(f"Processing page {page_num}...")
        
        # Extract products from current page with stock filter
        products = extract_product_links_with_prices(driver, limit=limit - len(result_urls), in_stock_only=in_stock_only)
        
        # Filter by price and add to results
        for url, price in products:
            if price is not None and price <= max_price:
                result_urls.append(url)
                logger.info(f"✓ Added product with price {price}: {url}")
                
                if len(result_urls) >= limit:
                    break
            else:
                logger.info(f"Product price {price} exceeds max {max_price}, skipping")
        
        # Check if we have enough results
        if len(result_urls) >= limit:
            logger.info(f"✓ Reached limit of {limit} items")
            break
        
        # Check if next page exists
        if has_next_page(driver):
            logger.info(f"More pages available, moving to page {page_num + 1}...")
            click_next_page(driver)
            page_num += 1
        else:
            logger.info(f"No more pages available, found {len(result_urls)} items in total")
            break
    
    # Attach results to Allure
    results_report = f"""
    SEARCH RESULTS SUMMARY
    ══════════════════════════════════════════════════════
    Query: {query}
    Max Price: {max_price}
    In Stock Only: {in_stock_only}
    Limit Requested: {limit}
    Results Found: {len(result_urls)}
    Pages Scanned: {page_num}
    
    PRODUCT LINKS:
    """
    
    for i, url in enumerate(result_urls, 1):
        results_report += f"\n{i}. {url}"
    
    allure.attach(
        results_report,
        name="search_results_summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(f"✓ Search completed. Returning {len(result_urls)} product URLs")
    
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
    
    wait = WebDriverWait(driver, 10)
    
    # Click "Login or register" link
    logger.info("ACTION: Clicking 'Login or register' link")
    try:
        login_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, AutomationTestStoreLoginLocators.LOGIN_OR_REGISTER_LINK[0][1]))
        )
        login_link.click()
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
        email_input = wait.until(
            EC.presence_of_element_located((By.ID, "loginFrm_loginname"))
        )
        email_input.clear()
        time.sleep(0.3)
        
        # Type with human-like speed
        for char in username:
            email_input.send_keys(char)
            time.sleep(0.05)
        
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
        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "loginFrm_password"))
        )
        password_input.clear()
        time.sleep(0.3)
        
        # Type with human-like speed
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(0.5)
        logger.info(f"✓ Entered password (masked)")
    except Exception as e:
        logger.error(f"✗ Failed to enter password: {e}")
        raise
    
    # Click Login button
    logger.info("ACTION: Clicking Login button")
    try:
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @title='Login']"))
        )
        login_button.click()
        time.sleep(2)
        logger.info("✓ Clicked Login button")
    except Exception as e:
        logger.error(f"✗ Failed to click login button: {e}")
        raise
    
    # Verify login success
    logger.info("ACTION: Verifying login success")
    try:
        # Wait for welcome message to appear
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Welcome back')]"))
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