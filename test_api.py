import requests
import json

print("=" * 70)
print("API ENDPOINT TESTING")
print("=" * 70)

base_url = "http://127.0.0.1:8000"

# Test 1: Fetch all venues
print("\n1. Testing GET /api/venues/")
print("-" * 70)
try:
    response = requests.get(f"{base_url}/api/venues/")
    if response.status_code == 200:
        venues = response.json()
        print(f"✅ Success! Retrieved {len(venues)} venues")
        print(f"\nFirst 3 venues:")
        for venue in venues[:3]:
            print(f"  - {venue['name']} ({venue['number_of_courts']} courts)")
    else:
        print(f"❌ Failed with status code: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get a specific venue
print("\n" + "=" * 70)
print("2. Testing GET /api/venues/{id}/")
print("-" * 70)
try:
    # Get first venue ID
    response = requests.get(f"{base_url}/api/venues/")
    if response.status_code == 200:
        venues = response.json()
        if len(venues) > 0:
            venue_id = venues[0]['id']
            detail_response = requests.get(f"{base_url}/api/venues/{venue_id}/")
            if detail_response.status_code == 200:
                venue_detail = detail_response.json()
                print(f"✅ Success! Retrieved venue details:")
                print(f"  Name: {venue_detail['name']}")
                print(f"  Address: {venue_detail['address']}")
                print(f"  Contact: {venue_detail['contact']}")
                print(f"  Status: {venue_detail['verification_status']}")
                print(f"  Number of courts: {venue_detail['number_of_courts']}")
            else:
                print(f"❌ Failed with status code: {detail_response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Fetch sports categories
print("\n" + "=" * 70)
print("3. Testing sports categories")
print("-" * 70)
try:
    response = requests.get(f"{base_url}/api/venues/")
    if response.status_code == 200:
        venues = response.json()
        categories = {}
        for venue in venues:
            # Count venues (categories are at court level in our structure)
            categories[venue.get('category', 'Unknown')] = categories.get(venue.get('category', 'Unknown'), 0) + 1
        
        print("✅ Venues distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} venues")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE!")
print("=" * 70)
