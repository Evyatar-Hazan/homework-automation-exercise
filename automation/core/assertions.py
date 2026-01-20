"""
Smart Assertions Module
========================

Centralized assertion framework for test automation.
Each assertion type:
- Logs the check
- Attaches to Allure report
- Handles failures gracefully
- Supports custom error messages

Usage:
    from automation.core import SmartAssert
    
    # Assert True
    SmartAssert.true(condition, "Step description", "Error message if false")
    
    # Assert False
    SmartAssert.false(condition, "Step description", "Error message if true")
    
    # Assert Equal
    SmartAssert.equal(actual, expected, "Step description", "Error message if not equal")
    
    # Assert Contains
    SmartAssert.contains(text, substring, "Step description", "Error message if not contains")
    
    # Custom assertion
    SmartAssert.custom(condition, "Step description", "Error message")
"""

import allure
from automation.core import get_logger

logger = get_logger(__name__)


class SmartAssert:
    """Smart assertion framework with logging and Allure integration."""
    
    @staticmethod
    def true(condition: bool, step_description: str, error_message: str = "Assertion failed") -> bool:
        """
        Assert that condition is True.
        
        Args:
            condition: Boolean condition to check
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If condition is False
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        
        if condition is True:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description} - Result: TRUE"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            
            with allure.step(f"❌ {step_description} - Error: {error_message}"):
                pass
            
            raise AssertionError(f"{step_description}\n{error_message}")
    
    @staticmethod
    def false(condition: bool, step_description: str, error_message: str = "Assertion failed") -> bool:
        """
        Assert that condition is False.
        
        Args:
            condition: Boolean condition to check
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If condition is True
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        
        if condition is False:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description} - Result: FALSE"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            
            with allure.step(f"❌ {step_description} - Error: {error_message}"):
                pass
            
            raise AssertionError(f"{step_description}\n{error_message}")
    
    @staticmethod
    def equal(actual, expected, step_description: str, error_message: str = "Values are not equal") -> bool:
        """
        Assert that actual equals expected.
        
        Args:
            actual: Actual value
            expected: Expected value
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If actual != expected
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        logger.info(f"   Expected: {expected}")
        logger.info(f"   Actual: {actual}")
        
        if actual == expected:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description}\nExpected: {expected}\nActual: {actual}\nMatch: ✓"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            logger.error(f"   Expected: {expected}")
            logger.error(f"   Actual: {actual}")
            
            with allure.step(f"❌ {step_description}\nError: {error_message}\nExpected: {expected}\nActual: {actual}"):
                pass
            
            raise AssertionError(f"{step_description}\nExpected: {expected}\nActual: {actual}\n{error_message}")
    
    @staticmethod
    def contains(text: str, substring: str, step_description: str, error_message: str = "Text does not contain substring") -> bool:
        """
        Assert that text contains substring.
        
        Args:
            text: Text to search in
            substring: Substring to find
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If substring not in text
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        logger.info(f"   Looking for: '{substring}'")
        logger.info(f"   In text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        if substring in text:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description}\nLooking for: '{substring}'\nFound in: '{text}'\nMatch: ✓"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            logger.error(f"   Substring not found: '{substring}'")
            logger.error(f"   In text: '{text}'")
            
            with allure.step(f"❌ {step_description}\nError: {error_message}\nLooking for: '{substring}'\nIn text: '{text}'"):
                pass
            
            raise AssertionError(f"{step_description}\n'{substring}' not found in '{text}'\n{error_message}")
    
    @staticmethod
    def not_contains(text: str, substring: str, step_description: str, error_message: str = "Text contains unwanted substring") -> bool:
        """
        Assert that text does NOT contain substring.
        
        Args:
            text: Text to search in
            substring: Substring that should NOT be found
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If substring found in text
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        logger.info(f"   Should NOT contain: '{substring}'")
        logger.info(f"   In text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        if substring not in text:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description}\nShould NOT contain: '{substring}'\nText: '{text}'\nCorrect: ✓"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            logger.error(f"   Unwanted substring found: '{substring}'")
            logger.error(f"   In text: '{text}'")
            
            with allure.step(f"❌ {step_description}\nError: {error_message}\nUnwanted substring: '{substring}'\nFound in: '{text}'"):
                pass
            
            raise AssertionError(f"{step_description}\n'{substring}' found in '{text}'\n{error_message}")
    
    @staticmethod
    def custom(condition: bool, step_description: str, error_message: str = "Custom assertion failed") -> bool:
        """
        Custom assertion with any condition.
        
        Args:
            condition: Boolean condition to check
            step_description: Description of what is being verified
            error_message: Custom error message if assertion fails
        
        Returns:
            True if assertion passes
        
        Raises:
            AssertionError: If condition is False
        """
        logger.info(f"🔍 CHECKING: {step_description}")
        
        if condition:
            log_msg = f"✅ PASS: {step_description}"
            logger.info(log_msg)
            
            with allure.step(f"✅ {step_description}\nCustom assertion passed"):
                pass
            
            return True
        else:
            log_msg = f"❌ FAIL: {step_description}\n   Error: {error_message}"
            logger.error(log_msg)
            
            with allure.step(f"❌ {step_description}\nError: {error_message}"):
                pass
            
            raise AssertionError(f"{step_description}\n{error_message}")

