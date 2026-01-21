"""
Locator Module
==============

Smart locator mechanism with gradual fallback support.

SmartLocator uses a list of alternative locators (CSS / XPath)
and attempts each one in turn with retry and smart timeout at runtime.

Principle: Page Objects define the locators,
BasePage uses them via SmartLocator.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum


class LocatorType(Enum):
    """Supported locator types."""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"  # text=... selector
    PLACEHOLDER = "placeholder"


@dataclass
class Locator:
    """
    Definition of a single locator.
    
    Attributes:
        type: LocatorType (CSS / XPATH / etc)
        value: locator value (selector / xpath / text)
        description: human-readable description of element (for logs)
    """
    type: LocatorType
    value: str
    description: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.type.value}={self.value}"
    
    def __repr__(self) -> str:
        desc = f" ({self.description})" if self.description else ""
        return f"Locator[{self.type.value}='{self.value}'{desc}]"


class SmartLocator:
    """
    Smart locator mechanism with fallback and resilience.
    
    Usage example:
        locator = SmartLocator(
            Locator(LocatorType.CSS, "#btn-submit", "Submit button"),
            Locator(LocatorType.XPATH, "//button[@type='submit']", "Submit by XPath"),
        )
        # BasePage will benefit from built-in resilience
    """
    
    def __init__(self, *locators: Union[Locator, tuple]) -> None:
        """
        Initialize SmartLocator with locators list.
        
        Args:
            *locators: Locator objects or tuples (type, value, description)
        """
        self.locators: List[Locator] = []
        
        for loc in locators:
            if isinstance(loc, Locator):
                self.locators.append(loc)
            elif isinstance(loc, tuple):
                # tuple: (type, value) or (type, value, description)
                if len(loc) == 2:
                    loc_type, loc_value = loc
                    self.locators.append(Locator(loc_type, loc_value))
                elif len(loc) == 3:
                    loc_type, loc_value, description = loc
                    self.locators.append(Locator(loc_type, loc_value, description))
            else:
                raise ValueError(f"Invalid locator format: {loc}")
    
    def get_all_locators(self) -> List[Locator]:
        """Get all locators for use in retry logic."""
        return self.locators.copy()
    
    def __str__(self) -> str:
        """Compact description of all locators."""
        return " | ".join(str(loc) for loc in self.locators)
    
    def __repr__(self) -> str:
        return f"SmartLocator({len(self.locators)} fallback(s))"


# Helper factories for easy use
def css_locator(selector: str, description: Optional[str] = None) -> Locator:
    """Factory for CSS locator."""
    return Locator(LocatorType.CSS, selector, description)


def xpath_locator(xpath: str, description: Optional[str] = None) -> Locator:
    """Factory for XPath locator."""
    return Locator(LocatorType.XPATH, xpath, description)


def text_locator(text: str, description: Optional[str] = None) -> Locator:
    """Factory for text locator (Playwright syntax)."""
    return Locator(LocatorType.TEXT, f"text={text}", description)
