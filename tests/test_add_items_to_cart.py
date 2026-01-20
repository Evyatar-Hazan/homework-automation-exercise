import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime

from automation.core import BaseSeleniumTest, get_logger, TestExecutionTracker, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    take_screenshot,
    log_success_message,
    perform_automation_test_store_login,
)

logger = get_logger(__name__)


@allure.step("Add items to cart")
def add_items_to_cart(driver, take_screenshot_func, urls: list) -> dict:
    """
    Add multiple items to cart from their product URLs.
    
    Behavior:
        - Iterates through each URL
        - Opens the product page
        - Selects random variants (size/color/quantity) if available
        - Clicks "Add to cart" button
        - Returns to search page/tab
        - Saves screenshot log for each item added
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        urls: List of product URLs to add to cart
    
    Returns:
        Dictionary with results summary
    """
    logger.info(f"ACTION: Adding {len(urls)} items to cart")
    
    tracker = TestExecutionTracker("add_items_to_cart")
    
    results = {
        "total_urls": len(urls),
        "successfully_added": 0,
        "failed_items": [],
        "added_items": []
    }
    
    # Store initial URL to return to search page
    initial_url = driver.current_url
    initial_window = driver.current_window_handle
    
    wait = WebDriverWait(driver, 10)
    
    for idx, product_url in enumerate(urls, 1):
        item_number = idx
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing item {item_number}/{len(urls)}: {product_url}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Step 1: Navigate to product page
            logger.info(f"ACTION: Opening product page {item_number}")
            driver.get(product_url)
            time.sleep(2)
            
            # Take screenshot of product page
            take_screenshot(
                driver,
                take_screenshot_func,
                name=f"Item_{item_number}_Product_Page"
            )
            
            tracker.log_step(
                f"Open product page {item_number}",
                f"URL: {product_url}"
            )
            
            # Step 2: Select random variants if available
            variants_selected = _select_random_variants(driver, wait, item_number)
            
            if variants_selected:
                logger.info(f"✓ Selected variants: {variants_selected}")
                tracker.log_step(
                    f"Select variants for item {item_number}",
                    f"Variants selected: {variants_selected}"
                )
                
                # Take screenshot of selected variants
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Variants_Selected"
                )
            else:
                logger.info(f"ℹ No variants to select for item {item_number}")
            
            # Step 3: Click "Add to cart" button
            logger.info(f"ACTION: Clicking 'Add to cart' for item {item_number}")
            add_to_cart_button = _find_add_to_cart_button(driver, wait)
            
            if add_to_cart_button:
                # Scroll to button to ensure it's visible
                driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
                time.sleep(0.5)
                add_to_cart_button.click()
                time.sleep(2)
                
                logger.info(f"✓ Clicked 'Add to cart' for item {item_number}")
                tracker.log_step(
                    f"Click Add to cart for item {item_number}",
                    "Button clicked successfully"
                )
                
                # Take screenshot of success
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Added_to_Cart"
                )
                
                results["successfully_added"] += 1
                results["added_items"].append({
                    "index": item_number,
                    "url": product_url,
                    "variants": variants_selected
                })
                
            else:
                raise Exception("Could not find 'Add to cart' button")
            
            # Step 4: Return to search page/previous page
            logger.info(f"ACTION: Returning to previous page")
            driver.execute_script("window.history.back();")
            time.sleep(2)
            
            tracker.log_step(
                f"Return to previous page after item {item_number}",
                "Navigation successful"
            )
            
            logger.info(f"✓ Successfully added item {item_number} to cart\n")
            
        except Exception as e:
            logger.error(f"✗ Failed to add item {item_number}: {str(e)}")
            results["failed_items"].append({
                "index": item_number,
                "url": product_url,
                "error": str(e)
            })
            tracker.log_step(
                f"Add item {item_number} to cart",
                f"❌ FAILED: {str(e)}"
            )
            
            # Try to navigate back on error
            try:
                driver.execute_script("window.history.back();")
                time.sleep(2)
            except:
                pass
    
    # Step 5: Final report
    success_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CART ADDITION SUMMARY                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Total URLs Processed:     {results['total_urls']}
Successfully Added:       {results['successfully_added']}
Failed:                   {len(results['failed_items'])}

"""
    
    if results["added_items"]:
        success_message += "✅ SUCCESSFULLY ADDED:\n"
        for item in results["added_items"]:
            success_message += f"\n  [{item['index']}] {item['url']}\n"
            if item['variants']:
                success_message += f"      Variants: {item['variants']}\n"
    
    if results["failed_items"]:
        success_message += "\n❌ FAILED ITEMS:\n"
        for item in results["failed_items"]:
            success_message += f"\n  [{item['index']}] {item['url']}\n"
            success_message += f"      Error: {item['error']}\n"
    
    success_message += "\n╚══════════════════════════════════════════════════════════════════════════════╝\n"
    
    logger.info(success_message)
    
    # Log to console
    print(success_message)
    
    # Attach summary to Allure
    allure.attach(
        success_message,
        name="cart_addition_summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    tracker.log_step("Cart Addition Process", success_message)
    tracker.attach_to_allure()
    
    # Log success message
    log_success_message(
        "Add Items to Cart",
        f"✅ Added {results['successfully_added']}/{results['total_urls']} items to cart"
    )
    
    return results


def _find_add_to_cart_button(driver, wait):
    """
    Find and return the 'Add to Cart' button.
    
    HTML structure:
    <a href="#" onclick="$(this).closest('form').submit(); return false;" class="cart">
        <i class="fa fa-cart-plus fa-fw"></i>
        Add to Cart
    </a>
    
    Tries multiple locators:
    1. Link with class="cart"
    2. Link with onclick containing form submit
    3. Element containing "Add to Cart" text with fa-cart-plus icon
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        WebElement of the button, or None if not found
    """
    logger.info("FIND: Looking for 'Add to Cart' button")
    
    locators = [
        # Primary: Link with class="cart"
        (By.CSS_SELECTOR, "a.cart"),
        (By.XPATH, "//a[@class='cart']"),
        # With fa-cart-plus icon
        (By.XPATH, "//a[contains(@class, 'cart')]//i[contains(@class, 'fa-cart-plus')]//parent::a"),
        # By onclick attribute with form submit
        (By.XPATH, "//a[contains(@onclick, 'form')]"),
        # By text content "Add to Cart"
        (By.XPATH, "//a[contains(., 'Add to Cart')]"),
        # Link with fa-cart-plus anywhere
        (By.XPATH, "//*[.//i[contains(@class, 'fa-cart-plus')]]"),
    ]
    
    for locator_type, locator_value in locators:
        try:
            logger.info(f"  Trying locator...")
            button = wait.until(EC.element_to_be_clickable((locator_type, locator_value)))
            logger.info(f"✓ Found 'Add to Cart' button")
            return button
        except Exception as e:
            logger.debug(f"  ✗ Not found with this locator")
            continue
    
    logger.warning("⚠ Could not find 'Add to Cart' button")
    return None


def _select_random_variants(driver, wait, item_number):
    """
    Find and select random variants (size, color, quantity) if available.
    
    Looks for:
    - <select> elements (dropdowns)
    - Radio buttons
    - Checkboxes
    - Quantity input
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        item_number: Current item number (for logging)
    
    Returns:
        Dictionary with selected variants, or empty dict if none available
    """
    logger.info(f"ACTION: Looking for variants to select for item {item_number}")
    
    selected_variants = {}
    
    try:
        # Find all select elements
        select_elements = driver.find_elements(By.TAG_NAME, "select")
        logger.info(f"Found {len(select_elements)} select elements")
        
        for idx, select_elem in enumerate(select_elements):
            try:
                # Get select label/name
                select_name = select_elem.get_attribute("name") or f"option_{idx}"
                select_id = select_elem.get_attribute("id") or select_name
                
                # Get all available options (excluding disabled)
                select = Select(select_elem)
                options = [opt for opt in select.options if opt.get_attribute("disabled") is None and opt.text.strip()]
                
                if len(options) > 1:  # Skip if only one option (usually placeholder)
                    # Select random option
                    random_option = random.choice(options[1:] if options[0].text.strip().lower() in ['select', 'choose', '---'] else options)
                    select.select_by_value(random_option.get_attribute("value"))
                    
                    selected_variants[select_name] = random_option.text.strip()
                    logger.info(f"✓ Selected '{selected_variants[select_name]}' for {select_name}")
                    
                    # Small delay between selections
                    time.sleep(0.3)
                    
            except Exception as e:
                logger.warning(f"✗ Error selecting from {select_name}: {str(e)[:50]}")
                continue
        
        # Find quantity input if available
        try:
            quantity_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='quantity'], input[id*='quantity']")
            if quantity_inputs:
                qty_input = quantity_inputs[0]
                # Select random quantity between 1 and 3
                random_qty = random.randint(1, 3)
                qty_input.clear()
                qty_input.send_keys(str(random_qty))
                selected_variants["quantity"] = str(random_qty)
                logger.info(f"✓ Set quantity to {random_qty}")
        except Exception as e:
            logger.debug(f"No quantity input or error: {str(e)[:50]}")
        
        # Find radio buttons for size/color if no select elements
        if not select_elements:
            try:
                radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radio_buttons:
                    # Get unique names (groups)
                    radio_groups = {}
                    for radio in radio_buttons:
                        group_name = radio.get_attribute("name")
                        if group_name not in radio_groups:
                            radio_groups[group_name] = []
                        radio_groups[group_name].append(radio)
                    
                    # Select one from each group
                    for group_name, radios in radio_groups.items():
                        available_radios = [r for r in radios if r.get_attribute("disabled") is None]
                        if available_radios:
                            selected_radio = random.choice(available_radios)
                            selected_radio.click()
                            
                            # Get the value or label
                            value = selected_radio.get_attribute("value") or selected_radio.text
                            selected_variants[group_name] = value
                            logger.info(f"✓ Selected radio button '{value}' for {group_name}")
                            time.sleep(0.3)
            except Exception as e:
                logger.debug(f"Error with radio buttons: {str(e)[:50]}")
        
    except Exception as e:
        logger.warning(f"Error finding variants: {str(e)}")
    
    if not selected_variants:
        logger.info(f"ℹ No variants found for item {item_number} (simple product)")
    
    return selected_variants


def perform_add_items_to_cart_test(driver, take_screenshot_func, product_urls: list, test_name: str = "Add Items to Cart"):
    """
    Helper function to perform add items to cart test.
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        product_urls: List of product URLs to add to cart
        test_name: Test name for logging
    """
    tracker = TestExecutionTracker(test_name.lower().replace(" ", "_"))
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📦 ADDING TO CART TEST: {test_name}")
    logger.info(f"URLs to process: {len(product_urls)}")
    logger.info(f"{'='*80}")
    
    for i, url in enumerate(product_urls, 1):
        logger.info(f"  {i}. {url}")
    
    logger.info(f"{'='*80}\n")
    
    # Step 0: Login first
    logger.info("\n🔐 STEP 0: Performing login")
    try:
        perform_automation_test_store_login(driver)
        tracker.log_step("Login to Automation Test Store", "Login successful")
        logger.info("✓ Login completed successfully")
        
        # Take screenshot after login
        take_screenshot(driver, take_screenshot_func, name="After_Login_Before_Adding_Items")
        time.sleep(2)
    except Exception as e:
        logger.error(f"✗ Login failed: {e}")
        tracker.log_step("Login to Automation Test Store", f"❌ FAILED: {e}")
        raise
    
    # Navigate to homepage
    result = navigate_to_automation_test_store(driver, url="https://automationteststore.com/")
    tracker.log_step("Navigate to Automation Test Store", f"URL: {result}")
    SmartAssert.equal(result, "https://automationteststore.com/", "Navigate to homepage", "URL mismatch")
    
    # Add items to cart
    results = _add_items_to_cart_sync(driver, take_screenshot_func, product_urls)
    
    tracker.log_step(
        "Add items to cart",
        f"Successfully added: {results['successfully_added']}/{results['total_urls']}"
    )
    
    SmartAssert.true(
        results['successfully_added'] > 0,
        "At least one item added to cart",
        f"Expected to add at least 1 item, added {results['successfully_added']}"
    )
    
    # Take screenshot of final cart state (navigate to cart)
    try:
        # Common cart URLs for Automation Test Store
        cart_urls = [
            "https://automationteststore.com/index.php?rt=checkout/cart",
            "https://automationteststore.com/checkout/cart",
        ]
        
        logger.info("ACTION: Navigating to cart page")
        cart_found = False
        for cart_url in cart_urls:
            try:
                driver.get(cart_url)
                time.sleep(2)
                # Check if we're on cart page
                if "cart" in driver.current_url.lower():
                    cart_found = True
                    logger.info("✓ Successfully navigated to cart page")
                    break
            except:
                continue
        
        if cart_found:
            take_screenshot(driver, take_screenshot_func, name="Final_Cart_Page")
            tracker.log_step("Take screenshot of final cart", "Cart page screenshot saved")
    except Exception as e:
        logger.warning(f"Could not navigate to cart page: {e}")
    
    # Log success
    success_msg = f"✅ Successfully processed {len(product_urls)} products and added {results['successfully_added']} to cart!"
    log_success_message("Add Items to Cart", success_msg)
    tracker.log_step("Final Summary", success_msg)
    
    # Attach all data to Allure
    tracker.attach_to_allure()
    
    return results


def _add_items_to_cart_sync(driver, take_screenshot_func, urls: list) -> dict:
    """
    Synchronous version of add_items_to_cart (without async).
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        urls: List of product URLs to add to cart
    
    Returns:
        Dictionary with results summary
    """
    logger.info(f"ACTION: Adding {len(urls)} items to cart (sync)")
    
    tracker = TestExecutionTracker("add_items_to_cart")
    
    results = {
        "total_urls": len(urls),
        "successfully_added": 0,
        "failed_items": [],
        "added_items": []
    }
    
    wait = WebDriverWait(driver, 10)
    
    for idx, product_url in enumerate(urls, 1):
        item_number = idx
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing item {item_number}/{len(urls)}: {product_url}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Step 1: Navigate to product page
            logger.info(f"ACTION: Opening product page {item_number}")
            driver.get(product_url)
            time.sleep(2)
            
            # Take screenshot of product page
            take_screenshot(
                driver,
                take_screenshot_func,
                name=f"Item_{item_number}_Product_Page"
            )
            
            tracker.log_step(
                f"Open product page {item_number}",
                f"URL: {product_url}"
            )
            
            # Step 2: Select random variants if available
            variants_selected = _select_random_variants(driver, wait, item_number)
            
            if variants_selected:
                logger.info(f"✓ Selected variants: {variants_selected}")
                tracker.log_step(
                    f"Select variants for item {item_number}",
                    f"Variants selected: {variants_selected}"
                )
                
                # Take screenshot of selected variants
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Variants_Selected"
                )
            else:
                logger.info(f"ℹ No variants to select for item {item_number}")
            
            # Step 3: Click "Add to cart" button
            logger.info(f"ACTION: Clicking 'Add to cart' for item {item_number}")
            add_to_cart_button = _find_add_to_cart_button(driver, wait)
            
            if add_to_cart_button:
                # Scroll to button to ensure it's visible
                driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
                time.sleep(0.5)
                add_to_cart_button.click()
                time.sleep(2)
                
                logger.info(f"✓ Clicked 'Add to cart' for item {item_number}")
                tracker.log_step(
                    f"Click Add to cart for item {item_number}",
                    "Button clicked successfully"
                )
                
                # Take screenshot of success
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Added_to_Cart"
                )
                
                results["successfully_added"] += 1
                results["added_items"].append({
                    "index": item_number,
                    "url": product_url,
                    "variants": variants_selected
                })
                
            else:
                raise Exception("Could not find 'Add to cart' button")
            
            # Step 4: Return to search page/previous page
            logger.info(f"ACTION: Returning to previous page")
            driver.execute_script("window.history.back();")
            time.sleep(2)
            
            tracker.log_step(
                f"Return to previous page after item {item_number}",
                "Navigation successful"
            )
            
            logger.info(f"✓ Successfully added item {item_number} to cart\n")
            
        except Exception as e:
            logger.error(f"✗ Failed to add item {item_number}: {str(e)}")
            results["failed_items"].append({
                "index": item_number,
                "url": product_url,
                "error": str(e)
            })
            tracker.log_step(
                f"Add item {item_number} to cart",
                f"❌ FAILED: {str(e)}"
            )
            
            # Try to navigate back on error
            try:
                driver.execute_script("window.history.back();")
                time.sleep(2)
            except:
                pass
    
    # Step 5: Final report
    success_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CART ADDITION SUMMARY                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Total URLs Processed:     {results['total_urls']}
Successfully Added:       {results['successfully_added']}
Failed:                   {len(results['failed_items'])}

"""
    
    if results["added_items"]:
        success_message += "✅ SUCCESSFULLY ADDED:\n"
        for item in results["added_items"]:
            success_message += f"\n  [{item['index']}] {item['url']}\n"
            if item['variants']:
                success_message += f"      Variants: {item['variants']}\n"
    
    if results["failed_items"]:
        success_message += "\n❌ FAILED ITEMS:\n"
        for item in results["failed_items"]:
            success_message += f"\n  [{item['index']}] {item['url']}\n"
            success_message += f"      Error: {item['error']}\n"
    
    success_message += "\n╚══════════════════════════════════════════════════════════════════════════════╝\n"
    
    logger.info(success_message)
    print(success_message)
    
    # Attach summary to Allure
    allure.attach(
        success_message,
        name="cart_addition_summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    tracker.log_step("Cart Addition Process", success_message)
    tracker.attach_to_allure()
    
    return results


class TestAddItemsToCart(BaseSeleniumTest):
    """Test suite for adding items to cart."""
    
    @allure.title("Add Items with Direct URLs to Cart")
    @allure.description("Add items to cart using direct product URLs")
    @allure.tag("automationteststore", "cart", "smoke", "direct")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_items_with_direct_urls(self):
        """
        Test flow:
        1. Navigate to Automation Test Store
        2. Add items to cart using direct URLs
        3. Select random variants for each item
        4. Verify items were added successfully
        """
        # Real product URLs from search results (in-stock items under $15)
        product_urls = [
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=60",  # $15.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=62",  # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=123", # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=59",  # $5.00
        ]
        
        perform_add_items_to_cart_test(
            self.driver,
            self.take_screenshot,
            product_urls=product_urls,
            test_name="Add Items to Cart (Direct URLs - In Stock Under $15)"
        )
    



if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
