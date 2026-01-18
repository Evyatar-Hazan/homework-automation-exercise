"""
Logger Module
=============

מסדר ריכוזי לכל המערכת. מספק:
- Unified logging across infrastructure
- File + Console output
- Structured logging for Allure integration
- סטנדרטיזציה של פורמט ההודעות
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class AutomationLogger:
    """מנהל יחיד לחיבורים לוגים בתשתית."""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def configure(cls, 
                  log_level: str = "INFO",
                  log_format: str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                  log_file: Optional[str] = None,
                  console_output: bool = True) -> None:
        """
        הגדרת Logger עולמי.
        
        Args:
            log_level: DEBUG | INFO | WARNING | ERROR | CRITICAL
            log_format: פורמט הלוגים
            log_file: נתיב לקובץ לוג (אם None - לא נשמר לקובץ)
            console_output: הדפסה לקונסול
        """
        if cls._initialized:
            return
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Formatter
        formatter = logging.Formatter(log_format)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_file_path = Path(log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        קבלת Logger ספציפי לרכיב.
        
        Args:
            name: שם הרכיב (בדרך כלל __name__)
        
        Returns:
            logging.Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]


def get_logger(name: str) -> logging.Logger:
    """
    Helper function להשגת logger בקלות.
    
    Example:
        from automation.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Starting automation...")
    """
    return AutomationLogger.get_logger(name)
