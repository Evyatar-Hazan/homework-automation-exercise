# Automation Framework for Automation Test Store

## Description
This project is a robust, modular test automation framework designed to test the **Automation Test Store** e-commerce platform. It is developed as a solution for the **Senior Automation Developer Exercise**, demonstrating advanced capabilities in handling dynamic web elements, resilience, and clean architecture.

The framework is designed to be resilient against bot detection and scalable for complex testing scenarios, implementing **Self-Healing mechanics** and **Smart Assertions**.

## Architecture & Design
The solution implements a layered architecture enabling high maintainability and scalability:

- **Page Object Model (POM)**: UI elements and interactions are strictly separated from test logic, located in `automation/pages/`.
- **OOP & SRP**: Adheres to Object-Oriented Programming and Single Responsibility Principles.
  - `SmartLocator`: Handles distinct strategies for finding elements (ID, CSS, XPath, Text).
  - `Logger`: Context-aware logging attached to report steps.
  - `BaseTest`: Manages driver lifecycle and setup/teardown.
- **Utils**: Helper functions for random data generation, price parsing, and robust interactions.

## Key Features & Robustness
- **Smart Locators & Self-Healing**: Utilizes a multi-strategy approach (CSS -> XPath -> Text) to find elements. If one selector fails, the framework automatically tries the next without failing the test.
- **Resilience**: 
  - **Retry Mechanism**: Built-in exponential backoff for flaky elements.
  - **Anti-Bot Defenses**: Uses `undetected-chromedriver` to bypass bot detection.
- **Dynamic Content Handling**:
  - **Variant Selection**: Automatically detects and randomly selects available product options (Size, Color) during the add-to-cart flow.
  - **Price Validation**: robust parsing of currency strings to perform arithmetic assertions.
- **Grid & Parallel Support**: Ready for execution on Selenium Grid/Moon and parallel execution via `pytest-xdist`.

## Limitations & Assumptions
- **Browser**: Optimized for **Google Chrome** (Headless or GUI).
- **User Credentials**: Assumes valid test user credentials are provided in `.env` or `config/test_data.json`.
- **Network**: Depends on the availability of `automationteststore.com`.
- **Data**: The `test_add_items_to_cart` test relies on product URLs defined in `test_data.json` but has fallback URLs if not provided.

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
- **Registered Account**: You must manually register on [Automation Test Store](https://automationteststore.com/) to create a valid user and password for the tests.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Evyatar-Hazan/homework-automation-exercise.git
   cd homework-automation-exercise
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
   > **Note**: `setuptools` is included to support `undetected-chromedriver` on Python 3.12+.

4. **Setup Environment Variables:**
   Copy the example and edit with your credentials (requires [manual registration](#prerequisites)):
   ```bash
   cp .env.example .env
   # Open .env and set ATS_TEST_USER_NAME and ATS_TEST_PASSWORD
   ```

5. **Install Browsers:**
   Install browsers with system dependencies (may require **sudo** on Linux):
   ```bash
   # On Linux:
   sudo playwright install-deps
   playwright install
   
   # Or with one command:
   # playwright install --with-deps
   ```

## Configuration

The framework uses environment variables for configuration. Defaults are managed in `automation/core/env_config.py`.

### Key Environment Variables
You can set these in your shell or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATS_URL` | Base URL of the application under test | `https://automationteststore.com/` |
| `ATS_TEST_USER_NAME` | Test user login (**Required**) | - |
| `ATS_TEST_PASSWORD` | Test user password (**Required**) | - |
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

### Parallel Execution & Cross-Browser Testing

**1. Parallel Execution:**
To run tests in parallel and significantly reduce execution time, use `pytest-xdist`:
```bash
pytest -n 4  # Runs 4 tests in parallel using 4 worker processes
```

**2. Cross-Browser & Multi-Version Testing:**
The framework features a powerful **Browser Matrix** capability. You can run your entire test suite against multiple browsers and versions in a single command using the `--browser-matrix` flag.

**Syntax:** `--browser-matrix="browser:version,browser:version"`

**Example:**
```bash
# Run all tests on Chrome (Latest), Firefox (v121), and Edge (Latest)
pytest --browser-matrix="chrome:latest,firefox:121,edge:latest"
```

**Combining Parallel & Matrix:**
You can combine both to run a massive cross-browser regression suite in parallel:
```bash
# Runs tests on multiple browsers, spread across 6 parallel workers
pytest -n 6 --browser-matrix="chrome:latest,firefox:latest,edge:latest"
```

> **Note**: For specific browser versions, ensure you have the corresponding drivers installed or are connected to a **Selenium Grid/Moon** instance (configured via `GRID_URL`).

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
