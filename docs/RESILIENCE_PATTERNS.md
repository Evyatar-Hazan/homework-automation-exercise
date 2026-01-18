"""
RESILIENCE PATTERNS DOCUMENTATION
==================================

התמודדות עם שינויים תכופים בממשק GUI
Handling Frequent GUI Changes Through Resilience

"""

# ============================================================================
# 1. PROBLEM STATEMENT
# ============================================================================

"""
PROBLEM: Frequent GUI Changes Break Automation Tests
====================================================

Scenario:
--------
eBay (או כל אתר אחר) משנה את ממשק המשתמש בתדירות:
- CSS classes תשנו כל שבוע (Bootstrap → Tailwind → Custom)
- IDs תשנו כאשר מוצא חדש מחליף את הישן
- HTML structure יוצא עם עדכוני React/Vue
- Selectors שעבדו אתמול - לא עובדים היום

Result:
-------
✗ Tests break immediately (brittle)
✗ שינוי קטן בממשק = שינוי בכל בדיקה
✗ תחזוקה יקרה וחוזרת תמיד
✗ ROI של אוטומציה נמוך מאוד

דוגמה:
------
כאשר eBay עברו מ:
  <button class="btn-primary search-btn">Search</button>
ל:
  <button class="gh-btn" data-testid="gh-btn">
    <svg>...</svg>
  </button>

כל בדיקה עם:
  await page.click('button.btn-primary')  ← BREAKS
או:
  await page.click('xpath=//button[@class="btn-primary"]')  ← BREAKS

"""

# ============================================================================
# 2. SOLUTION ARCHITECTURE
# ============================================================================

"""
RESILIENCE ARCHITECTURE
=======================

Level 1: MULTI-LOCATOR FALLBACK (SmartLocator)
----------------------------------------------
Primary:   Fast but fragile (CSS)
Secondary: Flexible (XPath)
Tertiary:  Reliable (Text/Aria)

Example:
  SEARCH_BUTTON = SmartLocator(
      Locator(CSS, "button#gh-btn"),          ← Fast, specific
      Locator(XPATH, "//button[@aria-label='Search']"),  ← Flexible
      Locator(TEXT, "text=Search"),           ← Reliable
  )

When CSS breaks:
  Attempt 1: button#gh-btn → FAIL (CSS changed)
  Attempt 2: //button[@aria-label='Search'] → SUCCESS ✓
  Test continues to work!


Level 2: ATTRIBUTE-BASED LOCATORS (Most Stable)
-----------------------------------------------
Instead of:
  ✗ .btn-primary-v2 (CSS class = fragile)
  ✗ button:nth-child(3) (position = fragile)

Use:
  ✓ [data-testid="search-button"] (intentional attribute)
  ✓ [aria-label="Search"] (semantic, accessibility-based)
  ✓ [role="button"] (ARIA role)
  ✓ [name="q"] (form attribute)

Why data-testid is best:
  - Intentionally added by developers for testing
  - Won't change with CSS refactors
  - Not affected by UI redesigns
  - Independent of implementation
  - Communicates "this is for testing"


Level 3: ADAPTIVE LEARNING (AdaptiveSmartLocator)
-------------------------------------------------
Track success/failure of each locator:

  Run 1:
    ✓ Locator A (CSS) - SUCCESS, move to front
    ✗ Locator B (XPath) - FAILURE
    ✓ Locator C (Text) - SUCCESS (backup)

  Run 2:
    ✓ Locator A - SUCCESS (front of queue)
    ✗ Locator B
    ✓ Locator C
  
  After learning:
    Order: [A (100%), C (100%), B (0%)]
    Next run tries A first (fastest)


Level 4: ABSTRACTION LAYER
--------------------------
Hide all selectors behind business methods:

  ✓ GOOD (business-focused):
    await page.search("laptop")
    await page.apply_price_filter(50, 200)
    title = await page.get_product_title()

  ✗ BAD (selector-exposed):
    await page.find(SmartLocator(...))
    await page.click(css_selector)
    text = await page.get_text(xpath)

Benefit: Tests never mention selectors.
When selectors change, only Page Object updates needed.


Level 5: RESILIENCE MONITORING
------------------------------
Track failures and detect patterns:

  Failure Pattern Detection:
    - Filter button failed 3 times in last hour
    - Price input worked 100% (reliable)
    - Product title failed 5 times (GUI changed?)

  Alerts:
    🚨 ALERT: Element 'price_filter' failed 5 times. GUI may have changed.

  Reports:
    Generate metrics showing:
    - Which selectors work best
    - When GUI changes occur
    - Recommendations for updates

"""

# ============================================================================
# 3. IMPLEMENTATION PATTERNS
# ============================================================================

"""
PATTERN 1: BASIC SMARTLOCATOR (Multiple Fallbacks)
===================================================

from automation.core.locator import SmartLocator, Locator, LocatorType

SEARCH_BUTTON = SmartLocator(
    Locator(LocatorType.CSS, "button#gh-btn", "eBay search button"),
    Locator(LocatorType.XPATH, "//button[@id='gh-btn']", "By ID"),
    Locator(LocatorType.XPATH, "//button[contains(text(), 'Search')]", "By text"),
)

# Usage in Page Object:
async def click_search(self):
    await self.click(self.SEARCH_BUTTON)
    # Tries CSS first, then XPath, then text match
    # Stops at first success ✓

Risk Mitigation:
  ✓ CSS class changed → XPath tries
  ✓ ID changed → Text match tries
  ✓ Button moved → Still finds by text
  ✗ All text matches changed → Would fail (last resort)


PATTERN 2: ATTRIBUTE-BASED RESILIENT LOCATOR (Most Recommended)
==============================================================

from automation.core.resilience import create_attribute_based_resilient_locator

SEARCH_INPUT = create_attribute_based_resilient_locator(
    data_testid="gh-ac",                        ← Ask developers to add this!
    aria_label="Search for anything",
    css_fallback="input#gh-ac",
    xpath_fallback="//input[@id='gh-ac']",
    description="eBay search input field"
)

Priority order:
  1. data-testid → Won't change with CSS
  2. aria-label → Semantic, accessibility-based
  3. CSS → Fast but fragile
  4. XPath → Flexible, last resort

Real-world scenario:
  Before: <input id="gh-ac" class="search-input-old">
  CSS refactor: <input id="gh-ac" class="search-input-v2">
  
  Status: ✓ STILL WORKS
  Tried: data-testid (not present) → aria-label (matches) ✓


PATTERN 3: SIMPLE RESILIENT LOCATOR HELPER
===========================================

from automation.core.resilience import create_resilient_locator

PRODUCT_PRICE = create_resilient_locator(
    primary_css=".s-item__price",
    xpath_fallback="//span[contains(@class, 'price')]",
    text_fallback="$",  # As last resort
    description="Product price"
)

Usage:
  await page.click(self.PRODUCT_PRICE)
  # Tries: CSS → XPath → Text match


PATTERN 4: ADAPTIVE SMARTLOCATOR (Learning)
==========================================

from automation.core.resilience import AdaptiveSmartLocator

class MyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.adaptive_search = AdaptiveSmartLocator(self.SEARCH_BUTTON)
    
    async def search(self, query):
        # Internally tracks success/failure
        await self.click(self.SEARCH_BUTTON)
        self.adaptive_search.record_success(...)  # Succeeds
    
    async def get_metrics(self):
        # See which selectors work best
        return self.adaptive_search.get_metrics_report()

Benefits:
  ✓ Learns optimal retry order after first few runs
  ✓ Tracks success rates (which ones are breaking?)
  ✓ Generates reports for analysis


PATTERN 5: SELF-HEALING LOCATOR (Advanced)
==========================================

from automation.core.resilience import SelfHealingLocator

class MyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.healer = SelfHealingLocator()
        
        # Register dynamic fallback strategy
        async def find_by_role(page, hint):
            # If primary fails, try finding by role
            return Locator(CSS, '[role="button"]', "Button by role")
        
        self.healer.register_fallback_strategy(find_by_role)

Benefits:
  ✓ When primary selectors fail
  ✓ Tries dynamic fallback strategies
  ✓ Caches successful alternative selectors
  ✗ Advanced pattern, use only when needed

"""

# ============================================================================
# 4. BEST PRACTICES
# ============================================================================

"""
BEST PRACTICE #1: USE DATA-TESTID ATTRIBUTES
==============================================

Coordinate with developers:

Frontend code (React example):
  <button data-testid="search-submit">
    <Icon type="search" />
    Search
  </button>

Test code:
  SEARCH_BUTTON = create_attribute_based_resilient_locator(
      data_testid="search-submit",
      ...
  )

Why:
  ✓ Won't break with CSS changes
  ✓ Clear intent: "this is for testing"
  ✓ Survives HTML restructuring
  ✓ Best practice in industry

Talking point for developers:
  "data-testid is great for testing without breaking on CSS changes."


BEST PRACTICE #2: MULTI-LOCATOR FALLBACK CHAIN
================================================

Always have 2+ strategies per element:

Priority order:
  1. Attribute-based (data-testid, aria-label, role)
  2. CSS (fast, but fragile)
  3. XPath (flexible, slower)
  4. Text (reliable for static text)
  5. Position-based (last resort, most fragile)

Never use:
  ✗ Just CSS (breaks on class changes)
  ✗ Just XPath (breaks on structure changes)
  ✗ Position-based (brittle if DOM reorders)

Example:
  BUTTON = SmartLocator(
      Locator(CSS, "[data-testid='btn']", "Primary"),
      Locator(CSS, "[aria-label='Search']", "Secondary"),
      Locator(XPATH, "//button[contains(text(), 'Search')]", "Fallback"),
      Locator(TEXT, "text=Search", "Last resort"),
  )


BEST PRACTICE #3: ABSTRACTION LAYER (Hide Selectors)
=====================================================

Rule: No selectors in test code

  ✓ GOOD:
    class eBaySearchPage(BasePage):
        SEARCH_INPUT = SmartLocator(...)  ← Locators here
        
        async def search(self, query):
            await self.type(self.SEARCH_INPUT, query)
            await self.click(self.SEARCH_BUTTON)
    
    # Test:
    await page.search("laptop")  ← Business method

  ✗ BAD:
    # Test:
    await page.find(SmartLocator(...))  ← Selectors exposed
    await page.click(css_selector)  ← Maintenance nightmare

Benefit:
  When selector changes:
    ✓ Update in Page Object only
    ✗ Don't touch test code
    ✗ Test code remains clean


BEST PRACTICE #4: COMPREHENSIVE LOGGING
========================================

Log every locator attempt:

  logger.debug(f"Attempt 1/3: CSS={selector}")  ← Which selector
  logger.debug(f"✓ Found with CSS (100ms)")      ← Which worked, how fast
  logger.warning(f"Locator failed: {selector}")  ← What failed
  logger.error(f"All 3 attempts failed")         ← Critical failure

Benefit:
  When test fails, logs show:
  - Which selector worked before
  - Why current selector failed
  - Recommendation for next attempt


BEST PRACTICE #5: MONITORING & REPORTING
=========================================

Track locator effectiveness:

from automation.core.resilience import ResilienceMonitor

monitor = ResilienceMonitor()

# After each test:
monitor.record_failure("search_button", "Timeout after 10s")

# Generate report:
report = monitor.get_failure_report()
# {
#   "search_button": 3 failures,
#   "price_filter": 0 failures,
#   "product_title": 1 failure
# }

Alerts:
  🚨 search_button failed 5 times → GUI probably changed
  ✓ product_title passed 20 times → Locator is reliable

"""

# ============================================================================
# 5. REAL-WORLD SCENARIO
# ============================================================================

"""
SCENARIO: CSS REFACTOR ON EBAY
===============================

Day 1: CSS refactor announced
  eBay is moving from Bootstrap to Tailwind CSS
  All class names will change
  Tests might break

Day 2: CSS refactor deployed
  Old: <button class="btn btn-primary">Search</button>
  New: <button class="px-4 py-2 bg-blue-600">Search</button>

Test Status:

❌ OLD APPROACH (Brittle):
  Selector: "button.btn-primary"
  Result: BROKEN ✗ (class changed)
  Fix required: Update all tests (many files)
  Time to fix: 2 hours
  Cost: High

✅ NEW APPROACH (Resilient):
  SEARCH_BUTTON = SmartLocator(
      Locator(CSS, "[data-testid='search']"),  ← 1st try
      Locator(XPATH, "//button[@aria-label='Search']"),  ← 2nd try
      Locator(TEXT, "text=Search"),  ← 3rd try
  )
  
  Execution:
    Attempt 1: [data-testid='search'] → TIMEOUT (attr exists)
    Attempt 2: //button[@aria-label='Search'] → SUCCESS ✓
    Result: WORKS ✓ (no code changes needed!)
    Time to realize: 15 seconds
    Cost: Zero


STEP-BY-STEP EXECUTION:
-----------------------

1. Test starts: await page.search("laptop")

2. Behind the scenes:
   BasePage.find(SmartLocator):
     for each locator in SmartLocator:
       try:
         create_playwright_locator(locator)
         wait_for(visible, timeout=10s)
         return ✓

3. Attempt 1: [data-testid='search']
   ✓ Locator created
   ✓ Element found
   ✓ Element visible
   ✓ RETURNS locator
   → Skip remaining attempts

4. Test continues normally
   ✓ No test code changes
   ✓ Works despite CSS refactor


WHAT IF ALL FALLBACKS FAIL?
----------------------------

If HTML structure changed significantly:

  SEARCH_BUTTON = SmartLocator(
      Locator(CSS, "[data-testid='search']"),
      Locator(XPATH, "//button[@aria-label='Search']"),
      Locator(TEXT, "text=Search"),
  )
  
  Day 10: Complete HTML restructure
  - data-testid removed
  - aria-label removed
  - Button text changed to "Find Items"
  
  All attempts fail:
    Attempt 1: ✗ data-testid gone
    Attempt 2: ✗ aria-label gone
    Attempt 3: ✗ Text "Search" not found
  
  Result: TimeoutError
  
  Fix: Add new fallback or update existing
    SEARCH_BUTTON = SmartLocator(
        ...,
        Locator(CSS, ".new-search-class"),  ← New selector
        Locator(TEXT, "text=Find Items"),  ← New text
    )
  
  Time to fix: 5 minutes (add 1 locator)
  Test count affected: 1 Page Object (not all tests)

"""

# ============================================================================
# 6. MONITORING & METRICS
# ============================================================================

"""
LOCATOR METRICS TRACKING
========================

Each locator tracked for:

Success Rate:
  = Successes / (Successes + Failures) × 100%
  
  100%: Locator always works (reliable)
  50-80%: Sometimes works, might be breaking
  <50%: Locator is broken, needs fix

Average Wait Time:
  Track how long each locator takes
  CSS usually faster than XPath
  Help optimize retry order

Health Status:
  ✓ Healthy: 80%+ success rate
  ⚠️ Degraded: 50-80% success rate
  ✗ Broken: <50% success rate


EXAMPLE METRICS REPORT:
-----------------------

search_button:
  CSS="button#gh-btn"
    Success Rate: 100% (15/15)
    Avg Wait Time: 45ms
    Status: ✓ HEALTHY

  XPath="//button[@aria-label='Search']"
    Success Rate: 0% (0/15)
    Avg Wait Time: N/A
    Status: ✗ NOT USED

  Text="text=Search"
    Success Rate: 0% (0/15)
    Avg Wait Time: N/A
    Status: ✗ NOT USED

Interpretation:
  → CSS selector is perfect
  → XPath selector not needed (slow fallback)
  → Text selector not needed
  → Reorder: Keep CSS first (optimal)


DETECTING GUI CHANGES:
---------------------

Metric Shifts:
  Before: CSS success = 100%
  After CSS refactor: CSS success = 0%
  Change: Sudden drop = GUI changed

Pattern Detection:
  Filter "price_input":
    Hour 1: 100% success
    Hour 2: 80% success
    Hour 3: 20% success
    Hour 4: 0% success
  
  Trend: Gradual degradation = GUI update ongoing
  Alert: Investigate what changed


RECOMMENDATIONS:
----------------

Low Success Rate → Investigate:
  - Is selector correct?
  - Did GUI change?
  - Is element hidden/off-screen?
  - Wrong timeout value?

High Success Rate for Fallback → Optimize:
  - Move successful fallback to front
  - Remove failing primary selector
  - Helps future tests (faster, more reliable)

GUI Change Detection → Act on:
  - Update failing locators
  - Add new attribute-based locators
  - Coordinate with development team

"""

# ============================================================================
# 7. MIGRATION GUIDE
# ============================================================================

"""
MIGRATING FROM BRITTLE TO RESILIENT LOCATORS
==============================================

Current Code (Brittle):
  class SearchPage:
      def __init__(self, page):
          self.search_button = page.locator("button.btn-primary")
      
      async def search(self, query):
          await self.search_button.click()


Step 1: Extract to SmartLocator
  class SearchPage(BasePage):
      SEARCH_BUTTON = SmartLocator(
          Locator(CSS, "button.btn-primary")
      )


Step 2: Add Fallbacks
  SEARCH_BUTTON = SmartLocator(
      Locator(CSS, "button.btn-primary"),
      Locator(XPATH, "//button[@type='submit']"),
  )


Step 3: Add Attribute-Based
  SEARCH_BUTTON = SmartLocator(
      Locator(CSS, "[data-testid='search']"),
      Locator(CSS, "[aria-label='Search']"),
      Locator(CSS, "button.btn-primary"),
      Locator(XPATH, "//button[@type='submit']"),
  )


Step 4: Use Helper (Recommended)
  SEARCH_BUTTON = create_attribute_based_resilient_locator(
      data_testid="search",
      aria_label="Search",
      css_fallback="button.btn-primary",
      xpath_fallback="//button[@type='submit']",
  )


Step 5: Use in Business Method
  async def search(self, query):
      await self.type(self.SEARCH_INPUT, query)
      await self.click(self.SEARCH_BUTTON)  ← Using SmartLocator


Step 6: (Optional) Add Adaptive Learning
  def __init__(self, page):
      super().__init__(page)
      self.adaptive_btn = AdaptiveSmartLocator(self.SEARCH_BUTTON)
  
  async def get_metrics(self):
      return self.adaptive_btn.get_metrics_report()


Migration Plan:
  Phase 1: Convert critical page objects (30% effort)
  Phase 2: Add fallbacks to all locators (40% effort)
  Phase 3: Add attribute-based locators (20% effort)
  Phase 4: Monitor and optimize (10% effort)

"""

# ============================================================================
# 8. TROUBLESHOOTING
# ============================================================================

"""
COMMON ISSUES & SOLUTIONS
==========================

ISSUE 1: All Locators Fail (Element not found)
==============================================

Causes:
  ✗ Element not on page yet (loading)
  ✗ Element is hidden
  ✗ All selectors are wrong
  ✗ Page changed significantly

Solutions:
  1. Increase timeout:
     await find(locator, timeout_sec=20)
  
  2. Wait for container first:
     await wait_for_element(RESULTS_CONTAINER)
     await find(PRODUCT)
  
  3. Verify selectors:
     Open DevTools → Inspect element
     Try selector manually: document.querySelector("...")
  
  4. Add new locator:
     Locator(CSS, "[new-selector]", "Updated")
  
  5. Take screenshot:
     await page.screenshot(path="debug.png")
     Check what's on page


ISSUE 2: Test Flaky (Sometimes Passes, Sometimes Fails)
=======================================================

Causes:
  ✗ Element appears/disappears
  ✗ Race conditions
  ✗ Timing issues
  ✗ Network delays

Solutions:
  1. Wait for element state:
     await wait_for_element(locator, state="visible")
     await wait_for_element_invisible(loading_spinner)
  
  2. Add explicit waits:
     await page.wait_for_load_state("networkidle")
  
  3. Increase retry timeouts:
     class RetryConfig(max_attempts=5, initial_backoff_ms=1000)
  
  4. Use adaptive backoff:
     Each retry waits longer than previous
     Gives page time to load


ISSUE 3: CSS Changes Break Tests
================================

Scenario:
  CSS class changed: btn-primary → btn-search-v2
  CSS selector fails: "button.btn-primary"

Solution:
  Already have fallback:
    SmartLocator([
        Locator(CSS, "[data-testid='search']"),  ← Tries first
        Locator(CSS, "button.btn-primary"),  ← Fails
        Locator(XPATH, "//button[contains(...)]"),  ← Tries next
    ])
  
  Test works! No changes needed.
  
  If all fail, add new selector:
    Locator(CSS, "[aria-label='Search']")


ISSUE 4: Element Hidden/Off-Screen
=================================

Test tries to click but element not visible

Solution:
  1. Scroll to element:
     await scroll_to_element(locator)
     await click(locator)
  
  2. Wait for visibility:
     await wait_for_element(locator, state="visible")
  
  3. Check visibility:
     is_visible = await is_visible(locator)
     if is_visible:
         await click(locator)


ISSUE 5: XPath Too Slow
=======================

XPath fallback works but too slow

Solution:
  1. Reorder locators (CSS first):
     SmartLocator([
         Locator(CSS, ...),  ← Fast
         Locator(XPATH, ...),  ← Slow
     ])
  
  2. Use adaptive learning:
     Successful CSS moves to front automatically
  
  3. Simplify XPath:
     ✗ //button/ancestor::form/div[2]/button[contains(...)]
     ✓ //button[@aria-label='Search']

"""

# ============================================================================
# 9. ADVANCED PATTERNS
# ============================================================================

"""
PATTERN: SELF-HEALING LOCATORS
==============================

Use when GUI changes are very frequent:

from automation.core.resilience import SelfHealingLocator

healer = SelfHealingLocator()

async def find_by_text_fallback(page, hint):
    # Dynamic fallback: find button containing search text
    buttons = await page.locator("button").all()
    for btn in buttons:
        text = await btn.text_content()
        if "search" in text.lower():
            return Locator(CSS, "[containing text]", "Found via text")
    return None

healer.register_fallback_strategy(find_by_text_fallback)

# Use:
element = await healer.find_with_healing(
    page,
    primary_locator=SEARCH_BUTTON,
    element_hint="search button"
)

Benefit:
  ✓ When primary fails, tries dynamic strategies
  ✓ Caches successful alternatives
  ✓ Self-adapts to UI changes


PATTERN: ATTRIBUTE-BASED DISCOVERY
==================================

Find elements by stable attributes:

from automation.core.resilience import AttributeBasedLocator

# Request from developers:
# <button data-testid="search-submit" aria-label="Search">...</button>

locator = AttributeBasedLocator.by_data_testid("search-submit")
locator = AttributeBasedLocator.by_aria_label("Search")
locator = AttributeBasedLocator.by_role("button", "Search")

Benefit:
  ✓ Semantic meaning
  ✓ Won't break with CSS
  ✗ Requires developer coordination

"""

# ============================================================================
# 10. SUMMARY
# ============================================================================

"""
KEY TAKEAWAYS
=============

1. MULTI-LOCATOR FALLBACK
   ✓ Never rely on single selector
   ✓ Always have CSS → XPath → Text chain
   ✓ Increases resilience from 50% → 95%

2. ATTRIBUTE-BASED LOCATORS
   ✓ Use data-testid (most stable)
   ✓ Use aria-label (semantic)
   ✓ Survives CSS refactors and rewrites

3. ABSTRACTION LAYER
   ✓ Hide all selectors in Page Objects
   ✓ Tests use business methods only
   ✓ Selector changes don't require test updates

4. ADAPTIVE LEARNING
   ✓ Track which selectors work best
   ✓ Optimize retry order automatically
   ✓ Detect GUI changes early

5. COMPREHENSIVE LOGGING
   ✓ Log every attempt
   ✓ Track success rates
   ✓ Generate reports for analysis

6. MONITORING & ALERTS
   ✓ Detect failure patterns
   ✓ Alert on sudden changes
   ✓ Proactive problem detection

דוגמה זה מה שהשתיור אמור להיות!
This is enterprise-grade automation.

"""
