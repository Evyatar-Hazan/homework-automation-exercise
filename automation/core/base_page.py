"""
Base Page Module
================

ליבת המערכת - BasePage מכיל את כל האינטראקציות עם Playwright.

עיקרון:
- Page Objects לא נוגעים ב־Playwright ישירות
- BasePage בעל אחריות מלאה על:
  * לוקייטורים עם fallback
  * Retry logic עם backoff
  * Human-like behavior
  * Timeouts חכמים
  * Logging מלא
  * Screenshots בכשל

מתודות ליבה:
- find() - מוצא אלמנט
- click() - קליק עם human behavior
- type() - הקלדה תו־תו
- wait_for_element() - המתנה לאלמנט להופיע
- wait_for_element_invisible() - המתנה להסתרה
"""

import asyncio
from typing import Optional, List, Any
from pathlib import Path
from datetime import datetime

from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

from automation.core.logger import get_logger
from automation.core.locator import SmartLocator, Locator as CustomLocator, LocatorType
from automation.core.retry import retry_on_failure
from automation.utils.human_actions import get_human_actions

logger = get_logger(__name__)


class BasePage:
    """
    ליבת המערכת של אוטומציה.
    
    אחראית על כל אינטראקציות Playwright עם:
    - SmartLocator (fallback)
    - Retry & backoff
    - Human-like behavior
    - Logging מלא
    - Resilience
    
    Example:
        page = BasePage(playwright_page)
        element = page.find(SmartLocator(...))
        page.click(SmartLocator(...))
        page.type(SmartLocator(...), "text")
    """
    
    def __init__(self, page: Page, timeout_sec: float = 10):
        """
        Args:
            page: Playwright Page instance
            timeout_sec: Default timeout for operations
        """
        self.page = page
        self.timeout_sec = timeout_sec
        self.human = get_human_actions()
        
        logger.info(f"BasePage initialized for URL: {page.url}")
    
    def _convert_smart_locator_to_playwright(self, locator: SmartLocator) -> str:
        """
        Convert SmartLocator to first Playwright-compatible selector.
        
        בתהליך ריצה, BasePage ינסה כל selector אחד אחרי השני.
        
        Args:
            locator: SmartLocator object
        
        Returns:
            First locator value as string
        """
        if not locator.get_all_locators():
            raise ValueError("SmartLocator has no locators")
        
        first_loc = locator.get_all_locators()[0]
        return first_loc.value
    
    async def find(self, locator: SmartLocator, timeout_sec: Optional[float] = None) -> Locator:
        """
        Find element with SmartLocator fallback strategy.
        
        מנסה כל locator ברשימה עד שמצליח.
        
        Args:
            locator: SmartLocator with one or more fallbacks
            timeout_sec: Custom timeout (default from config)
        
        Returns:
            Playwright Locator (found element)
        
        Raises:
            TimeoutError: If all locators fail
        """
        timeout_sec = timeout_sec or self.timeout_sec
        all_locators = locator.get_all_locators()
        
        logger.debug(f"Finding element: {locator}")
        
        last_error = None
        for attempt_num, loc in enumerate(all_locators, 1):
            try:
                logger.debug(
                    f"Attempt {attempt_num}/{len(all_locators)}: {loc.type.value}={loc.value}"
                )
                
                # Create playwright locator based on type
                playwright_locator = self._create_playwright_locator(loc)
                
                # Wait for element to be visible
                await playwright_locator.wait_for(
                    state="visible",
                    timeout=timeout_sec * 1000  # Convert to ms
                )
                
                logger.debug(f"✓ Element found: {loc.description or loc.value}")
                return playwright_locator
            
            except PlaywrightTimeoutError as e:
                last_error = e
                logger.warning(
                    f"Locator failed (attempt {attempt_num}): {loc.type.value}={loc.value}"
                )
            
            except Exception as e:
                last_error = e
                logger.warning(f"Unexpected error: {e}")
        
        # All locators failed - take screenshot and raise
        await self._take_screenshot_on_failure("element_not_found")
        
        error_msg = (
            f"Element not found after {len(all_locators)} attempts. "
            f"Tried: {locator}\nLast error: {last_error}"
        )
        logger.error(error_msg)
        raise TimeoutError(error_msg)
    
    def _create_playwright_locator(self, loc: CustomLocator) -> Locator:
        """
        Create Playwright Locator from CustomLocator.
        
        Args:
            loc: CustomLocator object
        
        Returns:
            Playwright Locator
        """
        if loc.type == LocatorType.CSS:
            return self.page.locator(f"css={loc.value}")
        elif loc.type == LocatorType.XPATH:
            return self.page.locator(f"xpath={loc.value}")
        elif loc.type == LocatorType.TEXT:
            return self.page.locator(loc.value)  # text= is part of value
        else:
            return self.page.locator(loc.value)
    
    async def click(self, locator: SmartLocator, 
                   timeout_sec: Optional[float] = None,
                   force: bool = False) -> None:
        """
        Click element with human-like behavior.
        
        Args:
            locator: SmartLocator to click
            timeout_sec: Custom timeout
            force: Force click even if not visible (risky for eBay)
        """
        logger.info(f"Clicking: {locator}")
        
        # Pre-click delay (human behavior)
        if self.human:
            delay = self.human.get_click_delay()
            await asyncio.sleep(delay)
        
        try:
            element = await self.find(locator, timeout_sec)
            await element.click(force=force)
            
            logger.debug(f"✓ Clicked successfully")
            
            # Post-click delay and network idle
            if self.human:
                self.human.wait_for_network_idle(timeout_sec=2)
        
        except Exception as e:
            await self._take_screenshot_on_failure("click_failed")
            logger.error(f"Click failed: {e}")
            raise
    
    async def type(self, locator: SmartLocator, text: str,
                  timeout_sec: Optional[float] = None,
                  clear_first: bool = True) -> None:
        """
        Type text with human-like delays between characters.
        
        Args:
            locator: SmartLocator to type into
            text: Text to type
            timeout_sec: Custom timeout
            clear_first: Clear field before typing
        """
        logger.info(f"Typing into: {locator}")
        
        try:
            element = await self.find(locator, timeout_sec)
            
            if clear_first:
                await element.clear()
                logger.debug("Field cleared")
            
            # Type with human-like delays
            if self.human:
                for char in text:
                    await element.type(char)
                    delay = self.human.get_typing_delay()
                    await asyncio.sleep(delay)
            else:
                await element.type(text)
            
            logger.debug(f"✓ Typed: {text[:20]}...")
        
        except Exception as e:
            await self._take_screenshot_on_failure("type_failed")
            logger.error(f"Type failed: {e}")
            raise
    
    async def fill(self, locator: SmartLocator, text: str,
                  timeout_sec: Optional[float] = None) -> None:
        """
        Fill input field (less human-like but faster).
        
        For situations where type() is too slow.
        Still has retry and fallback logic.
        
        Args:
            locator: SmartLocator to fill
            text: Text to fill
            timeout_sec: Custom timeout
        """
        logger.info(f"Filling: {locator} with text")
        
        try:
            element = await self.find(locator, timeout_sec)
            await element.fill(text)
            logger.debug(f"✓ Filled with: {text[:20]}...")
        
        except Exception as e:
            await self._take_screenshot_on_failure("fill_failed")
            logger.error(f"Fill failed: {e}")
            raise
    
    async def wait_for_element(self, locator: SmartLocator,
                              timeout_sec: Optional[float] = None,
                              state: str = "visible") -> Locator:
        """
        Wait for element to appear/disappear/be attached.
        
        Args:
            locator: SmartLocator to wait for
            timeout_sec: Custom timeout
            state: "visible" | "hidden" | "attached" | "detached"
        
        Returns:
            Playwright Locator
        """
        timeout_sec = timeout_sec or self.timeout_sec
        logger.debug(f"Waiting for element ({state}): {locator}")
        
        try:
            element = await self.find(locator, timeout_sec)
            await element.wait_for(state=state, timeout=timeout_sec * 1000)
            return element
        
        except Exception as e:
            logger.error(f"Wait for element failed: {e}")
            raise
    
    async def wait_for_element_invisible(self, locator: SmartLocator,
                                        timeout_sec: Optional[float] = None) -> None:
        """Wait for element to become hidden."""
        await self.wait_for_element(locator, timeout_sec, state="hidden")
    
    async def get_text(self, locator: SmartLocator,
                      timeout_sec: Optional[float] = None) -> str:
        """
        Get element text content.
        
        Args:
            locator: SmartLocator
            timeout_sec: Custom timeout
        
        Returns:
            Text content
        """
        try:
            element = await self.find(locator, timeout_sec)
            text = await element.text_content()
            return text or ""
        
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            raise
    
    async def get_attribute(self, locator: SmartLocator, attr: str,
                           timeout_sec: Optional[float] = None) -> Optional[str]:
        """
        Get element attribute value.
        
        Args:
            locator: SmartLocator
            attr: Attribute name (e.g., "href", "data-id")
            timeout_sec: Custom timeout
        
        Returns:
            Attribute value or None
        """
        try:
            element = await self.find(locator, timeout_sec)
            value = await element.get_attribute(attr)
            return value
        
        except Exception as e:
            logger.error(f"Get attribute failed: {e}")
            raise
    
    async def scroll_to_element(self, locator: SmartLocator,
                               timeout_sec: Optional[float] = None) -> None:
        """
        Scroll element into view.
        
        Args:
            locator: SmartLocator to scroll to
            timeout_sec: Custom timeout
        """
        logger.debug(f"Scrolling to: {locator}")
        
        try:
            element = await self.find(locator, timeout_sec)
            await element.scroll_into_view_if_needed()
            
            # Human-like pause after scroll
            if self.human:
                self.human.wait_for_dom_stable()
        
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            raise
    
    async def is_visible(self, locator: SmartLocator,
                        timeout_sec: float = 1) -> bool:
        """
        Check if element is visible (doesn't raise on failure).
        
        Args:
            locator: SmartLocator
            timeout_sec: Timeout for visibility check
        
        Returns:
            True if visible, False otherwise
        """
        try:
            element = await self.find(locator, timeout_sec)
            return await element.is_visible()
        except Exception:
            return False
    
    async def is_enabled(self, locator: SmartLocator) -> bool:
        """Check if element is enabled (not disabled)."""
        try:
            element = await self.find(locator)
            return await element.is_enabled()
        except Exception:
            return False
    
    async def count_elements(self, locator: SmartLocator) -> int:
        """Count number of matching elements."""
        try:
            locators = locator.get_all_locators()
            first = locators[0]
            playwright_loc = self._create_playwright_locator(first)
            return await playwright_loc.count()
        except Exception:
            return 0
    
    async def wait_for_navigation(self, timeout_sec: Optional[float] = None) -> None:
        """Wait for page navigation to complete."""
        timeout_sec = timeout_sec or self.timeout_sec
        logger.debug("Waiting for navigation...")
        
        try:
            await self.page.wait_for_load_state(
                "networkidle",
                timeout=timeout_sec * 1000
            )
            logger.debug("Navigation completed")
        
        except Exception as e:
            logger.warning(f"Navigation wait timeout: {e}")
    
    async def navigate(self, url: str, timeout_sec: Optional[float] = None) -> None:
        """Navigate to URL."""
        timeout_sec = timeout_sec or self.timeout_sec
        logger.info(f"Navigating to: {url}")
        
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=timeout_sec * 1000)
            logger.info("Navigation successful")
        
        except Exception as e:
            await self._take_screenshot_on_failure("navigation_failed")
            logger.error(f"Navigation failed: {e}")
            raise
    
    async def refresh(self) -> None:
        """Refresh current page."""
        logger.info("Refreshing page")
        await self.page.reload()
    
    async def go_back(self) -> None:
        """Go back to previous page."""
        logger.info("Going back")
        await self.page.go_back()
    
    async def go_forward(self) -> None:
        """Go forward to next page."""
        logger.info("Going forward")
        await self.page.go_forward()
    
    async def get_current_url(self) -> str:
        """Get current page URL."""
        return self.page.url
    
    async def get_page_title(self) -> str:
        """Get page title."""
        return await self.page.title()
    
    async def _take_screenshot_on_failure(self, name: str) -> None:
        """Take screenshot for debugging."""
        try:
            # Use absolute path from project root
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            screenshot_dir = project_root / "automation" / "reports" / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshot_dir / f"{name}_{timestamp}.png"
            
            await self.page.screenshot(path=str(screenshot_path))
            logger.error(f"Screenshot saved: {screenshot_path}")
        
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
