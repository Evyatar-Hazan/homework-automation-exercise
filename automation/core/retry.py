"""
Retry & Backoff Module
======================

מנגנון retry כללי עם exponential backoff.

עיקרון:
- Retry רק על שגיאות רלוונטיות (Timeout, Detached DOM, Network)
- Backoff מדורג (exponential) בין ניסיונות
- Graceful recovery ללא קריסה מיידית
- לוג מלא של כל ניסיון

שימוש:
    @retry_on_failure(max_attempts=3, backoff_ms=500)
    def some_action():
        ...
"""

import asyncio
import time
from typing import Callable, TypeVar, Optional, Type, Tuple, Any
from functools import wraps
from enum import Enum

from automation.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class RetryableError(Enum):
    """שגיאות שעליהן כדאי להתנסות מחדש."""
    TIMEOUT = "Timeout"
    DETACHED_ELEMENT = "Element detached from DOM"
    NETWORK_ERROR = "Network error"
    STALE_ELEMENT = "Stale element reference"
    NO_SUCH_ELEMENT = "Element not found"
    UNKNOWN = "Unknown error"


class RetryConfig:
    """הגדרת ההתנסות מחדש."""
    
    def __init__(self,
                 max_attempts: int = 3,
                 initial_backoff_ms: int = 500,
                 max_backoff_ms: int = 5000,
                 exponential_base: float = 2.0):
        """
        Args:
            max_attempts: מספר ניסיונות מקסימלי
            initial_backoff_ms: השהיה ראשונית (milliseconds)
            max_backoff_ms: השהיה מקסימלית (milliseconds)
            exponential_base: בסיס exponential (e.g., 2 = doubles)
        """
        self.max_attempts = max_attempts
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.exponential_base = exponential_base
    
    def calculate_backoff(self, attempt_number: int) -> float:
        """
        חישוב backoff עם exponential growth.
        
        Args:
            attempt_number: מספר הניסיון (0-indexed)
        
        Returns:
            השהיה בשניות
        """
        backoff_ms = self.initial_backoff_ms * (self.exponential_base ** attempt_number)
        backoff_ms = min(backoff_ms, self.max_backoff_ms)
        return backoff_ms / 1000.0  # Convert to seconds


def is_retryable_error(exception: Exception) -> bool:
    """
    בדיקה אם השגיאה כדאית לניסיון מחדש.
    
    Args:
        exception: השגיאה לבדוק
    
    Returns:
        True אם כדאי להתנסות שוב
    """
    error_message = str(exception).lower()
    
    retryable_keywords = [
        'timeout',
        'detached',
        'stale',
        'network',
        'connection',
        'refused',
        'reset',
        'no such element',
        'element not found',
    ]
    
    return any(keyword in error_message for keyword in retryable_keywords)


def retry_on_failure(max_attempts: int = 3,
                     initial_backoff_ms: int = 500,
                     max_backoff_ms: int = 5000,
                     exponential_base: float = 2.0,
                     retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None) -> Callable:
    """
    Decorator לפונקציות שדורשות retry.
    
    Args:
        max_attempts: מספר ניסיונות
        initial_backoff_ms: השהיה ראשונית
        max_backoff_ms: השהיה מקסימלית
        exponential_base: בסיס exponential
        retryable_exceptions: tuple של exception types לretry (None = הגדל כללית)
    
    Example:
        @retry_on_failure(max_attempts=3, initial_backoff_ms=500)
        def click_element():
            ...
    """
    config = RetryConfig(max_attempts, initial_backoff_ms, max_backoff_ms, exponential_base)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}: {func.__name__}")
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if exception is retryable
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    if not is_retryable_error(e):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    # Last attempt failed
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                        )
                        raise
                    
                    # Calculate backoff and wait
                    backoff_seconds = config.calculate_backoff(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {type(e).__name__} - {e}. "
                        f"Retrying in {backoff_seconds:.2f}s..."
                    )
                    time.sleep(backoff_seconds)
            
            # Safety: should never reach here
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator


async def retry_on_failure_async(max_attempts: int = 3,
                                  initial_backoff_ms: int = 500,
                                  max_backoff_ms: int = 5000,
                                  exponential_base: float = 2.0,
                                  retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None) -> Callable:
    """
    Async decorator לפונקציות עם retry.
    
    Args:
        (ראה retry_on_failure)
    
    Example:
        @retry_on_failure_async(max_attempts=3)
        async def async_action():
            ...
    """
    config = RetryConfig(max_attempts, initial_backoff_ms, max_backoff_ms, exponential_base)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}: {func.__name__}")
                    return await func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    if not is_retryable_error(e):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                        )
                        raise
                    
                    backoff_seconds = config.calculate_backoff(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {type(e).__name__} - {e}. "
                        f"Retrying in {backoff_seconds:.2f}s..."
                    )
                    await asyncio.sleep(backoff_seconds)
            
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator
