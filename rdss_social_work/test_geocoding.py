"""
Test script to debug geocoding functionality
"""

import frappe
from rdss_social_work.geocoding_utils import geocode_address, get_google_maps_api_key

def test_api_key():
    """Test if API key is accessible"""
    api_key = get_google_maps_api_key()
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    return api_key is not None

def test_geocoding_sample():
    """Test geocoding with sample postal code"""
    print("\nTesting geocoding with postal code 822126...")
    
    try:
        # Test the raw API call first
        import requests
        import json
        
        api_key = get_google_maps_api_key()
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": "822126, Singapore",
            "key": api_key
        }
        
        print(f"Making request to: {url}")
        print(f"With address: {params['address']}")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        
        data = response.json()
        print(f"API Response status: {data.get('status')}")
        print(f"API Response: {json.dumps(data, indent=2)}")
        
        # Now test our function
        result = geocode_address(
            address_line_1="Sample Address",
            postal_code="822126"
        )
        
        if result:
            print("✓ Geocoding successful!")
            print(f"Result: {result}")
        else:
            print("✗ Geocoding failed - no result returned")
            
    except Exception as e:
        print(f"✗ Geocoding failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_beneficiary_data():
    """Test with actual beneficiary data"""
    print("\nTesting with actual beneficiary data...")
    
    # Get one beneficiary
    beneficiary = frappe.get_all(
        "Beneficiary",
        filters={"postal_code": ["!=", ""]},
        fields=["name", "beneficiary_name", "postal_code", "address_line_1"],
        limit=1
    )
    
    if beneficiary:
        b = beneficiary[0]
        print(f"Testing with: {b['beneficiary_name']}")
        print(f"Postal Code: {b['postal_code']}")
        print(f"Address: {b['address_line_1']}")
        
        try:
            result = geocode_address(
                address_line_1=b['address_line_1'],
                postal_code=b['postal_code']
            )
            
            if result:
                print("✓ Geocoding successful!")
                print(f"Result: {result}")
            else:
                print("✗ Geocoding failed - no result returned")
                
        except Exception as e:
            print(f"✗ Geocoding failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("No beneficiaries with postal codes found")

def execute():
    """Main test function"""
    print("=== Geocoding Debug Test ===")
    
    # Test API key
    if not test_api_key():
        print("Cannot proceed - API key not found")
        return
    
    # Test sample geocoding
    test_geocoding_sample()
    
    # Test with beneficiary data
    test_beneficiary_data()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    execute()
