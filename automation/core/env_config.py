"""
Environment Configuration Module
==================================

Infrastructure-level configuration loader.
Reads Grid/Browser settings from .env and browsers.yaml
Provides clean configuration object for the entire test framework.

This module ensures that Grid/Browser configuration is infrastructure-level,
not tied to specific tests. All tests automatically use these settings.

Usage:
    from automation.core.env_config import EnvironmentConfig
    
    config = EnvironmentConfig()
    print(config.use_grid)           # bool
    print(config.grid_url)           # str
    print(config.browser_name)       # str
    print(config.browser_version)    # str
    print(config.capabilities)       # dict (from browsers.yaml)
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from automation.core.logger import get_logger

logger = get_logger(__name__)


class EnvironmentConfig:
    """
    Infrastructure-level environment configuration.
    
    Loads Grid/Browser settings from:
    1. Environment variables (.env file via python-dotenv)
    2. browsers.yaml for Capabilities
    
    All tests automatically use this configuration.
    """
    
    def __init__(self):
        """Initialize environment configuration from .env and browsers.yaml"""
        self._load_grid_settings()
        self._load_browser_capabilities()
        self._validate_config()
    
    def _load_grid_settings(self):
        """Load Grid/Browser settings from environment variables."""
        # Grid settings
        self.use_grid = os.getenv("USE_GRID", "false").lower() == "true"
        self.grid_url = os.getenv("GRID_URL", "http://localhost:4444/wd/hub")
        
        # Browser settings
        self.browser_name = os.getenv("BROWSER_NAME", "chrome").lower()
        self.browser_version = os.getenv("BROWSER_VERSION", "127")
        
        logger.info(f"🔧 Environment Configuration Loaded:")
        logger.info(f"   USE_GRID: {self.use_grid}")
        logger.info(f"   GRID_URL: {self.grid_url}")
        logger.info(f"   BROWSER_NAME: {self.browser_name}")
        logger.info(f"   BROWSER_VERSION: {self.browser_version}")
    
    def _load_browser_capabilities(self):
        """Load browser capabilities from browsers.yaml based on current settings."""
        try:
            # Load browsers.yaml
            config_path = Path(__file__).parent.parent / "config" / "browsers.yaml"
            
            if not config_path.exists():
                logger.warning(f"⚠️  browsers.yaml not found at {config_path}")
                self.capabilities = {}
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            browsers_config = config.get("browsers", {})
            
            # Get execution mode (local or remote)
            execution_mode = "remote" if self.use_grid else "local"
            
            # Get capabilities for current browser/version
            if self.browser_name not in browsers_config:
                logger.warning(f"⚠️  Browser '{self.browser_name}' not found in browsers.yaml")
                self.capabilities = {}
                return
            
            browser_config = browsers_config[self.browser_name]
            versions = browser_config.get(execution_mode, [])
            
            # Find matching version
            matching_version = None
            for v in versions:
                if v.get("version") == self.browser_version:
                    matching_version = v
                    break
            
            if matching_version:
                self.capabilities = matching_version.get("capabilities", {})
                logger.info(f"✅ Loaded capabilities for {self.browser_name}:{self.browser_version}")
            else:
                logger.warning(
                    f"⚠️  No capabilities found for {self.browser_name}:{self.browser_version} "
                    f"in {execution_mode} mode"
                )
                self.capabilities = {
                    "browserName": self.browser_name,
                    "browserVersion": self.browser_version if self.browser_version != "latest" else "",
                    "platformName": "linux"
                }
        
        except Exception as e:
            logger.error(f"❌ Error loading capabilities: {e}")
            self.capabilities = {}
    
    def _validate_config(self):
        """Validate configuration is valid."""
        valid_browsers = ["chrome", "firefox", "edge"]
        
        if self.browser_name not in valid_browsers:
            logger.warning(f"⚠️  Unknown browser: {self.browser_name}")
        
        if self.use_grid and not self.grid_url:
            logger.warning("⚠️  USE_GRID=true but GRID_URL is empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "use_grid": self.use_grid,
            "grid_url": self.grid_url,
            "browser_name": self.browser_name,
            "browser_version": self.browser_version,
            "capabilities": self.capabilities,
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"EnvironmentConfig("
            f"use_grid={self.use_grid}, "
            f"grid_url={self.grid_url}, "
            f"browser={self.browser_name}:{self.browser_version}"
            f")"
        )


# Singleton instance - loaded once at startup
_config_instance: Optional[EnvironmentConfig] = None


def get_environment_config() -> EnvironmentConfig:
    """
    Get singleton EnvironmentConfig instance.
    
    Loaded once at startup, reused for all tests.
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = EnvironmentConfig()
    
    return _config_instance


def reset_environment_config():
    """Reset singleton (for testing purposes)."""
    global _config_instance
    _config_instance = None
