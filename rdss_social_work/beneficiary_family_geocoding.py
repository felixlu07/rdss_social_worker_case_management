#!/usr/bin/env python3
"""
Beneficiary Family geocoding hooks for RDSS Social Work Case Management System

This module provides geocoding functionality that is triggered automatically
when Beneficiary Family documents are saved.
"""

import frappe
from rdss_social_work.geocoding_utils import geocode_beneficiary_family, should_geocode_beneficiary_family

def beneficiary_family_before_save(doc, method):
    """
    Hook that runs before saving a Beneficiary Family document
    Automatically geocodes the family's address if needed
    
    Args:
        doc: The Beneficiary Family document being saved
        method: The method being called (before_save)
    """
    try:
        # Check if this family should be geocoded
        is_new = doc.is_new()
        
        if should_geocode_beneficiary_family(doc, is_new):
            # Attempt to geocode the family's address
            success = geocode_beneficiary_family(doc)
            
            if success:
                frappe.msgprint(f"Address geocoded successfully for family: {doc.family_name}", 
                              alert=True, indicator='green')
            else:
                frappe.msgprint(f"Could not geocode address for family: {doc.family_name}. "
                              "Please check the address details.", 
                              alert=True, indicator='orange')
                
    except Exception as e:
        # Log the error but don't prevent the document from saving
        frappe.log_error(f"Error during geocoding for family {doc.name}: {str(e)}", 
                        "Beneficiary Family Geocoding Error")
        frappe.msgprint(f"Geocoding failed for family: {doc.family_name}. "
                       "The family record will still be saved.", 
                       alert=True, indicator='red')
