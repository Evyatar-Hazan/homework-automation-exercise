"""
Locator Module
==============

מנגנון לוקייטור חכם עם תמיכה ב־fallback הדרגתי.

SmartLocator מעביר רשימת לוקייטורים חלופיים (CSS / XPath)
ובזמן ריצה מנסה כל אחד בתורו עם retry ו־timeout חכם.

עקרון: Page Objects יגדירו את הלוקייטורים,
BasePage ישתמש בהם דרך SmartLocator.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum


class LocatorType(Enum):
    """סוגי לוקייטורים תומכים."""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"  # text=... selector
    PLACEHOLDER = "placeholder"


@dataclass
class Locator:
    """
    הגדרה של לוקייטור בודד.
    
    Attributes:
        type: LocatorType (CSS / XPATH / etc)
        value: ערך הלוקייטור (selector / xpath / text)
        description: תיאור אנושי של האלמנט (לוג בלבד)
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
    מנגנון לוקייטור חכם עם fallback ורילינס.
    
    דוגמה שימוש:
        locator = SmartLocator(
            Locator(LocatorType.CSS, "#btn-submit", "Submit button"),
            Locator(LocatorType.XPATH, "//button[@type='submit']", "Submit by XPath"),
        )
        # BasePage יהנה מresilience מובנה
    """
    
    def __init__(self, *locators: Union[Locator, tuple]) -> None:
        """
        אתחול SmartLocator עם רשימת locators.
        
        Args:
            *locators: Locator objects או tuples (type, value, description)
        """
        self.locators: List[Locator] = []
        
        for loc in locators:
            if isinstance(loc, Locator):
                self.locators.append(loc)
            elif isinstance(loc, tuple):
                # tuple: (type, value) או (type, value, description)
                if len(loc) == 2:
                    loc_type, loc_value = loc
                    self.locators.append(Locator(loc_type, loc_value))
                elif len(loc) == 3:
                    loc_type, loc_value, description = loc
                    self.locators.append(Locator(loc_type, loc_value, description))
            else:
                raise ValueError(f"Invalid locator format: {loc}")
    
    def get_all_locators(self) -> List[Locator]:
        """קבלת כל הלוקייטורים לשימוש ב־retry logic."""
        return self.locators.copy()
    
    def __str__(self) -> str:
        """תיאור קומפקטי של כל הלוקייטורים."""
        return " | ".join(str(loc) for loc in self.locators)
    
    def __repr__(self) -> str:
        return f"SmartLocator({len(self.locators)} fallback(s))"


# Helper factories לשימוש קל
def css_locator(selector: str, description: Optional[str] = None) -> Locator:
    """Factory לCSS locator."""
    return Locator(LocatorType.CSS, selector, description)


def xpath_locator(xpath: str, description: Optional[str] = None) -> Locator:
    """Factory לXPath locator."""
    return Locator(LocatorType.XPATH, xpath, description)


def text_locator(text: str, description: Optional[str] = None) -> Locator:
    """Factory לtext locator (Playwright syntax)."""
    return Locator(LocatorType.TEXT, f"text={text}", description)
