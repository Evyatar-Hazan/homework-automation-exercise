"""
Resilience Module - מודול התמודדות עם שינויים תכופים בממשק
==============================================================

מנגנון מתקדם להתמודדות עם GUI changes תכופים דרך:

1. SMART LOCATOR STRATEGY
   - רבים fallback locators (CSS, XPath, Text)
   - Adaptive fallback (לוקייטורים נבחרים לפי הצלחה)
   - Pattern-based selectors

2. ABSTRACTION LAYER
   - Business-focused Page Objects
   - No hardcoded selectors in tests
   - Attribute-based location finding

3. RESILIENCE PATTERNS
   - Retry with exponential backoff
   - Element visibility monitoring
   - DOM change detection
   - Screenshot comparison (future)
   - Self-healing locators (cache recent successes)

4. LOGGING & DIAGNOSTICS
   - Detailed failure analysis
   - Locator effectiveness metrics
   - Recommendations for locator updates

עיקרון: כל שינוי ממשק לא אמור לשבור את הטסטים מיד.
התשתית תנסה שינויים דינמיים לפני כשל סופי.
"""

import asyncio
from typing import Optional, List, Dict, Tuple, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from playwright.async_api import Page, Locator as PlaywrightLocator
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from automation.core.logger import get_logger
from automation.core.locator import SmartLocator, Locator, LocatorType

logger = get_logger(__name__)


@dataclass
class LocatorMetrics:
    """מדדים של ביצועי locator."""
    locator_value: str
    locator_type: LocatorType
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    avg_wait_time_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """אחוז הצלחה של הלוקייטור."""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0
    
    @property
    def is_healthy(self) -> bool:
        """האם הלוקייטור בריא (יותר מ־80% הצלחה)."""
        return self.success_rate >= 80 or self.success_count < 3
    
    def __repr__(self) -> str:
        return (
            f"LocatorMetrics[{self.locator_type.value}={self.locator_value}] "
            f"Success: {self.success_rate:.1f}% ({self.success_count}✓/{self.failure_count}✗)"
        )


class AdaptiveSmartLocator:
    """
    SmartLocator חכם שלומד מהנסיונות ומשפר את סדר ה־fallback.
    
    בכל ניסיון בר הצלחה, הלוקייטור עובר לחזית הרשימה.
    בכל כשל, נוספת נקודת כשל שלו.
    """
    
    def __init__(self, smart_locator: SmartLocator):
        """
        Args:
            smart_locator: SmartLocator object עם locators ראשוניים
        """
        self.original_locators = smart_locator.get_all_locators().copy()
        self.current_order = self.original_locators.copy()
        self.metrics: Dict[str, LocatorMetrics] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """אתחול metrics לכל locator."""
        for loc in self.original_locators:
            key = f"{loc.type.value}:{loc.value}"
            self.metrics[key] = LocatorMetrics(
                locator_value=loc.value,
                locator_type=loc.type,
            )
    
    def _get_metric_key(self, locator: Locator) -> str:
        """יצירת מפתח יחיד לlocator."""
        return f"{locator.type.value}:{locator.value}"
    
    def record_success(self, locator: Locator, wait_time_ms: float = 0.0) -> None:
        """רישום הצלחה בשימוש locator."""
        key = self._get_metric_key(locator)
        metric = self.metrics.get(key)
        if metric:
            metric.success_count += 1
            metric.last_used = datetime.now()
            # Update average wait time
            total = metric.success_count + metric.failure_count
            metric.avg_wait_time_ms = (
                (metric.avg_wait_time_ms * (total - 1) + wait_time_ms) / total
            )
            logger.debug(f"✓ {metric}")
            self._reorder_locators()
    
    def record_failure(self, locator: Locator) -> None:
        """רישום כשל בשימוש locator."""
        key = self._get_metric_key(locator)
        metric = self.metrics.get(key)
        if metric:
            metric.failure_count += 1
            metric.last_used = datetime.now()
            logger.debug(f"✗ {metric}")
    
    def _reorder_locators(self) -> None:
        """
        סדר מחדש את ה־locators לפי שיעור הצלחה.
        
        כל locator בריא עם הצלחות עוברים לחזית.
        """
        # Sort by success rate (descending) and success count
        sorted_locators = sorted(
            self.original_locators,
            key=lambda loc: (
                self.metrics[self._get_metric_key(loc)].success_rate,
                self.metrics[self._get_metric_key(loc)].success_count,
            ),
            reverse=True
        )
        
        # Update order if there's a change
        if sorted_locators != self.current_order:
            logger.debug("📊 Locator order reordered based on success metrics")
            self.current_order = sorted_locators
    
    def get_ordered_locators(self) -> List[Locator]:
        """קבל את הlocators בסדר מיטבי."""
        return self.current_order.copy()
    
    def get_metrics_report(self) -> Dict[str, LocatorMetrics]:
        """קבל דוח מפורט של ביצועי כל locator."""
        return {k: v for k, v in self.metrics.items()}
    
    def reset_metrics(self) -> None:
        """איפוס כל המדדים."""
        self._initialize_metrics()
        self.current_order = self.original_locators.copy()
        logger.info("Metrics reset to initial state")


class ResilienceMonitor:
    """
    מעקב אחרי שינויים בממשק ודיווח על בעיות.
    
    - מעקב אחרי כשלים בקצב
    - זיהוי patterns בכשלים
    - המלצות על עדכוני locators
    """
    
    def __init__(self, failure_threshold: int = 5):
        """
        Args:
            failure_threshold: מספר כשלים לפני הודעה חזויה
        """
        self.failure_threshold = failure_threshold
        self.failure_history: List[Tuple[str, datetime, str]] = []
        self.element_failures: Dict[str, int] = defaultdict(int)
    
    def record_failure(self, element_description: str, error_msg: str) -> None:
        """
        רישום כשל של אלמנט.
        
        Args:
            element_description: תיאור האלמנט (מה הוא אמור להיות)
            error_msg: הודעת שגיאה
        """
        self.failure_history.append((element_description, datetime.now(), error_msg))
        self.element_failures[element_description] += 1
        
        # Check if threshold exceeded
        if self.element_failures[element_description] >= self.failure_threshold:
            self._issue_alert(element_description)
    
    def _issue_alert(self, element_description: str) -> None:
        """הנפקת התראה בעיות בנוגע לאלמנט."""
        count = self.element_failures[element_description]
        logger.warning(
            f"🚨 ALERT: Element '{element_description}' failed {count} times. "
            f"GUI may have changed. Consider updating locators."
        )
    
    def get_failure_report(self) -> Dict[str, int]:
        """קבל דוח של אלמנטים בעיתיים."""
        return dict(sorted(
            self.element_failures.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def reset(self) -> None:
        """איפוס כל ההיסטוריה."""
        self.failure_history.clear()
        self.element_failures.clear()
        logger.info("Resilience monitor reset")


class AttributeBasedLocator:
    """
    Locator המבוסס על attributes במקום על CSS/XPath יציבים.
    
    שימושי כאשר CSS/XPath משתנים אך attributes (id, name, role) נשארים קבועים.
    
    דוגמה:
        # במקום: input#search-id.form-input
        # השתמש בattribute-based: [data-testid="search-input"]
    """
    
    @staticmethod
    def by_data_testid(test_id: str) -> Locator:
        """Locator based on data-testid attribute (recommended)."""
        return Locator(
            LocatorType.CSS,
            f"[data-testid='{test_id}']",
            f"Element with data-testid='{test_id}'"
        )
    
    @staticmethod
    def by_aria_label(label: str) -> Locator:
        """Locator based on aria-label (accessibility-friendly)."""
        return Locator(
            LocatorType.CSS,
            f"[aria-label='{label}']",
            f"Element with aria-label='{label}'"
        )
    
    @staticmethod
    def by_role(role: str, name: str = "") -> Locator:
        """
        Locator based on ARIA role (future: Playwright role selector).
        
        בעתיד: role=button[name="..."]
        לעת עתה: [role='button'] / [aria-label='...']
        """
        if name:
            return Locator(
                LocatorType.CSS,
                f"[role='{role}'][aria-label*='{name}']",
                f"{role.title()} with name containing '{name}'"
            )
        return Locator(
            LocatorType.CSS,
            f"[role='{role}']",
            f"Element with role='{role}'"
        )
    
    @staticmethod
    def by_name(name: str) -> Locator:
        """Locator based on name attribute."""
        return Locator(
            LocatorType.CSS,
            f"[name='{name}']",
            f"Element with name='{name}'"
        )
    
    @staticmethod
    def by_placeholder(placeholder: str) -> Locator:
        """Locator based on placeholder attribute."""
        return Locator(
            LocatorType.CSS,
            f"[placeholder*='{placeholder}']",
            f"Input with placeholder containing '{placeholder}'"
        )
    
    @staticmethod
    def by_value(value: str) -> Locator:
        """Locator based on value attribute."""
        return Locator(
            LocatorType.CSS,
            f"[value='{value}']",
            f"Element with value='{value}'"
        )
    
    @staticmethod
    def by_text_exact(text: str) -> Locator:
        """Locator based on exact text content."""
        return Locator(
            LocatorType.TEXT,
            f"text={text}",
            f"Element with exact text '{text}'"
        )
    
    @staticmethod
    def by_text_partial(text: str) -> Locator:
        """Locator based on partial text match."""
        return Locator(
            LocatorType.XPATH,
            f"//*[contains(text(), '{text}')]",
            f"Element containing text '{text}'"
        )


class SelfHealingLocator:
    """
    Locator שמשפר את עצמו כאשר הממשק משתנה.
    
    מנגנון:
    1. נסה את ה־locators העיקריים
    2. אם כל כשל, נסה fallback selectors דינמיים
    3. שמור את ה־selector שהצליח לשימוש הבא
    4. דווח על שינוי שהתגלה
    
    NOTE: זוהי התחלה של self-healing. ניתן להרחיב לעתיד.
    """
    
    def __init__(self):
        """אתחול self-healing cache."""
        self.cache: Dict[str, Locator] = {}
        self.fallback_strategies: List[Callable] = []
    
    def register_fallback_strategy(self, strategy: Callable) -> None:
        """
        רישום אסטרטגיה fallback דינמית.
        
        Args:
            strategy: async function(page: Page, element_hint: str) -> Optional[Locator]
        """
        self.fallback_strategies.append(strategy)
    
    async def find_with_healing(
        self,
        page: Page,
        primary_locator: SmartLocator,
        element_hint: str = "",
    ) -> Optional[PlaywrightLocator]:
        """
        חפוש אלמנט עם self-healing capabilities.
        
        Args:
            page: Playwright Page
            primary_locator: SmartLocator עם locators ראשוניים
            element_hint: תיאור האלמנט (לשימוש בfallback strategies)
        
        Returns:
            Playwright Locator או None אם כל כשל
        """
        # 1. Try primary locators
        for loc in primary_locator.get_all_locators():
            try:
                playwright_loc = self._create_playwright_locator(page, loc)
                await playwright_loc.wait_for(state="visible", timeout=3000)
                logger.debug(f"✓ Found element with primary locator: {loc}")
                return playwright_loc
            except PlaywrightTimeoutError:
                continue
        
        # 2. Try fallback strategies
        for strategy in self.fallback_strategies:
            try:
                fallback_loc = await strategy(page, element_hint)
                if fallback_loc:
                    playwright_loc = self._create_playwright_locator(page, fallback_loc)
                    await playwright_loc.wait_for(state="visible", timeout=3000)
                    logger.warning(
                        f"⚠️  Element found with fallback strategy: {fallback_loc}. "
                        f"GUI may have changed."
                    )
                    self.cache[element_hint] = fallback_loc
                    return playwright_loc
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.debug(f"Fallback strategy failed: {e}")
        
        # 3. All failed
        logger.error(f"Element not found: {element_hint}. Self-healing exhausted.")
        return None
    
    def _create_playwright_locator(self, page: Page, loc: Locator) -> PlaywrightLocator:
        """יצירת Playwright locator מ־CustomLocator."""
        if loc.type == LocatorType.CSS:
            return page.locator(f"css={loc.value}")
        elif loc.type == LocatorType.XPATH:
            return page.locator(f"xpath={loc.value}")
        elif loc.type == LocatorType.TEXT:
            return page.locator(loc.value)
        else:
            return page.locator(loc.value)
    
    def clear_cache(self) -> None:
        """ניקוי ה־cache של selectors שנשמרו."""
        self.cache.clear()
        logger.debug("Self-healing cache cleared")


# ============================================================================
# HELPER FUNCTIONS FOR SMART MULTI-LOCATOR STRATEGIES
# ============================================================================

def create_resilient_locator(
    primary_css: str,
    xpath_fallback: str,
    text_fallback: Optional[str] = None,
    description: Optional[str] = None,
) -> SmartLocator:
    """
    יציאה מהירה ל־יצירת SmartLocator עם locators רילינס.
    
    עדיפות: CSS (מהיר) → XPath (גמיש) → Text (reliable)
    
    Args:
        primary_css: CSS selector (מהיר)
        xpath_fallback: XPath selector (גמיש יותר)
        text_fallback: Text match (reliable בtext קבוע)
        description: תיאור האלמנט
    
    Returns:
        SmartLocator עם fallback chain
    """
    locators = [
        Locator(LocatorType.CSS, primary_css, description),
        Locator(LocatorType.XPATH, xpath_fallback, "XPath fallback"),
    ]
    
    if text_fallback:
        locators.append(
            Locator(LocatorType.TEXT, f"text={text_fallback}", "Text fallback")
        )
    
    return SmartLocator(*locators)


def create_attribute_based_resilient_locator(
    data_testid: Optional[str] = None,
    aria_label: Optional[str] = None,
    css_fallback: Optional[str] = None,
    xpath_fallback: Optional[str] = None,
    description: Optional[str] = None,
) -> SmartLocator:
    """
    יציאה מהירה ל־יצירת SmartLocator מבוסס attributes (יציב יותר).
    
    עדיפות: data-testid (הכי יציב) → aria-label → CSS → XPath
    
    Args:
        data_testid: data-testid attribute value
        aria_label: aria-label attribute value
        css_fallback: CSS fallback
        xpath_fallback: XPath fallback
        description: תיאור האלמנט
    
    Returns:
        SmartLocator עם fallback chain
    """
    locators = []
    
    # 1. data-testid (הכי יציב - לא משתנה עם CSS)
    if data_testid:
        locators.append(
            AttributeBasedLocator.by_data_testid(data_testid)
        )
    
    # 2. aria-label (accessibility-friendly, בדר"כ יציב)
    if aria_label:
        locators.append(
            AttributeBasedLocator.by_aria_label(aria_label)
        )
    
    # 3. CSS fallback
    if css_fallback:
        locators.append(
            Locator(LocatorType.CSS, css_fallback, "CSS fallback")
        )
    
    # 4. XPath fallback
    if xpath_fallback:
        locators.append(
            Locator(LocatorType.XPATH, xpath_fallback, "XPath fallback")
        )
    
    if not locators:
        raise ValueError("At least one locator strategy must be provided")
    
    return SmartLocator(*locators)


# ============================================================================
# BEST PRACTICES FOR GUI RESILIENCE
# ============================================================================

"""
🎯 Best Practices לתמודדות עם GUI Changes:

1. USE DATA-TESTID ATTRIBUTES
   ✓ Request developers to add data-testid attributes
   ✓ data-testid="search-button" is stable across CSS changes
   ✗ Don't rely on CSS classes that change frequently

2. MULTI-LOCATOR FALLBACK CHAIN
   ✓ Primary: CSS (fast)
   ✓ Secondary: XPath (flexible)
   ✓ Tertiary: Text/ARIA (semantic)
   ✗ Don't use only one selector strategy

3. ATTRIBUTE-BASED LOCATION
   ✓ Use [role="button"], [aria-label="..."], [name="..."]
   ✓ Prefer aria-label for semantic meaning
   ✗ Avoid brittle CSS classes like .btn-submit-red-v2

4. ABSTRACTION LAYER
   ✓ Hide all selectors in Page Objects
   ✓ Business methods in tests, selectors in page objects
   ✗ Don't hardcode selectors in test code

5. MONITORING & ALERTS
   ✓ Track locator success rates
   ✓ Alert when elements fail repeatedly
   ✓ Generate reports on GUI stability
   ✗ Don't ignore patterns in failures

6. SELF-HEALING LOCATORS
   ✓ Cache successful selectors
   ✓ Try dynamic fallback strategies
   ✓ Learn from each GUI change
   ✗ Don't fail immediately on first error

7. LOGGING & DIAGNOSTICS
   ✓ Log every locator attempt
   ✓ Include wait times and success rates
   ✓ Generate recovery recommendations
   ✗ Don't silently fail

דוגמה יישום:
    search_button = create_attribute_based_resilient_locator(
        data_testid="search-submit",
        aria_label="Search",
        css_fallback="button.search-action",
        xpath_fallback="//button[contains(@class, 'search')]",
        description="eBay search submit button"
    )
"""
