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
    
    @allure.title("Search Dress Items Under $100")
    @allure.description("Search for dress items with maximum price of $100")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_dress_under_100(self):
        """
        Search for dress products under $100 and verify results.
        
        Expected Results:
            - Search completes successfully
            - Returns list of product URLs (may be empty)
            - Product count is within limit
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="dress",
            max_price=100.0,
            limit=5
        )
        
        # Verify results
        SmartAssert.true(
            isinstance(product_urls, list),
            "Results are a list",
            "Results should be a list"
        )
        
        SmartAssert.true(
            len(product_urls) <= 5,
            "Results count is within limit",
            f"Expected <= 5 results, got {len(product_urls)}"
        )
        
        step_aware_loggerInfo(
            f"✓ Search completed: Found {len(product_urls)} products for 'dress' under $100"
        )
    
    @allure.title("Search 'a' Items Under $15 with Pagination")
    @allure.description("Search for items with 'a' with maximum price of $15, limit 6 items to test pagination")
    @allure.tag("automationteststore", "search", "price-filter", "pagination", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_a_under_15_with_pagination(self):
        """
        Search for 'a' products under $15 with pagination support.
        
        Expected Results:
            - Search completes successfully
            - Returns list of product URLs (may be empty)
            - Pagination works correctly if needed
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="a",
            max_price=15.0,
            limit=6
        )
        
        # Verify results
        SmartAssert.true(
            isinstance(product_urls, list),
            "Results are a list",
            "Results should be a list"
        )
        
        SmartAssert.true(
            len(product_urls) <= 6,
            "Results count is within limit",
            f"Expected <= 6 results, got {len(product_urls)}"
        )
        
        step_aware_loggerInfo(
            f"✓ Search completed: Found {len(product_urls)} products for 'a' under $15"
        )
    
    @allure.title("Search Soap Items Under $30")
    @allure.description("Search for soap items with maximum price of $30")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_soap_under_30(self):
        """
        Search for soap products under $30 and verify results.
        
        Expected Results:
            - Search completes successfully
            - Returns list of product URLs (may be empty)
            - Product count is within limit
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="soap",
            max_price=30.0,
            limit=5
        )
        
        # Verify results
        SmartAssert.true(
            isinstance(product_urls, list),
            "Results are a list",
            "Results should be a list"
        )
        
        SmartAssert.true(
            len(product_urls) <= 5,
            "Results count is within limit",
            f"Expected <= 5 results, got {len(product_urls)}"
        )
        
        step_aware_loggerInfo(
            f"✓ Search completed: Found {len(product_urls)} products for 'soap' under $30"
        )
    
    @allure.title("Search Perfume Items Under $80")
    @allure.description("Search for perfume items with maximum price of $80")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_perfume_under_80(self):
        """
        Search for perfume products under $80 and verify results.
        
        Expected Results:
            - Search completes successfully
            - Returns list of product URLs (may be empty)
            - Product count is within limit
        """
        product_urls = execute_search_flow(
            self.driver,
            search_query="perfume",
            max_price=80.0,
            limit=5
        )
        
        # Verify results
        SmartAssert.true(
            isinstance(product_urls, list),
            "Results are a list",
            "Results should be a list"
        )
        
        SmartAssert.true(
            len(product_urls) <= 5,
            "Results count is within limit",
            f"Expected <= 5 results, got {len(product_urls)}"
        )
        
        step_aware_loggerInfo(
            f"✓ Search completed: Found {len(product_urls)} products for 'perfume' under $80"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
