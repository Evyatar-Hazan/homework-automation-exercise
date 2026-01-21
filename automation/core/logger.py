"""
Logger Module
=============

Centralized logging system for the entire framework. Provides:
- Unified logging across infrastructure
- File + Console output
- Structured logging for Allure integration
- Standardized message formatting

Step-Aware Logging:
- loggerStep() - Open a new step with auto-context management
- loggerInfo() - Log info that attaches to active step
- loggerAttach() - Attach data to active step
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Callable, Any
from datetime import datetime
import allure
from automation.core.step_context import (
    StepContext, 
    get_active_step, 
    attach_to_active_step,
    is_step_active
)


class AutomationLogger:
    """Singleton manager for logging infrastructure."""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def configure(cls, 
                  log_level: str = "INFO",
                  log_format: str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                  log_file: Optional[str] = None,
                  console_output: bool = True) -> None:
        """
        Configure global logger.
        
        Args:
            log_level: DEBUG | INFO | WARNING | ERROR | CRITICAL
            log_format: Log format string
            log_file: Path to log file (if None - not saved to file)
            console_output: Print to console
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
        Get a component-specific logger.
        
        Args:
            name: Component name (usually __name__)
        
        Returns:
            logging.Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]
    
    @staticmethod
    def loggerStep(step_name: str, action: Callable[[], Any], validate: Callable[[Any], None] = None):
        """
        Docstring for loggerStep
        
        :param step_name: Description
        :type step_name: str
        :param action: Description
        :type action: Callable[[], Any]
        :param validate: Description
        :type validate: Callable[[Any], None]
        """
        print(f'step name: {step_name}')
        with allure.step(step_name):
            result = action()
            if validate:
                validate(result)
            return result


    @staticmethod
    def  loggerInfo(message: str) -> None:
        """
        Log info message to console and Allure.
        
        Args:
            message: Message to log
        """
        print(f'info: {message}')
        # Attach to Allure without creating a nested step
        allure.attach(message, name="info_log", attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def  loggerAttach(message: str, name: str = "attachment", attachment_type=allure.attachment_type.TEXT) -> None:
        """
        Log attach message to console and Allure.
        
        Args:
            message: Message to log
        """
        print(f'attach: {message}')
        allure.attach(f'attach: {message}', name=name, attachment_type=attachment_type)
    
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
        
        # Allure attachment - must be called within step context from parent
        allure_name = attachment_name or step_name.replace(" ", "_").lower()
        attachment_text = f"{step_name}\n" + ("=" * 50) + "\n"
        if details:
            attachment_text += f"{details}\n"
        attachment_text += f"[{datetime.now().isoformat()}]"
        
        # Ensure attachment_text is not empty
        if not attachment_text or attachment_text.isspace():
            attachment_text = step_name
        
        # Attach to Allure
        allure.attach(
            body=str(attachment_text),
            name=str(allure_name),
            attachment_type=allure.attachment_type.TEXT
        )


def get_logger(name: str) -> logging.Logger:
    """
    Helper function to get a logger easily.
    
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


def loggerStep(step_name: str, action: Callable[[], Any], validate: Callable[[Any], None] = None):
    """
    Docstring for loggerStep
    
    :param step_name: Description
    :type step_name: str
    :param action: Description
    :type action: Callable[[], Any]
    :param validate: Description
    :type validate: Callable[[Any], None]
    """
    AutomationLogger.loggerStep(step_name, action, validate)


def loggerInfo(message: str) -> None:
    """
    Log info message to console and Allure (creates nested step).
    
    Args:
        message: Message to log
    
    Note:
        Creates a nested step in Allure. Use within step context in tests.
    """
    AutomationLogger.loggerInfo(message)


def loggerAttach(message: str, name: str = "attachment", attachment_type=allure.attachment_type.TEXT) -> None:
    """
    Log attach message to console and Allure.
    
    Args:
        message: Message to log
        name: Name of the attachment (default: "attachment")
        attachment_type: Type of attachment (default: TEXT)
    
    Note:
        Creates an attachment in Allure.
    """
    AutomationLogger.loggerAttach(message, name, attachment_type)


# ============================================================================
# 🆕 STEP-AWARE LOGGING API (Thread-Safe, ContextVar-Based)
# ============================================================================
# These functions provide automatic step-scoped logging for Allure reports.
# Thread/process safe for parallel execution (pytest -n).
# ============================================================================


def step_aware_loggerStep(step_name: str, 
                          action: Optional[Callable[[], Any]] = None, 
                          validate: Optional[Callable[[Any], None]] = None) -> Any:
    """
    Open a new Allure step with automatic context management.
    
    🎯 Thread-safe step management using contextvars
    🎯 Auto-closes previous step when new step opens
    🎯 All subsequent loggerInfo/loggerAttach calls attach to this step
    
    Args:
        step_name: Step name (shown in Allure report)
        action: Optional callable to execute within step
        validate: Optional validation callable to run on action result
    
    Returns:
        Result of action() if provided, else the StepContext itself
    
    Usage:
        # With action
        result = step_aware_loggerStep("Step 1: Login", action=do_login)
        
        # As context manager
        with step_aware_loggerStep("Step 2: Navigate"):
            step_aware_loggerInfo("Navigating to page")
            # Code here
    
    Example:
        step_aware_loggerStep("Step 1: Perform login", action=lambda: driver.login())
        step_aware_loggerInfo("Username entered")
        step_aware_loggerInfo("Password entered") 
        step_aware_loggerAttach("Login successful", name="login_result")
        
        # In Allure HTML:
        # Step 1: Perform login
        #  ├── info_log: Username entered
        #  ├── info_log: Password entered
        #  └── login_result: Login successful
    """
    print(f'📌 Step: {step_name}')
    
    step_context = StepContext(step_name)
    
    if action is None:
        # Return context manager for 'with' usage
        return step_context
    
    # Execute action within step context
    with step_context:
        result = action()
        if validate:
            validate(result)
        return result


def step_aware_loggerInfo(message: str) -> None:
    """
    Log info message to console and attach to active Allure step.
    
    🎯 If a step is active (via step_aware_loggerStep), attaches to that step
    🎯 If no step is active, attaches at test level
    🎯 Does NOT create nested steps (unlike original loggerInfo)
    
    Args:
        message: Message to log
    
    Usage:
        step_aware_loggerStep("Step 1: Login", action=do_login)
        step_aware_loggerInfo("Username field filled")  # Attaches to Step 1
        step_aware_loggerInfo("Password field filled")  # Attaches to Step 1
    
    Note:
        Must be called after step_aware_loggerStep to attach to a step.
        Otherwise, attaches to test level.
    """
    print(f'ℹ️  {message}')
    
    # Ensure message is valid
    if not message or message.isspace():
        message = "(empty message)"
    
    # Attach to active step (or test level if no step active)
    attach_to_active_step(
        body=message,
        name="info_log",
        attachment_type=allure.attachment_type.TEXT
    )


def step_aware_loggerError(message: str) -> None:
    """
    Log an ERROR message and attach to active Allure step.
    
    🎯 If a step is active, attaches to that step
    🎯 If no step is active, attaches at test level
    
    Args:
        message: Error message to log
    
    Usage:
        with step_aware_loggerStep("Step 1: Verify data"):
            step_aware_loggerError("❌ FAIL: Value mismatch")
    
    Note:
        Error messages are automatically attached to the active step context.
    """
    print(f'❌ ERROR: {message}')
    
    # Also log to standard logger for file logging
    _logger = AutomationLogger.get_logger(__name__)
    _logger.error(message)
    
    # Attach to active step (or test level if no step active)
    attach_to_active_step(
        body=message,
        name="error_log",
        attachment_type=allure.attachment_type.TEXT
    )


def step_aware_loggerAttach(message: str, 
                            name: str = "attachment", 
                            attachment_type=allure.attachment_type.TEXT) -> None:
    """
    Attach data to active Allure step.
    
    🎯 If a step is active, attaches to that step
    🎯 If no step is active, attaches at test level
    
    Args:
        message: Content to attach
        name: Attachment name (default: "attachment")
        attachment_type: Allure attachment type (default: TEXT)
    
    Usage:
        step_aware_loggerStep("Step 1: API Call", action=make_api_call)
        step_aware_loggerAttach("Response: 200 OK", name="api_response")
    
    Note:
        Attachments are scoped to the active step context.
    """
    print(f'📎 Attach [{name}]: {message}')
    
    # Attach to active step (or test level if no step active)
    attach_to_active_step(
        body=message,
        name=name,
        attachment_type=attachment_type
    )


def get_current_step_name() -> Optional[str]:
    """
    Get the name of the currently active step.
    
    Returns:
        Step name if a step is active, None otherwise
    
    Usage:
        if get_current_step_name():
            print(f"Currently in step: {get_current_step_name()}")
    """
    active_step = get_active_step()
    return active_step.step_name if active_step else None


def is_in_step() -> bool:
    """
    Check if code is currently executing within a step.
    
    Returns:
        True if inside a step, False otherwise
    
    Usage:
        if is_in_step():
            step_aware_loggerInfo("Inside a step")
        else:
            print("Not in a step")
    """
    return is_step_active()

