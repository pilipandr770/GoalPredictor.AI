"""
Тест Football-Data.org API для диагностики
"""
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('FOOTBALL_DATA_ORG_KEY')
BASE_URL = 'https://api.football-data.org/v4'

headers = {
    'X-Auth-Token': API_KEY
}

print("="*70)
print("🔍 Football-Data.org API Diagnostic Test")
print("="*70)
print(f"API Key: {API_KEY[:20]}...{API_KEY[-5:]}")
print()

# Test 1: Get today's matches
print("📅 Test 1: Matches TODAY")
print("-"*70)
date_today = datetime.now().strftime('%Y-%m-%d')
print(f"Date: {date_today}")

response = requests.get(
    f"{BASE_URL}/matches",
    headers=headers,
    params={
        'dateFrom': date_today,
        'dateTo': date_today
    },
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers:")
print(f"  X-Requests-Available-Minute: {response.headers.get('X-Requests-Available-Minute', 'N/A')}")
print(f"  X-Requests-Available-Day: {response.headers.get('X-Requests-Available-Day', 'N/A')}")
print()

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    print(f"✅ Found {len(matches)} matches today")
    
    if matches:
        for i, match in enumerate(matches[:5], 1):
            print(f"\n  {i}. {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
            print(f"     Competition: {match['competition']['name']}")
            print(f"     Time: {match['utcDate']}")
            print(f"     Status: {match['status']}")
    else:
        print("  ℹ️  No matches scheduled for today")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text}")

print()
print()

# Test 2: Get matches for next 7 days
print("📅 Test 2: Matches NEXT 7 DAYS")
print("-"*70)
date_from = datetime.now().strftime('%Y-%m-%d')
date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
print(f"Date Range: {date_from} to {date_to}")

response = requests.get(
    f"{BASE_URL}/matches",
    headers=headers,
    params={
        'dateFrom': date_from,
        'dateTo': date_to
    },
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers:")
print(f"  X-Requests-Available-Minute: {response.headers.get('X-Requests-Available-Minute', 'N/A')}")
print(f"  X-Requests-Available-Day: {response.headers.get('X-Requests-Available-Day', 'N/A')}")
print()

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    print(f"✅ Found {len(matches)} matches in next 7 days")
    
    if matches:
        # Group by competition
        by_competition = {}
        for match in matches:
            comp = match['competition']['name']
            if comp not in by_competition:
                by_competition[comp] = []
            by_competition[comp].append(match)
        
        print(f"\n  Matches by Competition:")
        for comp, comp_matches in list(by_competition.items())[:10]:
            print(f"    - {comp}: {len(comp_matches)} matches")
        
        print(f"\n  First 5 matches:")
        for i, match in enumerate(matches[:5], 1):
            print(f"\n  {i}. {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
            print(f"     Competition: {match['competition']['name']}")
            print(f"     Time: {match['utcDate']}")
            print(f"     Status: {match['status']}")
    else:
        print("  ⚠️  No matches found in next 7 days (unusual!)")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text[:500]}")

print()
print()

# Test 3: Check specific competition (Premier League)
print("📅 Test 3: Premier League matches")
print("-"*70)

response = requests.get(
    f"{BASE_URL}/competitions/PL/matches",
    headers=headers,
    params={
        'dateFrom': date_from,
        'dateTo': date_to
    },
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers:")
print(f"  X-Requests-Available-Minute: {response.headers.get('X-Requests-Available-Minute', 'N/A')}")
print(f"  X-Requests-Available-Day: {response.headers.get('X-Requests-Available-Day', 'N/A')}")
print()

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    print(f"✅ Found {len(matches)} Premier League matches")
    
    if matches:
        for i, match in enumerate(matches[:3], 1):
            print(f"\n  {i}. {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
            print(f"     Time: {match['utcDate']}")
            print(f"     Status: {match['status']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text[:500]}")

print()
print("="*70)
print("✅ Diagnostic Complete")
print("="*70)
