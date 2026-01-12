"""
Unit tests for argument validation service.
"""

import pytest
from server.services.argument_validator import ArgumentQualityValidator


class TestArgumentQualityValidator:
    """Test argument validation logic."""
    
    def test_validate_argument_too_short(self):
        """Test that short arguments are rejected."""
        text = "Buy it"
        is_valid, error = ArgumentQualityValidator.validate_argument(text)
        
        assert not is_valid
        assert "too short" in error.lower()
    
    def test_validate_argument_no_reasoning(self):
        """Test that arguments without reasoning keywords are rejected."""
        text = "I want to buy a car for my daily commute and weekend trips"
        is_valid, error = ArgumentQualityValidator.validate_argument(text)
        
        assert not is_valid
        assert "reasoning keywords" in error.lower()
    
    def test_validate_argument_valid(self):
        """Test that valid arguments pass validation."""
        text = "I should buy a car because it will save me 2 hours daily on commute and provide flexibility for weekend trips"
        is_valid, error = ArgumentQualityValidator.validate_argument(text)
        
        assert is_valid
        assert error == ""
    
    def test_validate_arguments_all_valid(self):
        """Test validation of multiple valid arguments."""
        arguments = [
            {"text": "Buy because it saves time and money in the long run", "variant_name": "Buy"},
            {"text": "Wait since market conditions are unfavorable right now", "variant_name": "Wait"}
        ]
        
        result = ArgumentQualityValidator.validate_arguments(arguments)
        
        assert result['is_valid']
        assert result['quality_score'] == 1.0
        assert len(result['invalid_arguments']) == 0
    
    def test_validate_arguments_some_invalid(self):
        """Test validation with mix of valid and invalid arguments."""
        arguments = [
            {"text": "Buy", "variant_name": "Buy"},  # Invalid
            {"text": "Wait because market is down", "variant_name": "Wait"}  # Valid
        ]
        
        result = ArgumentQualityValidator.validate_arguments(arguments)
        
        assert not result['is_valid']
        assert result['quality_score'] == 0.5
        assert len(result['invalid_arguments']) == 1
    
    def test_assess_argument_quality_high(self):
        """Test quality assessment for high-quality argument."""
        text = """
        Based on extensive market research and financial analysis, purchasing now provides 
        optimal ROI because interest rates are at historic lows (2.5%), property values 
        are projected to appreciate 15% annually, and rental yields exceed mortgage costs.
        Multiple studies from Harvard Business Review and McKinsey support this timing.
        """
        
        score = ArgumentQualityValidator.assess_argument_quality(text)
        
        assert score > 0.7  # High quality
    
    def test_assess_argument_quality_low(self):
        """Test quality assessment for low-quality argument."""
        text = "Just buy it"
        
        score = ArgumentQualityValidator.assess_argument_quality(text)
        
        assert score < 0.2  # Low quality
    
    def test_assess_argument_quality_medium(self):
        """Test quality assessment for medium-quality argument."""
        text = "Buy because it's a good investment and prices are rising"
        
        score = ArgumentQualityValidator.assess_argument_quality(text)
        
        assert 0.2 <= score <= 0.7  # Medium quality


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
