import requests
import json

base_url = "https://web-production-defd0.up.railway.app"

def test_endpoint(path, method="GET", data=None):
    url = f"{base_url}{path}"
    print(f"\n--- Testing {method} {url} ---")
    try:
        if method == "GET":
            resp = requests.get(url, timeout=30)
        else:
            resp = requests.post(url, json=data, timeout=60)
            
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        return resp
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Checking Root...")
test_endpoint("/")

print("\nChecking Health...")
test_endpoint("/health")

print("\nChecking Chat API (Real Query)...")
test_endpoint("/api/chat", method="POST", data={"query": "Who is patient P001?"})
