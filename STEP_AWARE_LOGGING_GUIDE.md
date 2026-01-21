# 🎯 Step-Aware Logging Guide

## General Overview

The **Step-Aware Logging** system provides a thread-safe mechanism for managing steps in Allure, with automatic attachments under the active step.

---

## 🏗️ Architecture

### New Files
- **`automation/core/step_context.py`** - Step context management using `contextvars`
- **`automation/core/logger.py`** - Added new API: `step_aware_*` functions

### Technologies
- ✅ `contextvars.ContextVar` - Thread/process isolation
- ✅ `allure.step()` - Allure step integration
- ✅ Context managers - Clean resource management

---

## 📚 API Reference

### 1️⃣ `step_aware_loggerStep(step_name, action=None, validate=None)`

Opens a new step. If there's a previous active step - closes it automatically.

**Usage with action:**
```python
from automation.core.logger import step_aware_loggerStep

def login_action():
    # Your login logic
    return "logged_in"

result = step_aware_loggerStep("Step 1: Login", action=login_action)
```

**Usage as context manager:**
```python
with step_aware_loggerStep("Step 2: Navigate to page"):
    # Your code here
    driver.get("https://example.com")
```

---

### 2️⃣ `step_aware_loggerInfo(message)`

Adds an attachment of type `info_log` to the active step.

```python
step_aware_loggerStep("Step 1: Fill form", action=fill_form)
step_aware_loggerInfo("Username field filled")
step_aware_loggerInfo("Password field filled")
```

**Result in Allure HTML:**
```
Step 1: Fill form
 ├── info_log: Username field filled
 ├── info_log: Password field filled
```

---

### 3️⃣ `step_aware_loggerAttach(message, name, attachment_type)`

Adds a custom attachment to the active step.

```python
step_aware_loggerStep("Step 1: API Call", action=make_request)
step_aware_loggerAttach("Response: 200 OK", name="api_response")
step_aware_loggerAttach(screenshot_bytes, name="screenshot", 
                        attachment_type=allure.attachment_type.PNG)
```

---

### 4️⃣ Helper Functions

```python
# Check if currently inside a step
if is_in_step():
    print("Inside a step")

# Get current step name
current_step = get_current_step_name()
print(f"Current step: {current_step}")
```

---

## 🧪 Full Test Example

```python
import pytest
from automation.core.logger import (
    step_aware_loggerStep,
    step_aware_loggerInfo,
    step_aware_loggerAttach
)

class TestLogin:
    
    def test_successful_login(self):
        """Test login flow with step-aware logging."""
        
        # Step 1: Navigate
        with step_aware_loggerStep("Step 1: Navigate to login page"):
            step_aware_loggerInfo("Opening browser")
            step_aware_loggerInfo("URL: https://example.com/login")
            # driver.get("https://example.com/login")
        
        # Step 2: Fill form
        def fill_login_form():
            step_aware_loggerInfo("Username: testuser")
            step_aware_loggerInfo("Password: ********")
            return "form_filled"
        
        result = step_aware_loggerStep("Step 2: Fill login form", 
                                       action=fill_login_form)
        
        # Step 3: Submit
        with step_aware_loggerStep("Step 3: Submit form"):
            step_aware_loggerInfo("Clicking submit button")
            step_aware_loggerAttach("Response: 200 OK", name="submit_response")
        
        # Step 4: Verify
        with step_aware_loggerStep("Step 4: Verify successful login"):
            step_aware_loggerInfo("Checking dashboard visibility")
            step_aware_loggerAttach("Login successful ✅", name="verification")
```

---

## 📊 Result in Allure Report

```
Test: test_successful_login
├── Step 1: Navigate to login page
│   ├── info_log: Opening browser
│   └── info_log: URL: https://example.com/login
├── Step 2: Fill login form
│   ├── info_log: Username: testuser
│   └── info_log: Password: ********
├── Step 3: Submit form
│   ├── info_log: Clicking submit button
│   └── submit_response: Response: 200 OK
└── Step 4: Verify successful login
    ├── info_log: Checking dashboard visibility
    └── verification: Login successful ✅
```

---

## 🔄 Parallel Execution Support

The system supports **pytest-xdist** (parallel execution):

```bash
pytest -n 4  # 4 concurrent workers
```

**How it works:**
- Each worker gets its own `ContextVar`
- No state sharing between workers
- No log mixing between tests

---

## ⚠️ Differences from Existing API

### Old API (Still Active):
```python
from automation.core.logger import loggerStep, loggerInfo

loggerStep("Step 1", action=do_something)
loggerInfo("Message")  # Creates nested step in Allure
```

### New API (step-aware):
```python
from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo

step_aware_loggerStep("Step 1", action=do_something)
step_aware_loggerInfo("Message")  # Attachment under Step 1, not nested step
```

---

## 🚀 Migration Path

**Not mandatory to change existing code!**

You can combine both APIs:

```python
# Legacy
from automation.core.logger import loggerStep, loggerInfo

# New
from automation.core.logger import (
    step_aware_loggerStep,
    step_aware_loggerInfo,
    step_aware_loggerAttach
)

# Mixed usage in a test
def test_mixed():
    loggerStep("Old style step", action=old_action)
    
    with step_aware_loggerStep("New style step"):
        step_aware_loggerInfo("Using new API")
```

---

## 🧹 Best Practices

### ✅ Recommended:
```python
# Opening a step with action
result = step_aware_loggerStep("Step 1", action=do_work)

# Or context manager
with step_aware_loggerStep("Step 2"):
    # code
    pass

# Attachments under step
step_aware_loggerInfo("Progress update")
step_aware_loggerAttach(data, name="result")
```

### ❌ Not Recommended:
```python
# Do not call loggerInfo without an active step
step_aware_loggerInfo("Orphan message")  # Will work, but at test level

# Do not forget to close steps
step_aware_loggerStep("Step 1")  # ⚠️ Requires context manager or action
```

---

## 🔮 Future Features

- [ ] Auto-screenshot on failure
- [ ] Retry wrapper with logging
- [ ] ReportPortal integration
- [ ] Elastic/Kibana export
- [ ] Step duration metrics

---

## 📝 Summary

✅ **Thread-safe** - Supports pytest -n  
✅ **Clean API** - Simple to use  
✅ **Backward compatible** - Does not break existing code  
✅ **Allure integrated** - Correct attachments under steps  
✅ **Production ready** - Ready for immediate use

---

**Created:** 2026-01-21  
**Version:** 1.0.0  
**Author:** Automation Team
