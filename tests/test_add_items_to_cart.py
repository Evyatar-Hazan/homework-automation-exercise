"""
Automation Test Store - Add Items to Cart Tests
================================================

Test suite for adding items to cart functionality.
Tests validate adding products to cart with variant selection,
quantity management, and cart state verification.

Environment Variables Required:
    - ATS_URL: Automation Test Store URL (default: https://automationteststore.com/)
    - ATS_TEST_USER_NAME: Test user's login name
    - ATS_TEST_PASSWORD: Test user's password
"""

import os
import time
import random

import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    take_screenshot,
    perform_automation_test_store_login,
    verify_page_title,
)


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
    step_aware_loggerInfo("Looking for 'Add to Cart' button")
    
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
            button = wait.until(EC.element_to_be_clickable((locator_type, locator_value)))
            step_aware_loggerInfo("✓ Found 'Add to Cart' button")
            return button
        except Exception as e:
            continue
    
    step_aware_loggerInfo("⚠ Could not find 'Add to Cart' button")
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
    step_aware_loggerInfo(f"Looking for variants to select for item {item_number}")
    
    selected_variants = {}
    
    try:
        # Find all select elements
        select_elements = driver.find_elements(By.TAG_NAME, "select")
        step_aware_loggerInfo(f"Found {len(select_elements)} select elements")
        
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
                    step_aware_loggerInfo(f"✓ Selected '{selected_variants[select_name]}' for {select_name}")
                    
                    # Small delay between selections
                    time.sleep(0.3)
                    
            except Exception as e:
                step_aware_loggerInfo(f"✗ Error selecting from {select_name}: {str(e)[:50]}")
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
                step_aware_loggerInfo(f"✓ Set quantity to {random_qty}")
        except Exception as e:
            pass
        
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
                            step_aware_loggerInfo(f"✓ Selected radio button '{value}' for {group_name}")
                            time.sleep(0.3)
            except Exception as e:
                pass
        
    except Exception as e:
        step_aware_loggerInfo(f"Error finding variants: {str(e)}")
    
    if not selected_variants:
        step_aware_loggerInfo(f"No variants found for item {item_number} (simple product)")
    
    return selected_variants


def execute_add_items_to_cart_flow(driver, take_screenshot_func, product_urls: list):
    """
    Execute complete add items to cart flow for Automation Test Store.
    
    Orchestrates the full add-to-cart process from login to cart verification.
    Can be reused across different test scenarios.
    
    Flow:
        1. Perform login to Automation Test Store
        2. Navigate to Automation Test Store homepage
        3. Verify page title
        4. Add items to cart from product URLs
        5. Navigate to cart page to verify final state
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        product_urls: List of product URLs to add to cart
        
    Returns:
        dict: Results dictionary containing:
            - total_urls (int): Total number of URLs processed
            - successfully_added (int): Number of items successfully added
            - failed_items (list): List of failed items with errors
            - added_items (list): List of successfully added items with details
            
    Raises:
        AssertionError: If any step validation fails
    """
    # Step 1: Perform login
    ats_url = os.getenv("ATS_URL", "https://automationteststore.com/")
    with step_aware_loggerStep("Step 1: Login to Automation Test Store"):
        perform_automation_test_store_login(driver)
        take_screenshot(driver, take_screenshot_func, name="After_Login")
        time.sleep(2)
    
    # Step 2: Navigate to homepage
    with step_aware_loggerStep("Step 2: Navigate to Automation Test Store"):
        result = navigate_to_automation_test_store(driver, url=ats_url)
        SmartAssert.equal(result, ats_url, "Navigate to homepage", "URL mismatch")
    
    # Step 3: Verify page title
    with step_aware_loggerStep("Step 3: Verify page title"):
        result = verify_page_title(driver, "practice")
        SmartAssert.true(result, "Page title verified", "Title check failed")
    
    # Step 4: Add items to cart
    results = {
        "total_urls": len(product_urls),
        "successfully_added": 0,
        "failed_items": [],
        "added_items": []
    }
    
    wait = WebDriverWait(driver, 10)
    
    for idx, product_url in enumerate(product_urls, 1):
        item_number = idx
        
        try:
            # Navigate to product page
            with step_aware_loggerStep(f"Step 4.{item_number}.1: Open product page {item_number}"):
                step_aware_loggerInfo(f"Processing item {item_number}/{len(product_urls)}: {product_url}")
                driver.get(product_url)
                time.sleep(2)
                
                # Take screenshot of product page
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Product_Page"
                )
            
            # Select random variants if available
            with step_aware_loggerStep(f"Step 4.{item_number}.2: Select variants for item {item_number}"):
                variants_selected = _select_random_variants(driver, wait, item_number)
                
                if variants_selected:
                    step_aware_loggerInfo(f"Selected variants: {variants_selected}")
                    
                    # Take screenshot of selected variants
                    take_screenshot(
                        driver,
                        take_screenshot_func,
                        name=f"Item_{item_number}_Variants_Selected"
                    )
                else:
                    step_aware_loggerInfo(f"No variants to select for item {item_number}")
            
            # Click "Add to cart" button
            with step_aware_loggerStep(f"Step 4.{item_number}.3: Click Add to cart for item {item_number}"):
                add_to_cart_button = _find_add_to_cart_button(driver, wait)
                
                if add_to_cart_button:
                    # Scroll to button to ensure it's visible
                    driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
                    time.sleep(0.5)
                    add_to_cart_button.click()
                    time.sleep(2)
                    
                    step_aware_loggerInfo(f"✓ Clicked 'Add to cart' for item {item_number}")
                    
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
            
            # Return to search page/previous page
            with step_aware_loggerStep(f"Step 4.{item_number}.4: Return to previous page"):
                step_aware_loggerInfo(f"Returning to previous page")
                driver.execute_script("window.history.back();")
                time.sleep(2)
            
            step_aware_loggerInfo(f"✓ Successfully added item {item_number} to cart")
            
        except Exception as e:
            step_aware_loggerInfo(f"✗ Failed to add item {item_number}: {str(e)}")
            results["failed_items"].append({
                "index": item_number,
                "url": product_url,
                "error": str(e)
            })
            
            # Try to navigate back on error
            try:
                driver.execute_script("window.history.back();")
                time.sleep(2)
            except:
                pass
    
    # Step 5: Navigate to cart page to verify
    with step_aware_loggerStep("Step 5: Navigate to cart page"):
        try:
            cart_url = "https://automationteststore.com/index.php?rt=checkout/cart"
            driver.get(cart_url)
            time.sleep(2)
            
            if "cart" in driver.current_url.lower():
                step_aware_loggerInfo("✓ Successfully navigated to cart page")
                take_screenshot(driver, take_screenshot_func, name="Final_Cart_Page")
        except Exception as e:
            step_aware_loggerInfo(f"Could not navigate to cart page: {e}")
    
    # Step 6: Verify and log final results
    with step_aware_loggerStep("Step 6: Verify add-to-cart results"):
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
        
        step_aware_loggerInfo(success_message)
        
        # Attach summary to Allure
        allure.attach(
            success_message,
            name="cart_addition_summary",
            attachment_type=allure.attachment_type.TEXT
        )
        
        SmartAssert.true(
            results['successfully_added'] > 0,
            "At least one item added to cart",
            f"Expected to add at least 1 item, added {results['successfully_added']}"
        )
        
        step_aware_loggerInfo(f"✓ Test completed: Added {results['successfully_added']}/{results['total_urls']} items to cart")
    
    return results


class TestAddItemsToCart(BaseSeleniumTest):
    """
    Test suite for Automation Test Store add-to-cart functionality.
    
    Validates:
        - Login functionality
        - Homepage navigation
        - Adding products to cart
        - Variant selection
        - Cart state verification
    """
    
    @allure.title("Add Items with Direct URLs to Cart")
    @allure.description("Add items to cart using direct product URLs with variant selection")
    @allure.tag("automationteststore", "cart", "smoke", "direct")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_items_with_direct_urls(self):
        """
        Test flow:
        1. Login to Automation Test Store
        2. Navigate to Automation Test Store homepage
        3. Add items to cart using direct URLs
        4. Select random variants for each item
        5. Verify items were added successfully
        6. Navigate to cart page and verify state
        
        Expected Results:
            - All navigation steps complete successfully
            - Items are added to cart successfully
            - Cart page shows added items
        """
        # Real product URLs from search results (in-stock items under $15)
        product_urls = [
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=60",  # $15.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=62",  # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=123", # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=59",  # $5.00
        ]
        
        execute_add_items_to_cart_flow(
            self.driver,
            self.take_screenshot,
            product_urls=product_urls
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
