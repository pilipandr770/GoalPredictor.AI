"""
Quick test: Check if live site shows matches
"""
import requests
import json

print("="*70)
print("🌐 Testing LIVE Render.com deployment")
print("="*70)

BASE_URL = "https://goalpredictor-ai-1.onrender.com"

# Test 1: Homepage
print("\n1️⃣ Testing Homepage...")
response = requests.get(BASE_URL, timeout=30)
print(f"   Status: {response.status_code}")
print(f"   Size: {len(response.content)} bytes")
if response.status_code == 200:
    print("   ✅ Homepage loaded")
else:
    print("   ❌ Homepage failed")

# Test 2: Football matches API
print("\n2️⃣ Testing Football Matches API...")
response = requests.get(f"{BASE_URL}/api/football/matches?days=7", timeout=30)
print(f"   Status: {response.status_code}")
print(f"   Size: {len(response.content)} bytes")

if response.status_code == 200:
    data = response.json()
    print(f"   ✅ API Response:")
    print(f"      - Success: {data.get('success')}")
    print(f"      - Matches: {data.get('count')}")
    
    if data.get('matches'):
        print(f"\n   📋 First 3 matches:")
        for i, match in enumerate(data['matches'][:3], 1):
            print(f"      {i}. {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
            print(f"         Competition: {match['competition']}")
            print(f"         Date: {match['date']}")
    else:
        print("   ⚠️  No matches returned")
else:
    print(f"   ❌ API failed: {response.text}")

# Test 3: Football page
print("\n3️⃣ Testing Football Page...")
response = requests.get(f"{BASE_URL}/football", timeout=30)
print(f"   Status: {response.status_code}")
print(f"   Size: {len(response.content)} bytes")
if response.status_code == 200:
    print("   ✅ Football page loaded")
    # Check if JavaScript is present
    if 'loadMatches()' in response.text:
        print("   ✅ JavaScript loadMatches() found")
    if 'Array.isArray(data.matches)' in response.text:
        print("   ✅ Array.isArray fix applied!")
else:
    print("   ❌ Football page failed")

# Test 4: Tennis page
print("\n4️⃣ Testing Tennis Page...")
response = requests.get(f"{BASE_URL}/tennis", timeout=30)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ Tennis page loaded")
else:
    print("   ❌ Tennis page failed")

print("\n" + "="*70)
print("✅ Test Complete!")
print("="*70)
