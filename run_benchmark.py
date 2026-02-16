import requests
import time
import json

def run_benchmark():
    url = "http://localhost:10000/analyze-report/"
    headers = {
        "x-api-key": "test-key",
        "Content-Type": "application/json"
    }
    data = {"glucose": 110, "cholesterol": 190}
    
    print("--- Performance Benchmark ---")
    
    # First call (cold - should take a few seconds for LLM)
    print("Test 1: Cold start analysis (LLM extraction)...")
    start = time.time()
    resp1 = requests.post(url, headers=headers, json=data)
    duration1 = time.time() - start
    
    if resp1.status_code == 200:
        print(f"Cold duration: {duration1:.2f}s")
    else:
        print(f"Test failed with status {resp1.status_code}")
        return

    # Second call (cached - should be near instant)
    print("Test 2: Cached analysis (Instant results)...")
    start = time.time()
    resp2 = requests.post(url, headers=headers, json=data)
    duration2 = time.time() - start
    
    if resp2.status_code == 200:
        print(f"Cached duration: {duration2:.2f}s")
        improvement = duration1 / duration2 if duration2 > 0 else 100
        print(f"Speed Improvement: {improvement:.1f}x faster 🚀")
    else:
        print(f"Test failed with status {resp2.status_code}")

if __name__ == "__main__":
    run_benchmark()
