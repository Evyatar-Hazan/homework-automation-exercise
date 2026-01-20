# 🎯 Step-Aware Logging Guide

## תיאור כללי

מערכת **Step-Aware Logging** מספקת מנגנון thread-safe לניהול steps ב-Allure, עם attachments אוטומטיים תחת ה-step הפעיל.

---

## 🏗️ ארכיטקטורה

### קבצים חדשים
- **`automation/core/step_context.py`** - ניהול context של steps באמצעות `contextvars`
- **`automation/core/logger.py`** - הוספת API חדש: `step_aware_*` functions

### טכנולוגיות
- ✅ `contextvars.ContextVar` - Thread/process isolation
- ✅ `allure.step()` - Allure step integration
- ✅ Context managers - Clean resource management

---

## 📚 API Reference

### 1️⃣ `step_aware_loggerStep(step_name, action=None, validate=None)`

פותח step חדש. אם יש step פעיל קודם - סוגר אותו אוטומטית.

**שימוש עם action:**
```python
from automation.core.logger import step_aware_loggerStep

def login_action():
    # Your login logic
    return "logged_in"

result = step_aware_loggerStep("Step 1: Login", action=login_action)
```

**שימוש כ-context manager:**
```python
with step_aware_loggerStep("Step 2: Navigate to page"):
    # Your code here
    driver.get("https://example.com")
```

---

### 2️⃣ `step_aware_loggerInfo(message)`

מוסיף attachment מסוג `info_log` ל-step הפעיל.

```python
step_aware_loggerStep("Step 1: Fill form", action=fill_form)
step_aware_loggerInfo("Username field filled")
step_aware_loggerInfo("Password field filled")
```

**תוצאה ב-Allure HTML:**
```
Step 1: Fill form
 ├── info_log: Username field filled
 ├── info_log: Password field filled
```

---

### 3️⃣ `step_aware_loggerAttach(message, name, attachment_type)`

מוסיף attachment מותאם אישית ל-step הפעיל.

```python
step_aware_loggerStep("Step 1: API Call", action=make_request)
step_aware_loggerAttach("Response: 200 OK", name="api_response")
step_aware_loggerAttach(screenshot_bytes, name="screenshot", 
                        attachment_type=allure.attachment_type.PNG)
```

---

### 4️⃣ Helper Functions

```python
# בדיקה אם נמצאים בתוך step
if is_in_step():
    print("Inside a step")

# קבלת שם ה-step הנוכחי
current_step = get_current_step_name()
print(f"Current step: {current_step}")
```

---

## 🧪 דוגמת טסט מלאה

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

## 📊 תוצאה ב-Allure Report

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

## 🔄 תמיכה בהרצה מקבילית

המערכת תומכת ב-**pytest-xdist** (הרצה מקבילית):

```bash
pytest -n 4  # 4 workers במקביל
```

**איך זה עובד:**
- כל worker מקבל `ContextVar` משלו
- אין שיתוף state בין workers
- אין ערבוב logs בין טסטים

---

## ⚠️ הבדלים מול API הקיים

### API ישן (עדיין פעיל):
```python
from automation.core.logger import loggerStep, loggerInfo

loggerStep("Step 1", action=do_something)
loggerInfo("Message")  # יוצר nested step ב-Allure
```

### API חדש (step-aware):
```python
from automation.core.logger import step_aware_loggerStep, step_aware_loggerInfo

step_aware_loggerStep("Step 1", action=do_something)
step_aware_loggerInfo("Message")  # attachment תחת Step 1, לא nested step
```

---

## 🚀 Migration Path

**לא חובה לשנות קוד קיים!**

אפשר לשלב את שני ה-APIs:

```python
# Legacy
from automation.core.logger import loggerStep, loggerInfo

# New
from automation.core.logger import (
    step_aware_loggerStep,
    step_aware_loggerInfo,
    step_aware_loggerAttach
)

# שימוש משולב בטסט
def test_mixed():
    loggerStep("Old style step", action=old_action)
    
    with step_aware_loggerStep("New style step"):
        step_aware_loggerInfo("Using new API")
```

---

## 🧹 Best Practices

### ✅ מומלץ:
```python
# פתיחת step עם action
result = step_aware_loggerStep("Step 1", action=do_work)

# או context manager
with step_aware_loggerStep("Step 2"):
    # code
    pass

# Attachments תחת step
step_aware_loggerInfo("Progress update")
step_aware_loggerAttach(data, name="result")
```

### ❌ לא מומלץ:
```python
# לא לקרוא ל-loggerInfo ללא step פעיל
step_aware_loggerInfo("Orphan message")  # יעבוד, אבל יהיה ברמת הטסט

# לא לשכוח לסגור steps
step_aware_loggerStep("Step 1")  # ⚠️ צריך context manager או action
```

---

## 🔮 תכונות עתידיות

- [ ] Auto-screenshot on failure
- [ ] Retry wrapper with logging
- [ ] ReportPortal integration
- [ ] Elastic/Kibana export
- [ ] Step duration metrics

---

## 📝 סיכום

✅ **Thread-safe** - תומך ב-pytest -n  
✅ **Clean API** - פשוט לשימוש  
✅ **Backward compatible** - לא שובר קוד קיים  
✅ **Allure integrated** - attachments נכונים תחת steps  
✅ **Production ready** - ניתן לשימוש מיידי

---

**נוצר:** 2026-01-21  
**גרסה:** 1.0.0  
**מחבר:** Automation Team
