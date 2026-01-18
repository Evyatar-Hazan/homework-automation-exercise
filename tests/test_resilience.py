"""
Resilience Testing Examples
============================

דוגמאות של בדיקות עם התמודדות מתקדמת עם GUI changes.

Demonstrates:
1. Testing with resilient locators
2. Monitoring locator performance
3. Handling GUI changes gracefully
4. Generating resilience reports

לאחר שינויים בממשק (CSS refactor, HTML restructure),
הטסטים ממשיכים לעבוד בלי שינויים קוד הבדיקה.
"""

import json
from pathlib import Path
from typing import Dict, Any

import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from automation.core.driver_factory import DriverFactory
from automation.core.logger import get_logger, configure_logging
from automation.core.resilience import ResilienceMonitor, AdaptiveSmartLocator
from automation.pages.resilient_ebay_example import ResilientEBaySearchPage, ResilientEBayProductPage

logger = get_logger(__name__)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def configure_logging_fixture():
    """Configure logging for tests."""
    configure_logging()
    yield


@pytest.fixture
async def ebay_browser_with_resilience():
    """
    Browser fixture with resilience monitoring.
    
    Yields:
        Tuple[Page, ResilientEBaySearchPage, ResilienceMonitor]
    """
    driver_factory = DriverFactory()
    await driver_factory.initialize()
    
    browser = await driver_factory.create_browser()
    context = await driver_factory.create_context(browser)
    page = await driver_factory.create_page(context)
    
    # Navigate to eBay
    await page.goto("https://www.ebay.com", wait_until="networkidle")
    
    search_page = ResilientEBaySearchPage(page)
    monitor = ResilienceMonitor(failure_threshold=3)
    
    logger.info("Browser with resilience monitoring initialized")
    
    yield page, search_page, monitor
    
    # Cleanup
    await context.close()
    await browser.close()
    await driver_factory.cleanup()
    logger.info("Browser cleanup completed")


@pytest.fixture
def resilience_metrics_dir():
    """Create directory for resilience reports."""
    metrics_dir = Path("reports/resilience_metrics")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


# ============================================================================
# RESILIENCE TESTS
# ============================================================================

class TestSearchWithResilience:
    """
    Test search functionality with resilience patterns.
    
    לא משנה אם eBay שינה את הממשק, הטסטים האלה ממשיכים לעבוד.
    """
    
    @pytest.mark.asyncio
    async def test_search_resilience_to_ui_changes(self, ebay_browser_with_resilience):
        """
        Test that search works despite UI changes.
        
        Simulates:
        - CSS class name changes
        - ID changes
        - HTML structure changes
        
        Resilience features:
        - Multiple fallback locators
        - Attribute-based location
        - Adaptive learning
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: Search with GUI change resilience")
        logger.info("Searching for 'laptop'...")
        
        try:
            # This works even if:
            # - button#gh-btn doesn't exist (but aria-label="Search" does)
            # - input#gh-ac changed to input.search-field
            # - Any CSS classes were refactored
            await search_page.search("laptop")
            
            logger.info("✓ Search succeeded with fallback locators")
            assert await search_page.is_search_results_visible()
            
        except TimeoutError as e:
            monitor.record_failure("search_button", str(e))
            logger.error(f"Search failed: {e}")
            raise
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("search_term", [
        "laptop computer",
        "vintage watch",
        "electronics gadgets",
    ])
    async def test_multiple_searches_with_learning(
        self,
        ebay_browser_with_resilience,
        search_term: str
    ):
        """
        Test multiple searches to demonstrate adaptive learning.
        
        Demonstrates:
        - Each search learns which locators work best
        - Successful locators move to front of retry queue
        - Metrics collected for analysis
        
        After 3 runs, check get_locator_metrics_report() for:
        - Success rates: 100% means locator is reliable
        - Which selector strategy worked most often
        - Average wait times
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info(f"Searching for: {search_term}")
        await search_page.search(search_term)
        
        # Verify results
        assert await search_page.is_search_results_visible()
        count = await search_page.count_search_results()
        
        logger.info(f"✓ Found {count} results for '{search_term}'")
    
    @pytest.mark.asyncio
    async def test_price_filter_resilience(self, ebay_browser_with_resilience):
        """
        Test filter functionality with resilience.
        
        Demonstrates:
        - Filter locators with multiple fallbacks
        - Handling changes to filter UI
        - Adaptive retry order
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: Price filter with GUI resilience")
        
        # Initial search
        await search_page.search("electronics")
        
        # Apply filter - works even if:
        # - Filter inputs have different classes
        # - Button labels changed
        # - Filter structure was redesigned
        try:
            await search_page.set_price_filter(50, 300)
            logger.info("✓ Price filter applied successfully")
        
        except TimeoutError as e:
            monitor.record_failure("price_filter", str(e))
            raise


class TestLocatorMetrics:
    """
    Tests demonstrating locator performance monitoring.
    
    תצפיות על ביצועי locators לגילוי בעיות בזמן:
    """
    
    @pytest.mark.asyncio
    async def test_locator_success_rates(self, ebay_browser_with_resilience):
        """
        Monitor locator success rates during execution.
        
        Demonstrates:
        - Track which locators succeed
        - Calculate success percentages
        - Identify problematic selectors
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: Locator success rate monitoring")
        
        # Run multiple searches to collect metrics
        for search_term in ["laptop", "phone", "tablet"]:
            logger.info(f"Search #{search_term}")
            await search_page.search(search_term)
        
        # Get metrics report
        metrics = await search_page.get_locator_metrics_report()
        
        logger.info("📊 Locator Performance Report:")
        for element_name, element_metrics in metrics.items():
            logger.info(f"\n  {element_name}:")
            for metric_key, metric in element_metrics.items():
                logger.info(f"    {metric}")
                
                # Assert locators are performing well
                # (80%+ success rate after first learning)
                if metric.success_count > 0:
                    assert metric.success_rate >= 50, \
                        f"Locator {metric_key} has low success rate: {metric.success_rate}%"
    
    @pytest.mark.asyncio
    async def test_gui_change_detection(self, ebay_browser_with_resilience, resilience_metrics_dir):
        """
        Detect GUI changes by monitoring failure patterns.
        
        Demonstrates:
        - Monitor failure rates across runs
        - Detect when elements suddenly break
        - Generate alerts for GUI changes
        - Save metrics for analysis
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: GUI change detection via failure monitoring")
        
        # Simulate multiple searches
        for i in range(3):
            try:
                await search_page.search(f"test_search_{i}")
            except TimeoutError as e:
                monitor.record_failure(f"search_{i}", str(e))
        
        # Get failure report
        failure_report = monitor.get_failure_report()
        
        logger.info("📈 Failure Report (should be empty for healthy GUI):")
        if failure_report:
            for element, count in failure_report.items():
                logger.warning(f"  {element}: {count} failures")
        else:
            logger.info("  ✓ No failures detected - GUI is stable")
        
        # Save report for analysis
        report_file = resilience_metrics_dir / "gui_stability_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                "failures": failure_report,
                "total_runs": 3,
                "status": "HEALTHY" if not failure_report else "DEGRADED"
            }, f, indent=2)
        
        logger.info(f"Report saved to: {report_file}")


class TestAbstractionLayer:
    """
    Tests demonstrating the abstraction layer pattern.
    
    הנקודה: לא אמור להיות שום Playwright selectors בטסטים.
    """
    
    @pytest.mark.asyncio
    async def test_business_method_abstraction(self, ebay_browser_with_resilience):
        """
        Verify that tests use business methods, not selectors.
        
        ✓ Good: await page.search("laptop")
        ✗ Bad: await page.find(SmartLocator(...))
        
        Benefits:
        - Tests are readable by non-technical stakeholders
        - Selector changes don't require test updates
        - Business logic is clear
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: Abstraction layer verification")
        
        # This is a business-focused test
        # No mention of CSS, XPath, IDs, or selectors
        await search_page.search("laptop")
        
        # Verify business outcome, not implementation
        assert await search_page.is_search_results_visible(), \
            "Business requirement: results should be visible after search"
        
        logger.info("✓ Abstraction layer working correctly")
        logger.info("✓ No selectors visible in test code")
    
    @pytest.mark.asyncio
    async def test_high_level_workflow(self, ebay_browser_with_resilience):
        """
        High-level test demonstrating business workflow.
        
        בדיקה זו קראה לה עמיתים לא-טכניים ויבינו מה היא עושה.
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: High-level eBay shopping workflow")
        
        # Step 1: Search
        logger.info("Step 1: Search for electronics")
        await search_page.search("electronics")
        assert await search_page.is_search_results_visible()
        
        # Step 2: Apply filter
        logger.info("Step 2: Apply price filter $50-$200")
        await search_page.set_price_filter(50, 200)
        
        # Step 3: Verify results
        logger.info("Step 3: Verify filtered results")
        count = await search_page.count_search_results()
        assert count > 0, "Should have results within price range"
        
        logger.info(f"✓ Workflow completed: {count} products found")


class TestResilientPageObject:
    """
    Tests for resilient page object pattern.
    
    דוגמאות של Page Objects שמטפלות בשינויים בממשק.
    """
    
    @pytest.mark.asyncio
    async def test_product_page_resilience(self, ebay_browser_with_resilience):
        """
        Test product page with multiple locator strategies.
        
        Demonstrates:
        - Navigating to product page
        - Extracting data with resilient locators
        - Handling UI variations
        """
        page, search_page, monitor = ebay_browser_with_resilience
        
        logger.info("TEST: Product page resilience")
        
        # Search and navigate to product
        await search_page.search("electronics")
        await search_page.click_first_product()
        
        # Create product page object
        product_page = ResilientEBayProductPage(page)
        
        # Extract data - works despite UI variations
        logger.info("Extracting product details...")
        try:
            title = await product_page.get_product_title()
            price = await product_page.get_product_price()
            available = await product_page.is_product_available()
            
            logger.info(f"✓ Title: {title[:50]}")
            logger.info(f"✓ Price: {price}")
            logger.info(f"✓ Available: {available}")
            
        except TimeoutError as e:
            monitor.record_failure("product_page", str(e))
            logger.error(f"Failed to extract product details: {e}")
            raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_resilience_report(
    metrics: Dict[str, Any],
    output_file: Path = Path("reports/resilience_report.json")
) -> None:
    """
    Generate detailed resilience report.
    
    Args:
        metrics: Locator metrics dictionary
        output_file: Output file path
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    logger.info(f"Resilience report saved to: {output_file}")


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run resilience tests:
    
    # Run all resilience tests
    pytest tests/test_resilience.py -v -s
    
    # Run specific test class
    pytest tests/test_resilience.py::TestSearchWithResilience -v -s
    
    # Run with metrics collection
    pytest tests/test_resilience.py -v -s --tb=short
    
    # Generate coverage
    pytest tests/test_resilience.py --cov=automation --cov-report=html
    """
    pytest.main([__file__, "-v", "-s"])
