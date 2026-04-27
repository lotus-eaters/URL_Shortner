# tests/conftest.py
"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta, timezone

# Set test environment
os.environ["DEBUG"] = "True"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for async tests"""
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """Create event loop for async tests"""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


# pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (deselect with '-m \"not asyncio\"')"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication test"
    )
    config.addinivalue_line(
        "markers", "url: mark test as URL shortening test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
