import requests
import json

url = "http://localhost:5000/api/tennis/matches?days=7"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse type: {type(data)}")
    
    if isinstance(data, list):
        print(f"Number of matches: {len(data)}")
        if len(data) > 0:
            print("\n✅ FIRST MATCH:")
            print(json.dumps(data[0], indent=2, default=str))
        else:
            print("\n⚠️ Empty matches list")
    else:
        print(f"\nFull response:")
        print(json.dumps(data, indent=2, default=str))
        
except Exception as e:
    print(f"❌ Error: {e}")
