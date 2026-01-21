"""
Automation Test Store - Search and Price Filter Tests
======================================================

Test suite for Automation Test Store search functionality with price filtering.
Tests validate product search with price constraints, pagination handling,
and accurate result counting.

Environment Variables Required:
    - ATS_URL: Automation Test Store URL (default: https://automationteststore.com/)
"""

import os

import pytest
import allure

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    verify_page_title,
    search_items_by_name_under_price,
)


def search_items_by_name_under_price_flow(driver, search_query: str, max_price: float, limit: int = 5):
    """
    Execute complete search flow with price filtering for Automation Test Store.
    
    Orchestrates the full search process from homepage navigation to product collection
    with price filtering and pagination. Can be reused across different test scenarios.
    
    Flow:
        1. Navigate to Automation Test Store homepage
        2. Verify page title
        3. Search and collect products with price filtering and pagination
        4. Verify and return results
    
    Args:
        driver: Selenium WebDriver instance
        search_query: Search term (e.g., "dress", "soap", "perfume")
        max_price: Maximum price filter in dollars
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        list: Product URLs found (empty list if none found)
            
    Raises:
        AssertionError: If any step validation fails
    """
    # Step 1: Navigate to Automation Test Store
    ats_url = os.getenv("ATS_URL", "https://automationteststore.com/")
    with step_aware_loggerStep("Step 1: Navigate to Automation Test Store"):
        result = navigate_to_automation_test_store(driver, url=ats_url)
        SmartAssert.equal(result, ats_url, "Navigate to homepage", "URL mismatch")
    
    # Step 2: Verify page title
    with step_aware_loggerStep("Step 2: Verify page title"):
        result = verify_page_title(driver, "practice")
        SmartAssert.true(result, "Page title verified", "Title check failed")
    
    # Step 3: Search and collect products with price filtering
    with step_aware_loggerStep(f"Step 3: Search '{search_query}' and collect products under ${max_price} (limit: {limit})"):
        product_urls = search_items_by_name_under_price(
            driver,
            query=search_query,
            max_price=max_price,
            limit=limit,
            in_stock_only=True
        )
        
        SmartAssert.true(
            isinstance(product_urls, list),
            "Results are a list",
            "Results should be a list"
        )
        
        SmartAssert.true(
            len(product_urls) <= limit,
            "Results count is within limit",
            f"Expected <= {limit} results, got {len(product_urls)}"
        )
    
    # Step 4: Verify and log final results
    with step_aware_loggerStep(f"Step 4: Verify search results"):
        step_aware_loggerInfo(
            f"Search completed: Found {len(product_urls)} products for '{search_query}' under ${max_price}"
        )
        
        if len(product_urls) > 0:
            for i, url in enumerate(product_urls, 1):
                step_aware_loggerInfo(f"  {i}. {url}")
        else:
            step_aware_loggerInfo("No products found matching criteria")
    
    return product_urls


class TestAutomationTestStoreSearch(BaseSeleniumTest):
    """
    Test suite for Automation Test Store search and price filtering functionality.
    
    Validates:
        - Homepage navigation
        - Search with price filtering
        - Accurate result counting
        - Pagination support
        - Empty result handling
        
    DATA DRIVEN:
        Scenarios are loaded from config/test_data.json
    """
    
    from automation.utils.data_loader import get_test_data
    
    # Load test data at module level for parametrization
    try:
        data = get_test_data()
        search_scenarios = data.get("search_test", {}).get("scenarios", [])
    except Exception as e:
        import logging
        logging.warning(f"Could not load test data: {e}")
        search_scenarios = []

    @pytest.mark.parametrize("scenario", search_scenarios)
    @allure.title("Data Driven Search: {scenario[id]}")
    @allure.description("Dynamic search test based on external JSON configuration")
    @allure.tag("automationteststore", "search", "price-filter", "data-driven")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_items_data_driven(self, scenario):
        """
        Execute data-driven search test.
        
        Args:
            scenario (dict): Test scenario containing query, max_price, and expected_count
        """
        query = scenario["query"]
        max_price = scenario["max_price"]
        expected_count = scenario["expected_count"]
        
        step_aware_loggerInfo(f"Starting Data-Driven Test: {scenario['id']}")
        step_aware_loggerInfo(f"Query: '{query}', Max Price: {max_price}, Expecting: {expected_count}")
        
        product_urls = search_items_by_name_under_price_flow(
            self.driver,
            search_query=query,
            max_price=max_price,
            limit=5
        )
        
        with step_aware_loggerStep(f"Step 5: Verify exactly {expected_count} results returned"):
            SmartAssert.equal(
                len(product_urls), expected_count,
                f"Got exactly {expected_count} results",
                f"Expected {expected_count} results, but got {len(product_urls)}"
            )
            
            step_aware_loggerInfo(f"✓ Test passed: Got {len(product_urls)} products for '{query}' under ${max_price}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
