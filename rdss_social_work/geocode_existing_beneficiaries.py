"""
Manual geocoding script for existing Beneficiary Family records

This script geocodes all existing beneficiary families that have addresses
but no geolocation data, or allows selective geocoding.

Usage:
    # Geocode all families without geolocation
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_all
    
    # Geocode specific families by name pattern
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_by_pattern --kwargs "{'pattern': 'Family'}"
    
    # Force geocode all families (overwrite existing)
    bench execute rdss_social_work.geocode_existing_beneficiaries.geocode_all --kwargs "{'force': True}"
"""

import frappe
from rdss_social_work.geocoding_utils import geocode_beneficiary_family
import time

def geocode_all(force=False, batch_size=10, delay=1):
    """
    Geocode all existing beneficiary families
    
    Args:
        force (bool): If True, geocode even if geolocation already exists
        batch_size (int): Number of records to process in each batch
        delay (float): Delay in seconds between API calls to avoid rate limiting
    """
    print("Starting bulk geocoding of existing beneficiary families...")
    
    # Build filters
    filters = {"primary_address_line_1": ["!=", ""]}
    if not force:
        filters["geolocation"] = ["in", ["", None]]
    
    # Get families that need geocoding
    families = frappe.get_all(
        "Beneficiary Family",
        filters=filters,
        fields=["name", "family_name", "primary_address_line_1", "primary_address_line_2", "primary_postal_code", "geolocation"]
    )
    
    if not families:
        print("No beneficiary families found that need geocoding.")
        return
    
    total_count = len(families)
    print(f"Found {total_count} beneficiary families to geocode.")
    
    success_count = 0
    error_count = 0
    
    # Process in batches
    for i in range(0, total_count, batch_size):
        batch = families[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} records)...)")
        
        for family_data in batch:
            try:
                # Get the full document
                family_doc = frappe.get_doc("Beneficiary Family", family_data["name"])
                
                # Skip if already has geolocation and not forcing
                if not force and family_doc.geolocation:
                    print(f"  Skipping {family_doc.family_name} (already has geolocation)")
                    continue
                
                # Attempt geocoding
                success = geocode_beneficiary_family(family_doc)
                
                if success:
                    # Save the document with new geolocation
                    family_doc.save(ignore_permissions=True)
                    success_count += 1
                    print(f"  ✓ Geocoded: {family_doc.family_name}")
                else:
                    error_count += 1
                    print(f"  ✗ Failed: {family_doc.family_name}")
                
                # Add delay to avoid rate limiting
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                print(f"  ✗ Error processing {family_data['family_name']}: {str(e)}")
                frappe.log_error(f"Error geocoding family {family_data['name']}: {str(e)}", 
                               "Bulk Geocoding Error")
        
        # Commit after each batch
        frappe.db.commit()
        print(f"  Batch completed. Success: {success_count}, Errors: {error_count}")
    
    print(f"\nBulk geocoding completed!")
    print(f"Total families processed: {total_count}")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def geocode_by_pattern(pattern, force=False):
    """
    Geocode beneficiary families matching a name pattern
    
    Args:
        pattern (str): Name pattern to match
        force (bool): If True, geocode even if geolocation already exists
    """
    print(f"Geocoding beneficiary families matching pattern: '{pattern}'")
    
    # Build filters
    filters = {
        "family_name": ["like", f"%{pattern}%"],
        "primary_address_line_1": ["!=", ""]
    }
    if not force:
        filters["geolocation"] = ["in", ["", None]]
    
    # Get matching families
    families = frappe.get_all(
        "Beneficiary Family",
        filters=filters,
        fields=["name", "family_name", "primary_address_line_1", "primary_address_line_2", "primary_postal_code"]
    )
    
    if not families:
        print(f"No beneficiary families found matching pattern '{pattern}' that need geocoding.")
        return
    
    print(f"Found {len(families)} beneficiary families matching the pattern.")
    
    success_count = 0
    error_count = 0
    
    for family_data in families:
        try:
            # Get the full document
            family_doc = frappe.get_doc("Beneficiary Family", family_data["name"])
            
            # Attempt geocoding
            success = geocode_beneficiary_family(family_doc)
            
            if success:
                # Save the document with new geolocation
                family_doc.save(ignore_permissions=True)
                success_count += 1
                print(f"  ✓ Geocoded: {family_doc.family_name}")
            else:
                error_count += 1
                print(f"  ✗ Failed: {family_doc.family_name}")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {family_data['family_name']}: {str(e)}")
    
    frappe.db.commit()
    print(f"\nPattern geocoding completed!")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def geocode_specific(family_names, force=False):
    """
    Geocode specific beneficiary families by name
    
    Args:
        family_names (list): List of family names to geocode
        force (bool): If True, geocode even if geolocation already exists
    """
    print(f"Geocoding specific beneficiary families: {family_names}")
    
    success_count = 0
    error_count = 0
    
    for name in family_names:
        try:
            # Get the document
            family_doc = frappe.get_doc("Beneficiary Family", name)
            
            # Check if address exists
            if not family_doc.primary_address_line_1:
                print(f"  ⚠ Skipping {family_doc.family_name} (no address)")
                continue
            
            # Skip if already has geolocation and not forcing
            if not force and family_doc.geolocation:
                print(f"  ⚠ Skipping {family_doc.family_name} (already has geolocation)")
                continue
            
            # Attempt geocoding
            success = geocode_beneficiary_family(family_doc)
            
            if success:
                # Save the document with new geolocation
                family_doc.save(ignore_permissions=True)
                success_count += 1
                print(f"  ✓ Geocoded: {family_doc.family_name}")
            else:
                error_count += 1
                print(f"  ✗ Failed: {family_doc.family_name}")
                
        except frappe.DoesNotExistError:
            error_count += 1
            print(f"  ✗ Beneficiary Family not found: {name}")
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {name}: {str(e)}")
    
    frappe.db.commit()
    print(f"\nSpecific geocoding completed!")
    print(f"Successfully geocoded: {success_count}")
    print(f"Errors: {error_count}")

def check_geocoding_status():
    """
    Check the current geocoding status of all beneficiary families
    """
    print("Checking geocoding status...")
    
    # Get all families with addresses
    all_with_address = frappe.get_all(
        "Beneficiary Family",
        filters={"primary_address_line_1": ["!=", ""]},
        fields=["name", "family_name", "geolocation"]
    )
    
    # Count geocoded vs non-geocoded
    geocoded_count = 0
    not_geocoded_count = 0
    
    for family in all_with_address:
        if family.get("geolocation"):
            geocoded_count += 1
        else:
            not_geocoded_count += 1
    
    total_with_address = len(all_with_address)
    
    print(f"\nGeocoding Status Report:")
    print(f"Total beneficiary families with addresses: {total_with_address}")
    print(f"Already geocoded: {geocoded_count}")
    print(f"Not geocoded: {not_geocoded_count}")
    print(f"Geocoding completion rate: {(geocoded_count/total_with_address*100):.1f}%" if total_with_address > 0 else "N/A")

if __name__ == "__main__":
    check_geocoding_status()
