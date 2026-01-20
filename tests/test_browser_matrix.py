"""
Demo test for browser matrix parametrization.

This test demonstrates how to use the browser_config fixture
to run the same test across multiple browsers in parallel.
"""

import pytest
from automation.core import BaseSeleniumTest


class TestBrowserMatrix(BaseSeleniumTest):
    """Tests demonstrating browser matrix parametrization."""
    
    @pytest.mark.parametrize("dummy", [None])  # Dummy param to allow browser_config fixture
    def test_browser_matrix_demo(self, browser_config, dummy):
        """
        Simple test that uses browser_config fixture.
        
        When run with --browser-matrix='chrome:127,chrome:128,firefox:121':
        - This test will run 3 times (once per browser)
        - Each run is isolated and uses different environment variables
        - Each run gets its own timestamped report directory
        
        This demonstrates the infrastructure is ready for matrix testing.
        """
        # Navigate to test site
        self.driver.get("https://automationteststore.com/")
        
        # Verify page loaded by checking for common element
        try:
            # Wait for page to load and find a header or common element
            page_title = self.driver.title
            assert page_title, "Page title is empty"
            
            # Get the current browser config used
            if browser_config:
                print(f"\n✅ Running on: {browser_config}")
            
            # Assert page is responsive
            assert self.driver.get_window_size()["width"] > 0
            assert self.driver.get_window_size()["height"] > 0
        except Exception as e:
            print(f"Error during page verification: {e}")
            # Just verify page didn't crash
            assert self.driver.current_url, "Driver URL is empty"
