"""
Shared pytest fixtures and configuration.
"""

import pytest
import sys
from pathlib import Path

# Add server to path
server_path = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_path))


@pytest.fixture(scope="session")
def api_url():
    """API base URL for integration tests."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def test_user_id():
    """Test user ID."""
    return "test-user-123"


@pytest.fixture
def sample_decision():
    """Sample decision data for testing."""
    return {
        "context": "Should I invest in stocks or real estate?",
        "variants": ["Stocks", "Real Estate"],
        "arguments": [
            {
                "variant_name": "Stocks",
                "text": "Stocks provide higher liquidity because I can sell anytime without waiting for buyers or dealing with real estate agents",
                "type": "pro"
            },
            {
                "variant_name": "Real Estate",
                "text": "Real estate offers tangible assets and passive income through rental yields, plus tax benefits from depreciation",
                "type": "pro"
            }
        ]
    }
