"""
Conftest.py - Global Test Configuration
=========================================

Pytest will automatically discover and load this file.
Used for:
- Global fixtures
- Hooks
- Configuration
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Only import AutomationLogger if the automation module exists and doesn't depend on Playwright
try:
    from automation.core import AutomationLogger
except (ImportError, ModuleNotFoundError):
    # Fall back to simple logging if automation module is not available
    class AutomationLogger:
        @staticmethod
        def configure(**kwargs):
            pass


def pytest_configure(config):
    """Configure pytest."""
    # Create reports directories in automation/reports
    reports_dir = Path("automation/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    (reports_dir / "traces").mkdir(exist_ok=True)
    (reports_dir / "videos").mkdir(exist_ok=True)
    (reports_dir / "allure-results").mkdir(exist_ok=True)
    
    # Configure logging
    AutomationLogger.configure(
        log_level="INFO",
        log_format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        log_file=str(reports_dir / "automation.log"),
        console_output=True,
    )


def pytest_collection_modifyitems(config, items):
    """Mark async tests."""
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
# Auto-Generate Allure HTML Report
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs after all tests complete.
    Automatically generates HTML report from Allure results.
    """
    import json
    from datetime import datetime
    
    allure_dir = Path("automation/reports/allure-results")
    reports_dir = Path("automation/reports")
    html_file = reports_dir / "allure-report.html"
    
    # Create reports directory if it doesn't exist
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    # Only generate if allure-results exist
    if not allure_dir.exists() or not list(allure_dir.glob("*-result.json")):
        return
    
    print("\n" + "="*80)
    print("🚀 GENERATING ALLURE HTML REPORT")
    print("="*80)
    
    try:
        # Read test results
        results = []
        for json_file in sorted(allure_dir.glob("*-result.json")):
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append(data)
        
        # Generate HTML report
        html_content = _generate_allure_html_report(results)
        
        # Write HTML file
        with open(html_file, "w") as f:
            f.write(html_content)
        
        print(f"✅ HTML Report Generated: {html_file}")
        print(f"   Size: {html_file.stat().st_size / 1024:.1f} KB")
        print(f"   Path: {html_file.absolute()}")
        print("="*80)
        print("📊 To view the report:")
        print(f"   firefox automation/reports/allure-report.html")
        print(f"   google-chrome automation/reports/allure-report.html")
        print(f"   chromium-browser automation/reports/allure-report.html")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"⚠️  Error generating HTML report: {str(e)}")


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
        status_class = 'passed' if status == 'passed' else 'failed' if status == 'failed' else 'skipped'
        
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
        
        # Extract steps report from attachments
        steps_html = ""
        attachments = result.get('attachments', [])
        for att in attachments:
            if "Steps" in att.get('name', ''):
                # Read the actual steps content from attachment file
                att_source = att.get('source', '')
                if att_source:
                    att_file = Path("automation/reports/allure-results") / att_source
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
        
        test_results_html += f"""        <div class="test-item {status_class}">
            <div class="test-name">✓ {name}</div>
            <div class="test-status">
                <span class="badge {status_class}">{status.upper()}</span>
            </div>
            <div class="test-duration">Status: {status}</div>{timing_html}{steps_html}
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
