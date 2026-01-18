"""
Automation Utils Module
=======================

Utility functions for test support.

Modules:
- human_actions: Human-like behavior simulation
- random_utils: Random data generation
"""

from automation.utils.human_actions import HumanActions, initialize_human_actions, get_human_actions
from automation.utils.random_utils import (
    random_user_agent,
    random_viewport,
    random_delay,
    generate_random_email,
    generate_random_string,
)

__all__ = [
    'HumanActions',
    'initialize_human_actions',
    'get_human_actions',
    'random_user_agent',
    'random_viewport',
    'random_delay',
    'generate_random_email',
    'generate_random_string',
]
