"""
Human Actions Module
====================

Dedicated layer simulating human behavior to avoid bot detection.

Functions:
- human_click(): click with random delay
- human_type(): type char-by-char with varying speed
- human_scroll(): gradual scroll
- human_wait(): wait with randomization
- human_move_mouse(): natural mouse movement

Principle: Called ONLY via BasePage - tests do not call human actions directly.
"""

import time
import random
from typing import Tuple, Optional
from automation.core.logger import get_logger

logger = get_logger(__name__)


class HumanActions:
    """
    Simulates human-like behavior to avoid bot detection.
    
    All waits are randomized within an acceptable range.
    """
    
    def __init__(self,
                 typing_speed_min_ms: int = 20,
                 typing_speed_max_ms: int = 100,
                 click_delay_min_ms: int = 100,
                 click_delay_max_ms: int = 500,
                 scroll_pause_min_ms: int = 200,
                 scroll_pause_max_ms: int = 800):
        """
        Args:
            typing_speed_min_ms: minimum delay between key presses
            typing_speed_max_ms: maximum delay between key presses
            click_delay_min_ms: delay pre/post click
            click_delay_max_ms: delay maximum post click
            scroll_pause_min_ms: minimum pause between scroll steps
            scroll_pause_max_ms: maximum pause between scroll steps
        """
        self.typing_speed_min_ms = typing_speed_min_ms
        self.typing_speed_max_ms = typing_speed_max_ms
        self.click_delay_min_ms = click_delay_min_ms
        self.click_delay_max_ms = click_delay_max_ms
        self.scroll_pause_min_ms = scroll_pause_min_ms
        self.scroll_pause_max_ms = scroll_pause_max_ms
    
    @staticmethod
    def _random_delay(min_ms: int, max_ms: int) -> float:
        """
        Generate random delay in range.
        
        Args:
            min_ms: minimum delay in milliseconds
            max_ms: maximum delay in milliseconds
        
        Returns:
            Delay in seconds
        """
        delay_ms = random.uniform(min_ms, max_ms)
        return delay_ms / 1000.0
    
    def get_typing_delay(self) -> float:
        """
        Simulate realistic typing speed variation.
        
        Some keys might be typed faster, some slower.
        Returns delay in seconds for inter-character typing.
        """
        return self._random_delay(self.typing_speed_min_ms, self.typing_speed_max_ms)
    
    def get_click_delay(self) -> float:
        """
        Delay before/after clicking.
        Humans don't click instantly.
        """
        return self._random_delay(self.click_delay_min_ms, self.click_delay_max_ms)
    
    def get_scroll_pause(self) -> float:
        """
        Pause during scrolling.
        Humans scroll in steps, not continuously.
        """
        return self._random_delay(self.scroll_pause_min_ms, self.scroll_pause_max_ms)
    
    def get_wait_delay(self, min_ms: int = 100, max_ms: int = 500) -> float:
        """
        Generic wait delay with randomization.
        """
        return self._random_delay(min_ms, max_ms)
    
    def get_mouse_move_duration(self) -> float:
        """
        Duration for mouse movement from one point to another.
        Typically 0.1-0.3 seconds for natural movement.
        """
        return random.uniform(0.1, 0.3)
    
    def get_random_offset(self, max_offset: int = 10) -> Tuple[int, int]:
        """
        Random offset for clicking (not exactly center of element).
        
        Args:
            max_offset: maximum deviation in pixels
        
        Returns:
            Tuple of (x_offset, y_offset)
        """
        x_offset = random.randint(-max_offset, max_offset)
        y_offset = random.randint(-max_offset, max_offset)
        return x_offset, y_offset
    
    def wait_for_network_idle(self, timeout_sec: float = 5) -> None:
        """
        Wait for network to become idle (simulated).
        
        In reality, Playwright handles this via wait_for_load_state.
        This is for additional human-like delays after network events.
        """
        delay = self._random_delay(200, 500)
        logger.debug(f"Waiting for network idle (simulated): {delay:.2f}s")
        time.sleep(delay)
    
    def wait_for_dom_stable(self, timeout_sec: float = 2) -> None:
        """
        Wait for DOM to stabilize (no more mutations).
        
        Used after page load or element appearance.
        """
        delay = self._random_delay(300, 800)
        logger.debug(f"Waiting for DOM stable: {delay:.2f}s")
        time.sleep(delay)
    
    def random_pause(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """
        Random pause for human-like delays.
        
        Used between major actions (fill form, navigate, etc).
        """
        delay = self._random_delay(min_ms, max_ms)
        logger.debug(f"Human pause: {delay:.2f}s")
        time.sleep(delay)
    
    def think_delay(self) -> None:
        """
        Simulate "thinking" delay before action.
        Humans read content before acting on it.
        
        Typical range: 0.5-2 seconds.
        """
        delay = self._random_delay(500, 2000)
        logger.debug(f"Think delay: {delay:.2f}s")
        time.sleep(delay)


# Global instance for easy access
_human_actions_instance: Optional[HumanActions] = None


def initialize_human_actions(typing_speed_min_ms: int = 20,
                             typing_speed_max_ms: int = 100,
                             click_delay_min_ms: int = 100,
                             click_delay_max_ms: int = 500,
                             scroll_pause_min_ms: int = 200,
                             scroll_pause_max_ms: int = 800) -> None:
    """
    Initialize global HumanActions instance with configuration.
    
    Should be called once during test setup.
    """
    global _human_actions_instance
    _human_actions_instance = HumanActions(
        typing_speed_min_ms=typing_speed_min_ms,
        typing_speed_max_ms=typing_speed_max_ms,
        click_delay_min_ms=click_delay_min_ms,
        click_delay_max_ms=click_delay_max_ms,
        scroll_pause_min_ms=scroll_pause_min_ms,
        scroll_pause_max_ms=scroll_pause_max_ms,
    )
    logger.info("HumanActions initialized with anti-bot configuration")


def get_human_actions() -> HumanActions:
    """
    Get global HumanActions instance.
    
    If not initialized, returns default instance.
    """
    global _human_actions_instance
    if _human_actions_instance is None:
        initialize_human_actions()
    return _human_actions_instance
