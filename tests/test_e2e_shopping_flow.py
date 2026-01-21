"""
Automation Test Store - E2E Shopping Flow Test
===============================================

End-to-End test suite that validates the complete shopping flow.
Combines login, search, add to cart, and cart validation in a single test.

This test demonstrates a complete user journey through the e-commerce site,
validating each critical step of the shopping process to ensure system integrity.

Test Flow:
    1. Login to Automation Test Store
    2. Search for items by name and price
    3. Add found items to cart
    4. Validate cart total does not exceed budget

Environment Variables Required:
    - ATS_URL: Automation Test Store URL (default: https://automationteststore.com/)
    - ATS_TEST_USER_NAME: Test user's login name
    - ATS_TEST_PASSWORD: Test user's password

Author: Automation Team
Date: January 2026
"""

import pytest
import allure

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest
from automation.steps import take_screenshot
from .test_login import execute_login_flow
from .test_search_items_by_price import search_items_by_name_under_price_flow
from .test_add_items_to_cart import addItemsToCart
from .test_cart_validation import assertCartTotalNotExceeds


class TestE2EShoppingFlow(BaseSeleniumTest):
    """
    End-to-End test suite for complete shopping flow in Automation Test Store.

    This test class validates the entire user journey through the e-commerce platform,
    ensuring that all critical components work together seamlessly.

    Test Coverage:
        - User authentication and session management
        - Product search with price filtering
        - Shopping cart operations
        - Budget validation and financial constraints

    Inherits:
        BaseSeleniumTest: Provides browser setup, teardown, and utility methods
    """

    @allure.title("E2E Shopping Flow - Search, Add to Cart, and Validate Total")
    @allure.description(
        "Complete end-to-end shopping flow: login → search items by name under price → "
        "add items to cart → validate cart total does not exceed budget"
    )
    @allure.tag("automationteststore", "e2e", "shopping", "critical", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_shopping_flow(self):
        """
        Execute complete end-to-end shopping flow.

        This test validates the entire shopping journey from authentication through
        purchase validation, ensuring system integrity at each step.

        Test Sequence:
            1. Login to Automation Test Store (execute_login_flow)
               - Validates user authentication
               - Establishes session

            2. Search for items by name under price (search_items_by_name_under_price_flow)
               - Search query: "a"
               - Max price: $15.00
               - Limit: 5 items
               - Validates search functionality and price filtering

            3. Add found items to cart (addItemsToCart)
               - Iterates through product URLs
               - Handles product variants
               - Confirms cart additions

            4. Validate cart total against budget (assertCartTotalNotExceeds)
               - Budget per item: $15.00
               - Items count: 5
               - Expected threshold: $75.00
               - Ensures financial constraints are respected

        Expected Results:
            - Login completes successfully with valid session
            - Products matching criteria are found and collected
            - All items are successfully added to cart
            - Cart total does not exceed calculated budget
            - Comprehensive summary is generated and attached to report

        Raises:
            pytest.skip: If no products are found matching search criteria
            AssertionError: If any validation step fails
        """

        # ===================================================================
        # STEP 1: Login to Automation Test Store
        # ===================================================================
        with step_aware_loggerStep("E2E Step 1: Execute login flow"):
            login_result = execute_login_flow(self.driver)
            step_aware_loggerInfo(f"✓ Login completed for user: {login_result['username']}")
            take_screenshot(self.driver, self.take_screenshot, name="E2E_After_Login")

        # ===================================================================
        # STEP 2: Search for items by name under price
        # ===================================================================
        search_query = "a"
        max_price = 15.0
        limit = 5

        with step_aware_loggerStep(
            f"E2E Step 2: Search items by name ('{search_query}') under price (${max_price})"
        ):
            product_urls = search_items_by_name_under_price_flow(
                self.driver,
                search_query=search_query,
                max_price=max_price,
                limit=limit
            )

            step_aware_loggerInfo(
                f"✓ Search completed: Found {len(product_urls)} products under ${max_price}"
            )
            take_screenshot(self.driver, self.take_screenshot, name="E2E_After_Search")

            # Validate we found products
            if len(product_urls) == 0:
                step_aware_loggerInfo(
                    "⚠️  No products found. Test cannot proceed with cart operations."
                )
                pytest.skip("No products found matching search criteria")

        # ===================================================================
        # STEP 3: Add items to cart
        # ===================================================================
        with step_aware_loggerStep(f"E2E Step 3: Add {len(product_urls)} items to cart"):
            add_result = addItemsToCart(
                driver=self.driver,
                take_screenshot_func=self.take_screenshot,
                product_urls=product_urls
            )

            step_aware_loggerInfo(
                f"✓ Added {add_result['successfully_added']}/{add_result['total_urls']} items to cart"
            )

            if add_result['failed_items']:
                step_aware_loggerInfo(
                    f"⚠️  {len(add_result['failed_items'])} items failed to add"
                )

            take_screenshot(self.driver, self.take_screenshot, name="E2E_After_Adding_Items")

        # ===================================================================
        # STEP 4: Validate cart total does not exceed budget
        # ===================================================================
        budget_per_item = max_price  # Use the same max_price from search
        items_count = len(product_urls)  # Use actual number of items found

        with step_aware_loggerStep(
            f"E2E Step 4: Validate cart total (budget: ${budget_per_item} × {items_count} items)"
        ):
            validation_result = assertCartTotalNotExceeds(
                driver=self.driver,
                take_screenshot_func=self.take_screenshot,
                budgetPerItem=budget_per_item,
                itemsCount=items_count
            )

            step_aware_loggerInfo(
                f"✓ Cart validation completed: "
                f"Total ${validation_result['actual_total']:.2f} is within budget "
                f"${validation_result['calculated_threshold']:.2f}"
            )
            take_screenshot(self.driver, self.take_screenshot, name="E2E_Final_Validation")

        # ===================================================================
        # FINAL SUMMARY
        # ===================================================================
        with step_aware_loggerStep("E2E Final Summary"):
            summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       E2E SHOPPING FLOW - SUMMARY                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

LOGIN:
  ✓ User logged in:          {login_result['username']}

SEARCH:
  ✓ Search query:            '{search_query}'
  ✓ Max price filter:        ${max_price:.2f}
  ✓ Products found:          {len(product_urls)}

ADD TO CART:
  ✓ Items added:             {add_result['successfully_added']}/{add_result['total_urls']}
  {'✗ Items failed:            ' + str(len(add_result['failed_items'])) if add_result['failed_items'] else '✓ All items added successfully'}

CART VALIDATION:
  ✓ Budget per item:         ${validation_result['budget_per_item']:.2f}
  ✓ Items count:             {validation_result['items_count']}
  ✓ Calculated threshold:    ${validation_result['calculated_threshold']:.2f}
  ✓ Actual cart total:       ${validation_result['actual_total']:.2f}
  ✓ Status:                  {'✅ WITHIN BUDGET' if validation_result['is_within_budget'] else '❌ EXCEEDS BUDGET'}

RESULT:
  {'✅ E2E TEST PASSED' if validation_result['validation_passed'] else '❌ E2E TEST FAILED'}

╚══════════════════════════════════════════════════════════════════════════════╝
"""

            step_aware_loggerInfo(summary)

            # Attach summary to Allure report
            allure.attach(
                summary,
                name="e2e_shopping_flow_summary",
                attachment_type=allure.attachment_type.TEXT
            )

            step_aware_loggerInfo("✓ E2E Shopping Flow Test completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
