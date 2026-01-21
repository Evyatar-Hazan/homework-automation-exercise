# Automation Framework for Automation Test Store

## תיאור (Description)
פרויקט זה הוא תשתית אוטומציה מודולרית ויציבה לבדיקת פלטפורמת המסחר **Automation Test Store**. פותח כפתרון עבור **תרגיל מפתח אוטומציה בכיר**, ומדגים יכולות מתקדמות בהתמודדות עם אלמנטים דינמיים, עמידות וארכיטקטורה נקייה.

המערכת תוכננה להיות עמידה בפני מנגנוני זיהוי בוטים וכוללת מנגנוני **Self-Healing** ו-**Smart Assertions**.

## ארכיטקטורה ועיצוב (Architecture)
הפתרון מממש ארכיטקטורת שכבות המאפשרת תחזוקה וסקיילביליות:

- **Page Object Model (POM)**: הפרדה מלאה בין אלמנטים ואינטראקציות לבין לוגיקת הבדיקות (`automation/pages`).
- **OOP & SRP**: הקפדה על עקרונות תכנות מונחה עצמים ואחריות יחידה.
  - `SmartLocator`: ניהול אסטרטגיות איתור אלמנטים (ID, CSS, XPath, Text).
  - `Logger`: לוגר חכם המקושר לצעדי הבדיקה בדוח.
  - `BaseTest`: ניהול מחזור חיים של הדרייבר.
- **Utils**: פונקציות עזר לייצור דאטה, ניתוח מחירים ואינטראקציות יציבות.

## פיצ'רים מרכזיים ועמידות (Key Features & Robustness)
- **Smart Locators & Self-Healing**: שימוש במנגנון ריבוי אסטרטגיות (CSS -> XPath -> Text) למציאת אלמנטים. אם סלקטור אחד נכשל, המערכת מנסה אוטומטית את הבא בתור ללא הכשלת הטסט.
- **Resilience**: 
  - **מנגנון Retry**: חזרות חכמות (Exponential Backoff) להתמודדות עם בעיות רשת.
  - **הגנות Anti-Bot**: שימוש ב-`undetected-chromedriver`.
- **טיפול בתוכן דינמי**:
  - **בחירת וריאנטים**: זיהוי אוטומטי ובחירה רנדומלית של אפשרויות מוצר (צבע, גודל) במהלך ההוספה לסל.
  - **בדיקת מחירים**: פרסור חכם של מחירים כולל מטבעות וביצוע חישובים.
- **תמיכה ב-Grid ומקביליות**: הרצה על Selenium Grid ושימוש ב-`pytest-xdist`.

## הנחות ומגבלות (Limitations & Assumptions)
- **דפדפן**: מותאם עבור **Google Chrome**.
- **משתמשים**: מניח קיום משתמש בדיקה תקין ב-`.env` או `config/test_data.json`.
- **רשת**: תלות בזמינות האתר `automationteststore.com`.
- **Data**: הטסט `test_add_items_to_cart` מסתמך על כתובות בקובץ הקונפיגורציה, אך מכיל גיבוי למקרה שאין.

## טכנולוגיות (Stack)
- **שפה**: Python 3.12+
- **אוטומציה לדפדפן**: Selenium (`undetected-chromedriver`)
- **הרצת בדיקות**: Pytest
- **דוחות**: Allure Framework
- **תוספות**: Playwright (כלול בתלויות עבור כלי עזר ספציפיים)

## מבנה הפרויקט (Project Structure)
```text
automation-project1/
├── automation/
│   ├── core/           # ליבת התשתית (דרייבר, לוגר, מחלקות בסיס)
│   ├── pages/          # Page Objects (לוקייטורים ופעולות)
│   ├── steps/          # צעדי בדיקה לשימוש חוזר (Reusables)
│   ├── utils/          # כלי עזר (גנרטורים, פעולות אנושיות)
│   └── reports/        # דוחות ריצה
├── tests/              # טסטים (Suites)
├── requirements.txt    # תלויות הפרויקט
└── pytest.ini          # הגדרות Pytest
```

## דרישות קדם (Prerequisites)
- Python 3.12 ומעלה
- דפדפן Google Chrome מותקן
- Java (נדרש רק עבור הרצת שרת Allure לצפייה בדוחות)
- **משתמש רשום**: יש לבצע רישום ידני באתר [Automation Test Store](https://automationteststore.com/) כדי לייצר שם משתמש וסיסמה עבור הבדיקות.

## התקנה (Installation)

1. **שכפול ה-Repository:**
   ```bash
   git clone https://github.com/Evyatar-Hazan/homework-automation-exercise.git
   cd homework-automation-exercise
   ```

2. **יצירת סביבה וירטואלית (Virtual Environment):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **התקנת תלויות:**
   ```bash
   pip install -r requirements.txt
   ```
   > **הערה**: `setuptools` כלול כדי לתמוך ב-`undetected-chromedriver` ב-Python 3.12 ומעלה.

4. **התקנת דפדפנים:**
   התשתית משתמשת ברכיבי Playwright, יש להתקין דפדפנים עם תלויות מערכת:
   ```bash
   playwright install --with-deps
   ```

## הגדרות (Configuration)

התשתית משתמשת במשתני סביבה (Environment Variables). ערכי ברירת המחדל מנוהלים ב-`automation/core/env_config.py`.

### משתנים חשובים
ניתן להגדיר אותם בטרמינל או בקובץ `.env`:

| משתנה | תיאור | ברירת מחדל |
|-------|-------|------------|
| `ATS_URL` | כתובת האתר הנבדק | `https://automationteststore.com/` |
| `ATS_TEST_USER_NAME` | שם משתמש לבדיקה (**חובה**) | - |
| `ATS_TEST_PASSWORD` | סיסמה לבדיקה (**חובה**) | - |
| `GRID_URL` | כתובת Selenium Grid Hub | `http://localhost:4444/wd/hub` |
| `USE_GRID` | האם להשתמש ב-Grid במקום הרצה מקומית | `False` |
| `HEADLESS` | הרצה ללא ממשק גרפי | `False` |

## שימוש (Usage)

### הרצת בדיקות
**הרצת כל הבדיקות:**
```bash
pytest
```

**הרצת קובץ בדיקה ספציפי:**
```bash
pytest tests/test_login.py
```

### הרצה מקבילית ובדיקות דפדפנים (Parallel & Cross-Browser)

**1. הרצה מקבילית (Parallel Execution):**
להרצת בדיקות במקביל וחיסכון משמעותי בזמן, השתמש ב-`pytest-xdist`:
```bash
pytest -n 4  # מריץ 4 בדיקות במקביל באמצעות 4 תהליכונים
```

**2. בדיקות דפדפנים וגרסאות (Cross-Browser):**
התשתית כוללת יכולת **Browser Matrix** מתקדמת. ניתן להריץ את כל הטסטים על מספר דפדפנים וגרסאות בפקודה אחת באמצעות דגל ה-`--browser-matrix`.

**תחביר:** `--browser-matrix="browser:version,browser:version"`

**דוגמה:**
```bash
# הרצת הבדיקות על כרום (אחרון), פיירפוקס (121) ואדג' (אחרון)
pytest --browser-matrix="chrome:latest,firefox:121,edge:latest"
```

**שילוב מקביליות ומטריצה:**
ניתן לשלב את שתי היכולות לביצוע רגרסיה מקיפה ומהירה:
```bash
# מריץ על מספר דפדפנים במקביל באמצעות 6 Workers
pytest -n 6 --browser-matrix="chrome:latest,firefox:latest,edge:latest"
```

> **הערה**: לשימוש בגרסאות דפדפן ספציפיות, וודא שיש לך את הדרייברים המתאימים או שהפרויקט מחובר ל-**Selenium Grid/Moon** (מוגדר דרך `GRID_URL`).

### דוחות ולוגים
הפרויקט מוגדר להפיק דוחות **Allure**.

לאחר הרצת בדיקות, להפקת וצפייה בדו"ח:
```bash
allure serve automation/reports/latest/allure-results
```

לוגים מנוהלים על ידי המודול `automation/core/logger.py`, שמבטיח שכל שורת לוג מקושרת לצעד (Step) הנכון בדו"ח הסופי.

## מוסכמות פיתוח (Coding Conventions)
- **Steps**: יש להשתמש ב-`step_aware_loggerStep` עבור כל פעולה לוגית בטסט.
- **Assertions**: יש להשתמש תמיד ב-`SmartAssert` (למשל `SmartAssert.equal`) במקום `assert` רגיל, לקבלת לוגים ברורים.
- **Page Objects**: לוקייטורים ופעולות דף יוגדרו אך ורק תחת `automation/pages/`.
- **מחלקות בסיס**: כל טסט חייב לרשת מ-`BaseSeleniumTest` (`automation/core/base_test.py`).

## טיפול בשגיאות (Error Handling)
כישלונות נתפסים אוטומטית על ידי `BaseSeleniumTest`, אשר מבצע:
1. רישום ה-Stack Trace בלוג.
2. צילום מסך (Screenshot) של מצב הדפדפן.
3. צירוף צילום המסך לדו"ח ה-Allure.

## בעיות ידועות (Known Issues)
- שימוש ב-`undetected-chromedriver` עשוי לדרוש עדכונים תקופתיים כדי להתאים לגרסת ה-Chrome המותקנת במכונה.
- הרצה מקבילית (`pytest -n`) דורשת משאבי מערכת (CPU/RAM) מספקים עבור מספר דפדפנים בו-זמנית.
