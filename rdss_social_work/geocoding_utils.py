"""
Geocoding utilities for RDSS Social Work Case Management System

This module provides geocoding functionality using Google Maps API
to convert addresses to geolocation coordinates in GeoJSON format.
"""

import frappe
import requests
import json
from frappe.utils import cstr

def get_google_maps_api_key():
    """Get Google Maps API key from site config"""
    return frappe.conf.get("google_map_api_key")

def geocode_address(address_line_1, address_line_2=None, postal_code=None, country="Singapore"):
    """
    Geocode an address using Google Maps Geocoding API
    Prioritizes postal code for Singapore addresses for better accuracy
    
    Args:
        address_line_1 (str): Primary address line
        address_line_2 (str, optional): Secondary address line
        postal_code (str, optional): Postal code
        country (str): Country (default: Singapore)
    
    Returns:
        str: GeoJSON FeatureCollection string with coordinates or None if geocoding fails
    """
    api_key = get_google_maps_api_key()
    if not api_key:
        frappe.log_error("Google Maps API key not found in site config", "Geocoding Error")
        return None
    
    # For Singapore addresses, prioritize postal code for better accuracy
    if postal_code and country == "Singapore":
        full_address = f"{postal_code}, Singapore"
    else:
        # Build the full address
        address_parts = [address_line_1]
        if address_line_2:
            address_parts.append(address_line_2)
        if postal_code:
            address_parts.append(postal_code)
        address_parts.append(country)
        
        full_address = ", ".join(filter(None, address_parts))
    
    # Google Maps Geocoding API endpoint
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": full_address,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            location = result["geometry"]["location"]
            
            # Create GeoJSON FeatureCollection structure as required by Frappe
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [location["lng"], location["lat"]]
                        }
                    }
                ]
            }
            
            return json.dumps(geojson)
        else:
            error_msg = data.get("error_message", data.get("status", "Unknown error"))
            frappe.log_error(f"Geocoding failed for address '{full_address}': {error_msg}", "Geocoding Error")
            return None
            
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Network error during geocoding for address '{full_address}': {str(e)}", "Geocoding Error")
        return None
    except Exception as e:
        frappe.log_error(f"Unexpected error during geocoding for address '{full_address}': {str(e)}", "Geocoding Error")
        return None

def geocode_beneficiary_family(family_doc):
    """
    Geocode a beneficiary family's address and update the geolocation field
    
    Args:
        family_doc: Beneficiary Family document object
    
    Returns:
        bool: True if geocoding was successful, False otherwise
    """
    if not family_doc.primary_address_line_1:
        return False
    
    geolocation = geocode_address(
        address_line_1=family_doc.primary_address_line_1,
        address_line_2=family_doc.primary_address_line_2,
        postal_code=family_doc.primary_postal_code
    )
    
    if geolocation:
        family_doc.geolocation = geolocation
        return True
    
    return False

# Keep the old function for backward compatibility
def geocode_beneficiary(beneficiary_doc):
    """
    Geocode a beneficiary's address and update the geolocation field
    
    Args:
        beneficiary_doc: Beneficiary document object
    
    Returns:
        bool: True if geocoding was successful, False otherwise
    """
    if not beneficiary_doc.address_line_1:
        return False
    
    geolocation = geocode_address(
        address_line_1=beneficiary_doc.address_line_1,
        address_line_2=beneficiary_doc.address_line_2,
        postal_code=beneficiary_doc.postal_code
    )
    
    if geolocation:
        beneficiary_doc.geolocation = geolocation
        return True
    
    return False

def should_geocode_beneficiary_family(family_doc, is_new=False):
    """
    Determine if a beneficiary family should be geocoded
    
    Args:
        family_doc: Beneficiary Family document object
        is_new (bool): Whether this is a new document
    
    Returns:
        bool: True if geocoding should be performed
    """
    # Always geocode new families with address
    if is_new and family_doc.primary_address_line_1:
        return True
    
    # For existing families, geocode if address changed and no geolocation exists
    if not is_new:
        # Check if address fields have changed
        if family_doc.has_value_changed("primary_address_line_1") or \
           family_doc.has_value_changed("primary_address_line_2") or \
           family_doc.has_value_changed("primary_postal_code"):
            return True
        
        # If no geolocation exists but address is present, geocode
        if not family_doc.geolocation and family_doc.primary_address_line_1:
            return True
    
    return False

# Keep the old function for backward compatibility
def should_geocode_beneficiary(beneficiary_doc, is_new=False):
    """
    Determine if a beneficiary should be geocoded
    
    Args:
        beneficiary_doc: Beneficiary document object
        is_new (bool): Whether this is a new document
    
    Returns:
        bool: True if geocoding should be performed
    """
    # Always geocode new beneficiaries with address
    if is_new and beneficiary_doc.address_line_1:
        return True
    
    # For existing beneficiaries, geocode if address changed and no geolocation exists
    if not is_new:
        # Check if address fields have changed
        if beneficiary_doc.has_value_changed("address_line_1") or \
           beneficiary_doc.has_value_changed("address_line_2") or \
           beneficiary_doc.has_value_changed("postal_code"):
            return True
        
        # If no geolocation exists but address is present, geocode
        if not beneficiary_doc.geolocation and beneficiary_doc.address_line_1:
            return True
    
    return False

@frappe.whitelist()
def geocode_address_api(address_line_1, address_line_2=None, postal_code=None, country="Singapore"):
    """
    Whitelisted API method for geocoding addresses from client-side
    
    Args:
        address_line_1 (str): Primary address line
        address_line_2 (str, optional): Secondary address line
        postal_code (str, optional): Postal code
        country (str): Country (default: Singapore)
    
    Returns:
        str: GeoJSON FeatureCollection string with coordinates or None if geocoding fails
    """
    return geocode_address(address_line_1, address_line_2, postal_code, country)
