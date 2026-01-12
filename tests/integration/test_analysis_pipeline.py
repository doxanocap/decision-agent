"""
Integration tests for the complete analysis pipeline.
"""

import pytest
import requests
import time
from uuid import uuid4


API_URL = "http://localhost:8000"


class TestAnalysisPipeline:
    """Test end-to-end analysis flow."""
    
    @pytest.fixture(scope="class")
    def user_id(self):
        """Generate a test user ID."""
        return str(uuid4())
    
    def test_health_check(self):
        """Test that health check endpoints work."""
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_detailed_health_check(self):
        """Test detailed health check."""
        response = requests.get(f"{API_URL}/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "database" in data
        assert "ml_scoring" in data
    
    def test_analyze_valid_decision(self, user_id):
        """Test analyzing a valid decision."""
        decision_data = {
            "context": "Should I switch to remote work or stay in office?",
            "variants": ["Remote", "Office"],
            "arguments": [
                {
                    "variant_name": "Remote",
                    "text": "Remote work provides better work-life balance because I can save 2 hours daily on commute and have more flexibility for personal tasks",
                    "type": "pro"
                },
                {
                    "variant_name": "Office",
                    "text": "Office work enables better collaboration since face-to-face meetings are more effective for complex discussions and team building",
                    "type": "pro"
                }
            ]
        }
        
        # Start analysis
        response = requests.post(
            f"{API_URL}/analysis/analyze",
            json=decision_data,
            headers={"X-User-ID": user_id}
        )
        
        assert response.status_code == 202
        data = response.json()
        assert "decision_id" in data
        
        decision_id = data["decision_id"]
        
        # Poll for results
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(
                f"{API_URL}/analysis/{decision_id}/status",
                headers={"X-User-ID": user_id}
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                # Verify results structure
                results = status_data["results"]
                assert "ml_scores" in results
                assert "llm_analysis" in results
                assert "retrieved_context" in results
                
                # Verify ML scores
                assert len(results["ml_scores"]) == 2
                for score in results["ml_scores"].values():
                    assert 0 <= score <= 100
                
                # Verify LLM analysis
                analysis = results["llm_analysis"]
                assert "final_note" in analysis
                assert "key_weak_points_to_reconsider" in analysis
                
                return  # Success
            
            elif status_data["status"] == "failed":
                pytest.fail(f"Analysis failed: {status_data.get('results', {})}")
            
            time.sleep(3)
        
        pytest.fail("Analysis timed out")
    
    def test_analyze_insufficient_data(self, user_id):
        """Test that insufficient data is rejected."""
        decision_data = {
            "context": "Should I buy?",
            "variants": ["Buy", "Wait"],
            "arguments": [
                {
                    "variant_name": "Buy",
                    "text": "Just do it",  # Too short, no reasoning
                    "type": "pro"
                }
            ]
        }
        
        response = requests.post(
            f"{API_URL}/analysis/analyze",
            json=decision_data,
            headers={"X-User-ID": user_id}
        )
        
        assert response.status_code == 202
        decision_id = response.json()["decision_id"]
        
        # Wait a bit for validation
        time.sleep(2)
        
        status_response = requests.get(
            f"{API_URL}/analysis/{decision_id}/status",
            headers={"X-User-ID": user_id}
        )
        
        status_data = status_response.json()
        
        # Should fail with INSUFFICIENT_DATA
        assert status_data["status"] == "failed"
        assert "INSUFFICIENT_DATA" in str(status_data.get("results", {}))
    
    def test_get_decision_history(self, user_id):
        """Test retrieving decision history."""
        response = requests.get(
            f"{API_URL}/decisions",
            headers={"X-User-ID": user_id}
        )
        
        assert response.status_code == 200
        decisions = response.json()
        assert isinstance(decisions, list)
    
    def test_update_decision_outcome(self, user_id):
        """Test updating decision outcome."""
        # First create a decision
        decision_data = {
            "context": "Test decision for outcome update",
            "variants": ["A", "B"],
            "arguments": [
                {
                    "variant_name": "A",
                    "text": "Option A is better because it provides long-term benefits and aligns with strategic goals",
                    "type": "pro"
                }
            ]
        }
        
        create_response = requests.post(
            f"{API_URL}/analysis/analyze",
            json=decision_data,
            headers={"X-User-ID": user_id}
        )
        
        decision_id = create_response.json()["decision_id"]
        
        # Wait for analysis to complete
        time.sleep(5)
        
        # Update outcome
        outcome_data = {
            "selected_variant": "A",
            "outcome_reasoning": "Chose A because it aligned with long-term strategy"
        }
        
        update_response = requests.put(
            f"{API_URL}/decisions/{decision_id}/outcome",
            json=outcome_data,
            headers={"X-User-ID": user_id}
        )
        
        assert update_response.status_code == 200


if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{API_URL}/health", timeout=2)
    except:
        print("❌ Server not running! Start it with: make back")
        exit(1)
    
    pytest.main([__file__, "-v", "-s"])
