"""
Automation Test Store Search Page Object
=========================================

Page Object עם SmartLocator fallbacks לדף החיפוש של Automation Test Store.

כל אלמנט מוגדר עם 2-3 לוקייטורים חלופיים:
- Primary locator (הדיוק הגבוה ביותר)
- Fallback 1 (חלופי)
- Fallback 2 (אם קיים)

בזמן ריצה, SmartLocatorFinder ינסה כל אחד בתורו.
"""

from typing import Optional, List, Tuple

from automation.utils.smart_locator_finder import SmartLocatorFinder


class AutomationTestStoreSearchLocators:
    """
    הגדרת כל הלוקייטורים לדף החיפוש של Automation Test Store.
    
    פורמט: [(by_type, selector), (by_type, selector), ...]
    """
    
    # Search Input Field
    SEARCH_INPUT = [
        ("id", "filter_keyword"),
        ("name", "filter_keyword"),
        ("xpath", "//input[@id='filter_keyword']"),
        ("css", "input[id='filter_keyword']"),
    ]
    
    # Search Button / Submit
    SEARCH_BUTTON = [
        ("xpath", "//button[contains(@class, 'btn') and contains(text(), 'Search')]"),
        ("css", "button.btn-primary"),
        ("xpath", "//form[contains(@class, 'search')]//button[1]"),
    ]
    
    # Price Filter - Minimum Price Input
    PRICE_MIN_INPUT = [
        ("name", "filter_price_min"),
        ("id", "filter_price_min"),
        ("xpath", "//input[@name='filter_price_min']"),
        ("css", "input[name='filter_price_min']"),
    ]
    
    # Price Filter - Maximum Price Input
    PRICE_MAX_INPUT = [
        ("name", "filter_price_max"),
        ("id", "filter_price_max"),
        ("xpath", "//input[@name='filter_price_max']"),
        ("css", "input[name='filter_price_max']"),
    ]
    
    # Product Items Container
    PRODUCT_ITEMS_CONTAINER = [
        ("xpath", "//div[@class='thumbnail']"),
        ("css", ".thumbnail"),
        ("xpath", "//div[contains(@class, 'productcartitem')]"),
    ]
    
    # Product Link
    PRODUCT_LINK = [
        ("xpath", ".//a[@href and contains(@href, 'product_id=')]"),
        ("css", "a[href*='product_id=']"),
        ("xpath", ".//div[@class='shortlinks']//a[@class='details']"),
    ]
    
    # Product Price
    PRODUCT_PRICE = [
        ("xpath", ".//div[@class='price']//div[@class='oneprice']"),
        ("css", ".price .oneprice"),
        ("xpath", ".//div[contains(@class, 'price')]"),
    ]
    
    # Next Page Button / Link
    NEXT_PAGE_BUTTON = [
        ("xpath", "//div[@class='pull-right']//ul[@class='pagination']//a[contains(text(), '>')]"),
        ("xpath", "//ul[@class='pagination']//a[text()='>']"),
        ("xpath", "//a[contains(@href, 'page=') and contains(., '>')]"),
        ("xpath", "//a[contains(@title, 'Next')]"),
    ]
    
    # Previous Page Button / Link
    PREV_PAGE_BUTTON = [
        ("xpath", "//a[contains(@title, 'Previous')]"),
        ("css", "a[title*='Previous']"),
        ("xpath", "//a[contains(text(), 'Previous')]"),
    ]
    
    # Pagination Container
    PAGINATION_CONTAINER = [
        ("xpath", "//div[@class='pagination']"),
        ("css", ".pagination"),
        ("xpath", "//div[contains(@class, 'page')]"),
    ]
    
    # No Results Message
    NO_RESULTS_MESSAGE = [
        ("xpath", "//div[contains(text(), 'There is no product that matches')]"),
        ("css", ".norecord"),
        ("xpath", "//p[contains(text(), 'No products')]"),
    ]
    
    # Sort Dropdown
    SORT_DROPDOWN = [
        ("name", "sort"),
        ("id", "sort"),
        ("xpath", "//select[@name='sort']"),
        ("css", "select[name='sort']"),
    ]
    
    # Filter Apply Button (if exists)
    FILTER_APPLY_BUTTON = [
        ("xpath", "//button[contains(text(), 'Apply')]"),
        ("css", "button.apply"),
        ("xpath", "//input[@type='submit' and contains(@value, 'Filter')]"),
    ]
