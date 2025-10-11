"""
Test RapidAPI Tennis Key
Quick script to verify your RAPIDAPI_TENNIS_KEY works
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('RAPIDAPI_TENNIS_KEY')
BASE_URL = "https://tennis-api-atp-wta-itf.p.rapidapi.com"

print("=" * 70)
print("🎾 RAPIDAPI TENNIS KEY TEST")
print("=" * 70)
print()

# Check if key exists
if not API_KEY or API_KEY.startswith('your-'):
    print("❌ API key not found!")
    print()
    print("Please set RAPIDAPI_TENNIS_KEY in .env file:")
    print("  1. Open .env")
    print("  2. Find line: # RAPIDAPI_TENNIS_KEY=your-rapidapi-tennis-key-here")
    print("  3. Uncomment and paste your key")
    print("  4. Save and run this script again")
    print()
    print("Get your free key at:")
    print("👉 https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf")
    exit(1)

print(f"✓ API key found: {API_KEY[:20]}...{API_KEY[-10:]}")
print()

# Test API call
print("Testing API connection...")
print()

headers = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': 'tennis-api-atp-wta-itf.p.rapidapi.com'
}

try:
    # Test endpoint: Get today's ATP fixtures
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/tennis/v2/atp/fixtures/{today}",
        headers=headers,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API KEY WORKS!")
        print()
        
        # Show some data
        if 'results' in data:
            print(f"Found {data['results']} matches for today")
            
            if 'response' in data and len(data['response']) > 0:
                print()
                print("Sample matches:")
                for i, match in enumerate(data['response'][:3], 1):
                    tournament = match.get('tournament', {}).get('name', 'Unknown')
                    home = match.get('teams', {}).get('home', {}).get('name', 'Unknown')
                    away = match.get('teams', {}).get('away', {}).get('name', 'Unknown')
                    print(f"  {i}. {home} vs {away} ({tournament})")
            else:
                print("No matches today, but API key works!")
        else:
            print("API returned data but structure is different than expected.")
            print("This is OK - your key works!")
        
        print()
        print("🚀 Ready to use real tennis data!")
        print("Restart your app: python app.py")
        
    elif response.status_code == 401:
        print("❌ AUTHENTICATION FAILED")
        print()
        print("Your API key is invalid or expired.")
        print()
        print("Please check:")
        print("  1. Key is copied correctly (no extra spaces)")
        print("  2. You subscribed to the API on RapidAPI")
        print("  3. Your subscription is active")
        
    elif response.status_code == 429:
        print("⚠️  RATE LIMIT EXCEEDED")
        print()
        print("You've used all your free requests for this month.")
        print(f"Free plan: 100 requests/month")
        print()
        print("Wait until next month or upgrade your plan.")
        
    else:
        print(f"⚠️  UNEXPECTED RESPONSE: {response.status_code}")
        print()
        print("Response:")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("❌ REQUEST TIMEOUT")
    print()
    print("API server didn't respond in 10 seconds.")
    print("Please check your internet connection and try again.")
    
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR")
    print()
    print("Cannot connect to RapidAPI.")
    print("Please check your internet connection.")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Something went wrong. Please try again.")

print()
print("=" * 70)
