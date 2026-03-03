import urllib.request
import json

url = "http://127.0.0.1:8000/auth/register"
data = {
    "name": "Test User",
    "email": "test12345@example.com",
    "password": "TestPassword123!",
    "role": "candidate"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    response = urllib.request.urlopen(req)
    print(f"Status Code: {response.status}")
    print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
