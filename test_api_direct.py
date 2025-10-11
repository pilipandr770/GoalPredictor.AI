"""Quick test - fetch today's matches"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('RAPIDAPI_TENNIS_KEY')
BASE_URL = "https://tennis-api-atp-wta-itf.p.rapidapi.com"

today = datetime.now().strftime('%Y-%m-%d')
url = f"{BASE_URL}/tennis/v2/atp/fixtures/{today}"

headers = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': 'tennis-api-atp-wta-itf.p.rapidapi.com'
}

print(f"Requesting: {url}")
print(f"Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print()

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    print()
    print("Full response:")
    import json
    print(json.dumps(data, indent=2)[:1000])
else:
    print(f"Error: {response.text}")
