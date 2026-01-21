import json
import os
from pathlib import Path
from typing import Dict, Any

def load_test_data() -> Dict[str, Any]:
    """
    Load test data from config/test_data.json.
    
    Returns:
        Dict containing all test data configuration
    """
    # Assuming the config file is in automation-project1/config/test_data.json
    # and this file is in automation-project1/automation/utils/data_loader.py
    
    # Go up two levels from utils/data_loader.py to root, then into config
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parent.parent.parent
    config_path = project_root / "config" / "test_data.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Test data file not found at: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Singleton-like access to avoid reloading multiple times
_TEST_DATA = None

def get_test_data() -> Dict[str, Any]:
    global _TEST_DATA
    if _TEST_DATA is None:
        _TEST_DATA = load_test_data()
    return _TEST_DATA
