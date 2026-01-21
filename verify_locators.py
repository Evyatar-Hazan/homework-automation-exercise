#!/usr/bin/env python3
"""
Quick verification script to test the locator centralization.
Tests that all locators are properly structured for SmartLocatorFinder.
"""

from automation.pages.automation_test_store_cart_page import (
    AutomationTestStoreCartLocators,
    AutomationTestStoreCommonLocators
)
from automation.pages.automation_test_store_login_page import AutomationTestStoreLoginLocators
from automation.pages.automation_test_store_search_page import AutomationTestStoreSearchLocators


def validate_locator_structure(locator_list, name):
    """Validate that a locator follows the expected structure."""
    if not isinstance(locator_list, list):
        print(f"❌ {name}: Not a list")
        return False
    
    if len(locator_list) < 2:
        print(f"⚠️  {name}: Less than 2 fallback locators (only {len(locator_list)})")
    
    for idx, locator in enumerate(locator_list, 1):
        if not isinstance(locator, tuple) or len(locator) != 2:
            print(f"❌ {name}[{idx}]: Not a tuple of (by_type, selector)")
            return False
        
        by_type, selector = locator
        if not isinstance(by_type, str) or not isinstance(selector, str):
            print(f"❌ {name}[{idx}]: by_type or selector not strings")
            return False
    
    print(f"✅ {name}: {len(locator_list)} locators")
    return True


def main():
    print("=" * 80)
    print("🔍 LOCATOR CENTRALIZATION VALIDATION")
    print("=" * 80)
    print()
    
    all_valid = True
    
    # Test Cart Locators
    print("📦 AutomationTestStoreCartLocators:")
    print("-" * 80)
    for attr_name in dir(AutomationTestStoreCartLocators):
        if attr_name.isupper():  # Constants are uppercase
            locators = getattr(AutomationTestStoreCartLocators, attr_name)
            if not validate_locator_structure(locators, f"  {attr_name}"):
                all_valid = False
    print()
    
    # Test Login Locators
    print("🔐 AutomationTestStoreLoginLocators:")
    print("-" * 80)
    for attr_name in dir(AutomationTestStoreLoginLocators):
        if attr_name.isupper():
            locators = getattr(AutomationTestStoreLoginLocators, attr_name)
            if not validate_locator_structure(locators, f"  {attr_name}"):
                all_valid = False
    print()
    
    # Test Search Locators
    print("🔎 AutomationTestStoreSearchLocators:")
    print("-" * 80)
    for attr_name in dir(AutomationTestStoreSearchLocators):
        if attr_name.isupper():
            locators = getattr(AutomationTestStoreSearchLocators, attr_name)
            if not validate_locator_structure(locators, f"  {attr_name}"):
                all_valid = False
    print()
    
    # Test Common Locators
    print("🌐 AutomationTestStoreCommonLocators:")
    print("-" * 80)
    for attr_name in dir(AutomationTestStoreCommonLocators):
        if attr_name.isupper():
            locators = getattr(AutomationTestStoreCommonLocators, attr_name)
            if not validate_locator_structure(locators, f"  {attr_name}"):
                all_valid = False
    print()
    
    print("=" * 80)
    if all_valid:
        print("✅ SUCCESS: All locators are properly structured!")
        print("✅ All locators follow the pattern: [(by_type, selector), ...]")
        print("✅ SmartLocatorFinder will iterate through fallbacks correctly")
    else:
        print("❌ FAILED: Some locators have structural issues")
        return 1
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())
