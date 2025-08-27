"""
Server script for automatic geocoding of Beneficiary addresses

This module contains server-side hooks that automatically geocode
beneficiary addresses when documents are saved.
"""

import frappe
from rdss_social_work.geocoding_utils import geocode_beneficiary, should_geocode_beneficiary

def beneficiary_before_save(doc, method):
    """
    Hook function called before saving a Beneficiary document
    Automatically geocodes the address if conditions are met
    
    Args:
        doc: Beneficiary document object
        method: The method being called (before_save)
    """
    try:
        is_new = doc.is_new()
        
        if should_geocode_beneficiary(doc, is_new):
            success = geocode_beneficiary(doc)
            if success:
                frappe.msgprint(f"Address geocoded successfully for {doc.beneficiary_name}", 
                              alert=True, indicator="green")
            else:
                frappe.msgprint(f"Could not geocode address for {doc.beneficiary_name}. Please check the address details.", 
                              alert=True, indicator="orange")
    except Exception as e:
        frappe.log_error(f"Error in beneficiary geocoding: {str(e)}", "Beneficiary Geocoding Error")
        # Don't prevent saving if geocoding fails
        pass
