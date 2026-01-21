"""
Random Utils Module
===================

Helper tools for controlled randomization and data generation.

Utilities:
- random_user_agent()
- random_viewport()
- random_delay()
- generate_random_email()
- generate_random_string()
"""

import random
import string
from typing import Tuple, Optional

# Common user agents (realistically rotated)
REAL_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# Common realistic viewport sizes
REALISTIC_VIEWPORTS = [
    (1920, 1080),  # Full HD
    (1366, 768),   # HD
    (1440, 900),   # 16:10
    (1600, 900),   # 16:9
    (2560, 1440),  # QHD (less common but valid)
]


def random_user_agent() -> str:
    """
    Get a random, realistic user agent.
    
    Mimics real browser traffic.
    """
    return random.choice(REAL_USER_AGENTS)


def random_viewport() -> Tuple[int, int]:
    """
    Get a random, realistic viewport size.
    
    Returns:
        Tuple of (width, height)
    """
    return random.choice(REALISTIC_VIEWPORTS)


def random_delay(min_ms: int = 100, max_ms: int = 500) -> float:
    """
    Generate random delay.
    
    Args:
        min_ms: minimum delay in milliseconds
        max_ms: maximum delay in milliseconds
    
    Returns:
        Delay in seconds
    """
    return random.uniform(min_ms, max_ms) / 1000.0


def generate_random_email(domain: str = "testmail.com") -> str:
    """
    Generate random email address.
    
    Args:
        domain: email domain (default: testmail.com)
    
    Returns:
        Random email address
    """
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{domain}"


def generate_random_string(length: int = 10,
                          chars: str = string.ascii_letters + string.digits) -> str:
    """
    Generate random string.
    
    Args:
        length: string length
        chars: characters to use
    
    Returns:
        Random string
    """
    return ''.join(random.choices(chars, k=length))


def generate_random_phone() -> str:
    """
    Generate random phone number (US format).
    
    Returns:
        Phone number as string (e.g., "555-123-4567")
    """
    area = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"{area}-{exchange}-{number}"


def generate_random_zip() -> str:
    """
    Generate random ZIP code (US format).
    
    Returns:
        5-digit ZIP code
    """
    return ''.join(random.choices(string.digits, k=5))


def random_boolean(true_probability: float = 0.5) -> bool:
    """
    Random boolean with configurable probability.
    
    Args:
        true_probability: probability of True (0.0-1.0)
    
    Returns:
        Random boolean
    """
    return random.random() < true_probability


def random_choice_weighted(items: dict) -> str:
    """
    Select random item with weighted probability.
    
    Args:
        items: dict of {item: weight} (weights don't need to sum to 1)
    
    Returns:
        Selected item
    
    Example:
        color = random_choice_weighted({"red": 0.7, "blue": 0.3})
    """
    choices = list(items.keys())
    weights = list(items.values())
    return random.choices(choices, weights=weights, k=1)[0]
