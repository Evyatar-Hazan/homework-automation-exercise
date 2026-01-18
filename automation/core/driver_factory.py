"""
Driver Factory Module
=====================

מפעל מרכזי ליצירת Browser, Context, ו־Page instances.

תכונות:
- Local browser support (Chromium, Firefox, WebKit)
- Remote Grid support (Selenium Grid, Moon)
- Anti-bot capabilities מובנה (user-agent, viewport, headless)
- Trace / Video recording
- Isolated browser instances per test
- Auto cleanup

עיקרון:
- Each test gets isolated browser/context/page
- No state leakage between tests
- Configuration from YAML
- Graceful teardown
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Literal
import yaml
from datetime import datetime

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    BrowserType,
)

from automation.core.logger import get_logger
from automation.utils.random_utils import random_user_agent, random_viewport

logger = get_logger(__name__)


class DriverFactory:
    """
    מפעל מרכזי ליצירת browser instances עם תמיכה ב־anti-bot.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: Path to env.yaml configuration
                        (defaults to automation/config/env.yaml)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.playwright = None
        self._instances: Dict[str, Any] = {}
    
    @staticmethod
    def _get_default_config_path() -> str:
        """Get default config path relative to this module."""
        script_dir = Path(__file__).parent.parent
        return str(script_dir / "config" / "env.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
            return self._default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        logger.info(f"Loaded configuration from {self.config_path}")
        return config
    
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Default configuration if config file not found."""
        return {
            "environment": "local",
            "headless": False,
            "trace": False,
            "video": False,
            "screenshot_on_failure": True,
            "timeouts": {
                "page_load": 30,
                "element_visibility": 15,
                "element_interaction": 10,
                "network_idle": 8,
                "dom_stable": 2,
            },
            "retries": {
                "max_attempts": 3,
                "initial_backoff_ms": 500,
                "max_backoff_ms": 5000,
                "exponential_base": 2,
            },
            "human_behavior": {
                "enabled": True,
                "typing_speed_min_ms": 20,
                "typing_speed_max_ms": 100,
                "click_delay_min_ms": 100,
                "click_delay_max_ms": 500,
                "scroll_pause_min_ms": 200,
                "scroll_pause_max_ms": 800,
            },
            "browser": {
                "type": "chromium",
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ],
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": None,
            },
            "logging": {
                "level": "INFO",
            },
            "proxy": None,
        }
    
    async def initialize(self) -> None:
        """Initialize Playwright instance."""
        if self.playwright is not None:
            logger.warning("Playwright already initialized")
            return
        
        self.playwright = await async_playwright().start()
        logger.info("Playwright initialized")
    
    async def create_browser(self,
                            browser_type: Optional[Literal["chromium", "firefox", "webkit"]] = None) -> Browser:
        """
        Create a new browser instance.
        
        Args:
            browser_type: Browser type (defaults to config)
        
        Returns:
            Browser instance
        """
        if self.playwright is None:
            await self.initialize()
        
        browser_type = browser_type or self.config.get("browser", {}).get("type", "chromium")
        headless = self.config.get("headless", False)
        
        # Get browser type object
        browser_type_obj: BrowserType
        if browser_type == "firefox":
            browser_type_obj = self.playwright.firefox
        elif browser_type == "webkit":
            browser_type_obj = self.playwright.webkit
        else:
            browser_type_obj = self.playwright.chromium
        
        # Browser launch options
        launch_options = {
            "headless": headless,
        }
        
        # Add custom args
        if browser_type == "chromium":
            args = self.config.get("browser", {}).get("args", [])
            launch_options["args"] = args
        
        # Add proxy if configured
        proxy = self.config.get("proxy")
        if proxy:
            launch_options["proxy"] = proxy
        
        browser = await browser_type_obj.launch(**launch_options)
        logger.info(f"Browser created: {browser_type} (headless={headless})")
        
        self._instances['browser'] = browser
        return browser
    
    async def create_context(self,
                            browser: Browser,
                            test_name: Optional[str] = None) -> BrowserContext:
        """
        Create a new browser context with anti-bot settings.
        
        Args:
            browser: Browser instance
            test_name: Name of the test (for trace/video naming)
        
        Returns:
            BrowserContext instance
        """
        # Anti-bot configuration
        browser_config = self.config.get("browser", {})
        
        context_options = {
            "viewport": {
                "width": browser_config.get("viewport", {}).get("width", 1920),
                "height": browser_config.get("viewport", {}).get("height", 1080),
            },
            "ignore_https_errors": True,
        }
        
        # User agent (randomize or use config)
        user_agent = browser_config.get("user_agent")
        if user_agent is None:
            user_agent = random_user_agent()
        context_options["user_agent"] = user_agent
        
        # Trace recording
        context = await browser.new_context(**context_options)
        
        if self.config.get("trace", False):
            trace_path = self._get_trace_path(test_name)
            await context.tracing.start(screenshots=True, snapshots=True)
            self._instances['trace_path'] = trace_path
        
        # Video recording
        if self.config.get("video", False):
            video_dir = Path("reports/videos")
            video_dir.mkdir(parents=True, exist_ok=True)
            # Video is set per-context via context creation
        
        logger.info(f"Context created (UA: {user_agent[:50]}...)")
        self._instances['context'] = context
        
        return context
    
    async def create_page(self,
                         context: BrowserContext,
                         test_name: Optional[str] = None) -> Page:
        """
        Create a new page with default configurations.
        
        Args:
            context: BrowserContext instance
            test_name: Name of the test
        
        Returns:
            Page instance
        """
        page = await context.new_page()
        
        # Set timeouts
        timeouts = self.config.get("timeouts", {})
        page.set_default_timeout(timeouts.get("element_interaction", 10) * 1000)
        page.set_default_navigation_timeout(timeouts.get("page_load", 30) * 1000)
        
        # Set view port
        viewport = self.config.get("browser", {}).get("viewport", {})
        if viewport:
            await page.set_viewport_size({
                "width": viewport.get("width", 1920),
                "height": viewport.get("height", 1080),
            })
        
        logger.info(f"Page created for test: {test_name}")
        self._instances['page'] = page
        
        return page
    
    async def cleanup_page(self, page: Page) -> None:
        """Close a page."""
        if page:
            await page.close()
            logger.info("Page closed")
    
    async def cleanup_context(self, context: BrowserContext, test_name: Optional[str] = None) -> None:
        """Close a context and save trace if enabled."""
        if not context:
            return
        
        # Save trace
        if self.config.get("trace", False) and 'trace_path' in self._instances:
            trace_path = self._instances['trace_path']
            await context.tracing.stop(path=trace_path)
            logger.info(f"Trace saved to {trace_path}")
        
        await context.close()
        logger.info("Context closed")
    
    async def cleanup_browser(self, browser: Browser) -> None:
        """Close a browser."""
        if browser:
            await browser.close()
            logger.info("Browser closed")
    
    async def cleanup(self) -> None:
        """Cleanup all Playwright resources."""
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            logger.info("Playwright stopped")
    
    @staticmethod
    def _get_trace_path(test_name: Optional[str] = None) -> str:
        """Generate trace file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_suffix = f"_{test_name}" if test_name else ""
        trace_dir = Path("reports/traces")
        trace_dir.mkdir(parents=True, exist_ok=True)
        return str(trace_dir / f"trace{test_suffix}_{timestamp}.zip")
    
    def get_config(self) -> Dict[str, Any]:
        """Get loaded configuration."""
        return self.config
