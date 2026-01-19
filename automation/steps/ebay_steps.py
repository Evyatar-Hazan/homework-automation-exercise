"""
Automation Steps Module
=======================

Re-exports all step functions for easy importing.
"""

from automation.steps import (
    # Navigation
    navigate_to_ebay,
    # Verification
    verify_ebay_homepage,
    verify_page_title,
    verify_page_url,
    # Screenshots
    take_screenshot,
    # Element Interaction
    click_element,
    type_text,
    # Page Inspection
    get_page_title,
    get_current_url,
    get_page_source,
    # Wait
    wait_for_element_to_appear,
    wait_for_element_clickable,
    # Utility
    refresh_page,
    human_delay,
    test_success_message,
)

__all__ = [
    # Navigation
    'navigate_to_ebay',
    # Verification
    'verify_ebay_homepage',
    'verify_page_title',
    'verify_page_url',
    # Screenshots
    'take_screenshot',
    # Element Interaction
    'click_element',
    'type_text',
    # Page Inspection
    'get_page_title',
    'get_current_url',
    'get_page_source',
    # Wait
    'wait_for_element_to_appear',
    'wait_for_element_clickable',
    # Utility
    'refresh_page',
    'human_delay',
    'test_success_message',
]
