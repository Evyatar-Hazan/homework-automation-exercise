"""
Automation Test Store - Search and Price Filter Tests
======================================================

Test suite for Automation Test Store search functionality with price filtering.
Includes a reusable search flow function that can be imported and used in other tests.

Environment Variables Required:
    - ATS_URL: Automation Test Store URL (default: https://automationteststore.com/)
"""

import os

import pytest
import allure

from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo
from automation.core import BaseSeleniumTest, get_logger, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    verify_page_title,
    search_items_by_query,
    search_and_collect_products_by_price,
)


logger = get_logger(__name__)


def execute_search_flow(driver, search_query: str, max_price: float, limit: int = 5):
    """
    Execute complete search flow with price filtering for Automation Test Store.
    
    This function orchestrates the full search process from homepage navigation
    to product search with price filtering and pagination. It can be reused 
    across different test scenarios.
    
    Flow:
        1. Navigate to Automation Test Store homepage
        2. Verify page title
        3. Perform search query
        4. Collect products with price filtering and pagination
        5. Verify and return results
    
    Args:
        driver: Selenium WebDriver instance
        search_query: Search term to look for (e.g., "dress", "soap")
        max_price: Maximum price filter in dollars
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        list: List of product URLs found (empty list if none found)
            
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
    
    # Step 3: Perform search query
    with step_aware_loggerStep(f"Step 3: Search for '{search_query}'"):
        result = search_items_by_query(driver, search_query)
        SmartAssert.true(result, "Search performed", "Search failed")
    
    # Step 4: Collect products with price filtering and pagination
    with step_aware_loggerStep(f"Step 4: Collect products under ${max_price} (limit: {limit})"):
        product_urls = search_and_collect_products_by_price(
            driver,
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
    
    # Step 5: Verify and log final results
    with step_aware_loggerStep(f"Step 5: Verify search results"):
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
    
    This test class validates search capabilities including:
    - Homepage navigation
    - Search with price filtering
    - Result verification
    - Pagination support (when needed)
    """
    
    @allure.title("Search 'a' Items Under $15 - Expect 5 Results")
    @allure.description("Search for items with 'a' with maximum price of $15, expecting exactly 5 results")
    @allure.tag("automationteststore", "search", "price-filter", "pagination", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_a_under_15_expect_5_results(self):
        """
        Search for 'a' products under $15 and verify we get exactly 5 results.
        
        Expected Results:
            - Search completes successfully
            - Returns exactly 5 product URLs
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="a",
            max_price=15.0,
            limit=5
        )
        
        # Step 6: Verify we got exactly 5 results
        with step_aware_loggerStep("Step 6: Verify exactly 5 results returned"):
            SmartAssert.true(
                isinstance(product_urls, list),
                "Results are a list",
                "Results should be a list"
            )
            
            SmartAssert.equal(
                len(product_urls), 5,
                "Got exactly 5 results",
                f"Expected exactly 5 results, but got {len(product_urls)}"
            )
            
            step_aware_loggerInfo(
                f"✓ Test passed: Got exactly 5 products for 'a' under $15"
            )
    
    @allure.title("Search Dress Items Under $100 - Expect No Results")
    @allure.description("Search for dress items with maximum price of $100, expecting empty results")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_dress_under_100_expect_empty(self):
        """
        Search for dress products under $100 and verify we get no results.
        
        Expected Results:
            - Search completes successfully
            - Returns empty list (no products found)
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="dress",
            max_price=100.0,
            limit=5
        )
        
        # Step 6: Verify we got empty results
        with step_aware_loggerStep("Step 6: Verify empty results returned"):
            SmartAssert.true(
                isinstance(product_urls, list),
                "Results are a list",
                "Results should be a list"
            )
            
            SmartAssert.equal(
                len(product_urls), 0,
                "Got empty results",
                f"Expected 0 results, but got {len(product_urls)}"
            )
            
            step_aware_loggerInfo(
                f"✓ Test passed: Got 0 products for 'dress' under $100 (as expected)"
            )
    
    @allure.title("Search Perfume Items Under $200 - Expect 2 Results")
    @allure.description("Search for perfume items with maximum price of $200, expecting exactly 2 results")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_perfume_under_200_expect_2_results(self):
        """
        Search for perfume products under $200 and verify we get exactly 2 results.
        
        Expected Results:
            - Search completes successfully
            - Returns exactly 2 product URLs
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="perfume",
            max_price=200.0,
            limit=5
        )
        
        # Step 6: Verify we got exactly 2 results
        with step_aware_loggerStep("Step 6: Verify exactly 2 results returned"):
            SmartAssert.true(
                isinstance(product_urls, list),
                "Results are a list",
                "Results should be a list"
            )
            
            SmartAssert.equal(
                len(product_urls), 2,
                "Got exactly 2 results",
                f"Expected exactly 2 results, but got {len(product_urls)}"
            )
            
            step_aware_loggerInfo(
                f"✓ Test passed: Got exactly 2 products for 'perfume' under $200"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
