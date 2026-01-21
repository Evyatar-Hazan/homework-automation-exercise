"""
Automation Steps
================

צעדים נפרדים וחוזרים להשימוש בהם בבדיקות שונות.

כל פונקציה כאן היא "step" שיכולה להיות בשימוש חוזר בכמה בדיקות שונות.

הצעדים מארגנים לקטגוריות:
  - automation_test_store_steps: צעדים לאתר Automation Test Store
  - verification_steps: אימות וטענות
  - element_steps: אינטראקציה עם אלמנטים
  - utility_steps: כלים ויחידות בעזרה
"""

# Import from category modules
from .automation_test_store_steps import (
    navigate_to_automation_test_store,
    click_login_or_register_link,
    verify_account_login_page,
    enter_username_from_env_ats,
    enter_email_from_env_ats,
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
    perform_automation_test_store_login,
    # Search and Price Filter Functions
    search_items_by_query,
    apply_price_filter,
    extract_product_links_with_prices,
    has_next_page,
    click_next_page,
    search_items_by_name_under_price,
    # Cart Management Functions
    navigate_to_product_page,
    select_product_variants,
    click_add_to_cart_button,
    navigate_back_to_previous_page,
    navigate_to_cart_page,
    get_cart_total,
)

from .verification_steps import (
    verify_page_title,
    verify_page_url,
)

from .utility_steps import (
    take_screenshot,
    get_page_title,
    get_current_url,
    get_page_source,
    wait_for_element_to_appear,
    wait_for_element_clickable,
    refresh_page,
    human_delay,
    log_success_message,
    test_success_message,  # Backward compatibility alias
)

# Export all functions
__all__ = [
    # Navigation
    "navigate_to_automation_test_store",
    # Verification
    "verify_automation_test_store_homepage",
    "verify_account_login_page",
    "verify_page_title",
    "verify_page_url",
    # Element Interaction
    "click_login_or_register_link",
    "enter_username_from_env_ats",
    "enter_email_from_env_ats",
    "enter_password_from_env_ats",
    "click_login_button",
    "verify_login_success",
    "perform_automation_test_store_login",
    # Search and Price Filter
    "search_items_by_query",
    "apply_price_filter",
    "extract_product_links_with_prices",
    "has_next_page",
    "click_next_page",
    "search_items_by_name_under_price",
    # Utility
    "take_screenshot",
    "get_page_title",
    "get_current_url",
    "get_page_source",
    "wait_for_element_to_appear",
    "wait_for_element_clickable",
    "refresh_page",
    "human_delay",
    "log_success_message",
    "test_success_message",  # Backward compatibility alias
]
