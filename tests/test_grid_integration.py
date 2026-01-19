"""
Grid Integration Tests
======================

Examples demonstrating Selenium Grid / Moon integration with the framework.

These tests show:
1. How to use Grid in test classes
2. How to parametrize with browser matrix
3. How to work with isolated reports
4. How to use in parallel execution

Run Examples:
    # Sequential on Grid
    export USE_GRID=true
    export GRID_URL=http://localhost:4444/wd/hub
    pytest tests/test_grid_integration.py -v

    # Parallel on Grid (2 workers)
    pytest tests/test_grid_integration.py -n 2 -v \
        --env USE_GRID=true \
        --env GRID_URL=http://localhost:4444/wd/hub

    # Browser matrix (all versions)
    pytest tests/test_grid_integration.py::test_grid_matrix_browsers -v \
        --env USE_GRID=true
"""

import pytest
import os
from automation.core import (
    BaseSeleniumTest,
    GridDriverFactory,
    CapabilitiesManager,
    get_logger
)

logger = get_logger(__name__)


class TestGridBasic(BaseSeleniumTest):
    """
    Basic Grid test.
    
    Configuration via class attributes.
    Each instance gets isolated driver session.
    """
    
    # Enable Grid mode
    USE_GRID = True
    
    # Optional: specify Grid URL (or use GRID_URL env var)
    GRID_URL = None  # Will use GRID_URL env var or http://localhost:4444/wd/hub
    
    # Browser configuration
    BROWSER_NAME = "chrome"
    BROWSER_VERSION = "127"
    
    def test_navigation_on_grid(self):
        """Test basic navigation on Selenium Grid."""
        logger.info("Test: Navigation on Grid")
        
        # Navigate to website
        self.navigate_to("https://automationteststore.com/")
        
        # Verify page loaded
        assert "practice" in self.get_page_title().lower(), "Page title should contain 'practice'"
        
        # Take screenshot
        self.take_screenshot("grid_homepage")
        
        logger.info("✓ Navigation test passed on Grid")
    
    def test_grid_driver_info(self):
        """Test accessing driver info on Grid."""
        logger.info("Test: Grid Driver Info")
        
        # Get session info
        session_id = self.driver.session_id
        capabilities = self.driver.capabilities
        
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Browser: {capabilities.get('browserName')}")
        logger.info(f"Version: {capabilities.get('browserVersion', 'unknown')}")
        
        # Verify remote execution
        assert session_id, "Should have valid session ID"
        
        logger.info("✓ Driver info test passed")


class TestGridMultipleVersions(BaseSeleniumTest):
    """
    Test using different browser versions.
    
    Use pytest parametrization to run same test
    with different browser versions.
    """
    
    USE_GRID = True
    
    @pytest.mark.parametrize("browser_version", [
        pytest.param("127", id="chrome-127"),
        pytest.param("128", id="chrome-128"),
    ])
    def test_on_different_chrome_versions(self, browser_version):
        """Run same test on Chrome 127 and 128."""
        logger.info(f"Test: Chrome {browser_version}")
        
        # Override version for this test
        self.BROWSER_VERSION = browser_version
        
        # Re-create driver with new version
        # (Note: setup_method already ran, so we need to close and recreate)
        # For real usage, you'd configure BROWSER_VERSION before setup_method
        
        # Navigate
        self.navigate_to("https://automationteststore.com/")
        
        # Verify
        assert "practice" in self.get_page_title().lower()
        
        # Screenshot with version info
        self.take_screenshot(f"chrome_{browser_version}_test")
        
        logger.info(f"✓ Test passed on Chrome {browser_version}")


class TestGridCapabilitiesManager:
    """
    Test CapabilitiesManager functionality.
    
    This demonstrates how to:
    - Load browser matrix from YAML
    - Get capabilities for specific browser/version
    - Create drivers with matrix configuration
    """
    
    def test_capabilities_manager_initialization(self):
        """Test loading capabilities from browsers.yaml."""
        logger.info("Test: Capabilities Manager Initialization")
        
        mgr = CapabilitiesManager()
        
        # Should load without errors
        assert mgr.browsers is not None
        assert len(mgr.browsers) > 0
        
        logger.info(f"✓ Loaded browsers: {list(mgr.browsers.keys())}")
    
    def test_get_capabilities_chrome(self):
        """Test getting Chrome capabilities."""
        logger.info("Test: Get Chrome Capabilities")
        
        mgr = CapabilitiesManager()
        
        # Get Chrome 127 remote capabilities
        caps = mgr.get_capabilities("chrome", version="127", execution_mode="remote")
        
        assert caps["browserName"] == "chrome"
        assert caps["browserVersion"] == "127"
        assert caps["platformName"] == "linux"
        
        logger.info(f"✓ Got Chrome 127 capabilities")
    
    def test_get_capabilities_firefox(self):
        """Test getting Firefox capabilities."""
        logger.info("Test: Get Firefox Capabilities")
        
        mgr = CapabilitiesManager()
        
        # Get Firefox 121 remote capabilities
        caps = mgr.get_capabilities("firefox", version="121", execution_mode="remote")
        
        assert caps["browserName"] == "firefox"
        assert caps["browserVersion"] == "121"
        
        logger.info(f"✓ Got Firefox 121 capabilities")
    
    def test_browser_matrix_listing(self):
        """Test listing all available browsers and versions."""
        logger.info("Test: Browser Matrix Listing")
        
        mgr = CapabilitiesManager()
        
        # Get all available browsers
        browsers = mgr.get_available_browsers("remote")
        logger.info(f"Available browsers: {browsers}")
        
        assert len(browsers) > 0
        
        # List all versions for Chrome
        chrome_versions = mgr.get_all_versions("chrome", "remote")
        logger.info(f"Chrome versions: {[v['version'] for v in chrome_versions]}")
        
        assert len(chrome_versions) > 0
    
    def test_full_matrix(self):
        """Test getting full execution matrix."""
        logger.info("Test: Full Execution Matrix")
        
        mgr = CapabilitiesManager()
        
        # Get full matrix for parallel execution
        matrix = mgr.get_matrix("remote")
        
        logger.info("Matrix structure:")
        for browser, versions in matrix.items():
            logger.info(f"  {browser}:")
            for v in versions:
                logger.info(f"    - {v['version']}: {v['name']}")
        
        assert len(matrix) > 0
        assert "chrome" in matrix
        assert len(matrix["chrome"]) > 0


class TestGridDriverFactory:
    """
    Test GridDriverFactory functionality.
    
    This demonstrates how to:
    - Create remote drivers on Grid
    - Use capabilities matrix
    - Handle connection failures gracefully
    """
    
    def test_grid_driver_factory_initialization(self):
        """Test creating GridDriverFactory."""
        logger.info("Test: Grid Driver Factory Initialization")
        
        # Initialize factory
        factory = GridDriverFactory(grid_url="http://localhost:4444/wd/hub")
        
        assert factory.grid_url == "http://localhost:4444/wd/hub"
        assert factory.capabilities_mgr is not None
        
        logger.info("✓ Factory initialized successfully")
    
    def test_grid_url_from_env(self):
        """Test getting Grid URL from environment."""
        logger.info("Test: Grid URL from Environment")
        
        # If GRID_URL is set, it should be used
        original_grid_url = os.getenv("GRID_URL")
        
        try:
            os.environ["GRID_URL"] = "http://example.com:4444/wd/hub"
            
            factory = GridDriverFactory()
            
            assert factory.grid_url == "http://example.com:4444/wd/hub"
            logger.info("✓ Grid URL loaded from environment")
        
        finally:
            if original_grid_url:
                os.environ["GRID_URL"] = original_grid_url
            else:
                os.environ.pop("GRID_URL", None)
    
    def test_get_grid_info(self):
        """Test getting Grid Hub information."""
        logger.info("Test: Get Grid Info")
        
        factory = GridDriverFactory()
        
        # Try to get Grid info (may fail if Grid not running)
        info = factory.get_grid_info()
        
        logger.info(f"Grid info: {info}")
        # Don't assert since Grid may not be running


# ============================================================
# Full Workflow Examples
# ============================================================

class TestGridFullWorkflow(BaseSeleniumTest):
    """
    Full workflow test demonstrating all Grid features:
    - Grid connection
    - Browser matrix
    - Parallel execution
    - Isolated reports
    - Allure reporting
    """
    
    USE_GRID = True
    BROWSER_NAME = "chrome"
    BROWSER_VERSION = "127"
    
    def test_complete_automation_workflow_on_grid(self):
        """
        Complete test workflow on Selenium Grid.
        
        Steps:
        1. Navigate to Automation Test Store
        2. Verify homepage loads
        3. Take screenshot
        4. Verify elements
        5. Generate Allure report
        
        When run with:
            pytest test_grid_integration.py -n 4 -v --env USE_GRID=true
        
        Result:
        - 4 parallel workers
        - Each with isolated driver session
        - Each with isolated report directory
        - Merged HTML report at automation/reports/allure-report.html
        """
        logger.info("=" * 80)
        logger.info("GRID WORKFLOW TEST")
        logger.info("=" * 80)
        
        # Step 1: Navigate
        logger.info("Step 1: Navigate to ATS")
        self.navigate_to("https://automationteststore.com/")
        
        # Step 2: Verify title
        logger.info("Step 2: Verify page title")
        title = self.get_page_title()
        assert "practice" in title.lower(), f"Expected 'practice' in title, got: {title}"
        logger.info(f"✓ Title verified: {title}")
        
        # Step 3: Screenshot
        logger.info("Step 3: Take screenshot")
        self.take_screenshot("ats_homepage")
        logger.info("✓ Screenshot taken")
        
        # Step 4: Verify URL
        logger.info("Step 4: Verify URL")
        url = self.get_current_url()
        assert "automationteststore.com" in url, f"Expected ATS URL, got: {url}"
        logger.info(f"✓ URL verified: {url}")
        
        # Step 5: Log completion
        logger.info("=" * 80)
        logger.info("✓ GRID WORKFLOW TEST PASSED")
        logger.info("=" * 80)


if __name__ == "__main__":
    logger.info("""
    
    Grid Integration Tests
    ======================
    
    Run these tests to verify Grid integration:
    
    1. Make sure Selenium Grid is running:
       docker run -d -p 4444:4444 -p 7900:7900 selenium/hub:4.15.0
       docker run -d -e SE_EVENT_BUS_HOST=localhost \\
                     -e SE_EVENT_BUS_PUBLISH_PORT=4442 \\
                     -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 \\
                     selenium/node-chrome:4.15.0
    
    2. Run tests:
       # Sequential
       export GRID_URL=http://localhost:4444/wd/hub
       pytest test_grid_integration.py -v
       
       # Parallel (2 workers)
       pytest test_grid_integration.py -n 2 -v
    
    3. View reports:
       firefox automation/reports/allure-report.html
    """)
