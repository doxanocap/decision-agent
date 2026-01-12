"""
Unit tests for ML scoring service.
"""

import pytest
from server.services.ml_scoring import MLScoring


class TestMLScoring:
    """Test ML scoring logic."""
    
    @pytest.fixture
    def ml_scoring(self):
        """Create ML scoring instance."""
        return MLScoring()
    
    def test_score_single_argument(self, ml_scoring):
        """Test scoring a single argument."""
        arguments = [
            {
                "id": "arg_1",
                "text": "Buy because it provides long-term value and stability"
            }
        ]
        context = "Should I buy or rent?"
        
        scores = ml_scoring.score_arguments(arguments, context)
        
        assert "arg_1" in scores
        assert 0 <= scores["arg_1"] <= 100
    
    def test_score_multiple_arguments(self, ml_scoring):
        """Test scoring multiple arguments."""
        arguments = [
            {
                "id": "arg_1",
                "text": "Buy because it builds equity and provides tax benefits over time"
            },
            {
                "id": "arg_2",
                "text": "Rent because it offers flexibility and lower upfront costs"
            }
        ]
        context = "Should I buy or rent a house?"
        
        scores = ml_scoring.score_arguments(arguments, context)
        
        assert len(scores) == 2
        assert all(0 <= score <= 100 for score in scores.values())
    
    def test_weak_argument_gets_low_score(self, ml_scoring):
        """Test that weak arguments get calibrated to low scores."""
        arguments = [
            {
                "id": "arg_1",
                "text": "Just buy it"  # Very weak
            }
        ]
        context = "Should I buy?"
        
        scores = ml_scoring.score_arguments(arguments, context)
        
        # Should be calibrated to low score (< 20)
        assert scores["arg_1"] < 20
    
    def test_strong_argument_gets_high_score(self, ml_scoring):
        """Test that strong arguments get high scores."""
        arguments = [
            {
                "id": "arg_1",
                "text": """
                Based on comprehensive market analysis and financial projections, 
                purchasing now is optimal because interest rates are at 2.5% (historic low), 
                property values are expected to appreciate 15% annually according to 
                multiple real estate studies, and rental yields in this area exceed 
                mortgage costs by 20%. This creates positive cash flow from day one.
                """
            }
        ]
        context = "Should I buy investment property?"
        
        scores = ml_scoring.score_arguments(arguments, context)
        
        # Should get high score (> 60)
        assert scores["arg_1"] > 60
    
    def test_zero_shot_calibration(self, ml_scoring):
        """Test that zero-shot calibration works."""
        # Argument weaker than baseline "I just want it, no reason"
        weak_arg = [
            {
                "id": "arg_1",
                "text": "Buy"  # Extremely weak
            }
        ]
        context = "Should I buy?"
        
        scores = ml_scoring.score_arguments(weak_arg, context)
        
        # Should be forced to 0-10 range
        assert scores["arg_1"] <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
