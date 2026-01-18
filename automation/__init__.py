"""
Automation Package
==================

Enterprise-grade automation infrastructure for web testing.

Key Principles:
- Infrastructure First: Tests are clients of the infrastructure
- Separation of Concerns: Each layer has clear responsibility
- Anti-bot Resilience: Human-like behavior out of the box
- Page Object Model: Clean abstraction for UI elements
- Scalability: Support for local & remote execution

Usage Example:
    from automation.core import DriverFactory, BasePage, get_logger
    from automation.pages.my_page import MyPage
    
    logger = get_logger(__name__)
    
    # Create browser
    factory = DriverFactory()
    browser = await factory.create_browser()
    context = await factory.create_context(browser)
    page = await factory.create_page(context)
    
    # Create Page Object
    my_page = MyPage(BasePage(page))
    await my_page.navigate("https://example.com")
    await my_page.do_something()

Layers:
1. core/       - Infrastructure (logger, retry, locator, driver, base_page)
2. utils/      - Support functions (human_actions, random_utils)
3. config/     - Configuration (YAML files)
4. pages/      - Page Objects (to be implemented by user)
5. tests/      - Test cases (to be implemented by user)
6. reports/    - Output (logs, screenshots, traces, videos)
"""

__version__ = "1.0.0"
__author__ = "Senior Automation Engineer"

from automation.core import *
from automation.utils import *
