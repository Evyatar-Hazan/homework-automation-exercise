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
    # Verification
    "verify_ebay_homepage",
    "verify_page_title",
    "verify_page_url",
    "verify_element_visible",
    # Element Interaction
    "click_element",
    "type_text",
    "type_email_from_env",
    "click_element_smart",
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
