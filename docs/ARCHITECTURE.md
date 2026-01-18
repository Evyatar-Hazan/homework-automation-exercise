# 🏗️ Architecture Overview

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      TEST LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ tests/test_*.py - Business Logic Tests (Pure Python)     │   │
│  │ - No Playwright knowledge                                │   │
│  │ - No CSS selectors                                       │   │
│  │ - No timeout handling                                    │   │
│  │ Example: await my_page.login("user", "pass")            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PAGE OBJECT MODEL LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ automation/pages/*.py - Business Abstractions            │   │
│  │ - Inherit from BasePage                                  │   │
│  │ - Define UI elements as SmartLocators                    │   │
│  │ - Implement high-level business methods                  │   │
│  │ Example: async def login(self, email, password): ...     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           CORE INFRASTRUCTURE LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  BasePage - Playwright Interaction Layer                 │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │ Methods: find, click, type, wait_for, etc.        │   │   │
│  │  │ - Handles all Playwright interactions             │   │   │
│  │  │ - Integrates SmartLocator                         │   │   │
│  │  │ - Integrates Retry/Backoff                        │   │   │
│  │  │ - Integrates HumanActions                         │   │   │
│  │  │ - Auto screenshots on failure                     │   │   │
│  │  │ - Full logging                                    │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
       ↓                    ↓                    ↓
   ┌────────────┐    ┌──────────────┐    ┌────────────────┐
   │SmartLocator│    │Retry/Backoff │    │ HumanActions   │
   │with Fallback│   │with Exponential│  │- Randomization │
   │            │    │Backoff        │    │- Anti-Bot      │
   │- CSS       │    │              │    │- Delays        │
   │- XPath     │    │- Retryable    │    │- Typing Speed  │
   │- Text      │    │  Error detect │    │- Mouse moves   │
   │            │    │- Retry logic  │    │                │
   └────────────┘    └──────────────┘    └────────────────┘
       ↓                    ↓                    ↓
   ┌────────────┐    ┌──────────────┐    ┌────────────────┐
   │  Locator   │    │ RetryConfig  │    │RandomUtils     │
   │  & Logging │    │ & Decorators │    │                │
   └────────────┘    └──────────────┘    │- User agents   │
                                          │- Viewports     │
                                          │- Random data   │
                                          └────────────────┘
```

## Execution Flow - How Requests Travel Through Layers

```
Test calls Page Object method
    │
    └──→ MyPage.login("user@example.com", "password")
         │
         └──→ self.type(EMAIL_INPUT, email)  [Page Object]
              │
              └──→ BasePage.type(locator, text)  [Core Layer]
                   │
                   ├──→ SmartLocator.get_all_locators()
                   │    └──→ Try CSS selector
                   │    └──→ On failure, try XPath
                   │    └──→ On failure, try Text
                   │
                   ├──→ Retry Decorator Applied
                   │    ├──→ Attempt 1: Find element
                   │    ├──→ If timeout → Wait exponential backoff
                   │    ├──→ Attempt 2: Find element
                   │    ├──→ If timeout → Wait exponential backoff
                   │    └──→ Attempt 3: Find element (final)
                   │
                   ├──→ HumanActions.get_typing_delay()
                   │    └──→ Return random delay (20-100ms)
                   │
                   └──→ Playwright.type(char) + delay loop
                        └──→ Logs every step
                        └──→ Screenshots on failure

                        ✓ Character typed with human delay
```

## Key Design Principles

### 1. Infrastructure First
- Tests should NOT know about Playwright
- Tests should NOT know about selectors
- Tests should NOT know about timeouts
- Tests focus on business logic only
- Infrastructure handles all technical details

### 2. Separation of Concerns
```
┌─────────────────┐
│ Test Layer      │  What: Business logic
│ (Pure Python)   │  Where: tests/*.py
└─────────────────┘

┌─────────────────┐
│ Page Objects    │  What: UI abstraction
│ (POM Pattern)   │  Where: automation/pages/*.py
└─────────────────┘

┌─────────────────┐
│ Core Layer      │  What: Playwright interaction
│ (Infrastructure)│  Where: automation/core/*.py
└─────────────────┘

┌─────────────────┐
│ Support Layer   │  What: Helper utilities
│ (Utils)         │  Where: automation/utils/*.py
└─────────────────┘
```

### 3. Resilience by Default
Every action automatically includes:
- ✓ Retry with exponential backoff
- ✓ SmartLocator fallback selectors
- ✓ Human-like behavior (delays, typing speed)
- ✓ Comprehensive logging
- ✓ Screenshots on failure

### 4. Configuration-Driven
```
YAML Configuration → DriverFactory → Playwright
                  → BasePage → All methods
                  → HumanActions → Delays
                  → Logging → Output
```

## SmartLocator Fallback Strategy

```
Element not found?

SmartLocator has multiple selectors:
[0] CSS:   #login-btn
[1] XPath: //button[@id='login']
[2] Text:  text=Log In

Execution:
Try [0] with timeout 15s
  └─ FAILED (selector mismatch)
    │
    └─→ Log warning and wait backoff
        │
        └─→ Try [1] with timeout 15s
            └─ FAILED (element not in DOM yet)
              │
              └─→ Log warning and wait backoff
                  │
                  └─→ Try [2] with timeout 15s
                      └─ SUCCESS ✓
                        │
                        └─→ Return Locator
                            │
                            └─→ Continue execution
```

## Retry & Backoff Strategy

```
Action fails with TimeoutError

Is it retryable? (Check error message)
  └─ NO → Raise immediately
  └─ YES → Continue

attempt_number = 0
max_attempts = 3

Loop:
  Attempt 1:
    └─ Try action
      └─ FAILED: Timeout
       └─ Calculate backoff: 0.5s * (2^0) = 0.5s
        └─ Sleep 0.5s
         └─ Log warning
          │
          └─→ Continue to Attempt 2

  Attempt 2:
    └─ Try action
      └─ FAILED: DOM detached
       └─ Calculate backoff: 0.5s * (2^1) = 1.0s
        └─ Sleep 1.0s
         └─ Log warning
          │
          └─→ Continue to Attempt 3

  Attempt 3:
    └─ Try action
      └─ SUCCESS ✓
       └─ Return result
```

## Human Actions - Anti-Bot Simulation

```
await page.click(element)

Without HumanActions:
  - Instant click
  - Bot-like behavior
  - High detection risk

With HumanActions:
  - Pre-click delay: random(100-500ms)
  - Slight offset from center: ±10px
  - Post-click delay: random(100-500ms)
  - Network idle wait: random(200-500ms)
  - Result: Human-like clicking
```

```
await page.type(element, "password123")

Without HumanActions:
  - Type "password123" instantly (25ms)
  - Bot-like behavior
  - High detection risk

With HumanActions:
  - Type 'p' → delay random(20-100ms)
  - Type 'a' → delay random(20-100ms)
  - Type 's' → delay random(20-100ms)
  - ... (continues for all chars)
  - Result: Human-like typing (varies by speed)
```

## Configuration Cascade

```
YAML Configuration
       ↓
DriverFactory._load_config()
       ↓
Used by:
├─→ BasePage (timeouts)
├─→ HumanActions (delays)
├─→ Logging (level, format)
├─→ Browser (headless, args)
└─→ Retry (max attempts, backoff)
```

## File Organization Logic

```
automation/
├── core/           ← ALL Playwright interaction
│   ├── base_page.py        ← ONLY layer touching Playwright
│   ├── driver_factory.py    ← Browser/Context/Page creation
│   ├── locator.py           ← Selector management
│   ├── retry.py             ← Retry logic
│   └── logger.py            ← Unified logging
│
├── utils/          ← SUPPORT functions (not Playwright)
│   ├── human_actions.py     ← Anti-bot behavior
│   └── random_utils.py      ← Data generation
│
├── config/         ← EXTERNAL configuration (no code)
│   ├── env.yaml
│   └── grid.yaml
│
├── pages/          ← USER Page Objects (inherit BasePage)
│   └── (user creates these)
│
├── tests/          ← USER Tests (pure business logic)
│   └── (user creates these)
│
└── reports/        ← OUTPUT (logs, screenshots, traces)
    ├── logs/
    ├── screenshots/
    ├── traces/
    └── videos/
```

## Why This Architecture?

### Problem: Bot Detection on Modern Sites
- eBay, Amazon, etc. actively detect automation
- Traditional automation is easily detected
- Retry failures cost time and resources
- Brittle tests fail on minor selector changes

### Solution: Infrastructure-First Design
1. **Resilience** → Retry + Backoff + Fallback selectors
2. **Anti-Bot** → Human behavior simulation + randomization
3. **Maintainability** → Clear separation of concerns
4. **Scalability** → Easy to add features without breaking tests
5. **Observability** → Comprehensive logging throughout

### Benefits
- ✓ Tests focus on business logic (higher readability)
- ✓ Infrastructure handles complexity (lower maintenance)
- ✓ Automatic resilience (no manual retry in tests)
- ✓ Anti-bot by default (less detection)
- ✓ Configuration-driven (easy customization)

## Extension Points for Users

### Adding New Page Objects
```python
from automation.core import BasePage, SmartLocator, Locator, LocatorType

class MyPage(BasePage):
    MY_ELEMENT = SmartLocator(...)
    
    async def my_action(self):
        # Your business logic using SmartLocator
        await self.click(self.MY_ELEMENT)
```

### Adding Custom Behaviors
```python
class MyPage(BasePage):
    async def complex_action(self):
        # Combine multiple BasePage methods
        # Infrastructure handles all retry/human behavior
        await self.type(self.EMAIL, "user@example.com")
        await self.click(self.SUBMIT)
        await self.wait_for_navigation()
```

### Adjusting Configuration
```yaml
# automation/config/env.yaml
human_behavior:
  typing_speed_min_ms: 10  # Faster typing
  click_delay_min_ms: 50   # Shorter delays
```

## Summary

This architecture provides:

1. **Clean Separation** - Tests, Pages, Core, Utils clearly separated
2. **Automatic Resilience** - Retry, fallback, human behavior built-in
3. **Scalability** - Easy to add tests without touching infrastructure
4. **Anti-Bot** - Human-like behavior reduces detection
5. **Maintainability** - Changes in selectors only affect Page Objects
6. **Observability** - Comprehensive logging for debugging
7. **Configuration** - YAML-based, no hardcoding

The result: Enterprise-grade automation that works on sites with bot detection.
