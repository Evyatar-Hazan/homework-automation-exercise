"""
Step-Aware Logging Example
===========================

Demonstrates the new step-aware logging API with Allure integration.
Run this test to see hierarchical steps with attachments in Allure report.

Run:
    pytest tests/example_step_aware_logging.py --alluredir=automation/reports/allure-results
    allure serve automation/reports/allure-results
"""

import pytest
import allure
from automation.core.logger import (
    step_aware_loggerStep,
    step_aware_loggerInfo,
    step_aware_loggerAttach,
    get_current_step_name,
    is_in_step
)


@allure.feature("Step-Aware Logging Demo")
@allure.story("Basic Usage")
class TestStepAwareLogging:
    
    def test_login_with_steps(self):
        """
        Example: Login flow with hierarchical steps.
        
        Shows how attachments automatically bind to active steps.
        """
        
        # Step 1: Navigate (using context manager)
        with step_aware_loggerStep("Step 1: Navigate to login page"):
            step_aware_loggerInfo("Opening browser")
            step_aware_loggerInfo("URL: https://automationteststore.com/")
            
            assert is_in_step(), "Should be inside a step"
            assert get_current_step_name() == "Step 1: Navigate to login page"
        
        # Step 2: Fill form (using action callable)
        def fill_form_action():
            step_aware_loggerInfo("Entering username: admin")
            step_aware_loggerInfo("Entering password: ********")
            step_aware_loggerAttach("Form data validated", name="form_validation")
            return "form_filled"
        
        result = step_aware_loggerStep(
            "Step 2: Fill login credentials",
            action=fill_form_action
        )
        
        assert result == "form_filled", "Action should return result"
        
        # Step 3: Submit (with validation)
        def submit_action():
            step_aware_loggerInfo("Clicking submit button")
            return {"status": 200, "message": "Login successful"}
        
        def validate_response(response):
            step_aware_loggerInfo(f"Validating response: {response['status']}")
            step_aware_loggerAttach(
                str(response),
                name="api_response",
                attachment_type=allure.attachment_type.JSON
            )
            assert response["status"] == 200
        
        response = step_aware_loggerStep(
            "Step 3: Submit login form",
            action=submit_action,
            validate=validate_response
        )
        
        # Step 4: Verify dashboard
        with step_aware_loggerStep("Step 4: Verify dashboard loaded"):
            step_aware_loggerInfo("Checking dashboard title")
            step_aware_loggerInfo("Verifying user menu visible")
            step_aware_loggerAttach("Dashboard verification passed ✅", name="verification_result")
    
    
    def test_search_with_steps(self):
        """
        Example: Search flow with multiple steps.
        
        Demonstrates automatic step closure when new step opens.
        """
        
        # Step 1 opens
        with step_aware_loggerStep("Step 1: Enter search term"):
            step_aware_loggerInfo("Search term: 'skincare'")
            step_aware_loggerAttach("Search input: skincare", name="search_input")
        
        # Step 2 opens (Step 1 auto-closed)
        with step_aware_loggerStep("Step 2: Execute search"):
            step_aware_loggerInfo("Clicking search button")
            step_aware_loggerInfo("Loading results...")
            step_aware_loggerAttach("Found 15 results", name="search_results_count")
        
        # Step 3
        with step_aware_loggerStep("Step 3: Verify results"):
            step_aware_loggerInfo("Verifying result count > 0")
            step_aware_loggerInfo("Checking first result visibility")
            step_aware_loggerAttach("Search completed successfully", name="verification")
    
    
    def test_no_step_fallback(self):
        """
        Example: Logging without active step.
        
        Shows that attachments work at test level when no step is active.
        """
        
        # No step active - attaches at test level
        step_aware_loggerInfo("This is test-level info (no step)")
        step_aware_loggerAttach("Test-level attachment", name="test_attachment")
        
        assert not is_in_step(), "Should not be in a step"
        assert get_current_step_name() is None, "Step name should be None"
        
        # Now create a step
        with step_aware_loggerStep("Step 1: Inside step"):
            step_aware_loggerInfo("This attaches to Step 1")
            assert is_in_step(), "Should be in a step now"
    
    
    def test_nested_actions(self):
        """
        Example: Nested action calls with steps.
        
        Shows that each action gets its own step context.
        """
        
        def outer_action():
            step_aware_loggerInfo("Outer action started")
            
            # Inner step
            def inner_action():
                step_aware_loggerInfo("Inner action executed")
                return "inner_result"
            
            inner_result = step_aware_loggerStep(
                "Substep: Inner operation",
                action=inner_action
            )
            
            step_aware_loggerInfo(f"Inner result: {inner_result}")
            return "outer_result"
        
        result = step_aware_loggerStep(
            "Step 1: Outer operation",
            action=outer_action
        )
        
        assert result == "outer_result"


@allure.feature("Step-Aware Logging Demo")
@allure.story("Parallel Execution Safety")
class TestParallelSafety:
    """
    These tests demonstrate thread safety.
    
    Run with: pytest -n 4 tests/example_step_aware_logging.py
    """
    
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    def test_concurrent_users(self, user_id):
        """
        Simulates multiple users logging in concurrently.
        
        Each test execution has isolated step context (no cross-talk).
        """
        
        with step_aware_loggerStep(f"Step 1: User {user_id} - Navigate"):
            step_aware_loggerInfo(f"User {user_id}: Opening page")
            step_aware_loggerAttach(f"User ID: {user_id}", name="user_context")
        
        def login_user():
            step_aware_loggerInfo(f"User {user_id}: Entering credentials")
            step_aware_loggerInfo(f"User {user_id}: Submitting form")
            return f"user_{user_id}_logged_in"
        
        result = step_aware_loggerStep(
            f"Step 2: User {user_id} - Login",
            action=login_user
        )
        
        with step_aware_loggerStep(f"Step 3: User {user_id} - Verify"):
            step_aware_loggerInfo(f"User {user_id}: Checking dashboard")
            step_aware_loggerAttach(
                f"Login result: {result}",
                name="login_verification"
            )
        
        assert f"user_{user_id}" in result


if __name__ == "__main__":
    """
    Direct execution for quick testing.
    """
    pytest.main([__file__, "-v", "--alluredir=automation/reports/allure-results"])
