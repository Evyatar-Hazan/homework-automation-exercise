"""
eBay Automation Steps
====================

צעדים נפרדים וחוזרים להשימוש בהם בבדיקות שונות.

כל פונקציה כאן היא "step" שיכולה להיות בשימוש חוזר בכמה בדיקות שונות.

הצעדים מארגנים לקטגוריות:
  - navigation_steps: ניווט בדפים
  - verification_steps: אימות וטענות
  - element_steps: אינטראקציה עם אלמנטים
  - utility_steps: כלים ויחידות בעזרה
"""

# Import from category modules
from .navigation_steps import (
    navigate_to_ebay,
)

from .automation_test_store_steps import (
    navigate_to_automation_test_store,
    verify_automation_test_store_homepage,
    click_login_or_register_link,
    verify_account_login_page,
    enter_username_from_env_ats,
    enter_email_from_env_ats,
    enter_password_from_env_ats,
    click_login_button,
    verify_login_success,
)

from .verification_steps import (
    verify_ebay_homepage,
    verify_page_title,
    verify_page_url,
    verify_element_visible,
)

from .element_steps import (
    click_element,
    type_text,
    type_email_from_env,
    click_element_smart,
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
    "navigate_to_ebay",
    "navigate_to_automation_test_store",
    # Verification
    "verify_ebay_homepage",
    "verify_automation_test_store_homepage",
    "verify_account_login_page",
    "verify_page_title",
    "verify_page_url",
    "verify_element_visible",
    # Element Interaction
    "click_element",
    "type_text",
    "type_email_from_env",
    "click_element_smart",
    "click_login_or_register_link",
    "enter_username_from_env_ats",
    "enter_email_from_env_ats",
    "enter_password_from_env_ats",
    "click_login_button",
    "verify_login_success",
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
