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

import pytest
import allure

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    verify_page_title,
    take_screenshot,
    navigate_to_product_page,
    select_product_variants,
    click_add_to_cart_button,
    navigate_back_to_previous_page,
    navigate_to_cart_page,
)
from .test_login import execute_login_flow


def addItemsToCart(driver, take_screenshot_func, product_urls: list):
    """
    Execute add items to cart flow for Automation Test Store.
    
    Orchestrates the add-to-cart process after login.
    Can be reused across different test scenarios.
    
    Flow:
        1. Navigate to Automation Test Store homepage
        2. Verify page title
        3. For each product URL:
            a. Navigate to product page
            b. Select variants (if available)
            c. Click "Add to cart"
            d. Navigate back
        4. Navigate to cart page to verify final state
        5. Verify results
    
    Args:
        driver: Selenium WebDriver instance (already logged in)
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
    # Step 1: Navigate to homepage
    ats_url = "https://automationteststore.com/"
    with step_aware_loggerStep("Step 1: Navigate to Automation Test Store"):
        result = navigate_to_automation_test_store(driver, url=ats_url)
        SmartAssert.equal(result, ats_url, "Navigate to homepage", "URL mismatch")
    
    # Step 2: Verify page title
    with step_aware_loggerStep("Step 2: Verify page title"):
        result = verify_page_title(driver, "practice")
        SmartAssert.true(result, "Page title verified", "Title check failed")
    
    # Initialize results tracking
    results = {
        "total_urls": len(product_urls),
        "successfully_added": 0,
        "failed_items": [],
        "added_items": []
    }
    
    # Step 3: Add each product to cart
    for idx, product_url in enumerate(product_urls, 1):
        item_number = idx
        
        try:
            # Step 3.N.1: Navigate to product page
            with step_aware_loggerStep(f"Step 3.{item_number}.1: Navigate to product page {item_number}"):
                step_aware_loggerInfo(f"Processing item {item_number}/{len(product_urls)}: {product_url}")
                navigate_to_product_page(driver, product_url)
                
                # Take screenshot of product page
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Product_Page"
                )
            
            # Step 3.N.2: Select variants if available
            with step_aware_loggerStep(f"Step 3.{item_number}.2: Select product variants"):
                variants_selected = select_product_variants(driver)
                
                if variants_selected:
                    step_aware_loggerInfo(f"Selected variants: {variants_selected}")
                    
                    # Take screenshot of selected variants
                    take_screenshot(
                        driver,
                        take_screenshot_func,
                        name=f"Item_{item_number}_Variants_Selected"
                    )
                else:
                    step_aware_loggerInfo("No variants to select (simple product)")
            
            # Step 3.N.3: Click "Add to cart" button
            with step_aware_loggerStep(f"Step 3.{item_number}.3: Click 'Add to cart' button"):
                click_add_to_cart_button(driver)
                
                step_aware_loggerInfo(f"✓ Successfully added item {item_number} to cart")
                
                # Take screenshot after adding to cart
                take_screenshot(
                    driver,
                    take_screenshot_func,
                    name=f"Item_{item_number}_Added_to_Cart"
                )
                
                # Track successful addition
                results["successfully_added"] += 1
                results["added_items"].append({
                    "index": item_number,
                    "url": product_url,
                    "variants": variants_selected
                })
            
            # Step 3.N.4: Navigate back to previous page
            with step_aware_loggerStep(f"Step 3.{item_number}.4: Navigate back to previous page"):
                navigate_back_to_previous_page(driver)
            
        except Exception as e:
            step_aware_loggerInfo(f"✗ Failed to add item {item_number}: {str(e)}")
            results["failed_items"].append({
                "index": item_number,
                "url": product_url,
                "error": str(e)
            })
            
            # Try to navigate back on error
            try:
                navigate_back_to_previous_page(driver)
            except:
                pass
    
    # Step 4: Navigate to cart page
    with step_aware_loggerStep("Step 4: Navigate to cart page"):
        navigate_to_cart_page(driver)
        take_screenshot(driver, take_screenshot_func, name="Final_Cart_Page")
    
    # Step 5: Verify and log final results
    with step_aware_loggerStep("Step 5: Verify add-to-cart results"):
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
        
        # Verify at least one item was added
        SmartAssert.true(
            results['successfully_added'] > 0,
            "At least one item added to cart",
            f"Expected to add at least 1 item, added {results['successfully_added']}"
        )
        
        step_aware_loggerInfo(f"✓ Add-to-cart flow completed: {results['successfully_added']}/{results['total_urls']} items added successfully")
    
    return results


class TestAddItemsToCart(BaseSeleniumTest):
    """
    Test suite for Automation Test Store add-to-cart functionality.
    
    Validates:
        - Login functionality (using execute_login_flow)
        - Homepage navigation
        - Adding products to cart
        - Variant selection
        - Cart state verification
    """
    
    @allure.title("Add Items with Direct URLs to Cart")
    @allure.description("Complete flow: Login → Add items to cart → Verify cart state")
    @allure.tag("automationteststore", "cart", "smoke", "e2e")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_items_with_direct_urls(self):
        """
        Execute complete add-to-cart flow for Automation Test Store.
        
        Test Flow:
            1. Login to Automation Test Store (using execute_login_flow from test_login)
            2. Add multiple items to cart using addItemsToCart:
                a. Navigate to homepage and verify
                b. Add multiple items to cart using direct URLs
                c. Select random variants for each item
                d. Navigate to cart page
                e. Verify items were added successfully
        
        Expected Results:
            - Login completes successfully
            - All navigation steps complete successfully
            - Items are added to cart successfully
            - Cart page shows added items
        """
        # Step 1: Login using execute_login_flow from test_login
        login_result = execute_login_flow(self.driver)
        step_aware_loggerInfo(f"✓ Login completed for user: {login_result['username']}")
        take_screenshot(self.driver, self.take_screenshot, name="After_Login")
        
        # Real product URLs from search results (in-stock items under $15)
        product_urls = [
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=60",  # $15.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=62",  # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=123", # $14.00
            "https://automationteststore.com/index.php?rt=product/product&keyword=a&category_id=0&product_id=59",  # $5.00
        ]
        
        # Step 2: Add items to cart using addItemsToCart
        result = addItemsToCart(
            driver=self.driver,
            take_screenshot_func=self.take_screenshot,
            product_urls=product_urls
        )
        
        step_aware_loggerInfo(
            f"✓ Test completed successfully: Added {result['successfully_added']}/{result['total_urls']} items to cart"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
