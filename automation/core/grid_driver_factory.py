"""
Grid Driver Factory Module
==========================

Factory for creating Remote WebDriver instances against Selenium Grid / Moon.
Supports:
- Selenium Grid Hub (http://hub:4444/wd/hub)
- Moon (http://moon:4444/wd/hub)
- Custom Grid URLs via GRID_URL environment variable
- Capability matrix per browser/version

שימוש:
    factory = GridDriverFactory(grid_url="http://localhost:4444/wd/hub")
    
    # Using Matrix
    capabilities = factory.get_capabilities("chrome", version="127")
    driver = await factory.create_remote_driver(capabilities)
    
    # Or specify custom capabilities
    capabilities = {
        "browserName": "chrome",
        "browserVersion": "128",
        "platformName": "linux"
    }
    driver = await factory.create_remote_driver(capabilities)
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from automation.core.logger import get_logger

logger = get_logger(__name__)


class CapabilitiesManager:
    """
    Manages browser capabilities matrix from YAML configuration.
    Provides easy access to Selenium Grid compatible capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CapabilitiesManager.
        
        Args:
            config_path: Path to browsers.yaml (auto-detected if None)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.browsers = self.config.get("browsers", {})
    
    @staticmethod
    def _get_default_config_path() -> str:
        """Get default browsers.yaml path."""
        script_dir = Path(__file__).parent.parent
        return str(script_dir / "config" / "browsers.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config not found: {self.config_path}")
            return {"browsers": {}}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        logger.info(f"Loaded capabilities from {self.config_path}")
        return config
    
    def get_capabilities(self, 
                        browser_name: str, 
                        version: Optional[str] = None,
                        execution_mode: str = "local") -> Dict[str, Any]:
        """
        Get capabilities for a specific browser/version.
        
        Args:
            browser_name: "chrome", "firefox", "edge"
            version: Browser version (e.g., "127", "latest")
            execution_mode: "local" or "remote"
        
        Returns:
            Capabilities dictionary compatible with Selenium Grid
        
        Example:
            caps = mgr.get_capabilities("chrome", version="127", execution_mode="remote")
            # Returns:
            # {
            #   "browserName": "chrome",
            #   "browserVersion": "127",
            #   "platformName": "linux",
            #   ...
            # }
        """
        browser_name = browser_name.lower()
        version = version or "latest"
        execution_mode = execution_mode.lower()
        
        if browser_name not in self.browsers:
            raise ValueError(f"Unknown browser: {browser_name}. Available: {list(self.browsers.keys())}")
        
        browser_config = self.browsers[browser_name]
        
        if execution_mode not in browser_config:
            raise ValueError(f"Unknown execution mode: {execution_mode}. Available: {list(browser_config.keys())}")
        
        versions_list = browser_config[execution_mode]
        
        # Find matching version
        matching_version = None
        for v_config in versions_list:
            if v_config.get("version") == version:
                matching_version = v_config
                break
        
        if not matching_version:
            logger.warning(f"Version {version} not found. Using latest available.")
            matching_version = versions_list[-1]
        
        capabilities = matching_version.get("capabilities", {})
        logger.info(f"✓ Got capabilities for {browser_name}:{version} (mode: {execution_mode})")
        
        return capabilities
    
    def get_all_versions(self, browser_name: str, execution_mode: str = "local") -> List[Dict[str, Any]]:
        """
        Get all available versions for a browser.
        
        Returns:
            List of {version, name, capabilities}
        """
        browser_name = browser_name.lower()
        
        if browser_name not in self.browsers:
            return []
        
        browser_config = self.browsers[browser_name]
        return browser_config.get(execution_mode, [])
    
    def get_available_browsers(self, execution_mode: str = "local") -> List[str]:
        """Get list of available browsers for execution mode."""
        browsers = []
        for browser_name, config in self.browsers.items():
            if execution_mode in config and config[execution_mode]:
                browsers.append(browser_name)
        return browsers
    
    def get_matrix(self, execution_mode: str = "local") -> Dict[str, List[Dict[str, Any]]]:
        """
        Get full matrix for parallel execution.
        
        Returns:
            {
              "chrome": [
                {version: "127", name: "Chrome 127", capabilities: {...}},
                {version: "128", name: "Chrome 128", capabilities: {...}}
              ],
              "firefox": [...]
            }
        
        Usage for pytest parametrize:
            matrix = mgr.get_matrix("remote")
            @pytest.mark.parametrize("browser_config", [
                (b, v["version"]) 
                for b, versions in matrix.items() 
                for v in versions
            ])
            def test_something(browser_config):
                browser, version = browser_config
                ...
        """
        matrix = {}
        
        for browser_name in self.get_available_browsers(execution_mode):
            versions = self.get_all_versions(browser_name, execution_mode)
            matrix[browser_name] = versions
        
        logger.info(f"✓ Generated matrix for {execution_mode}: {list(matrix.keys())}")
        return matrix


class GridDriverFactory:
    """
    Factory for creating Remote WebDriver instances on Selenium Grid / Moon.
    
    Supports:
    - Selenium Grid Hub
    - Moon (https://aerokube.com/moon/)
    - Custom Grid URLs via environment variable
    - Capability matrix from browsers.yaml
    """
    
    def __init__(self, grid_url: Optional[str] = None):
        """
        Initialize GridDriverFactory.
        
        Args:
            grid_url: Selenium Grid Hub URL (e.g., http://localhost:4444/wd/hub)
                     Defaults to GRID_URL env var, falls back to http://localhost:4444/wd/hub
        """
        self.grid_url = grid_url or os.getenv("GRID_URL", "http://localhost:4444/wd/hub")
        self.capabilities_mgr = CapabilitiesManager()
        
        logger.info(f"Grid Factory initialized with URL: {self.grid_url}")
    
    def create_remote_driver(self, 
                            capabilities: Dict[str, Any],
                            timeout: int = 30,
                            command_executor: Optional[str] = None) -> webdriver.Remote:
        """
        Create a Remote WebDriver instance.
        
        Args:
            capabilities: Browser capabilities dict
            timeout: Page load timeout in seconds
            command_executor: Custom command executor URL (defaults to self.grid_url)
        
        Returns:
            selenium.webdriver.Remote instance
        
        Raises:
            ConnectionError: If Grid is not reachable
            TimeoutException: If browser creation times out
        
        Example:
            factory = GridDriverFactory(grid_url="http://grid:4444/wd/hub")
            caps = factory.capabilities_mgr.get_capabilities("chrome", "127", "remote")
            driver = factory.create_remote_driver(caps)
            try:
                driver.get("https://example.com")
            finally:
                driver.quit()
        """
        executor = command_executor or self.grid_url
        
        try:
            logger.info(f"Creating remote driver: {executor}")
            logger.info(f"Capabilities: {capabilities.get('browserName')} {capabilities.get('browserVersion', 'latest')}")
            
            driver = webdriver.Remote(
                command_executor=executor,
                desired_capabilities=capabilities,
                keep_alive=True
            )
            
            # Set timeouts
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(10)
            
            # Get session ID
            session_id = driver.session_id
            logger.info(f"✓ Remote driver created. Session ID: {session_id}")
            
            return driver
        
        except ConnectionError as e:
            logger.error(f"Failed to connect to Grid: {executor}")
            logger.error(f"Make sure Selenium Grid / Moon is running at {executor}")
            raise
        except Exception as e:
            logger.error(f"Error creating remote driver: {str(e)}")
            raise
    
    def create_driver_from_matrix(self,
                                  browser_name: str,
                                  version: Optional[str] = None,
                                  timeout: int = 30) -> webdriver.Remote:
        """
        Create driver using browser matrix configuration.
        
        Args:
            browser_name: "chrome", "firefox", "edge"
            version: Browser version from matrix
            timeout: Page load timeout
        
        Returns:
            selenium.webdriver.Remote instance
        
        Example:
            factory = GridDriverFactory()
            driver = factory.create_driver_from_matrix("chrome", "127")
            driver.get("https://example.com")
            driver.quit()
        """
        capabilities = self.capabilities_mgr.get_capabilities(
            browser_name, 
            version, 
            execution_mode="remote"
        )
        return self.create_remote_driver(capabilities, timeout)
    
    def verify_grid_connectivity(self) -> bool:
        """
        Verify Grid Hub is reachable and responsive.
        
        Returns:
            True if reachable, False otherwise
        """
        try:
            logger.info(f"Checking Grid connectivity: {self.grid_url}")
            driver = webdriver.Remote(command_executor=self.grid_url)
            status = driver.execute_script("return navigator.userAgent")
            driver.quit()
            logger.info("✓ Grid is reachable and responsive")
            return True
        except Exception as e:
            logger.error(f"Grid connectivity check failed: {str(e)}")
            return False
    
    def get_grid_info(self) -> Dict[str, Any]:
        """
        Get Grid Hub information and statistics.
        
        Returns:
            Grid status information
        """
        try:
            from urllib.request import urlopen
            import json
            
            status_url = self.grid_url.replace("/wd/hub", "/status")
            response = urlopen(status_url)
            status = json.loads(response.read().decode())
            
            logger.info(f"Grid Status: {status}")
            return status
        except Exception as e:
            logger.warning(f"Could not fetch Grid info: {str(e)}")
            return {}
