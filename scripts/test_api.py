#!/usr/bin/env python3
"""
Test the Analysis API endpoint.
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoints."""
    print("=" * 60)
    print("Testing Health Checks")
    print("=" * 60)
    
    # Main health
    response = requests.get(f"{API_URL}/health")
    print(f"\nMain Health: {response.json()}")
    
    # Analysis health
    response = requests.get(f"{API_URL}/analysis/health")
    print(f"Analysis Health: {response.json()}")


def test_analyze():
    """Test the analyze endpoint and polling."""
    print("\n" + "=" * 60)
    print("Testing Analysis (Async + Polling)")
    print("=" * 60)
    
    # Sample decision
    decision_data = {
        "context": "Выбор между покупкой квартиры в ипотеку или арендой и инвестированием разницы.",
        "variants": ["Ипотека", "Аренда + Инвестиции"],
        "arguments": [
            {
                "variant_name": "Ипотека",
                "text": "Своё жилье дает чувство стабильности и безопасности.",
                "type": "pro"
            },
            {
                "variant_name": "Ипотека",
                "text": "Ипотека — это долговая кабала на 20 лет, которая ограничивает мобильность.",
                "type": "con"
            },
            {
                "variant_name": "Аренда + Инвестиции",
                "text": "Аренда позволяет легко сменить район или город при необходимости.",
                "type": "pro"
            },
            {
                "variant_name": "Аренда + Инвестиции",
                "text": "При аренде деньги уходят 'в никуда', не создавая капитала в виде недвижимости.",
                "type": "con"
            }
        ]
    }
    
    print("\nSending request to start analysis...")
    response = requests.post(
        f"{API_URL}/analysis/analyze",
        json=decision_data
    )
    
    if response.status_code != 202:
        print(f"❌ Failed to start: {response.status_code}")
        print(response.json())
        return

    data = response.json()
    decision_id = data["decision_id"]
    print(f"✅ Started! ID: {decision_id}")

    # Polling
    print("\nPolling for results (timeout 60s)...")
    start_time = time.time()
    while time.time() - start_time < 60:
        status_res = requests.get(f"{API_URL}/analysis/{decision_id}/status")
        status_data = status_res.json()
        current_status = status_data["status"]
        
        print(f"  [{int(time.time() - start_time)}s] Status: {current_status}")
        
        if current_status == "completed":
            print("\n✅ Analysis complete!")
            results = status_data["results"]
            
            print("\nML Scores:")
            for arg_id, score in results['ml_scores'].items():
                print(f"  {arg_id}: {score:.2f}/100")
            
            print("\nLLM Analysis Summary:")
            analysis = results['llm_analysis']
            print(f"  Weak Points: {len(analysis['key_weak_points_to_reconsider'])}")
            print(f"  Final Note: {analysis['final_note']}")
            return
            
        if current_status == "failed":
            print("\n❌ Analysis failed according to DB status.")
            return
            
        time.sleep(3)
    
    print("\n⏱️ Polling timed out.")

if __name__ == "__main__":
    print("Starting API Tests...\n")
    
    # Check if server is running
    try:
        requests.get(f"{API_URL}/", timeout=2)
    except:
        print("❌ Server not running! Start it with:")
        print("   cd server && python main.py")
        exit(1)
    
    test_health()
    test_analyze()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
