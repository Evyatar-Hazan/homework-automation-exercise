"""
Step Context Manager
====================

Thread-safe step context management for Allure integration.
Uses contextvars for isolation between parallel test executions.

Features:
- ✅ Automatic step opening/closing with allure.step()
- ✅ Thread/Process safe (pytest -n compatible)
- ✅ Attachments are scoped to active step
- ✅ Clean context cleanup on step exit
- ✅ No globals - pure contextvars
"""

import allure
from contextvars import ContextVar
from typing import Optional, Any, Callable
from contextlib import contextmanager


# Thread-safe context variable for tracking active step
_active_step_context: ContextVar[Optional['StepContext']] = ContextVar('active_step', default=None)


class StepContext:
    """
    Represents an active Allure step with context management.
    
    Each test/thread has its own isolated context.
    """
    
    def __init__(self, step_name: str):
        """
        Initialize step context.
        
        Args:
            step_name: Name of the step (shown in Allure report)
        """
        self.step_name = step_name
        self._allure_step_context = None
        self._previous_step = None
    
    def __enter__(self):
        """Enter step context - opens allure.step and registers as active."""
        # Save previous step (if any) for restoration
        self._previous_step = _active_step_context.get()
        
        # Close previous step if exists
        if self._previous_step and self._previous_step._allure_step_context:
            try:
                self._previous_step._allure_step_context.__exit__(None, None, None)
            except Exception:
                pass  # Fail silently if step was already closed
        
        # Open new allure step
        self._allure_step_context = allure.step(self.step_name)
        self._allure_step_context.__enter__()
        
        # Register as active step
        _active_step_context.set(self)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit step context - closes allure.step and cleans up."""
        # Close allure step
        if self._allure_step_context:
            try:
                self._allure_step_context.__exit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        
        # Restore previous step (or None)
        _active_step_context.set(self._previous_step)
        
        return False  # Don't suppress exceptions
    
    def attach(self, body: str, name: str = "attachment", 
               attachment_type=allure.attachment_type.TEXT) -> None:
        """
        Attach data to current step.
        
        Args:
            body: Content to attach
            name: Attachment name
            attachment_type: Allure attachment type
        """
        # Ensure body is not empty and is a string
        if not body:
            body = "(empty)"
        
        body_str = str(body) if body else "(no content)"
        name_str = str(name) if name else "attachment"
        
        # Attach directly to allure
        allure.attach(
            body=body_str,
            name=name_str,
            attachment_type=attachment_type
        )


def get_active_step() -> Optional[StepContext]:
    """
    Get currently active step context.
    
    Returns:
        Active StepContext or None if no step is active
    """
    return _active_step_context.get()


def is_step_active() -> bool:
    """
    Check if a step is currently active.
    
    Returns:
        True if step is active, False otherwise
    """
    return _active_step_context.get() is not None


@contextmanager
def step(step_name: str):
    """
    Context manager for creating a step.
    
    Usage:
        with step("Step 1: Login"):
            # Your code here
            pass
    
    Args:
        step_name: Name of the step
    """
    step_context = StepContext(step_name)
    with step_context:
        yield step_context


def attach_to_active_step(body: str, name: str = "attachment", 
                          attachment_type=allure.attachment_type.TEXT) -> None:
    """
    Attach data to the currently active step.
    If no step is active, attaches to test level.
    
    Args:
        body: Content to attach
        name: Attachment name
        attachment_type: Allure attachment type
    """
    # Ensure body is not empty
    if not body:
        body = "(empty)"
    
    body_str = str(body) if body else "(no content)"
    name_str = str(name) if name else "attachment"
    
    active_step = get_active_step()
    if active_step:
        # We're inside a step - attach to it
        allure.attach(
            body=body_str,
            name=name_str,
            attachment_type=attachment_type
        )
    else:
        # Fallback to test-level attachment
        allure.attach(
            body=body_str,
            name=name_str,
            attachment_type=attachment_type
        )


def clear_step_context() -> None:
    """
    Clear step context (useful for cleanup in hooks).
    Should rarely be needed as context is auto-managed.
    """
    _active_step_context.set(None)
