"""
Browser Matrix Utility
Handles parametrization and configuration for running tests across multiple browser versions and types.
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path
import yaml


class BrowserConfig:
    """Represents a single browser configuration (name:version)"""
    
    def __init__(self, browser_name: str, browser_version: str):
        self.browser_name = browser_name
        self.browser_version = browser_version
        self.id = f"{browser_name}_{browser_version}"
        self.display_name = f"{browser_name}:{browser_version}"
    
    def __repr__(self):
        return self.display_name
    
    def __str__(self):
        return self.display_name


class BrowserMatrix:
    """Manages browser matrix parsing and configuration generation"""
    
    @staticmethod
    def parse_matrix_string(matrix_string: str) -> List[BrowserConfig]:
        """
        Parse browser matrix string format: "chrome:127,chrome:128,firefox:121"
        
        Args:
            matrix_string: Comma-separated browser:version pairs
            
        Returns:
            List of BrowserConfig objects
            
        Raises:
            ValueError: If matrix string format is invalid
        """
        if not matrix_string or not matrix_string.strip():
            return []
        
        configs = []
        
        # Split by comma and process each entry
        entries = [entry.strip() for entry in matrix_string.split(",")]
        
        for entry in entries:
            if not entry:
                continue
            
            # Validate format: browser:version
            match = re.match(r'^([a-zA-Z]+):([a-zA-Z0-9\.]+)$', entry)
            if not match:
                raise ValueError(
                    f"Invalid browser matrix format: '{entry}'. "
                    f"Expected format: 'browser:version' (e.g., 'chrome:127')"
                )
            
            browser_name, browser_version = match.groups()
            configs.append(BrowserConfig(browser_name, browser_version))
        
        if not configs:
            raise ValueError("Browser matrix string resulted in no valid configurations")
        
        return configs
    
    @staticmethod
    def validate_against_browsers_yaml(configs: List[BrowserConfig], browsers_yaml_path: str = None) -> Dict[str, bool]:
        """
        Validate that matrix configurations exist in browsers.yaml
        
        Args:
            configs: List of BrowserConfig objects to validate
            browsers_yaml_path: Path to browsers.yaml (auto-detected if None)
            
        Returns:
            Dict mapping config display_name to validity (True if exists in YAML)
        """
        if browsers_yaml_path is None:
            # Auto-detect browsers.yaml path
            current_dir = Path(__file__).parent.parent
            browsers_yaml_path = current_dir / "config" / "browsers.yaml"
        
        browsers_yaml_path = Path(browsers_yaml_path)
        
        if not browsers_yaml_path.exists():
            raise FileNotFoundError(f"browsers.yaml not found at {browsers_yaml_path}")
        
        with open(browsers_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        available_browsers = yaml_data.get('browsers', {})
        validity_map = {}
        
        for config in configs:
            if config.browser_name in available_browsers:
                # Check if version exists in local or remote
                browser_data = available_browsers[config.browser_name]
                local_versions = [v['version'] for v in browser_data.get('local', [])]
                remote_versions = [v['version'] for v in browser_data.get('remote', [])]
                
                is_valid = config.browser_version in local_versions or config.browser_version in remote_versions
                validity_map[config.display_name] = is_valid
            else:
                validity_map[config.display_name] = False
        
        return validity_map
    
    @staticmethod
    def generate_parametrize_ids(configs: List[BrowserConfig]) -> List[str]:
        """
        Generate pytest parametrize IDs from browser configs
        
        Args:
            configs: List of BrowserConfig objects
            
        Returns:
            List of IDs suitable for pytest parametrization
        """
        return [config.id for config in configs]
    
    @staticmethod
    def get_env_overrides(config: BrowserConfig) -> Dict[str, str]:
        """
        Generate environment variable overrides for a browser config
        
        Args:
            config: BrowserConfig object
            
        Returns:
            Dict of environment variable names and values to override
        """
        return {
            "BROWSER_NAME": config.browser_name,
            "BROWSER_VERSION": config.browser_version,
        }


def parse_browser_matrix(matrix_string: str) -> List[BrowserConfig]:
    """Convenience function for parsing browser matrix strings"""
    return BrowserMatrix.parse_matrix_string(matrix_string)


def validate_browser_matrix(matrix_string: str) -> Dict[str, bool]:
    """Convenience function for validating browser matrices"""
    configs = parse_browser_matrix(matrix_string)
    return BrowserMatrix.validate_against_browsers_yaml(configs)
