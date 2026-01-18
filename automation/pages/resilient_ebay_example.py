"""
Enhanced eBay Page Examples with Resilience Patterns
=====================================================

דוגמאות של Page Objects עם התמודדות מתקדמת עם GUI changes.

Demonstrates:
1. SmartLocator with multiple fallback strategies
2. Attribute-based locators (data-testid, aria-label)
3. Adaptive locator ordering
4. Resilience patterns

עיקרון: כל שינוי בממשק לא אמור לשבור את הטסטים.
"""

from typing import Optional
from playwright.async_api import Page

from automation.core.base_page import BasePage
from automation.core.locator import SmartLocator, Locator, LocatorType, css_locator, xpath_locator, text_locator
from automation.core.resilience import (
    create_resilient_locator,
    create_attribute_based_resilient_locator,
    AdaptiveSmartLocator,
    AttributeBasedLocator,
)
from automation.core.logger import get_logger

logger = get_logger(__name__)


class ResilientEBaySearchPage(BasePage):
    """
    Enhanced eBay Search Page with Resilience Patterns.
    
    Handles GUI changes gracefully through:
    - Multiple fallback locators
    - Attribute-based location
    - Adaptive locator ordering
    - Smart error handling
    """
    
    # ========================================================================
    # LOCATORS WITH MULTIPLE FALLBACK STRATEGIES
    # ========================================================================
    
    # Strategy 1: Attribute-based (most stable)
    # data-testid אם קיים - לא משתנה עם CSS changes
    SEARCH_INPUT = create_attribute_based_resilient_locator(
        data_testid="gh-ac",  # eBay's search input
        aria_label="Search for anything",
        css_fallback="input#gh-ac",
        xpath_fallback="//input[@id='gh-ac']",
        description="eBay search input field"
    )
    
    # Strategy 2: Traditional multi-locator with fallbacks
    # CSS (fast) → XPath (flexible) → Text (reliable)
    SEARCH_BUTTON = create_resilient_locator(
        primary_css="button#gh-btn",
        xpath_fallback="//button[@id='gh-btn']",
        text_fallback="Search",
        description="eBay search button"
    )
    
    # Strategy 3: Rich SmartLocator with many fallbacks
    FIRST_PRODUCT_LINK = SmartLocator(
        Locator(LocatorType.CSS, "a.s-item-card__link", "First product CSS"),
        Locator(LocatorType.XPATH, "//a[contains(@class, 's-item-card') and contains(@class, '__link')]", "First product XPath"),
        Locator(LocatorType.CSS, "div.s-item a:first-child", "First link in first item"),
        Locator(LocatorType.TEXT, r"text=/^[\w\s]+$/", "First visible text link"),  # Fallback
    )
    
    # Product details with attribute-based resilience
    PRODUCT_TITLE = create_attribute_based_resilient_locator(
        css_fallback="h2.s-item__title",
        xpath_fallback="//h2[contains(@class, 's-item__title')]",
        description="Product title"
    )
    
    PRODUCT_PRICE = SmartLocator(
        Locator(LocatorType.CSS, ".s-item__price", "Price CSS"),
        Locator(LocatorType.XPATH, "//span[contains(@class, 's-item__price')]", "Price XPath"),
        Locator(LocatorType.XPATH, "//span[contains(text(), '$')]", "Price by currency symbol"),
    )
    
    # Filters with attribute-based approach
    FILTER_PRICE_MIN = create_attribute_based_resilient_locator(
        data_testid="price-min",
        css_fallback="input[name='_nkw-min-price']",
        xpath_fallback="//input[contains(@placeholder, 'Min')]",
        description="Minimum price filter"
    )
    
    FILTER_PRICE_MAX = create_attribute_based_resilient_locator(
        data_testid="price-max",
        css_fallback="input[name='_nkw-max-price']",
        xpath_fallback="//input[contains(@placeholder, 'Max')]",
        description="Maximum price filter"
    )
    
    APPLY_FILTERS_BUTTON = SmartLocator(
        Locator(LocatorType.CSS, "button[aria-label='Apply']", "Apply button by aria-label"),
        Locator(LocatorType.CSS, ".btn--primary", "Primary button"),
        Locator(LocatorType.TEXT, "text=Apply", "Apply text"),
        Locator(LocatorType.XPATH, "//button[contains(@class, 'apply')]", "Apply by class"),
    )
    
    # Results container (to verify search completion)
    SEARCH_RESULTS_CONTAINER = SmartLocator(
        Locator(LocatorType.CSS, "div.s-result-list", "Results list container"),
        Locator(LocatorType.XPATH, "//div[contains(@class, 'results')]", "Generic results container"),
        Locator(LocatorType.CSS, "main", "Main content area"),
    )
    
    # ========================================================================
    # ADAPTIVE LOCATOR TRACKING
    # ========================================================================
    
    def __init__(self, page: Page, timeout_sec: float = 10):
        """
        Args:
            page: Playwright Page
            timeout_sec: Default timeout
        """
        super().__init__(page, timeout_sec)
        
        # Initialize adaptive locators for learning
        self.adaptive_search_input = AdaptiveSmartLocator(self.SEARCH_INPUT)
        self.adaptive_search_button = AdaptiveSmartLocator(self.SEARCH_BUTTON)
        self.adaptive_product_link = AdaptiveSmartLocator(self.FIRST_PRODUCT_LINK)
        
        logger.info("ResilientEBaySearchPage initialized with adaptive locators")
    
    # ========================================================================
    # BUSINESS METHODS (High-level, no Playwright details)
    # ========================================================================
    
    async def search(self, query: str) -> None:
        """
        Perform search with resilience.
        
        Args:
            query: Search term
        """
        logger.info(f"🔍 Searching for: {query}")
        
        # Type search query
        await self.type(self.SEARCH_INPUT, query)
        
        # Click search button (with human-like delay)
        await self.click(self.SEARCH_BUTTON)
        
        # Wait for results to load
        await self.wait_for_navigation()
        logger.info("✓ Search completed")
    
    async def get_first_product_title(self) -> str:
        """
        Get title of first product in results.
        
        Returns:
            Product title
        
        Resilience: Multiple locator strategies ensure title extraction
        even if UI slightly changes.
        """
        logger.debug("Retrieving first product title...")
        
        # First, navigate to product to see full details
        await self.click(self.FIRST_PRODUCT_LINK)
        await self.wait_for_navigation()
        
        # Now get title from product page
        title = await self.get_text(self.PRODUCT_TITLE)
        logger.info(f"Product title: {title[:50]}...")
        
        return title
    
    async def get_first_product_price(self) -> str:
        """
        Get price of first product.
        
        Returns:
            Price string (e.g., "$99.99")
        
        Resilience: Multiple price selectors handle different UI variations.
        """
        logger.debug("Retrieving product price...")
        
        price = await self.get_text(self.PRODUCT_PRICE)
        logger.info(f"Product price: {price}")
        
        return price
    
    async def click_first_product(self) -> None:
        """Click on first product in search results."""
        logger.info("Clicking first product...")
        await self.click(self.FIRST_PRODUCT_LINK)
        await self.wait_for_navigation()
        logger.info("✓ Product page loaded")
    
    async def set_price_filter(self, min_price: float, max_price: float) -> None:
        """
        Apply price range filter.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
        
        Resilience: Adaptive locators learn best selectors for next time.
        """
        logger.info(f"🏷️  Setting price filter: ${min_price} - ${max_price}")
        
        # Fill price fields
        await self.fill(self.FILTER_PRICE_MIN, str(int(min_price)))
        await self.fill(self.FILTER_PRICE_MAX, str(int(max_price)))
        
        # Apply filters
        await self.click(self.APPLY_FILTERS_BUTTON)
        await self.wait_for_navigation()
        
        logger.info("✓ Price filter applied")
    
    async def is_search_results_visible(self) -> bool:
        """
        Check if search results are displayed.
        
        Returns:
            True if results visible, False otherwise
        
        Resilience: Checks multiple possible result containers.
        """
        is_visible = await self.is_visible(self.SEARCH_RESULTS_CONTAINER)
        logger.debug(f"Search results visible: {is_visible}")
        return is_visible
    
    async def count_search_results(self) -> int:
        """
        Count number of products in search results.
        
        Returns:
            Number of results
        """
        # Count first product links (most reliable indicator)
        count = await self.count_elements(self.FIRST_PRODUCT_LINK)
        logger.info(f"Found {count} search results")
        return count
    
    # ========================================================================
    # ADAPTIVE LEARNING (Optional - for advanced usage)
    # ========================================================================
    
    async def get_locator_metrics_report(self) -> dict:
        """
        Get detailed report of locator performance.
        
        Shows which locators work best after multiple runs.
        
        Returns:
            Dictionary of locator metrics
        """
        report = {
            "search_input": self.adaptive_search_input.get_metrics_report(),
            "search_button": self.adaptive_search_button.get_metrics_report(),
            "product_link": self.adaptive_product_link.get_metrics_report(),
        }
        
        logger.info("📊 Locator Performance Report")
        for element, metrics in report.items():
            logger.info(f"  {element}:")
            for key, metric in metrics.items():
                logger.info(f"    {metric}")
        
        return report
    
    def reset_locator_metrics(self) -> None:
        """Reset all locator learning metrics."""
        self.adaptive_search_input.reset_metrics()
        self.adaptive_search_button.reset_metrics()
        self.adaptive_product_link.reset_metrics()
        logger.info("Locator metrics reset")


class ResilientEBayProductPage(BasePage):
    """
    Enhanced eBay Product Page with Resilience.
    
    Demonstrates resilience for product details page.
    """
    
    # Use attribute-based locators for stability
    PRODUCT_TITLE = create_attribute_based_resilient_locator(
        aria_label="Product name",
        css_fallback="h1.it-title",
        xpath_fallback="//h1[contains(@class, 'title')]",
        description="Product title"
    )
    
    CURRENT_PRICE = SmartLocator(
        Locator(LocatorType.CSS, ".vi-VR-cvipPrice", "eBay price span"),
        Locator(LocatorType.XPATH, "//span[contains(@id, 'prcIsum')]", "Price by ID"),
        Locator(LocatorType.CSS, "span.vi-VR-cvipPrice span:first-child", "Price currency"),
    )
    
    ADD_TO_CART_BUTTON = create_attribute_based_resilient_locator(
        aria_label="Add to basket",
        data_testid="atc-button",
        css_fallback="a#atcBtn",
        xpath_fallback="//a[@id='atcBtn']",
        description="Add to cart button"
    )
    
    QUANTITY_INPUT = SmartLocator(
        Locator(LocatorType.CSS, "input#qtySubTxt", "Quantity input"),
        Locator(LocatorType.XPATH, "//input[@id='qtySubTxt']", "Qty by ID"),
        Locator(LocatorType.CSS, "input[name='quantity']", "Qty by name"),
    )
    
    PRODUCT_AVAILABILITY = SmartLocator(
        Locator(LocatorType.CSS, ".vi-acc-del-range", "Availability text"),
        Locator(LocatorType.XPATH, "//*[contains(text(), 'In stock')]", "In stock text"),
        Locator(LocatorType.CSS, ".vi-VR-cvipAvail", "Availability span"),
    )
    
    async def get_product_title(self) -> str:
        """Get product title."""
        return await self.get_text(self.PRODUCT_TITLE)
    
    async def get_product_price(self) -> str:
        """Get current price."""
        return await self.get_text(self.CURRENT_PRICE)
    
    async def add_to_cart(self, quantity: int = 1) -> None:
        """
        Add product to cart.
        
        Args:
            quantity: Number of items
        """
        logger.info(f"Adding {quantity} item(s) to cart")
        
        if quantity > 1:
            await self.fill(self.QUANTITY_INPUT, str(quantity))
        
        await self.click(self.ADD_TO_CART_BUTTON)
        logger.info("✓ Added to cart")
    
    async def is_product_available(self) -> bool:
        """Check if product is in stock."""
        return await self.is_visible(self.PRODUCT_AVAILABILITY)


# ============================================================================
# BEST PRACTICES DEMONSTRATED
# ============================================================================

"""
🎯 Resilience Patterns Implemented:

1. MULTI-LEVEL FALLBACK LOCATORS
   ✓ Primary: data-testid (most stable, no CSS changes affect it)
   ✓ Secondary: aria-label (accessibility-based, semantic)
   ✓ Tertiary: CSS (fast but fragile)
   ✓ Fallback: XPath (flexible, last resort)
   
   Why: If one selector breaks due to UI redesign, others still work.

2. ATTRIBUTE-BASED LOCATORS (Recommended)
   ✓ [data-testid="gh-ac"] - ideal for developers to add
   ✓ [aria-label="Search"] - accessibility-first approach
   ✓ [name="search"] - form attribute stability
   
   Why: These don't break when CSS classes change.

3. ADAPTIVE LOCATOR LEARNING
   ✓ Track success/failure rate of each locator
   ✓ Reorder locators to try successful ones first next time
   ✓ Monitor trends to detect GUI changes
   
   Why: Learn what works and optimize retry order.

4. BUSINESS-FOCUSED METHODS
   ✓ search() - high-level business action
   ✓ get_price() - extract data, not implementation details
   ✓ All locators hidden in Page Object
   
   Why: Tests are maintainable and readable.

5. COMPREHENSIVE FALLBACK CHAIN
   ✓ Each UI element has 3-4 different selector strategies
   ✓ Tries them in order until one succeeds
   ✓ Logs which strategy worked (for reporting)
   
   Why: Handles CSS rewrites, ID changes, HTML restructuring.

דוגמה שימוש:
    page = ResilientEBaySearchPage(playwright_page)
    await page.search("laptop")
    title = await page.get_first_product_title()  # Works even if UI changed!
    await page.set_price_filter(100, 500)
    metrics = await page.get_locator_metrics_report()  # See what worked
"""
