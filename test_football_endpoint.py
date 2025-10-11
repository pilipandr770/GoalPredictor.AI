import requests
import json

url = "http://localhost:5000/api/football/matches?days=7"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse type: {type(data)}")
    print(f"Success: {data.get('success')}")
    print(f"Count: {data.get('count')}")
    
    matches = data.get('matches', [])
    print(f"\nNumber of matches: {len(matches)}")
    
    if len(matches) > 0:
        print("\n✅ FIRST 3 MATCHES:")
        for i, match in enumerate(matches[:3]):
            print(f"\n{i+1}. {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
            print(f"   Competition: {match['competition']}")
            print(f"   Date: {match['date']}")
            print(f"   Status: {match['status']}")
    else:
        print("\n⚠️ No matches found")
        
except Exception as e:
    print(f"❌ Error: {e}")
