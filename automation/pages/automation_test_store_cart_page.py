"""
Automation Test Store Cart & Common Page Locators
===================================================

Page Object with SmartLocator fallbacks for cart page and common elements of Automation Test Store.

Each element is defined with 2-3 alternative locators:
- Primary locator (highest accuracy)
- Fallback 1 (alternative)
- Fallback 2 (if exists)

At runtime, SmartLocatorFinder will try each one in order.
"""

from typing import List, Tuple


class AutomationTestStoreCartLocators:
    """
    Defines all locators for the cart page and shopping operations in Automation Test Store.
    
    Format: [(by_type, selector), (by_type, selector), ...]
    """
    
    # USERNAME/EMAIL INPUT (Login form)
    USERNAME_INPUT = [
        ("id", "loginFrm_loginname"),
        ("name", "loginname"),
        ("xpath", "//input[@id='loginFrm_loginname']"),
        ("xpath", "//input[@name='loginname']"),
    ]
    
    # PASSWORD INPUT (Login form)
    PASSWORD_INPUT = [
        ("id", "loginFrm_password"),
        ("name", "password"),
        ("xpath", "//input[@id='loginFrm_password']"),
        ("xpath", "//input[@name='password']"),
    ]
    
    # LOGIN SUBMIT BUTTON
    LOGIN_SUBMIT_BUTTON = [
        ("xpath", "//button[@type='submit' and @title='Login']"),
        ("css", "button[type='submit'][title='Login']"),
        ("xpath", "//button[@type='submit' and contains(@class, 'btn')]"),
        ("xpath", "//button[contains(text(), 'Login')]"),
    ]
    
    # WELCOME MESSAGE (after successful login)
    WELCOME_MESSAGE = [
        ("xpath", "//div[contains(text(), 'Welcome back')]"),
        ("css", "div.menu_text"),
        ("xpath", "//span[contains(text(), 'Welcome back')]"),
        ("xpath", "//*[contains(text(), 'Welcome back')]"),
    ]
    
    # SELECT ELEMENTS (general dropdown/select)
    SELECT_ELEMENTS = [
        ("tag", "select"),
        ("xpath", "//select"),
        ("css", "select"),
    ]
    
    # QUANTITY INPUT (product page)
    QUANTITY_INPUT = [
        ("css", "input[name*='quantity']"),
        ("css", "input[id*='quantity']"),
        ("xpath", "//input[contains(@name, 'quantity')]"),
        ("xpath", "//input[contains(@id, 'quantity')]"),
    ]
    
    # RADIO BUTTONS (general radio options)
    RADIO_BUTTONS = [
        ("css", "input[type='radio']"),
        ("xpath", "//input[@type='radio']"),
    ]
    
    # ADD TO CART BUTTON
    ADD_TO_CART_BUTTON = [
        ("css", "a.cart"),
        ("xpath", "//a[@class='cart']"),
        ("xpath", "//a[contains(@class, 'cart')]//i[contains(@class, 'fa-cart-plus')]//parent::a"),
        ("xpath", "//a[contains(@onclick, 'form')]"),
        ("xpath", "//a[contains(., 'Add to Cart')]"),
        ("xpath", "//*[.//i[contains(@class, 'fa-cart-plus')]]"),
    ]
    
    # CART TOTAL (on cart page)
    CART_TOTAL = [
        ("xpath", "//span[contains(@class, 'totalamout')]"),
        ("xpath", "//td[contains(., 'Total:')]/following-sibling::td//span"),
        ("xpath", "//tr[contains(., 'Total:')]//td[last()]//span"),
        ("xpath", "//span[@class='bold totalamout']"),
        ("css", "span.totalamout"),
        ("css", "span.bold.totalamout"),
    ]
    
    # CART PAGE ITEMS (product rows in cart)
    CART_ITEMS = [
        ("xpath", "//table[@class='table table-striped table-bordered']//tbody//tr"),
        ("css", "table.table-striped tbody tr"),
        ("xpath", "//div[@class='cart']//table//tbody//tr"),
    ]
    
    # CONTINUE SHOPPING BUTTON
    CONTINUE_SHOPPING = [
        ("xpath", "//a[contains(text(), 'Continue Shopping')]"),
        ("css", "a[title='Continue Shopping']"),
        ("xpath", "//a[@title='Continue Shopping']"),
    ]
    
    # CHECKOUT BUTTON
    CHECKOUT_BUTTON = [
        ("xpath", "//a[@id='cart_checkout1']"),
        ("id", "cart_checkout1"),
        ("xpath", "//a[contains(text(), 'Checkout')]"),
        ("css", "a#cart_checkout1"),
    ]


class AutomationTestStoreCommonLocators:
    """
    Common locators used across the entire site.
    """
    
    # HOME/LOGO LINK
    HOME_LOGO = [
        ("xpath", "//img[@alt='Automation Test Store']"),
        ("xpath", "//a[@class='logo']//img"),
        ("css", "a.logo img"),
    ]
    
    # SEARCH BOX (header)
    SEARCH_INPUT_HEADER = [
        ("id", "filter_keyword"),
        ("name", "filter_keyword"),
        ("xpath", "//input[@id='filter_keyword']"),
        ("css", "input#filter_keyword"),
    ]
    
    # CART ICON (header - to view cart)
    CART_ICON_HEADER = [
        ("xpath", "//a[@href='#' and contains(@class, 'top') and .//i[contains(@class, 'fa-shopping-cart')]]"),
        ("css", "a.top i.fa-shopping-cart"),
        ("xpath", "//i[contains(@class, 'fa-shopping-cart')]//parent::a"),
    ]
    
    # ACCOUNT DROPDOWN (header)
    ACCOUNT_DROPDOWN = [
        ("xpath", "//a[@class='top menu_account']"),
        ("css", "a.top.menu_account"),
        ("xpath", "//ul[@id='customer_menu_top']"),
    ]
