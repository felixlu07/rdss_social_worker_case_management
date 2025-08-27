"""
Manual geocoding script for existing Beneficiary records

This script geocodes all existing beneficiaries that have addresses
but no geolocation data, or allows selective geocoding.

Usage:
    # Geocode all beneficiaries without geolocation
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_all
    
    # Geocode specific beneficiaries by name pattern
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_by_pattern --kwargs "{'pattern': 'Ahmad'}"
    
    # Force geocode all beneficiaries (overwrite existing)
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_all --kwargs "{'force': True}"
"""

import frappe
from rdss_social_work.geocoding_utils import geocode_beneficiary
import time

def geocode_all(force=False, batch_size=10, delay=1):
    """
    Geocode all existing beneficiaries
    
    Args:
        force (bool): If True, geocode even if geolocation already exists
        batch_size (int): Number of records to process in each batch
        delay (float): Delay in seconds between API calls to avoid rate limiting
    """
    print("Starting bulk geocoding of existing beneficiaries...")
    
    # Build filters
    filters = {"address_line_1": ["!=", ""]}
    if not force:
        filters["geolocation"] = ["in", ["", None]]
    
    # Get beneficiaries that need geocoding
    beneficiaries = frappe.get_all(
        "Beneficiary",
        filters=filters,
        fields=["name", "beneficiary_name", "address_line_1", "address_line_2", "postal_code", "geolocation"]
    )
    
    if not beneficiaries:
        print("No beneficiaries found that need geocoding.")
        return
    
    total_count = len(beneficiaries)
    print(f"Found {total_count} beneficiaries to geocode.")
    
    success_count = 0
    error_count = 0
    
    # Process in batches
    for i in range(0, total_count, batch_size):
        batch = beneficiaries[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} records)...")
        
        for beneficiary_data in batch:
            try:
                # Get the full document
                beneficiary_doc = frappe.get_doc("Beneficiary", beneficiary_data["name"])
                
                # Skip if already has geolocation and not forcing
                if not force and beneficiary_doc.geolocation:
                    print(f"  Skipping {beneficiary_doc.beneficiary_name} (already has geolocation)")
                    continue
                
                # Attempt geocoding
                success = geocode_beneficiary(beneficiary_doc)
                
                if success:
                    # Save the document with new geolocation
                    beneficiary_doc.save(ignore_permissions=True)
                    success_count += 1
                    print(f"  ✓ Geocoded: {beneficiary_doc.beneficiary_name}")
                else:
                    error_count += 1
                    print(f"  ✗ Failed: {beneficiary_doc.beneficiary_name}")
                
                # Add delay to avoid rate limiting
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                print(f"  ✗ Error processing {beneficiary_data['beneficiary_name']}: {str(e)}")
                frappe.log_error(f"Error geocoding beneficiary {beneficiary_data['name']}: {str(e)}", 
                               "Bulk Geocoding Error")
        
        # Commit after each batch
        frappe.db.commit()
        print(f"  Batch completed. Success: {success_count}, Errors: {error_count}")
    
    print(f"\nBulk geocoding completed!")
    print(f"Total processed: {total_count}")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def geocode_by_pattern(pattern, force=False):
    """
    Geocode beneficiaries matching a name pattern
    
    Args:
        pattern (str): Name pattern to match
        force (bool): If True, geocode even if geolocation already exists
    """
    print(f"Geocoding beneficiaries matching pattern: '{pattern}'")
    
    # Build filters
    filters = {
        "beneficiary_name": ["like", f"%{pattern}%"],
        "address_line_1": ["!=", ""]
    }
    if not force:
        filters["geolocation"] = ["in", ["", None]]
    
    # Get matching beneficiaries
    beneficiaries = frappe.get_all(
        "Beneficiary",
        filters=filters,
        fields=["name", "beneficiary_name", "address_line_1", "address_line_2", "postal_code"]
    )
    
    if not beneficiaries:
        print(f"No beneficiaries found matching pattern '{pattern}' that need geocoding.")
        return
    
    print(f"Found {len(beneficiaries)} beneficiaries matching the pattern.")
    
    success_count = 0
    error_count = 0
    
    for beneficiary_data in beneficiaries:
        try:
            # Get the full document
            beneficiary_doc = frappe.get_doc("Beneficiary", beneficiary_data["name"])
            
            # Attempt geocoding
            success = geocode_beneficiary(beneficiary_doc)
            
            if success:
                # Save the document with new geolocation
                beneficiary_doc.save(ignore_permissions=True)
                success_count += 1
                print(f"  ✓ Geocoded: {beneficiary_doc.beneficiary_name}")
            else:
                error_count += 1
                print(f"  ✗ Failed: {beneficiary_doc.beneficiary_name}")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {beneficiary_data['beneficiary_name']}: {str(e)}")
    
    frappe.db.commit()
    print(f"\nPattern geocoding completed!")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def geocode_specific(beneficiary_names, force=False):
    """
    Geocode specific beneficiaries by name
    
    Args:
        beneficiary_names (list): List of beneficiary names to geocode
        force (bool): If True, geocode even if geolocation already exists
    """
    print(f"Geocoding specific beneficiaries: {beneficiary_names}")
    
    success_count = 0
    error_count = 0
    
    for name in beneficiary_names:
        try:
            # Get the document
            beneficiary_doc = frappe.get_doc("Beneficiary", name)
            
            # Check if address exists
            if not beneficiary_doc.address_line_1:
                print(f"  ⚠ Skipping {beneficiary_doc.beneficiary_name} (no address)")
                continue
            
            # Skip if already has geolocation and not forcing
            if not force and beneficiary_doc.geolocation:
                print(f"  ⚠ Skipping {beneficiary_doc.beneficiary_name} (already has geolocation)")
                continue
            
            # Attempt geocoding
            success = geocode_beneficiary(beneficiary_doc)
            
            if success:
                # Save the document with new geolocation
                beneficiary_doc.save(ignore_permissions=True)
                success_count += 1
                print(f"  ✓ Geocoded: {beneficiary_doc.beneficiary_name}")
            else:
                error_count += 1
                print(f"  ✗ Failed: {beneficiary_doc.beneficiary_name}")
                
        except frappe.DoesNotExistError:
            error_count += 1
            print(f"  ✗ Beneficiary not found: {name}")
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {name}: {str(e)}")
    
    frappe.db.commit()
    print(f"\nSpecific geocoding completed!")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def check_geocoding_status():
    """
    Check the current geocoding status of all beneficiaries
    """
    print("Checking geocoding status...")
    
    # Get all beneficiaries with addresses
    all_with_address = frappe.get_all(
        "Beneficiary",
        filters={"address_line_1": ["!=", ""]},
        fields=["name", "beneficiary_name", "geolocation"]
    )
    
    # Count geocoded vs non-geocoded
    geocoded_count = 0
    not_geocoded_count = 0
    
    for beneficiary in all_with_address:
        if beneficiary.get("geolocation"):
            geocoded_count += 1
        else:
            not_geocoded_count += 1
    
    total_with_address = len(all_with_address)
    
    print(f"\nGeocoding Status Report:")
    print(f"Total beneficiaries with addresses: {total_with_address}")
    print(f"Already geocoded: {geocoded_count}")
    print(f"Not geocoded: {not_geocoded_count}")
    print(f"Geocoding completion rate: {(geocoded_count/total_with_address*100):.1f}%" if total_with_address > 0 else "N/A")

if __name__ == "__main__":
    check_geocoding_status()
