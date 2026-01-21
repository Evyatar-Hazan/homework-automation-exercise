# Automation Framework for Automation Test Store

## Description
This project is a robust, modular test automation framework designed to test the **Automation Test Store** e-commerce platform. It is built using **Python**, **Selenium (Undetected Chromedriver)**, and **Pytest**, featuring a custom logging system, smart assertions, and Allure report integration.

The framework is designed to be resilient against bot detection and scalable for complex testing scenarios.

## Key Features
- **Anti-Bot Defenses**: Utilizes `undetected-chromedriver` and custom driver options to bypass bot detection mechanisms.
- **Page Object Model (POM)**: Organizes code into reusable pages (`automation/pages`) for better maintainability.
- **Step-Aware Logging**: Implements a thread-safe, context-aware logging system that integrates seamlessly with Allure reporting steps (`automation/core/logger.py`).
- **Smart Assertions**: Custom `SmartAssert` class provides detailed failure reporting and step verification.
- **Retry Mechanism**: Built-in exponential backoff for handling flaky network operations.
- **Grid & Parallel Support**: Ready for execution on Selenium Grid/Moon and parallel execution via `pytest-xdist`.

## Technologies & Stack
- **Language**: Python 3.12+
- **Web Driver**: Selenium (`undetected-chromedriver`)
- **Test Runner**: Pytest
- **Reporting**: Allure Framework
- **Utilities**: Playwright (included in dependencies for specific utility extensions)

## Project Structure
```text
automation-project1/
├── automation/
│   ├── core/           # Core framework logic (Driver, Logger, Base classes)
│   ├── pages/          # Page Object Models (Locators & Actions)
│   ├── steps/          # Reusable high-level test steps
│   ├── utils/          # Utility functions (Random generators, Human actions)
│   └── reports/        # Generated test reports
├── tests/              # Test suites
├── requirements.txt    # Project dependencies
└── pytest.ini          # Pytest configuration
```

## Prerequisites
- Python 3.12 or higher
- Google Chrome browser installed
- Java (required only for running the Allure server)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd automation-project1
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Browsers (Optional):**
   If using Playwright components:
   ```bash
   playwright install
   ```

## Configuration

The framework uses environment variables for configuration. Defaults are managed in `automation/core/env_config.py`.

### Key Environment Variables
You can set these in your shell or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATS_URL` | Base URL of the application under test | `https://automationteststore.com/` |
| `ATS_TEST_USER_NAME` | Test user login (Recommended) | - |
| `ATS_TEST_PASSWORD` | Test user password (Recommended) | - |
| `GRID_URL` | URL for Selenium Grid/Moon hub | `http://localhost:4444/wd/hub` |
| `USE_GRID` | Set to `True` to use Grid instead of local | `False` |
| `HEADLESS` | Run in headless mode | `False` |

## Usage

### Running Tests
**Run all tests:**
```bash
pytest
```

**Run a specific test suite:**
```bash
pytest tests/test_login.py
```

**Run in parallel (using multiple workers):**
```bash
pytest -n 4
```

### Reports & Logging
The project is configured to generate **Allure** reports.

After running tests, generate and view the report:
```bash
allure serve automation/reports/latest/allure-results
```

Logs are handled by the custom `automation/core/logger.py` module, which ensures that log entries are correctly attached to their respective test steps in the report.

## Coding Conventions
- **Steps**: Use `step_aware_loggerStep` for grouping logical test actions.
- **Assertions**: Always use `SmartAssert` methods (e.g., `SmartAssert.equal`, `SmartAssert.true`) instead of raw `assert` statements for better reporting.
- **Page Objects**: Define locators and page-specific methods in `automation/pages/`.
- **Base Classes**: All tests must inherit from `BaseSeleniumTest` (`automation/core/base_test.py`).

## Error Handling
Failures are automatically captured by the `BaseSeleniumTest` class, which:
1. Logs the error stack trace.
2. Captures a screenshot of the browser state.
3. Attaches the screenshot to the Allure report.

## Known Issues
- The `undetected-chromedriver` may require periodic updates to match the installed Google Chrome version.
- Parallel execution (`pytest -n`) requires ensuring that system resources (CPU/RAM) are sufficient for multiple browser instances.
