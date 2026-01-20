"""
Conftest.py - Global Test Configuration
=========================================

Pytest will automatically discover and load this file.
Used for:
- Global fixtures
- Hooks
- Configuration
- Parallel execution with isolated reports
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Only import AutomationLogger if the automation module exists and doesn't depend on Playwright
try:
    from automation.core import AutomationLogger, get_environment_config, reset_environment_config
except (ImportError, ModuleNotFoundError):
    # Fall back to simple logging if automation module is not available
    class AutomationLogger:
        @staticmethod
        def configure(**kwargs):
            pass
    
    def get_environment_config():
        return None
    
    def reset_environment_config():
        pass

# Import browser matrix utilities
try:
    from automation.utils.browser_matrix import BrowserMatrix, BrowserConfig
except (ImportError, ModuleNotFoundError):
    BrowserMatrix = None
    BrowserConfig = None


# ============================================================
# Global Variables for Report Management
# ============================================================

UNIQUE_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
WORKER_REPORTS_DIRS = {}  # Map worker names to their report directories


def get_worker_allure_dir(worker_id=None):
    """
    Get isolated Allure results directory for this worker.
    
    In parallel execution (pytest-xdist):
    - Each worker gets its own report directory
    - Example: automation/reports/20250119_143022_worker0/allure-results
    
    In sequential execution:
    - Unique directory for this run: automation/reports/20250119_143022/allure-results
    
    Args:
        worker_id: pytest-xdist worker ID (None if not using xdist)
    
    Returns:
        Path to allure-results directory
    """
    if worker_id and worker_id != "master":
        # Parallel execution - each worker gets isolated directory
        run_dir = project_root / "automation" / "reports" / f"{UNIQUE_RUN_ID}_{worker_id}"
    else:
        # Sequential execution - unique directory for this run
        run_dir = project_root / "automation" / "reports" / UNIQUE_RUN_ID
    
    allure_dir = run_dir / "allure-results"
    allure_dir.mkdir(exist_ok=True, parents=True)
    
    return allure_dir


def pytest_configure(config):
    """Configure pytest and load infrastructure configuration."""
    # Get browser matrix if specified
    matrix_string = config.getoption("browser_matrix")
    
    # Load infrastructure configuration (Grid/Browser settings from .env)
    env_config = get_environment_config()
    
    # Print infrastructure configuration
    print(f"\n{'='*80}")
    print(f"🏗️  INFRASTRUCTURE CONFIGURATION")
    print(f"{'='*80}")
    if env_config:
        print(f"Grid Enabled: {env_config.use_grid}")
        print(f"Grid URL: {env_config.grid_url}")
        print(f"Browser: {env_config.browser_name}:{env_config.browser_version}")
        print(f"Capabilities loaded: {len(env_config.capabilities)} keys")
    if matrix_string:
        print(f"\n📊 Browser Matrix Mode: ENABLED")
        print(f"   Matrix: {matrix_string}")
        print(f"   (Each test will run on each configured browser)")
    print(f"{'='*80}\n")
    
    # Get worker ID if using pytest-xdist
    worker_id = os.getenv("PYTEST_XDIST_WORKER", None)
    
    # Determine report directory name
    # Include browser info if parametrized
    run_id_suffix = ""
    if matrix_string:
        # Sanitize matrix string for directory name
        sanitized_matrix = matrix_string.replace(":", "_").replace(",", "-")
        run_id_suffix = f"_matrix_{sanitized_matrix}"
    
    # Create isolated reports directories - each run gets its own folder
    if worker_id and worker_id != "master":
        reports_dir = project_root / "automation" / "reports" / f"{UNIQUE_RUN_ID}{run_id_suffix}_{worker_id}"
        logger_name = f"Test Worker: {worker_id}"
    else:
        reports_dir = project_root / "automation" / "reports" / f"{UNIQUE_RUN_ID}{run_id_suffix}"
        logger_name = "Test Runner"
    
    reports_dir.mkdir(exist_ok=True, parents=True)
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    (reports_dir / "traces").mkdir(exist_ok=True)
    (reports_dir / "videos").mkdir(exist_ok=True)
    (reports_dir / "allure-results").mkdir(exist_ok=True)
    
    # Store paths for later use
    allure_results_dir = str(reports_dir / "allure-results")
    
    # Set alluredir option - this must be done via option to be recognized by pytest-allure
    config.option.alluredir = allure_results_dir
    
    # Store report directories in config for access in session finish hook
    config.reports_dir = reports_dir
    config.allure_results_dir = allure_results_dir
    
    # Also set screenshot_dir from pytest config to use absolute path
    screenshot_dir = project_root / "automation" / "reports" / "screenshots"
    config.option.screenshot_dir = str(screenshot_dir)
    
    # Configure logging
    AutomationLogger.configure(
        log_level="INFO",
        log_format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        log_file=str(reports_dir / "automation.log"),
        console_output=True,
    )
    
    # Log worker/session info
    if worker_id and worker_id != "master":
        print(f"\n{'='*80}")
        print(f"🔷 WORKER: {worker_id}")
        print(f"📁 Reports: {reports_dir}")
        print(f"📊 Allure Results: {allure_results_dir}")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"🚀 TEST SESSION")
        print(f"📁 Reports: {reports_dir}")
        print(f"📊 Allure Results: {allure_results_dir}")
        print(f"⏰ Run ID: {UNIQUE_RUN_ID}")
        if matrix_string:
            print(f"📊 Browser Matrix: {matrix_string}")
        print(f"{'='*80}\n")


def pytest_addoption(parser):
    """Add custom command line options for browser matrix parametrization."""
    parser.addoption(
        "--browser-matrix",
        action="store",
        default=None,
        help="Browser matrix for parametrization. Format: 'browser:version,browser:version,...' "
             "Example: --browser-matrix='chrome:127,chrome:128,firefox:121'",
    )


def pytest_generate_tests(metafunc):
    """
    Automatically parametrize ALL tests with browser matrix configurations.
    
    If --browser-matrix is provided, every test will run once per browser config.
    Each run gets its own environment variable overrides (BROWSER_NAME, BROWSER_VERSION).
    
    This is infrastructure-level: no test code changes needed.
    """
    if not BrowserMatrix or not BrowserConfig:
        return
    
    # Get the --browser-matrix option
    matrix_string = metafunc.config.getoption("browser_matrix")
    
    if not matrix_string:
        # No browser matrix specified - use default browser from .env
        return
    
    try:
        # Parse the browser matrix string
        configs = BrowserMatrix.parse_matrix_string(matrix_string)
        
        if not configs:
            return
        
        # Validate against browsers.yaml
        validity_map = BrowserMatrix.validate_against_browsers_yaml(configs)
        invalid_configs = [name for name, is_valid in validity_map.items() if not is_valid]
        
        if invalid_configs:
            pytest.skip(
                f"Invalid browser configurations in matrix: {', '.join(invalid_configs)}. "
                f"Check browsers.yaml for available options."
            )
        
        # Generate pytest parametrize IDs
        parametrize_ids = BrowserMatrix.generate_parametrize_ids(configs)
        
        # Parametrize ALL tests (not just those with specific fixture)
        # Use indirect=True so the fixture can access the parameter
        metafunc.parametrize(
            "_matrix_config",
            configs,
            ids=parametrize_ids,
            indirect=True,
        )
        
    except ValueError as e:
        pytest.exit(f"Invalid browser matrix format: {e}")


@pytest.fixture
def _matrix_config(request):
    """
    Indirect fixture that automatically applies browser matrix configuration.
    
    When --browser-matrix is used, this fixture:
    1. Receives a BrowserConfig parameter
    2. Overrides BROWSER_NAME and BROWSER_VERSION environment variables
    3. Resets infrastructure config so it reloads with new env vars
    4. Yields to test execution
    5. Restores original environment
    
    This works with ANY test - no modifications needed!
    """
    if hasattr(request, 'param'):
        config = request.param
        
        # Override environment variables for this parametrization
        env_overrides = BrowserMatrix.get_env_overrides(config)
        original_env = {}
        
        for key, value in env_overrides.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        # Reset infrastructure config so it reloads with new env vars
        reset_environment_config()
        
        yield config
        
        # Restore original environment variables
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
        
        # Reset infrastructure config back to original
        reset_environment_config()
    else:
        yield None


@pytest.fixture(autouse=True)
def _matrix_setup(request, _matrix_config):
    """
    Auto-use fixture that ensures _matrix_config is applied to every test.
    
    This makes browser matrix transparent to the test code.
    """
    yield


def pytest_collection_modifyitems(config, items):
    """Mark async tests and handle browser matrix collection."""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================
# Test Execution Tracking - Add Timestamp and Duration to Allure
# ============================================================
# Test Execution Tracking
# Note: Timing is now tracked directly in each test via allure.dynamic.parameter()
# ============================================================

# Removed pytest_runtest_protocol hook - timing is now handled per-test


# ============================================================
# Parallel Execution Support (pytest-xdist)
# ============================================================

# Note: Worker configuration is handled via pytest_configure hook above
# which checks PYTEST_XDIST_WORKER environment variable


# ============================================================
# Auto-Generate Allure HTML Report
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs after all tests complete.
    Collects and generates Allure report.
    
    Handles both worker and master processes in xdist.
    """
    worker_id = os.getenv("PYTEST_XDIST_WORKER", None)
    
    if worker_id and worker_id != "master":
        # Worker process - results already in worker directory
        pass
    else:
        # Master process - collect results and generate report
        _generate_allure_report_master(session.config)


def _generate_allure_report_master(config):
    """
    Master process - collect results from all workers and generate report.
    
    Handles both regular and xdist parallel runs with matrix.
    """
    import shutil
    import subprocess
    from pathlib import Path
    
    # Get the master allure directory (from config)
    master_allure_dir = Path(config.option.alluredir) if hasattr(config.option, 'alluredir') and config.option.alluredir else None
    
    # Fallback: Check if there are any results in the standard location
    if not master_allure_dir or not list(master_allure_dir.glob("*-result.json")):
        # Try to find results in standard allure-results location
        standard_results_dir = project_root / "automation" / "reports" / "allure-results"
        if standard_results_dir.exists() and list(standard_results_dir.glob("*-result.json")):
            master_allure_dir = standard_results_dir
    
    if not master_allure_dir:
        print(f"\n⚠️  No allure directory found")
        return
    
    # If using xdist, collect results from worker directories
    worker_id = os.getenv("PYTEST_XDIST_WORKER", None)
    if not worker_id:
        # Not using xdist - use master_allure_dir
        result_dir = master_allure_dir
    else:
        # Using xdist - collect from all worker directories
        result_dir = master_allure_dir
        reports_base = master_allure_dir.parent.parent  # Go up to reports/
        
        # Find all worker directories and collect results
        worker_pattern = f"{master_allure_dir.parent.name}_gw*"
        for worker_dir in reports_base.glob(worker_pattern):
            worker_allure_dir = worker_dir / "allure-results"
            if worker_allure_dir.exists():
                # Copy results from worker to master
                for result_file in worker_allure_dir.glob("*-result.json"):
                    dest = result_dir / result_file.name
                    if not dest.exists():
                        shutil.copy2(result_file, dest)
    
    # Check if we have test results
    result_files = list(result_dir.glob("*-result.json")) if result_dir and result_dir.exists() else []
    
    if not result_files:
        # No test results found, skip report generation
        return
    
    # Generate HTML report
    run_report_dir = result_dir.parent / "allure-report"
    result_count = len(result_files)
    
    print(f"\n{'='*80}")
    print(f"✅ ALLURE RESULTS COLLECTED")
    print(f"{'='*80}")
    print(f"📊 Results location: {result_dir}")
    print(f"📦 Test results: {result_count} result JSON files")
    
    # Try to generate HTML report automatically
    try:
        print(f"\n🚀 GENERATING HTML REPORT...")
        subprocess.run(
            ["allure", "generate", str(result_dir), "-o", str(run_report_dir), "--clean"],
            check=True,
            capture_output=True
        )
        print(f"✅ HTML report generated successfully!")
        print(f"\n📖 VIEW REPORT (requires HTTP server):")
        print(f"\n   1️⃣  Start HTTP server:")
        print(f"      python3 -m http.server 8000 --directory {run_report_dir}")
        print(f"\n   2️⃣  Then open in browser:")
        print(f"      http://localhost:8000")
        print(f"\n   📝 Note: HTML reports need HTTP server due to CORS restrictions")
        print(f"      (file:// protocol won't load data files)")
    except FileNotFoundError:
        print(f"\n⚠️ 'allure' command not found. To generate HTML report manually, run:")
        print(f"   allure generate {result_dir} -o {run_report_dir} --clean")
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️ Error generating report: {e.stderr.decode() if e.stderr else str(e)}")
        print(f"   To generate HTML report manually, run:")
        print(f"   allure generate {result_dir} -o {run_report_dir} --clean")
    
    print(f"{'='*80}\n")




# ============================================================
# Fixtures and Helper Functions
# ============================================================



def _get_base64_image(image_path):
    """Convert image file to base64 string"""
    import base64
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return ""


def _generate_allure_html_report(results):
    """Generate HTML report from Allure results"""
    from datetime import datetime
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('status') == 'passed')
    failed_tests = sum(1 for r in results if r.get('status') == 'failed')
    skipped_tests = total_tests - passed_tests - failed_tests
    
    # Generate test results HTML
    test_results_html = ""
    for result in results:
        name = result.get('name', 'Unknown Test')
        status = result.get('status', 'unknown')
        status_class = 'passed' if status == 'passed' else 'failed' if status == 'failed' else 'broken' if status == 'broken' else 'skipped'
        
        # Extract timing parameters
        timing_html = ""
        params = result.get('parameters', [])
        timing_params = {p.get('name'): p.get('value') for p in params if '⏱️' in p.get('name', '') or 'Start' in p.get('name', '') or 'Duration' in p.get('name', '')}
        
        if timing_params:
            start_time = timing_params.get('⏱️ Start Time', 'N/A')
            duration = timing_params.get('⏱️ Duration', 'N/A')
            steps_count = timing_params.get('📊 Steps Count', 'N/A')
            
            timing_html = f"""
            <div style="margin-top: 15px; padding: 15px; background: #f0f7ff; border-radius: 5px; border-left: 4px solid #2196F3;">
                <div style="font-weight: bold; color: #1976D2; margin-bottom: 10px;">⏱️ Timing Information:</div>
                <div style="color: #333;">
                    <div>🕐 <strong>Start Time:</strong> {start_time}</div>
                    <div>⏰ <strong>Duration:</strong> {duration}</div>
                    <div>📊 <strong>Steps Count:</strong> {steps_count}</div>
                </div>
            </div>"""
        
        # Extract steps and build step-by-step view
        steps_list = result.get('steps', [])
        steps_detailed_html = ""
        
        if steps_list:
            steps_html_rows = ""
            for step_idx, step in enumerate(steps_list, 1):
                step_name = step.get('name', 'Unknown Step')
                step_status = step.get('status', 'unknown')
                step_status_icon = "✅" if step_status == "passed" else "❌" if step_status in ["failed", "broken"] else "⊘"
                step_status_color = "#4caf50" if step_status == "passed" else "#f44336"
                
                # Get attachments for screenshots
                step_attachments = step.get('attachments', [])
                screenshot_info = ""
                for att in step_attachments:
                    if att.get('type', '').startswith('image/'):
                        att_source = att.get('source', '')
                        if att_source:
                            screenshot_info = f"<br><span style='color: #666; font-size: 10px;'>📸 {att.get('name', 'Screenshot')}</span>"
                            break
                
                steps_html_rows += f"""
                <div style="margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 3px solid {step_status_color}; border-radius: 3px;">
                    <div style="color: {step_status_color}; font-weight: bold; font-size: 12px;">
                        {step_status_icon} Step {step_idx}: {step_name}
                    </div>{screenshot_info}
                </div>"""
            
            steps_detailed_html = f"""
            <div style="margin-top: 15px; padding: 15px; background: #f5f5f5; border-radius: 5px; border-left: 4px solid #9C27B0;">
                <div style="font-weight: bold; color: #6A1B9A; margin-bottom: 15px; font-size: 13px;">📋 Step-by-Step Execution:</div>
                <div style="color: #333; font-size: 11px; line-height: 1.8;">
{steps_html_rows}
                </div>
            </div>"""
        
        # Extract failure information if test failed or broken
        failure_html = ""
        if status in ['failed', 'broken']:
            status_details = result.get('statusDetails', {})
            error_message = status_details.get('message', 'No error message available')
            
            # Clean up error message (remove unicode escape sequences)
            error_message = error_message.replace('\\n', '<br>')
            
            # Find last failed step and get its screenshot
            last_failed_step = None
            for step in reversed(steps_list):
                if step.get('status') in ['failed', 'broken']:
                    last_failed_step = step
                    break
            
            failure_screenshot_html = ""
            if last_failed_step:
                attachments = last_failed_step.get('attachments', [])
                for att in attachments:
                    if att.get('type', '').startswith('image/'):
                        att_source = att.get('source', '')
                        if att_source:
                            att_file = project_root / "automation" / "reports" / "allure-results" / att_source
                            if att_file.exists():
                                failure_screenshot_html = f"""
            <div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-radius: 4px; border: 1px solid #ffc107;">
                <div style="font-weight: bold; color: #856404; font-size: 11px; margin-bottom: 8px;">📸 Failure Point Screenshot:</div>
                <img src="data:image/png;base64,{_get_base64_image(att_file)}" style="max-width: 100%; border-radius: 4px; max-height: 300px;">
            </div>"""
                            break
            
            failure_html = f"""
            <div style="margin-top: 15px; padding: 15px; background: #ffebee; border-radius: 5px; border-left: 4px solid #f44336;">
                <div style="font-weight: bold; color: #c62828; margin-bottom: 15px; font-size: 13px;">❌ Error Details:</div>
                <div style="color: #333; font-size: 11px; font-family: 'Courier New', monospace; white-space: pre-wrap; word-break: break-word; line-height: 1.6; background: white; padding: 12px; border-radius: 4px; border: 1px solid #ffcdd2; max-height: 400px; overflow-y: auto;">
{error_message}
                </div>{failure_screenshot_html}
            </div>"""
        
        # Extract steps report from attachments
        steps_html = ""
        attachments = result.get('attachments', [])
        for att in attachments:
            if "Steps" in att.get('name', ''):
                # Read the actual steps content from attachment file
                att_source = att.get('source', '')
                if att_source:
                    att_file = project_root / "automation" / "reports" / "allure-results" / att_source
                    try:
                        with open(att_file, 'r') as f:
                            steps_content = f.read()
                            # Format the steps content nicely in HTML
                            steps_html = f"""
            <div style="margin-top: 15px; padding: 15px; background: #fafafa; border-radius: 5px; border-left: 4px solid #9C27B0;">
                <div style="font-weight: bold; color: #6A1B9A; margin-bottom: 15px; font-size: 13px;">📋 Steps Executed:</div>
                <div style="color: #333; font-size: 11px; font-family: 'Courier New', monospace; white-space: pre-wrap; word-break: break-word; line-height: 1.6; background: white; padding: 12px; border-radius: 4px; border: 1px solid #ddd; max-height: 400px; overflow-y: auto;">
{steps_content}
                </div>
            </div>"""
                    except Exception as e:
                        steps_html = f"""
            <div style="margin-top: 15px; padding: 15px; background: #f5f5f5; border-radius: 5px; border-left: 4px solid #9C27B0;">
                <div style="font-weight: bold; color: #6A1B9A; margin-bottom: 10px;">📋 Steps Executed:</div>
                <div style="color: #333; font-size: 12px;">
                    ✓ All steps executed successfully
                </div>
            </div>"""
                break
        
        # Build test result HTML
        status_icon = "✓" if status == "passed" else "✗" if status in ["failed", "broken"] else "⊘"
        test_results_html += f"""        <div class="test-item {status_class}">
            <div class="test-name">{status_icon} {name}</div>
            <div class="test-status">
                <span class="badge {status_class}">{status.upper()}</span>
            </div>
            <div class="test-duration">Status: {status}</div>{timing_html}{steps_detailed_html}{failure_html}{steps_html}
        </div>"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Allure Report - Test Results</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .subtitle {{ color: #666; font-size: 16px; }}
        .status {{ 
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            color: white;
            margin-top: 15px;
        }}
        .status.passed {{ background-color: #4caf50; }}
        .status.failed {{ background-color: #f44336; }}
        .status.broken {{ background-color: #ff6f00; }}
        .status.skipped {{ background-color: #ff9800; }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section h2 {{ 
            color: #333; 
            margin-bottom: 20px; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 10px; 
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card .number {{ font-size: 32px; font-weight: bold; }}
        .stat-card .label {{ font-size: 14px; margin-top: 10px; }}
        
        .test-item {{
            background: #f5f5f5;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #667eea;
            border-radius: 5px;
        }}
        .test-item.passed {{ border-left-color: #4caf50; }}
        .test-item.failed {{ border-left-color: #f44336; }}
        .test-item.broken {{ border-left-color: #ff6f00; }}
        
        .test-name {{ font-weight: bold; color: #333; font-size: 16px; }}
        .test-status {{ display: inline-block; margin-top: 8px; font-size: 12px; }}
        .test-duration {{ color: #666; font-size: 12px; margin-top: 5px; }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-item {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
        }}
        .info-item .key {{ font-weight: bold; color: #667eea; }}
        .info-item .value {{ color: #333; margin-top: 5px; }}
        
        footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #666;
        }}
        
        .timestamp {{ color: #999; font-size: 12px; }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 5px;
        }}
        .badge.passed {{ background: #e8f5e9; color: #2e7d32; }}
        .badge.failed {{ background: #ffebee; color: #c62828; }}
        .badge.broken {{ background: #ffe0b2; color: #e65100; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Allure Test Report</h1>
            <p class="subtitle">Automated Test Results Dashboard</p>
            <div style="margin-top: 20px;">
                <span class="status passed">✅ AUTO-GENERATED</span>
                <span class="timestamp" style="margin-left: 20px;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
            </div>
        </header>
        
        <div class="section">
            <h2>📊 Test Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="number">{total_tests}</div>
                    <div class="label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="number">{passed_tests}</div>
                    <div class="label">Passed</div>
                </div>
                <div class="stat-card">
                    <div class="number">{failed_tests}</div>
                    <div class="label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="number">{skipped_tests}</div>
                    <div class="label">Skipped</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Test Results</h2>
            {test_results_html}
        </div>
        
        <div class="section">
            <h2>📁 Infrastructure</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="key">Report Type</div>
                    <div class="value">Allure Framework</div>
                </div>
                <div class="info-item">
                    <div class="key">Results Location</div>
                    <div class="value">./allure-results/</div>
                </div>
                <div class="info-item">
                    <div class="key">Report Format</div>
                    <div class="value">Auto-Generated HTML</div>
                </div>
                <div class="info-item">
                    <div class="key">Generation</div>
                    <div class="value">Automatic (pytest plugin)</div>
                </div>
                <div class="info-item">
                    <div class="key">Framework</div>
                    <div class="value">pytest + allure-pytest</div>
                </div>
                <div class="info-item">
                    <div class="key">Async Support</div>
                    <div class="value">pytest-asyncio</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Generated by Allure Framework | Auto-Generated Report</p>
            <p style="margin-top: 10px; font-size: 12px; color: #999;">
                This report is automatically generated after each test run using pytest hooks.
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    return html
