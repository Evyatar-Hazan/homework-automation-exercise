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
import allure


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
    
    @staticmethod
    def log_step_with_allure(step_name: str, 
                             details: str = "",
                             attachment_name: str = None) -> None:
        """
        Log step to console + Allure attachment simultaneously.
        
        Args:
            step_name: Step title (e.g., "Navigate to page")
            details: Additional details to log (e.g., "URL: https://example.com")
            attachment_name: Custom attachment name for Allure (default: step_name)
        
        Example:
            AutomationLogger.log_step_with_allure(
                step_name="Verify page title",
                details="Expected: 'practice'\\nActual: 'A place to practice...'",
                attachment_name="page_title_verification"
            )
        
        Note:
            Should be called within an allure.step() context in tests.
            The attachment will be associated with the current step.
        """
        # Console logging
        logger = logging.getLogger()
        message = f"✅ {step_name}"
        if details:
            message += f"\n   {details}"
        logger.info(message)
        
        # Allure attachment - assumes it's called within a step context
        allure_name = attachment_name or step_name.replace(" ", "_").lower()
        attachment_text = f"{step_name}\n" + ("=" * 50) + "\n"
        if details:
            attachment_text += f"{details}\n"
        attachment_text += f"[{datetime.now().isoformat()}]"
        
        allure.attach(
            attachment_text,
            name=allure_name,
            attachment_type=allure.attachment_type.TEXT
        )


def get_logger(name: str) -> logging.Logger:
    """
    Helper function להשגת logger בקלות.
    
    Example:
        from automation.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Starting automation...")
    """
    return AutomationLogger.get_logger(name)


def log_step_with_allure(step_name: str, 
                         details: str = "",
                         attachment_name: str = None) -> None:
    """
    Log step to console + Allure attachment with proper context.
    
    Args:
        step_name: Step title (e.g., "Verify page title")
        details: Additional details (e.g., "Expected: 'practice'")
        attachment_name: Custom Allure attachment name
    
    Example:
        from automation.core.logger import log_step_with_allure
        
        # Must be called within an allure.step() context:
        with allure.step("Step 1: Verify page title"):
            log_step_with_allure(
                step_name="Verify page title",
                details="Expected: 'practice'\\nFound: 'A place to practice'",
                attachment_name="title_verification"
            )
    
    Note:
        Must be called within an allure.step() context in tests.
        The attachment will be associated with the parent step.
    """
    AutomationLogger.log_step_with_allure(step_name, details, attachment_name)
