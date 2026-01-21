"""
Automation Test Store - Cart Validation Tests
==============================================

Test suite for shopping cart validation functionality.
Tests validate cart totals against budget constraints.

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
    navigate_to_cart_page,
    get_cart_total,
    take_screenshot,
)
from .test_login import execute_login_flow


def assertCartTotalNotExceeds(driver, take_screenshot_func, budgetPerItem: float, itemsCount: int):
    """
    Validate that shopping cart total does not exceed the calculated budget threshold.
    
    Orchestrates the cart validation process after login.
    Can be reused across different test scenarios.
    
    Flow:
        1. Navigate to cart page
        2. Extract total amount from cart
        3. Calculate budget threshold and validate
    
    Args:
        driver: Selenium WebDriver instance (already logged in)
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        budgetPerItem: Maximum budget per item (USD)
        itemsCount: Number of items expected in cart
        
    Returns:
        dict: Results dictionary containing:
            - budget_per_item (float): Budget per item
            - items_count (int): Number of items
            - calculated_threshold (float): Budget threshold (budgetPerItem * itemsCount)
            - actual_total (float): Actual cart total
            - is_within_budget (bool): Whether total is within budget
            - validation_passed (bool): Overall validation result
            
    Raises:
        AssertionError: If validation fails
    """
    # Initialize results tracking
    results = {
        "budget_per_item": budgetPerItem,
        "items_count": itemsCount,
        "calculated_threshold": budgetPerItem * itemsCount,
        "actual_total": None,
        "is_within_budget": False,
        "validation_passed": False
    }
    
    # Step 1: Navigate to cart page
    with step_aware_loggerStep("Step 1: Navigate to cart page"):
        navigate_to_cart_page(driver)
        take_screenshot(driver, take_screenshot_func, name="Cart_Page")
        step_aware_loggerInfo("✓ Navigated to cart page")
    
    # Step 2: Extract cart total
    with step_aware_loggerStep("Step 2: Extract cart total from page"):
        actual_total = get_cart_total(driver)
        results["actual_total"] = actual_total
        step_aware_loggerInfo(f"✓ Cart total extracted: ${actual_total:.2f}")
    
    # Step 3: Calculate threshold and validate
    with step_aware_loggerStep("Step 3: Validate cart total against budget"):
        calculated_threshold = budgetPerItem * itemsCount
        is_within_budget = actual_total <= calculated_threshold
        results["is_within_budget"] = is_within_budget
        results["validation_passed"] = is_within_budget
        
        validation_message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          CART VALIDATION REPORT                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

BUDGET CALCULATION:
  Budget per item:       ${budgetPerItem:.2f}
  Items count:           {itemsCount}
  Calculated threshold:  ${calculated_threshold:.2f}

CART TOTAL:
  Actual total:          ${actual_total:.2f}
  Status:                {'✅ WITHIN BUDGET' if is_within_budget else '❌ EXCEEDS BUDGET'}

DIFFERENCE:
  Amount:                ${abs(actual_total - calculated_threshold):.2f}
  Type:                  {'Under' if is_within_budget else 'Over'} budget

╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        step_aware_loggerInfo(validation_message)
        
        # Attach summary to Allure
        allure.attach(
            validation_message,
            name="cart_validation_report",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Assert validation passed
        SmartAssert.true(
            is_within_budget,
            "Cart total within budget",
            f"Expected cart total <= ${calculated_threshold:.2f}, got ${actual_total:.2f}"
        )
        
        step_aware_loggerInfo(
            f"✓ Cart total (${actual_total:.2f}) is within budget threshold (${calculated_threshold:.2f})"
        )
    
    return results


class TestCartValidation(BaseSeleniumTest):
    """
    Test suite for Automation Test Store cart validation functionality.
    
    Validates:
        - Login functionality (using execute_login_flow)
        - Cart navigation
        - Cart total extraction
        - Budget validation
    """
    
    @allure.title("Validate Cart Total - 4 Items Under $15 Budget")
    @allure.description("Validate that shopping cart total does not exceed calculated budget (4 items × $15)")
    @allure.tag("automationteststore", "cart", "validation", "budget", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_validate_cart_total_under_budget(self):
        """
        Execute complete cart validation flow for Automation Test Store.
        
        Test Flow:
            1. Login to Automation Test Store (using execute_login_flow from test_login)
            2. Validate cart total using assertCartTotalNotExceeds:
                a. Navigate to cart page
                b. Extract total amount
                c. Validate against budget threshold
        
        Budget Parameters:
            - Budget per item: $15.00
            - Items count: 4
            - Expected threshold: $60.00
        
        Expected Results:
            - Login completes successfully
            - Cart total is extracted successfully
            - Cart total does not exceed $60.00
        """
        # Step 1: Login using execute_login_flow from test_login
        login_result = execute_login_flow(self.driver)
        step_aware_loggerInfo(f"✓ Login completed for user: {login_result['username']}")
        take_screenshot(self.driver, self.take_screenshot, name="After_Login")
        
        # Budget parameters
        budget_per_item = 15.0  # $15 per item
        items_count = 4         # 4 items in cart
        
        # Step 2: Validate cart total using assertCartTotalNotExceeds
        result = assertCartTotalNotExceeds(
            self.driver,
            self.take_screenshot,
            budgetPerItem=budget_per_item,
            itemsCount=items_count
        )
        
        step_aware_loggerInfo(
            f"✓ Test completed successfully: Cart total ${result['actual_total']:.2f} is within budget ${result['calculated_threshold']:.2f}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
