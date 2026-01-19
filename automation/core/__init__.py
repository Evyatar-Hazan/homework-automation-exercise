"""
Automation Core Module
======================

ליבת התשתית - כל המרכיבים הבסיסיים לאוטומציה.

Components:
- logger: Unified logging system
- locator: SmartLocator with fallback
- retry: Retry mechanism with exponential backoff
- driver_factory: Browser/Context/Page factory
- base_page: Core interaction layer with Playwright
"""

from automation.core.logger import AutomationLogger, get_logger
from automation.core.locator import SmartLocator, Locator, LocatorType
from automation.core.retry import retry_on_failure, RetryConfig
from automation.core.driver_factory import DriverFactory
from automation.core.base_page import BasePage
from automation.core.base_test import BaseSeleniumTest

__all__ = [
    'AutomationLogger',
    'get_logger',
    'SmartLocator',
    'Locator',
    'LocatorType',
    'retry_on_failure',
    'RetryConfig',
    'DriverFactory',
    'BasePage',
    'BaseSeleniumTest',
]
