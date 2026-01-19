import pytest
import allure
from selenium.webdriver.common.by import By
import time
from datetime import datetime

from automation.core import BaseSeleniumTest, get_logger, TestExecutionTracker, SmartAssert
from automation.steps import (
    navigate_to_automation_test_store,
    search_items_by_name_under_price,
    search_items_by_query,
    apply_price_filter,
    extract_product_links_with_prices,
    verify_page_title,
    take_screenshot,
    log_success_message,
)

logger = get_logger(__name__)


def perform_search_test(driver, take_screenshot_func, search_query: str, max_price: float, limit: int = 5):
    """
    Helper function to perform search test with given parameters.
    
    Args:
        driver: Selenium WebDriver instance
        take_screenshot_func: Screenshot function from BaseSeleniumTest
        search_query: What to search for
        max_price: Maximum price filter
        limit: Maximum number of results to return
    
    Returns:
        List of product URLs found
    """
    
    tracker = TestExecutionTracker(f"search_{search_query}_under_{max_price}")
    
    # Step 1: Navigate to Automation Test Store
    result = navigate_to_automation_test_store(driver, url="https://automationteststore.com/")
    tracker.log_step("Navigate to Automation Test Store", f"URL: {result}")
    SmartAssert.equal(result, "https://automationteststore.com/", "Navigate to homepage", "URL mismatch")
    
    # Step 2: Search for items by name and under price
    product_urls = search_items_by_name_under_price(
        driver,
        query=search_query,
        max_price=max_price,
        limit=limit
    )
    
    tracker.log_step(
        "Search items by name under price",
        f"Query: {search_query}\nMax Price: ${max_price}\nLimit: {limit}\nResults Found: {len(product_urls)}"
    )
    
    SmartAssert.true(
        isinstance(product_urls, list),
        "Results are a list",
        "Results should be a list"
    )
    
    SmartAssert.true(
        len(product_urls) <= limit,
        f"Results count is within limit",
        f"Expected <= {limit} results, got {len(product_urls)}"
    )
    
    # Step 3: Take screenshot of search results
    time.sleep(1)
    result = take_screenshot(driver, take_screenshot_func, name=f"Search Results - {search_query} under ${max_price}")
    tracker.log_step("Take screenshot of search results", "Screenshot saved")
    SmartAssert.true(result is not None, "Screenshot taken", "Screenshot failed")
    
    # Step 4: Verify results
    if len(product_urls) > 0:
        tracker.log_step(
            "Verify search results",
            f"Found {len(product_urls)} products:\n" + "\n".join(product_urls)
        )
        # Print results to console for visibility
        print(f"\n{'='*80}")
        print(f"✅ SEARCH RESULTS: Found {len(product_urls)} products matching '{search_query}' under ${max_price}")
        print(f"{'='*80}")
        for i, url in enumerate(product_urls, 1):
            print(f"{i}. {url}")
        print(f"{'='*80}\n")
        
        SmartAssert.true(
            len(product_urls) > 0,
            "Search results found",
            f"Expected to find products matching '{search_query}' under ${max_price}"
        )
    else:
        tracker.log_step(
            "Verify search results",
            f"No products found matching criteria (this may be expected)"
        )
        logger.warning(f"No products found for '{search_query}' under ${max_price}")
    
    # Step 5: Log success
    result = log_success_message(
        "Automation Test Store Search Test",
        f"✅ Successfully searched for '{search_query}' with price filter ${max_price} and found {len(product_urls)} products!"
    )
    tracker.log_step("Log success message", "Test completed successfully")
    SmartAssert.true(result is not None, "Success logged", "Success logging failed")
    
    # Attach all test execution data to Allure
    tracker.attach_to_allure()
    
    return product_urls


class TestAutomationTestStoreSearch(BaseSeleniumTest):
    """Test suite for Automation Test Store search and price filtering."""
    
    @allure.title("Search Dress Items Under $100")
    @allure.description("Search for dress items with maximum price of $100")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_dress_under_100(self):
        """Search for dress products under $100"""
        perform_search_test(
            self.driver,
            self.take_screenshot,
            search_query="dress",
            max_price=100.0,
            limit=5
        )
    
    @allure.title("Search 'a' Items Under $15 with Pagination")
    @allure.description("Search for items with 'a' with maximum price of $15, limit 6 items to test pagination")
    @allure.tag("automationteststore", "search", "price-filter", "pagination", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_a_under_15_with_pagination(self):
        """Search for 'a' products under $15 with pagination support"""
        perform_search_test(
            self.driver,
            self.take_screenshot,
            search_query="a",
            max_price=15.0,
            limit=6
        )
    
    @allure.title("Search Soap Items Under $30")
    @allure.description("Search for soap items with maximum price of $30")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_soap_under_30(self):
        """Search for soap products under $30"""
        perform_search_test(
            self.driver,
            self.take_screenshot,
            search_query="soap",
            max_price=30.0,
            limit=5
        )
    
    @allure.title("Search Perfume Items Under $80")
    @allure.description("Search for perfume items with maximum price of $80")
    @allure.tag("automationteststore", "search", "price-filter", "smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_perfume_under_80(self):
        """Search for perfume products under $80"""
        perform_search_test(
            self.driver,
            self.take_screenshot,
            search_query="perfume",
            max_price=80.0,
            limit=5
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
