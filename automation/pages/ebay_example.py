"""
Example Page Object - eBay Search Page
======================================

This is an example Page Object to demonstrate the pattern.

Key Points:
- Inherits from BasePage (gets all Playwright interaction methods)
- Defines UI elements as SmartLocators (with fallbacks)
- Methods are high-level business actions
- NO direct Playwright usage
- NO hardcoded selectors outside this file
"""

from automation.core import BasePage, SmartLocator, Locator, LocatorType


class eBaySearchPage(BasePage):
    """
    eBay search/results page abstraction.
    
    Demonstrates how to structure Page Objects:
    - UI elements defined as class constants
    - Multiple fallback selectors per element
    - High-level business methods
    """
    
    # =========================================================================
    # UI ELEMENTS - Define all selectors here with fallbacks
    # =========================================================================
    
    SEARCH_INPUT = SmartLocator(
        Locator(LocatorType.CSS, "input#gh-ac", "eBay search input box"),
        Locator(LocatorType.XPATH, "//input[@id='gh-ac']", "Search input by XPath"),
        Locator(LocatorType.CSS, "input[placeholder*='Search']", "Search by placeholder"),
    )
    
    SEARCH_BUTTON = SmartLocator(
        Locator(LocatorType.CSS, "button#gh-btn", "Search button"),
        Locator(LocatorType.XPATH, "//button[@id='gh-btn']", "Search button by XPath"),
        Locator(LocatorType.XPATH, "//button[contains(text(), 'Search')]", "Search by text"),
    )
    
    # Results page elements
    FIRST_PRODUCT_LINK = SmartLocator(
        Locator(LocatorType.CSS, ".s-item a", "First search result"),
        Locator(LocatorType.XPATH, "//div[@class='s-item']//a", "Product link by XPath"),
    )
    
    PRODUCT_TITLE = SmartLocator(
        Locator(LocatorType.CSS, ".s-item__title", "Product title"),
        Locator(LocatorType.XPATH, "//h2[@class='s-item__title']", "Title by XPath"),
    )
    
    PRODUCT_PRICE = SmartLocator(
        Locator(LocatorType.CSS, ".s-item__price", "Product price"),
        Locator(LocatorType.XPATH, "//span[contains(@class, 'price')]", "Price by XPath"),
    )
    
    FILTER_PRICE_MIN = SmartLocator(
        Locator(LocatorType.CSS, "input[aria-label*='Minimum']", "Min price filter"),
        Locator(LocatorType.XPATH, "//input[contains(@aria-label, 'Minimum')]", "Min by XPath"),
    )
    
    FILTER_PRICE_MAX = SmartLocator(
        Locator(LocatorType.CSS, "input[aria-label*='Maximum']", "Max price filter"),
        Locator(LocatorType.XPATH, "//input[contains(@aria-label, 'Maximum')]", "Max by XPath"),
    )
    
    APPLY_FILTERS_BUTTON = SmartLocator(
        Locator(LocatorType.CSS, "button[aria-label*='Apply']", "Apply filters button"),
        Locator(LocatorType.XPATH, "//button[contains(@aria-label, 'Apply')]", "Apply by XPath"),
    )
    
    # =========================================================================
    # HIGH-LEVEL BUSINESS METHODS
    # =========================================================================
    
    async def search(self, query: str) -> None:
        """
        Perform eBay search.
        
        High-level business action - doesn't reveal Playwright details.
        
        Args:
            query: Search term (e.g., "vintage laptop")
        """
        await self.type(self.SEARCH_INPUT, query)
        await self.click(self.SEARCH_BUTTON)
        await self.wait_for_navigation()
    
    async def get_first_product_title(self) -> str:
        """Get title of first search result."""
        return await self.get_text(self.PRODUCT_TITLE)
    
    async def get_first_product_price(self) -> str:
        """Get price of first search result."""
        return await self.get_text(self.PRODUCT_PRICE)
    
    async def click_first_product(self) -> None:
        """Click first search result to open product page."""
        await self.click(self.FIRST_PRODUCT_LINK)
        await self.wait_for_navigation()
    
    async def set_price_filter(self, min_price: float, max_price: float) -> None:
        """
        Set price range filter.
        
        Args:
            min_price: Minimum price (e.g., 50.0)
            max_price: Maximum price (e.g., 200.0)
        """
        await self.fill(self.FILTER_PRICE_MIN, str(min_price))
        await self.fill(self.FILTER_PRICE_MAX, str(max_price))
        await self.click(self.APPLY_FILTERS_BUTTON)
        await self.wait_for_navigation()
    
    async def count_search_results(self) -> int:
        """Count number of products in search results."""
        return await self.count_elements(self.FIRST_PRODUCT_LINK)
    
    async def is_search_results_visible(self) -> bool:
        """Check if search results are displayed."""
        return await self.is_visible(self.FIRST_PRODUCT_LINK, timeout_sec=5)


class eBayProductPage(BasePage):
    """
    eBay product details page.
    
    Example of another Page Object using same infrastructure.
    """
    
    PRODUCT_TITLE = SmartLocator(
        Locator(LocatorType.CSS, "h1.it-title", "Product title"),
        Locator(LocatorType.XPATH, "//h1[contains(@class, 'title')]", "Title by XPath"),
    )
    
    CURRENT_PRICE = SmartLocator(
        Locator(LocatorType.CSS, ".vi-VR-cvipPrice", "Current price"),
        Locator(LocatorType.XPATH, "//span[@id='prcIsum']", "Price by ID"),
    )
    
    ADD_TO_CART_BUTTON = SmartLocator(
        Locator(LocatorType.CSS, "a#atcBtn", "Add to cart button"),
        Locator(LocatorType.XPATH, "//a[@id='atcBtn']", "Add to cart by XPath"),
    )
    
    QUANTITY_INPUT = SmartLocator(
        Locator(LocatorType.CSS, "input#qtyTextBox", "Quantity input"),
    )
    
    async def get_product_title(self) -> str:
        """Get product title."""
        return await self.get_text(self.PRODUCT_TITLE)
    
    async def get_product_price(self) -> str:
        """Get current product price."""
        return await self.get_text(self.CURRENT_PRICE)
    
    async def add_to_cart(self, quantity: int = 1) -> None:
        """
        Add product to cart.
        
        Args:
            quantity: Number of items to add
        """
        if quantity > 1:
            await self.fill(self.QUANTITY_INPUT, str(quantity))
        await self.click(self.ADD_TO_CART_BUTTON)
        await self.wait_for_navigation()
    
    async def is_product_available(self) -> bool:
        """Check if product is available for purchase."""
        return await self.is_enabled(self.ADD_TO_CART_BUTTON)
