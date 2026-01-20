import pytest
import allure
from selenium.webdriver.common.by import By
import time
from datetime import datetime

from automation.core import BaseSeleniumTest, get_logger, TestExecutionTracker, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    take_screenshot,
    log_success_message,
    perform_automation_test_store_login,
)

logger = get_logger(__name__)


@allure.step("Assert cart total does not exceed budget")
async def assert_cart_total_not_exceeds(driver, take_screenshot_func, budget_per_item: float, items_count: int) -> dict:
    """
    Validate that shopping cart total does not exceed the calculated budget threshold.
    
    Behavior:
        1. Navigate to shopping cart page
        2. Extract total amount from the cart page
        3. Calculate budget threshold: budget_per_item * items_count
        4. Assert that cart total <= threshold
        5. Save screenshot/trace of cart page
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        budget_per_item: Maximum budget per item (USD)
        items_count: Number of items in cart
    
    Returns:
        Dictionary with validation results
    """
    logger.info(f"ACTION: Validating cart total (budget_per_item: ${budget_per_item}, items: {items_count})")
    
    tracker = TestExecutionTracker("validate_cart_total")
    
    results = {
        "budget_per_item": budget_per_item,
        "items_count": items_count,
        "calculated_threshold": budget_per_item * items_count,
        "actual_total": None,
        "is_within_budget": False,
        "validation_passed": False
    }
    
    try:
        # Step 1: Navigate to cart page
        logger.info("ACTION: Navigating to shopping cart page")
        
        cart_urls = [
            "https://automationteststore.com/index.php?rt=checkout/cart",
            "https://automationteststore.com/checkout/cart",
        ]
        
        cart_found = False
        for cart_url in cart_urls:
            try:
                driver.get(cart_url)
                time.sleep(2)
                
                if "cart" in driver.current_url.lower():
                    cart_found = True
                    logger.info(f"✓ Successfully navigated to cart page: {driver.current_url}")
                    tracker.log_step("Navigate to cart page", f"URL: {driver.current_url}")
                    break
            except Exception as e:
                logger.debug(f"Could not navigate to {cart_url}: {e}")
                continue
        
        if not cart_found:
            raise Exception("Could not find or navigate to cart page")
        
        time.sleep(2)
        
        # Step 2: Extract cart total from page
        logger.info("ACTION: Extracting cart total from page")
        
        # Try multiple locators to find cart total
        cart_total_locators = [
            # Common total elements
            (By.XPATH, "//span[contains(text(), 'Total:')]/../following-sibling::*//span"),
            (By.XPATH, "//td[contains(text(), 'Total:')]/following-sibling::td//strong"),
            (By.XPATH, "//div[@class='total']//span[contains(@class, 'price')]"),
            (By.XPATH, "//*[contains(text(), 'Total')]/ancestor::tr//td[last()]"),
            (By.CSS_SELECTOR, ".cart-total, .total-amount, .order-total"),
            (By.XPATH, "//table[contains(@class, 'cart')]//tr[last()]//td[last()]"),
        ]
        
        cart_total_text = None
        for locator_type, locator_value in cart_total_locators:
            try:
                logger.info(f"  Trying locator to find cart total...")
                element = driver.find_element(locator_type, locator_value)
                cart_total_text = element.text.strip()
                
                if cart_total_text and ('$' in cart_total_text or any(char.isdigit() for char in cart_total_text)):
                    logger.info(f"✓ Found cart total: {cart_total_text}")
                    break
            except Exception as e:
                logger.debug(f"  ✗ Locator failed: {str(e)[:50]}")
                continue
        
        if not cart_total_text:
            raise Exception("Could not find cart total element on page")
        
        # Extract numeric value from total text
        logger.info(f"ACTION: Parsing cart total from text: '{cart_total_text}'")
        
        # Remove currency symbols and extra text
        total_str = ''.join(filter(lambda x: x.isdigit() or x == '.', cart_total_text))
        
        if not total_str:
            raise Exception(f"Could not parse numeric value from: {cart_total_text}")
        
        actual_total = float(total_str)
        results["actual_total"] = actual_total
        
        logger.info(f"✓ Parsed cart total: ${actual_total:.2f}")
        
        tracker.log_step(
            "Extract cart total",
            f"Raw text: {cart_total_text}\nParsed amount: ${actual_total:.2f}"
        )
        
        # Step 3: Calculate threshold
        calculated_threshold = budget_per_item * items_count
        logger.info(f"ACTION: Calculating budget threshold: ${budget_per_item} × {items_count} = ${calculated_threshold:.2f}")
        
        tracker.log_step(
            "Calculate budget threshold",
            f"Budget per item: ${budget_per_item}\nItems count: {items_count}\nThreshold: ${calculated_threshold:.2f}"
        )
        
        # Step 4: Validate cart total against threshold
        logger.info(f"ACTION: Validating cart total...")
        
        is_within_budget = actual_total <= calculated_threshold
        results["is_within_budget"] = is_within_budget
        
        validation_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          CART VALIDATION REPORT                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

BUDGET CALCULATION:
  Budget per item:       ${budget_per_item:.2f}
  Items count:           {items_count}
  Calculated threshold:  ${calculated_threshold:.2f}

CART TOTAL:
  Actual total:          ${actual_total:.2f}
  Status:                {'✅ WITHIN BUDGET' if is_within_budget else '❌ EXCEEDS BUDGET'}

DIFFERENCE:
  Amount:                ${abs(actual_total - calculated_threshold):.2f}
  Type:                  {'Under' if is_within_budget else 'Over'} budget

╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        logger.info(validation_message)
        
        if is_within_budget:
            logger.info(f"✓ Cart total (${actual_total:.2f}) is within budget threshold (${calculated_threshold:.2f})")
            results["validation_passed"] = True
        else:
            logger.warning(f"✗ Cart total (${actual_total:.2f}) EXCEEDS budget threshold (${calculated_threshold:.2f})")
            results["validation_passed"] = False
        
        tracker.log_step(
            "Validate cart total",
            validation_message
        )
        
        # Step 5: Take screenshot of cart page
        logger.info("ACTION: Taking screenshot of cart page")
        
        screenshot_name = f"Cart_Validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        take_screenshot(driver, take_screenshot_func, name=screenshot_name)
        
        tracker.log_step(
            "Take cart page screenshot",
            f"Screenshot saved: {screenshot_name}"
        )
        
        logger.info(f"✓ Screenshot saved: {screenshot_name}")
        
        # Attach validation report to Allure
        allure.attach(
            validation_message,
            name="cart_validation_report",
            attachment_type=allure.attachment_type.TEXT
        )
        
        tracker.log_step("Final Result", validation_message)
        tracker.attach_to_allure()
        
        return results
        
    except Exception as e:
        logger.error(f"✗ Cart validation failed: {str(e)}")
        
        error_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CART VALIDATION ERROR                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Error: {str(e)}
Budget per item: ${budget_per_item}
Items count: {items_count}
Threshold: ${budget_per_item * items_count:.2f}

╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        logger.error(error_message)
        allure.attach(
            error_message,
            name="cart_validation_error",
            attachment_type=allure.attachment_type.TEXT
        )
        
        tracker.log_step("Cart Validation", f"❌ FAILED: {str(e)}")
        tracker.attach_to_allure()
        
        raise


class TestCartValidation(BaseSeleniumTest):
    """Test suite for cart validation and budget checking."""
    
    @allure.title("Validate Cart Total - 4 Items Under $15 Budget")
    @allure.description("Validate that shopping cart total does not exceed calculated budget (4 items × $15)")
    @allure.tag("automationteststore", "cart", "validation", "budget", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_validate_cart_total_under_budget(self):
        """
        Test flow:
        1. Perform login to Automation Test Store
        2. Add items to cart (done in previous test)
        3. Navigate to cart page
        4. Validate cart total does not exceed budget threshold
        5. Capture screenshot and traces
        
        Budget Parameters:
        - Budget per item: $15.00
        - Items count: 4
        - Expected threshold: $60.00
        """
        tracker = TestExecutionTracker("validate_cart_total")
        
        # Step 1: Login first
        logger.info("\n🔐 STEP 1: Performing login before cart validation")
        try:
            from automation.steps import perform_automation_test_store_login
            
            perform_automation_test_store_login(self.driver)
            tracker.log_step("Login to Automation Test Store", "Login successful")
            logger.info("✓ Login completed successfully")
            
            time.sleep(2)
        except Exception as e:
            logger.error(f"✗ Login failed: {e}")
            tracker.log_step("Login to Automation Test Store", f"❌ FAILED: {e}")
            raise
        
        # Step 2: Navigate to homepage
        logger.info("\n📍 STEP 2: Navigating to Automation Test Store homepage")
        result = navigate_to_automation_test_store(self.driver, url="https://automationteststore.com/")
        tracker.log_step("Navigate to homepage", f"URL: {result}")
        SmartAssert.equal(result, "https://automationteststore.com/", "Navigate to homepage", "URL mismatch")
        
        # Step 3: Validate cart
        logger.info("\n🛒 STEP 3: Validating cart total")
        
        # Budget parameters
        budget_per_item = 15.0  # $15 per item
        items_count = 4         # 4 items in cart
        
        # Call async validation function
        try:
            import asyncio
            results = asyncio.run(assert_cart_total_not_exceeds(
                self.driver,
                self.take_screenshot,
                budget_per_item=budget_per_item,
                items_count=items_count
            ))
            
            # Assert validation passed
            SmartAssert.true(
                results["validation_passed"],
                "Cart total within budget",
                f"Expected cart total <= ${results['calculated_threshold']:.2f}, got ${results['actual_total']:.2f}"
            )
            
            logger.info(f"\n✅ Cart validation completed successfully!")
            logger.info(f"   Cart total: ${results['actual_total']:.2f}")
            logger.info(f"   Budget threshold: ${results['calculated_threshold']:.2f}")
            logger.info(f"   Status: {'✅ WITHIN BUDGET' if results['is_within_budget'] else '❌ EXCEEDS BUDGET'}")
            
            tracker.log_step(
                "Final Validation Result",
                f"Cart total (${results['actual_total']:.2f}) is within budget threshold (${results['calculated_threshold']:.2f})"
            )
            
        except Exception as e:
            logger.error(f"✗ Cart validation failed: {e}")
            tracker.log_step("Cart Validation", f"❌ FAILED: {str(e)}")
            raise
        
        # Log success
        success_msg = f"✅ Successfully validated cart total: ${results['actual_total']:.2f} <= ${results['calculated_threshold']:.2f}"
        log_success_message("Cart Validation", success_msg)
        tracker.log_step("Final Summary", success_msg)
        
        # Attach all data to Allure
        tracker.attach_to_allure()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
