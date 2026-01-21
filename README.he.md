# Automation Framework for Automation Test Store

## תיאור (Description)
פרויקט זה הוא תשתית אוטומציה מודולרית ויציבה לבדיקת פלטפורמת המסחר **Automation Test Store**. התשתית בנויה על גבי **Python**, **Selenium (Undetected Chromedriver)** ו-**Pytest**, וכוללת מערכת לוגים מותאמת אישית, בדיקות חכמות (Smart Assertions) ואינטגרציה מלאה עם דוחות Allure.

המערכת תוכננה להיות עמידה בפני מנגנוני זיהוי בוטים וסקיילבילית עבור תרחישי בדיקה מורכבים.

## פיצ'רים מרכזיים (Key Features)
- **הגנות Anti-Bot**: שימוש ב-`undetected-chromedriver` ובקונפיגורציות דפדפן ייחודיות לעקיפת חסימות.
- **Page Object Model (POM)**: ארגון הקוד בדפים (`automation/pages`) לתחזוקה קלה ושימוש חוזר.
- **Step-Aware Logging**: מערכת לוגים בטוחה (Thread-safe) המקשרת אוטומטית כל לוג לצעד (Step) הרלוונטי בדו"ח Allure (`automation/core/logger.py`).
- **Smart Assertions**: מחלקת `SmartAssert` ייעודית המספקת פירוט מלא במקרה של כישלון.
- **מנגנון Retry**: ניהול חזרות (Exponential Backoff) להתמודדות עם בעיות רשת או אלמנטים לא יציבים.
- **תמיכה ב-Grid ומקביליות**: מוכן להרצה על Selenium Grid/Moon והרצה מקבילית באמצעות `pytest-xdist`.

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

## התקנה (Installation)

1. **שכפול ה-Repository:**
   ```bash
   git clone <repository-url>
   cd automation-project1
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

4. **התקנת דפדפנים (אופציונלי):**
   במידה ומשתמשים ברכיבי Playwright:
   ```bash
   playwright install
   ```

## הגדרות (Configuration)

התשתית משתמשת במשתני סביבה (Environment Variables). ערכי ברירת המחדל מנוהלים ב-`automation/core/env_config.py`.

### משתנים חשובים
ניתן להגדיר אותם בטרמינל או בקובץ `.env`:

| משתנה | תיאור | ברירת מחדל |
|-------|-------|------------|
| `ATS_URL` | כתובת האתר הנבדק | `https://automationteststore.com/` |
| `ATS_TEST_USER_NAME` | שם משתמש לבדיקה (מומלץ) | - |
| `ATS_TEST_PASSWORD` | סיסמה לבדיקה (מומלץ) | - |
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

**הרצה במקביל (עם מספר Workers):**
```bash
pytest -n 4
```

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
