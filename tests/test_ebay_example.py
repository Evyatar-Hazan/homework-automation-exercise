"""
Example Test Module
===================

Demonstrates how to write clean, business-focused tests.

Key Points:
- Tests focus on business logic
- No Playwright, CSS selectors, or timeouts in tests
- All technical details handled by infrastructure
- Fixtures handle setup/teardown
- Tests are readable by non-technical stakeholders
"""

import pytest
import json
from pathlib import Path

from automation.core import DriverFactory, BasePage, get_logger, AutomationLogger
from automation.pages.ebay_example import eBaySearchPage
from automation.utils.random_utils import generate_random_email

logger = get_logger(__name__)


# ============================================================================
# FIXTURES - Setup & Teardown Infrastructure
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for all tests."""
    AutomationLogger.configure(
        log_level="DEBUG",
        log_format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        log_file="reports/automation.log",
        console_output=True,
    )
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTED")
    logger.info("=" * 80)


@pytest.fixture(scope="function")
async def ebay_browser_setup_teardown():
    """
    Setup and teardown browser for each test.
    
    Yields:
        eBaySearchPage object ready for testing
    """
    logger.info("=" * 80)
    logger.info("TEST SETUP: Initializing browser")
    logger.info("=" * 80)
    
    # Initialize driver factory
    factory = DriverFactory()
    await factory.initialize()
    
    # Create isolated browser instance
    browser = await factory.create_browser()
    context = await factory.create_context(browser, test_name="ebay_search")
    page = await factory.create_page(context)
    
    # Create page object (infrastructure + business abstraction)
    base_page = BasePage(page)
    search_page = eBaySearchPage(base_page)
    
    # Navigate to eBay (or your test site)
    await search_page.navigate("https://www.ebay.com")
    
    logger.info("✓ Browser setup complete")
    
    # Yield to test
    yield search_page
    
    # Teardown
    logger.info("=" * 80)
    logger.info("TEST TEARDOWN: Closing browser")
    logger.info("=" * 80)
    
    await factory.cleanup_page(page)
    await factory.cleanup_context(context)
    await factory.cleanup_browser(browser)
    await factory.cleanup()
    
    logger.info("✓ Browser cleanup complete")


def load_test_data():
    """Load test data from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "test_data.json"
    with open(data_path, 'r') as f:
        return json.load(f)


# ============================================================================
# TEST CASES - Business Logic Only
# ============================================================================

@pytest.mark.asyncio
class TestEBaySearch:
    """
    Test suite for eBay search functionality.
    
    Tests demonstrate how to write business-focused tests:
    - No Playwright details
    - No selectors or timeouts
    - Clear assertions
    - Readable by stakeholders
    """
    
    @pytest.mark.asyncio
    async def test_search_product_basic(self, ebay_browser_setup_teardown):
        """
        Test basic product search.
        
        Given: User is on eBay home page
        When:  User searches for "laptop"
        Then:  Search results are displayed
        """
        search_page = ebay_browser_setup_teardown
        
        logger.info("TEST: test_search_product_basic")
        logger.info("ACTION: Searching for 'laptop'")
        
        # Perform search
        await search_page.search("laptop")
        
        # Verify results displayed
        logger.info("ASSERTION: Verifying search results are visible")
        assert await search_page.is_search_results_visible(), \
            "Search results should be visible after search"
        
        logger.info("✓ TEST PASSED")
    
    @pytest.mark.asyncio
    async def test_product_count_after_search(self, ebay_browser_setup_teardown):
        """
        Test that search returns multiple results.
        
        Given: User is on eBay home page
        When:  User searches for "vintage"
        Then:  Multiple products are displayed (at least 1)
        """
        search_page = ebay_browser_setup_teardown
        
        logger.info("TEST: test_product_count_after_search")
        logger.info("ACTION: Searching for 'vintage'")
        
        await search_page.search("vintage")
        
        logger.info("ASSERTION: Checking product count")
        product_count = await search_page.count_search_results()
        assert product_count > 0, f"Should have at least 1 result, got {product_count}"
        
        logger.info(f"✓ Found {product_count} products")
        logger.info("✓ TEST PASSED")
    
    @pytest.mark.asyncio
    async def test_get_first_product_details(self, ebay_browser_setup_teardown):
        """
        Test retrieving first product details.
        
        Given: User searches for a product
        When:  User views search results
        Then:  Product title and price are visible
        """
        search_page = ebay_browser_setup_teardown
        test_data = load_test_data()
        
        logger.info("TEST: test_get_first_product_details")
        
        # Search for first test product
        search_term = test_data["test_search_terms"][0]
        logger.info(f"ACTION: Searching for '{search_term}'")
        await search_page.search(search_term)
        
        # Get product details
        logger.info("ACTION: Retrieving product title and price")
        title = await search_page.get_first_product_title()
        price = await search_page.get_first_product_price()
        
        # Assertions
        logger.info("ASSERTION: Verifying product details exist")
        assert title, "Product title should not be empty"
        assert price, "Product price should not be empty"
        
        logger.info(f"✓ Product Title: {title[:50]}...")
        logger.info(f"✓ Product Price: {price}")
        logger.info("✓ TEST PASSED")


class TestEBayFilters:
    """Test suite for eBay filter functionality."""
    
    @pytest.mark.asyncio
    async def test_price_filter(self, ebay_browser_setup_teardown):
        """
        Test price range filter.
        
        Given: User searches for a product
        When:  User applies price filter (50-200)
        Then:  Filtered results are displayed
        """
        search_page = ebay_browser_setup_teardown
        
        logger.info("TEST: test_price_filter")
        logger.info("ACTION: Searching for 'electronics'")
        
        # Initial search
        await search_page.search("electronics")
        
        # Apply price filter
        logger.info("ACTION: Applying price filter: $50-$200")
        await search_page.set_price_filter(50, 200)
        
        # Verify results still visible
        logger.info("ASSERTION: Verifying filtered results are displayed")
        assert await search_page.is_search_results_visible(), \
            "Filtered results should be visible"
        
        logger.info("✓ TEST PASSED")


class TestDataDriven:
    """
    Test suite demonstrating data-driven testing.
    
    Uses test data from test_data.json.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("search_term", [
        "laptop",
        "shoes",
        "vintage",
    ])
    async def test_search_various_terms(self, ebay_browser_setup_teardown, search_term):
        """
        Parametrized test - runs multiple times with different data.
        
        Given: User is on eBay
        When:  User searches for various terms
        Then:  Results are displayed for each term
        """
        search_page = ebay_browser_setup_teardown
        
        logger.info(f"TEST: test_search_various_terms[{search_term}]")
        logger.info(f"ACTION: Searching for '{search_term}'")
        
        await search_page.search(search_term)
        
        logger.info("ASSERTION: Verifying results are displayed")
        assert await search_page.is_search_results_visible(), \
            f"Results should be visible for '{search_term}'"
        
        logger.info(f"✓ TEST PASSED for '{search_term}'")


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run tests from command line:
    
    pytest tests/test_ebay_example.py -v -s
    pytest tests/test_ebay_example.py::TestEBaySearch::test_search_product_basic -v -s
    pytest tests/test_ebay_example.py --log-cli-level=DEBUG
    """
    pytest.main([__file__, "-v", "-s"])
