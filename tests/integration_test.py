import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    print("Testing health checks...")
    services = ["auth", "ingestion", "audit", "analytics", "configuration", "transformation"]
    for service in services:
        try:
            resp = requests.get(f"{BASE_URL}/{service}/health")
            print(f"Service {service} health: {resp.status_code} {resp.json()}")
        except Exception as e:
            print(f"Service {service} health FAILED: {e}")

def test_auth():
    print("\nTesting Auth...")
    login_data = {
        "username": "admin@territorial.com",
        "password": "admin123"
    }
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print("Login successful")
        return token
    else:
        print(f"Login FAILED: {resp.status_code} {resp.text}")
        return None

def test_ingestion(token):
    print("\nTesting Ingestion...")
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': ('test.csv', 'zone_code,zone_name,score_value,score_level\nBOG01,Test Zone,0.95,ALTA')}
    data = {"sourceName": "Test Source", "sourceType": "CSV"}
    resp = requests.post(f"{BASE_URL}/ingestion/datasets/upload", headers=headers, files=files, data=data)
    if resp.status_code == 200:
        dataset_id = resp.json()["datasetId"]
        print(f"Ingestion successful: dataset_id={dataset_id}")
        return dataset_id
    else:
        print(f"Ingestion FAILED: {resp.status_code} {resp.text}")
        return None

def test_ranking(token):
    print("\nTesting Ranking...")
    headers = {"Authorization": f"Bearer {token}"}
    # Using mock data by providing a random execution_id
    resp = requests.get(f"{BASE_URL}/analytics/ranking?execution_id=test-exec", headers=headers)
    if resp.status_code == 200:
        print(f"Ranking successful: {len(resp.json()['data'])} items found")
    else:
        print(f"Ranking FAILED: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    # Wait for gateway to be fully ready
    time.sleep(2)
    test_health()
    token = test_auth()
    if token:
        test_ingestion(token)
        test_ranking(token)
    else:
        print("Skipping further tests due to auth failure")
