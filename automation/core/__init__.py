"""
Automation Core Module
======================

ליבת התשתית - כל המרכיבים הבסיסיים לאוטומציה.

Components:
- logger: Unified logging system
- locator: SmartLocator with fallback
- retry: Retry mechanism with exponential backoff
- driver_factory: Browser/Context/Page factory
- grid_driver_factory: Selenium Grid / Moon remote driver factory
- base_page: Core interaction layer with Playwright
"""

from automation.core.logger import (
    AutomationLogger, 
    get_logger, 
    log_step_with_allure, 
    loggerInfo, 
    loggerAttach, 
    loggerStep
)
from automation.core.logger import (
    step_aware_loggerStep,
    step_aware_loggerInfo,
    step_aware_loggerError,
    step_aware_loggerAttach,
    get_current_step_name,
    is_in_step
)
from automation.core.locator import SmartLocator, Locator, LocatorType
from automation.core.retry import retry_on_failure, RetryConfig
from automation.core.driver_factory import DriverFactory
from automation.core.grid_driver_factory import GridDriverFactory, CapabilitiesManager
from automation.core.base_page import BasePage
from automation.core.base_test import BaseSeleniumTest, TestExecutionTracker
from automation.core.assertions import SmartAssert
from automation.core.env_config import EnvironmentConfig, get_environment_config, reset_environment_config

__all__ = [
    'AutomationLogger',
    'get_logger',
    'log_step_with_allure',
    'loggerAttach',
    'loggerInfo',
    'loggerStep',
    'step_aware_loggerStep',
    'step_aware_loggerInfo',
    'step_aware_loggerError',
    'step_aware_loggerAttach',
    'get_current_step_name',
    'is_in_step',
    'SmartLocator',
    'Locator',
    'LocatorType',
    'retry_on_failure',
    'RetryConfig',
    'DriverFactory',
    'GridDriverFactory',
    'CapabilitiesManager',
    'BasePage',
    'BaseSeleniumTest',
    'TestExecutionTracker',
    'SmartAssert',
    'EnvironmentConfig',
    'get_environment_config',
    'reset_environment_config',
]

