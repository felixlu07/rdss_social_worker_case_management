import frappe
import pandas as pd
import datetime
import re
import time
import os
import csv
from frappe.utils import getdate, cint, cstr, validate_email_address
from codecs import BOM_UTF8

"""
Beneficiary CSV Import Script for RDSS Social Work Module

This script imports beneficiary data from a CSV file into the Frappe Beneficiary DocType.
It handles various data transformations, validations, and mappings to ensure data integrity.

Features:
- Handles BOM (Byte Order Mark) in CSV files
- Parses dates in multiple formats
- Maps gender values (M/F to Male/Female)
- Sets required fields like naming_series
- Validates and cleans data
- Maps emergency contacts
- Provides detailed error logging

Usage:
    bench --site [site-name] execute rdss_social_work.scripts.import_beneficiaries.import_beneficiaries
    
Optional parameters can be added to the function call:
    bench --site [site-name] execute rdss_social_work.scripts.import_beneficiaries.import_beneficiaries \
        --kwargs '{"file_path": "/custom/path/to/file.csv", "test_mode": True}'
"""

def import_beneficiaries(file_path=None, test_mode=False, cleanup_first=False):
    """
    Import beneficiaries from CSV file into Frappe DocType and create Beneficiary Family records
    
    Args:
        file_path (str, optional): Custom path to the CSV file. If not provided, uses default location.
        test_mode (bool, optional): If True, runs in test mode without committing changes to database.
        cleanup_first (bool, optional): If True, deletes all existing beneficiary records before import.
    
    Returns:
        dict: Statistics about the import process
    
    Usage: 
        bench --site erp.rdss.org.sg execute rdss_social_work.scripts.import_beneficiaries.import_beneficiaries
    """
    # Use default file path if not provided
    if not file_path:
        file_path = os.path.join(
            os.path.dirname(frappe.get_module("rdss_social_work").__file__),
            "rdss_social_work", "doctype", "beneficiary", "RD Registry_ 18.10.2024.csv"
        )
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        frappe.log_error(error_msg, "Beneficiary Import Error")
        frappe.msgprint(error_msg, alert=True)
        return {"error": error_msg}
    
    # Check for BOM in the file
    with open(file_path, 'rb') as f:
        content = f.read()
        has_bom = content.startswith(BOM_UTF8)
    
    # Open file with appropriate encoding
    encoding = 'utf-8-sig' if has_bom else 'utf-8'
    
    # Cleanup existing records if requested
    if cleanup_first and not test_mode:
        cleanup_stats = cleanup_existing_beneficiaries()
        frappe.msgprint(f"Cleanup completed: {cleanup_stats['deleted_beneficiaries']} beneficiaries deleted, {cleanup_stats['deleted_families']} families deleted, {cleanup_stats['errors']} errors")
    
    # Statistics tracking
    stats = {
        "total_rows": 0,
        "successful_imports": 0,
        "successful_family_imports": 0,
        "successful_parent_imports": 0,
        "skipped_rows": 0,
        "errors": [],
        "warnings": []
    }
    
    # Track families to avoid duplicates
    created_families = {}
    
    try:
        with open(file_path, 'r', encoding=encoding) as csvfile:
            # Use csv.Sniffer to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Clean up field names (remove extra spaces, handle special characters)
            fieldnames = [field.strip() for field in reader.fieldnames]
            reader.fieldnames = fieldnames
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                stats["total_rows"] += 1
                
                try:
                    # Skip empty rows
                    if not any(row.values()) or not row.get('Name', '').strip():
                        stats["skipped_rows"] += 1
                        stats["warnings"].append(f"Row {row_num}: Skipped empty row")
                        continue
                    
                    # Check if beneficiary already exists by name only
                    beneficiary_name = clean_text(row.get('Name', ''))
                    if not beneficiary_name:
                        stats["skipped_rows"] += 1
                        stats["warnings"].append(f"Row {row_num}: Missing beneficiary name")
                        continue
                    
                    # Additional validation for beneficiary name
                    if len(beneficiary_name) > 140:  # Frappe field limit
                        beneficiary_name = beneficiary_name[:140]
                        stats["warnings"].append(f"Row {row_num}: Beneficiary name truncated to 140 characters")
                    
                    name_exists = frappe.db.exists("Beneficiary", {"beneficiary_name": beneficiary_name})
                    if name_exists:
                        stats["skipped_rows"] += 1
                        stats["warnings"].append(f"Row {row_num}: Name '{beneficiary_name}' already exists")
                        if test_mode:
                            print(f"TEST MODE: Would skip existing beneficiary {beneficiary_name}")
                        continue
                    
                    # Step 1: Create or get beneficiary family first
                    try:
                        family_doc = create_or_get_beneficiary_family(row, None, created_families, test_mode)
                        if family_doc:
                            stats["successful_family_imports"] += 1
                        else:
                            # If family creation fails, we can't proceed with beneficiary
                            stats["errors"].append(f"Row {row_num}: Failed to create family for {beneficiary_name}")
                            continue
                    except Exception as family_error:
                        error_msg = f"Row {row_num}: Family creation error for {beneficiary_name}: {str(family_error)}"
                        stats["errors"].append(error_msg)
                        frappe.log_error(error_msg, "Family Creation Error")
                        continue
                    
                    # Step 2: Create beneficiary document with family reference
                    beneficiary_data = map_csv_to_beneficiary(row, row_num, stats)
                    if beneficiary_data:
                        # Link to family from the start
                        if family_doc and not test_mode:
                            beneficiary_data["beneficiary_family"] = family_doc.name
                            beneficiary_data["relationship_to_family"] = "Primary Beneficiary"
                        
                        beneficiary_doc = frappe.get_doc(beneficiary_data)
                        
                        if not test_mode:
                            # Use retry logic for document save operations
                            max_retries = 3
                            for attempt in range(max_retries):
                                try:
                                    beneficiary_doc.save(ignore_permissions=True)
                                    break
                                except Exception as e:
                                    if "Document has been modified" in str(e) and attempt < max_retries - 1:
                                        # Reload the document and try again
                                        frappe.db.rollback()
                                        time.sleep(0.2 * (attempt + 1))  # Progressive delay
                                        if hasattr(beneficiary_doc, 'name') and beneficiary_doc.name:
                                            beneficiary_doc.reload()
                                        continue
                                    else:
                                        raise e
                            
                            # Update family head to point to this beneficiary
                            if family_doc and not family_doc.family_head:
                                for attempt in range(max_retries):
                                    try:
                                        family_doc.reload()  # Ensure we have latest version
                                        family_doc.family_head = beneficiary_doc.name
                                        family_doc.save(ignore_permissions=True)
                                        break
                                    except Exception as e:
                                        if "Document has been modified" in str(e) and attempt < max_retries - 1:
                                            frappe.db.rollback()
                                            time.sleep(0.2 * (attempt + 1))
                                            continue
                                        else:
                                            raise e
                            
                            # Commit after both operations
                            frappe.db.commit()
                        
                        stats["successful_imports"] += 1
                        frappe.msgprint(f"Successfully imported: {beneficiary_doc.beneficiary_name}", alert=False)
                        
                        # Step 3: Create parent/guardian as additional beneficiary if exists
                        parent_doc = create_parent_beneficiary(row, family_doc, test_mode)
                        if parent_doc:
                            stats["successful_parent_imports"] += 1
                            
                        if test_mode:
                            print(f"TEST MODE: Would import {beneficiary_data['beneficiary_name']}")
                    else:
                        stats["errors"].append(f"Row {row_num}: Failed to create beneficiary document")
                    
                except Exception as e:
                    error_msg = f"Row {row_num}: Error processing {row.get('Name', 'Unknown')}: {str(e)}"
                    stats["errors"].append(error_msg)
                    # Shorten error message for logging to avoid character limit
                    short_error = f"Row {row_num}: {str(e)[:100]}"
                    frappe.log_error(short_error, "Import Error")
                    continue
    
    except Exception as e:
        error_msg = f"Error reading CSV file: {str(e)}"
        stats["errors"].append(error_msg)
        # Shorten error message for logging
        short_error = f"CSV Error: {str(e)[:100]}"
        frappe.log_error(short_error, "Import File Error")
    
    # Display summary
    display_import_summary(stats, test_mode)
    
    return stats

def map_csv_to_beneficiary(row, row_num, stats):
    """
    Map CSV row data to Beneficiary DocType fields
    
    Args:
        row (dict): CSV row data
        row_num (int): Row number for error reporting
        stats (dict): Statistics tracking object
    
    Returns:
        dict: Mapped beneficiary data or None if validation fails
    """
    try:
        # Basic required fields
        beneficiary_data = {
            "doctype": "Beneficiary",
            "naming_series": "BEN-.YYYY.-",
        }
        
        # Map basic personal information
        beneficiary_data["beneficiary_name"] = clean_text(row.get('Name', ''))
        if not beneficiary_data["beneficiary_name"]:
            raise ValueError("Beneficiary name is required")
        
        # Map gender with transformation
        gender_raw = clean_text(row.get('Gender', ''))
        beneficiary_data["gender"] = map_gender(gender_raw)
        
        # Map and parse date of birth
        dob_raw = clean_text(row.get('DOB', ''))
        if dob_raw:
            beneficiary_data["date_of_birth"] = parse_date(dob_raw)
        
        # Map BC/NRIC number - handle various formats
        bc_nric = clean_text(row.get('BC / NRIC no.', ''))
        if bc_nric:
            # Clean BC/NRIC format - remove extra characters but keep alphanumeric
            bc_nric = clean_bc_nric(bc_nric)
            if bc_nric:  # Only set if we have a valid cleaned value
                beneficiary_data["bc_nric_no"] = bc_nric
        
        # Map primary diagnosis (required)
        diagnosis = clean_text(row.get('Diagnosis', ''))
        if not diagnosis:
            raise ValueError("Primary diagnosis is required")
        beneficiary_data["primary_diagnosis"] = diagnosis
        
        # Set diagnosis_date (required field) - use registration date or current date as fallback
        diagnosis_date = parse_date(row.get('Date of Registration')) or datetime.date.today()
        beneficiary_data["diagnosis_date"] = diagnosis_date
        
        # Map address information with length validation
        address = clean_text(row.get('Address', ''))
        if address:
            beneficiary_data["address_line_1"] = address[:140] if len(address) > 140 else address
        
        postal_code = clean_text(row.get('Postal Code', ''))
        if postal_code:
            beneficiary_data["postal_code"] = postal_code[:20] if len(postal_code) > 20 else postal_code
        
        # Map contact information with validation
        contact_phone = clean_text(row.get('Contact', ''))
        # Only set mobile if it looks like a Singapore mobile number (starts with 8 or 9)
        if contact_phone and (contact_phone.startswith('9') or contact_phone.startswith('8')):
            beneficiary_data["mobile_number"] = contact_phone[:20] if len(contact_phone) > 20 else contact_phone
            
        # Map email with validation
        email_raw = clean_text(row.get('Email', ''))
        email = parse_and_validate_email(email_raw)
        if email:
            beneficiary_data["email_address"] = email[:140] if len(email) > 140 else email
        elif email_raw:
            stats["warnings"].append(f"Row {row_num}: Invalid email format in: {email_raw}")
        
        # Map emergency contact information
        parent_name = clean_text(row.get("Parent's name", ''))
        if parent_name:
            beneficiary_data["emergency_contact_1_name"] = parent_name
        
        contact_phone = clean_text(row.get('Contact', ''))
        if contact_phone:
            beneficiary_data["emergency_contact_1_phone"] = contact_phone
        
        relationship = clean_text(row.get('Beneficiary Relationship', ''))
        if relationship:
            beneficiary_data["emergency_contact_1_relationship"] = relationship
        
        # Map status (required)
        status_raw = clean_text(row.get('Status', ''))
        beneficiary_data["current_status"] = map_status(status_raw)
        if not beneficiary_data["current_status"]:
            beneficiary_data["current_status"] = "Active"  # Default status
        
        # Map registration date
        reg_date_raw = clean_text(row.get('Date of Registration', ''))
        if reg_date_raw:
            beneficiary_data["registration_date"] = parse_date(reg_date_raw)
        else:
            # Use current date as default registration date
            beneficiary_data["registration_date"] = datetime.date.today().strftime('%Y-%m-%d')
        
        # Set mobile number from contact if it looks like a mobile number
        if contact_phone and (contact_phone.startswith('9') or contact_phone.startswith('8')):
            beneficiary_data["mobile_number"] = contact_phone
        
        return beneficiary_data
        
    except Exception as e:
        raise ValueError(f"Mapping error: {str(e)}")

def cleanup_existing_beneficiaries():
    """
    Delete all existing beneficiary records and families in proper order
    
    Returns:
        dict: Statistics about cleanup process
    """
    cleanup_stats = {
        "deleted_beneficiaries": 0,
        "deleted_families": 0,
        "errors": 0,
        "error_messages": []
    }
    
    try:
        # Step 1: Delete all beneficiaries first (they reference families)
        beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
        
        for beneficiary in beneficiaries:
            try:
                frappe.delete_doc("Beneficiary", beneficiary.name, force=True)
                cleanup_stats["deleted_beneficiaries"] += 1
            except Exception as e:
                cleanup_stats["errors"] += 1
                cleanup_stats["error_messages"].append(f"Error deleting beneficiary {beneficiary.name}: {str(e)}")
        
        # Step 2: Delete all beneficiary families after beneficiaries are gone
        families = frappe.get_all("Beneficiary Family", fields=["name"])
        
        for family in families:
            try:
                frappe.delete_doc("Beneficiary Family", family.name, force=True)
                cleanup_stats["deleted_families"] += 1
            except Exception as e:
                cleanup_stats["errors"] += 1
                cleanup_stats["error_messages"].append(f"Error deleting family {family.name}: {str(e)}")
        
        frappe.db.commit()
        
    except Exception as e:
        cleanup_stats["error_messages"].append(f"General cleanup error: {str(e)}")
        cleanup_stats["errors"] += 1
    
    return cleanup_stats

def clean_bc_nric(bc_nric):
    """
    Clean BC/NRIC number format
    
    Args:
        bc_nric (str): Raw BC/NRIC number
    
    Returns:
        str: Cleaned BC/NRIC number or empty string if invalid
    """
    if not bc_nric:
        return ''
    
    # Remove extra spaces and convert to string
    bc_nric = str(bc_nric).strip()
    
    # Handle special cases
    if bc_nric.upper() in ['N.A', 'NA', 'NULL', 'NONE', '']:
        return ''
    
    # Remove common prefixes/suffixes and clean
    bc_nric = bc_nric.replace('S(', 'S').replace(')', '')
    
    # Keep only alphanumeric characters
    cleaned = ''.join(char for char in bc_nric if char.isalnum())
    
    # Basic validation - should have some content
    if len(cleaned) < 2:
        return ''
    
    return cleaned

def clean_text(text):
    """Clean and normalize text data"""
    if not text or text in ['', 'NULL', 'null', 'None']:
        return ''
    return str(text).strip()

def map_gender(gender_raw):
    """Map gender values from CSV to Frappe format"""
    if not gender_raw:
        return ''
    
    gender_mapping = {
        'M': 'Male',
        'F': 'Female',
        'Male': 'Male',
        'Female': 'Female',
        'Other': 'Other'
    }
    
    return gender_mapping.get(gender_raw.strip().upper(), '')

def map_status(status_raw):
    """Map status values from CSV to valid Frappe options"""
    if not status_raw:
        return 'Active'
    
    status_mapping = {
        'Active': 'Active',
        'Inactive': 'Inactive',
        'Deceased': 'Deceased',
        'Transferred': 'Transferred',
        'On Hold': 'On Hold'
    }
    
    return status_mapping.get(status_raw.strip(), 'Active')

def parse_date(date_string):
    """
    Parse date from various formats commonly found in CSV
    
    Args:
        date_string (str): Date string to parse
    
    Returns:
        str: Date in YYYY-MM-DD format or None if parsing fails
    """
    if not date_string or date_string.strip() == '':
        return None
    
    date_string = date_string.strip()
    
    # Common date formats to try
    date_formats = [
        '%d %b %Y',      # 16 Oct 2002
        '%d/%m/%Y',      # 16/10/2002
        '%d-%m-%Y',      # 16-10-2002
        '%Y-%m-%d',      # 2002-10-16
        '%d %B %Y',      # 16 October 2002
        '%d.%m.%Y',      # 16.10.2002
        '%m/%d/%Y',      # 10/16/2002
        '%d/%m/%y',      # 16/10/02
        '%d-%m-%y',      # 16-10-02
    ]
    
    for date_format in date_formats:
        try:
            parsed_date = datetime.datetime.strptime(date_string, date_format)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # Try to handle dates with additional text like "16/03/2022: Updated email add"
    date_match = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', date_string)
    if date_match:
        clean_date = date_match.group(1)
        return parse_date(clean_date)
    
    # Log warning for unparseable dates
    frappe.log_error(f"Could not parse date: {date_string}", "Date Parse Warning")
    return None

def display_import_summary(stats, test_mode):
    """Display import summary statistics"""
    mode_text = "TEST MODE - " if test_mode else ""
    
    summary_msg = f"""
{mode_text}Import Summary:
===================
Total rows processed: {stats['total_rows']}
Successful beneficiary imports: {stats['successful_imports']}
Successful family imports: {stats['successful_family_imports']}
Successful parent/guardian imports: {stats['successful_parent_imports']}
Skipped rows: {stats['skipped_rows']}
Errors: {len(stats['errors'])}
Warnings: {len(stats['warnings'])}
"""
    
    frappe.msgprint(summary_msg, title="Import Complete")
    print(summary_msg)
    # Log detailed errors and warnings
    if stats['errors']:
        error_log = "\n".join(stats['errors'])
        frappe.log_error(error_log, "Beneficiary Import Errors")
    
    if stats['warnings']:
        warning_log = "\n".join(stats['warnings'])
        frappe.log_error(warning_log, "Beneficiary Import Warnings")
    
    print(summary_msg)
    
    if stats['errors']:
        print("\nErrors:")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")
    
    if stats['warnings']:
        print("\nWarnings:")
        for warning in stats['warnings'][:10]:  # Show first 10 warnings
            print(f"  - {warning}")
        if len(stats['warnings']) > 10:
            print(f"  ... and {len(stats['warnings']) - 10} more warnings")

def parse_and_validate_email(email_string):
    """Parse multiple emails and return the first valid one"""
    if not email_string or not email_string.strip():
        return ""
    
    # Split by semicolon and comma, clean up each email
    emails = []
    for separator in [';', ',']:
        if separator in email_string:
            emails = [email.strip() for email in email_string.split(separator)]
            break
    
    if not emails:
        emails = [email_string.strip()]
    
    # Return first valid email or empty string
    for email in emails:
        email = email.strip()
        if email and '@' in email and '.' in email.split('@')[-1]:
            # Basic email validation
            try:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(email_pattern, email):
                    return email
            except:
                pass
    
    return ""

def create_or_get_beneficiary_family(row, beneficiary_doc, created_families, test_mode):
    """
    Create or get existing Beneficiary Family record
    Each CSV row represents one family unit, so create unique family per row
    
    Args:
        row (dict): CSV row data
        beneficiary_doc: The beneficiary document (can be None if creating family first)
        created_families (dict): Track created families to avoid duplicates
        test_mode (bool): Whether running in test mode
    
    Returns:
        Beneficiary Family document or None
    """
    try:
        # Extract family name from beneficiary name
        beneficiary_name = row.get('Name', '').strip()
        if not beneficiary_name:
            return None
            
        # Create unique family name using full beneficiary name + parent info to ensure uniqueness
        # This ensures each CSV row creates its own family
        parent_name = row.get("Parent's name", '').strip()
        contact_info = row.get('Contact', '').strip()
        
        # Use beneficiary name + parent name + contact to create truly unique family identifier
        if parent_name:
            family_name = f"{beneficiary_name} & {parent_name} Family"
        else:
            # If no parent, use beneficiary name + contact info for uniqueness
            family_name = f"{beneficiary_name} Family"
            if contact_info:
                # Add last 4 digits of contact for uniqueness
                contact_suffix = contact_info[-4:] if len(contact_info) >= 4 else contact_info
                family_name = f"{beneficiary_name} Family ({contact_suffix})"
            
        # Ensure family name doesn't exceed field limits (140 chars for Frappe)
        if len(family_name) > 140:
            family_name = family_name[:137] + "..."
            
        # Create unique identifier using row data hash to prevent any duplicates
        # This ensures each CSV row gets its own family regardless of name similarities
        row_identifier = f"{beneficiary_name}_{parent_name}_{contact_info}_{row.get('Address', '')}_{row.get('Email', '')}"
        row_hash = frappe.generate_hash(row_identifier)[:8]
        
        # Check if this exact family combination already exists in this import session
        family_key = f"{family_name}_{row_hash}"
        if family_key in created_families:
            return created_families[family_key]
            
        # Ensure final family name is unique in database
        original_family_name = family_name
        counter = 1
        while frappe.db.exists("Beneficiary Family", {"family_name": family_name}):
            family_name = f"{original_family_name} ({counter})"
            if len(family_name) > 140:
                # Truncate original name to make room for counter
                truncated_original = original_family_name[:130]
                family_name = f"{truncated_original} ({counter})"
            counter += 1
            if counter > 100:  # Safety valve to prevent infinite loop
                family_name = f"Family_{row_hash}"
                break
        
        # Check if family already exists in database (should not happen with our unique naming)
        existing_family = frappe.db.exists("Beneficiary Family", {"family_name": family_name})
        if existing_family:
            family_doc = frappe.get_doc("Beneficiary Family", existing_family)
            created_families[family_key] = family_doc
            return family_doc
        
        # Create new family record
        family_data = {
            "doctype": "Beneficiary Family",
            "naming_series": "FAM-.YYYY.-",
            "family_name": family_name,
            "family_head": beneficiary_doc.name if beneficiary_doc and not test_mode else None,
            "registration_date": parse_date(row.get('Date of Registration')) or datetime.date.today(),
            "family_status": map_status(row.get('Status', '').strip()) or "Active",
            "primary_address_line_1": row.get('Address', '').strip(),
            "primary_postal_code": row.get('Postal Code', '').strip(),
            "primary_mobile_number": row.get('Contact', '').strip(),
            "primary_email_address": parse_and_validate_email(row.get('Email', '')),
            "emergency_contact_1_name": row.get("Parent's name", '').strip(),
            "emergency_contact_1_relationship": row.get('Beneficiary Relationship', '').strip(),
            "emergency_contact_1_phone": row.get('Contact', '').strip(),
            "primary_social_worker": "Administrator"  # Default, can be updated later
        }
        
        family_doc = frappe.get_doc(family_data)
        
        if not test_mode:
            # Use retry logic for family document save operations
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    family_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    break
                except Exception as save_error:
                    if "Duplicate entry" in str(save_error) or "already exists" in str(save_error):
                        # Handle duplicate family name by adding timestamp
                        import time
                        timestamp = str(int(time.time()))[-4:]
                        family_doc.family_name = f"{original_family_name} ({timestamp})"
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise save_error
                    elif "Document has been modified" in str(save_error) and attempt < max_retries - 1:
                        frappe.db.rollback()
                        time.sleep(0.2 * (attempt + 1))
                        continue
                    else:
                        raise save_error
        
        created_families[family_key] = family_doc
        return family_doc
        
    except Exception as e:
        error_details = f"Family creation error: {str(e)} | Row data: {str(row)[:200]}"
        frappe.log_error(error_details, "Family Creation Error")
        print(f"DEBUG: Family creation failed - {error_details}")
        return None

def create_parent_beneficiary(row, family_doc, test_mode):
    """
    Create parent/guardian as additional beneficiary if data exists
    
    Args:
        row (dict): CSV row data
        family_doc: The family document
        test_mode (bool): Whether running in test mode
    
    Returns:
        Beneficiary document for parent or None
    """
    try:
        parent_name = row.get("Parent's name", '').strip()
        if not parent_name:
            return None
        
        # Check if parent already exists
        existing_parent = frappe.db.exists("Beneficiary", {"beneficiary_name": parent_name})
        if existing_parent:
            return frappe.get_doc("Beneficiary", existing_parent)
        
        # Determine parent gender from relationship
        relationship = row.get('Beneficiary Relationship', '').strip().lower()
        parent_gender = "Female" if relationship == "mother" else "Male" if relationship == "father" else ""
        
        # Validate and clean parent data
        parent_name = parent_name[:140] if len(parent_name) > 140 else parent_name
        parent_address = row.get('Address', '').strip()[:140] if row.get('Address', '').strip() else ""
        parent_postal = row.get('Postal Code', '').strip()[:20] if row.get('Postal Code', '').strip() else ""
        parent_mobile = row.get('Contact', '').strip()[:20] if row.get('Contact', '').strip() else ""
        parent_email = parse_and_validate_email(row.get('Email', ''))
        
        # Create parent beneficiary data
        parent_data = {
            "doctype": "Beneficiary",
            "naming_series": "BEN-.YYYY.-",
            "beneficiary_name": parent_name,
            "gender": parent_gender,
            "beneficiary_status": "Active",
            "address_line_1": parent_address,
            "postal_code": parent_postal,
            "mobile_number": parent_mobile,
            "email_address": parent_email,
            "beneficiary_family": family_doc.name if family_doc and not test_mode else None,
            "relationship_to_family": "Parent/Guardian",
            "registration_date": parse_date(row.get('Date of Registration')) or datetime.date.today(),
            "diagnosis_date": datetime.date.today(),  # Required field for parents
            "primary_diagnosis": "Family Member"  # Required field for parents
        }
        
        parent_doc = frappe.get_doc(parent_data)
        
        if not test_mode:
            # Use retry logic for parent document save operations
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    parent_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    break
                except Exception as e:
                    if "Document has been modified" in str(e) and attempt < max_retries - 1:
                        # Reload the document and try again
                        frappe.db.rollback()
                        time.sleep(0.2 * (attempt + 1))  # Progressive delay
                        if hasattr(parent_doc, 'name') and parent_doc.name:
                            parent_doc.reload()
                        continue
                    else:
                        raise e
        
        return parent_doc
        
    except Exception as e:
        frappe.log_error(f"Error creating parent beneficiary: {str(e)}", "Parent Beneficiary Creation Error")
        return None

def create_family(row, test_mode=False):
    """
    Create a Beneficiary Family record from CSV row data
    
    Args:
        row (dict): CSV row data
        test_mode (bool): If True, don't actually save to database
    
    Returns:
        frappe.Document: Created family document or None if creation fails
    """
    try:
        beneficiary_name = clean_text(row.get('Beneficiary Name', ''))
        if not beneficiary_name:
            return None
        
        # Create unique family name based on beneficiary name
        family_name = generate_unique_family_name(beneficiary_name)
        
        family_data = {
            "doctype": "Beneficiary Family",
            "family_name": family_name,
            "family_status": "Active",
            "registration_date": parse_date(row.get('Date of Registration')) or datetime.date.today()
        }
        
        family_doc = frappe.get_doc(family_data)
        
        if not test_mode:
            # Use retry logic for family document save operations
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    family_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    break
                except Exception as e:
                    if "Document has been modified" in str(e) and attempt < max_retries - 1:
                        # Reload the document and try again
                        frappe.db.rollback()
                        time.sleep(0.2 * (attempt + 1))  # Progressive delay
                        if hasattr(family_doc, 'name') and family_doc.name:
                            family_doc.reload()
                        continue
                    else:
                        raise e
        
        return family_doc
        
    except Exception as e:
        frappe.log_error(f"Error creating family: {str(e)}", "Family Creation Error")
        return None

def map_status(status_value):
    """Map CSV status to Beneficiary Family status"""
    if not status_value:
        return "Active"
    
    status_lower = status_value.lower()
    if status_lower == "active":
        return "Active"
    elif status_lower == "inactive":
        return "Inactive"
    else:
        return "Active"  # Default

# Test function for development
def test_import():
    """Test function to run import in test mode"""
    return import_beneficiaries(test_mode=True)

def test_specific_rows():
    """Test specific problematic rows"""
    import os
    import csv
    from codecs import BOM_UTF8
    
    # Target rows that failed
    target_rows = [37, 45, 63]
    
    file_path = os.path.join(
        os.path.dirname(frappe.get_module("rdss_social_work").__file__),
        "rdss_social_work", "doctype", "beneficiary", "RD Registry_ 18.10.2024.csv"
    )
    
    # Check for BOM in the file
    with open(file_path, 'rb') as f:
        content = f.read()
        has_bom = content.startswith(BOM_UTF8)
    
    encoding = 'utf-8-sig' if has_bom else 'utf-8'
    
    with open(file_path, 'r', encoding=encoding) as csvfile:
        sample = csvfile.read(1024)
        csvfile.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        fieldnames = [field.strip() for field in reader.fieldnames]
        reader.fieldnames = fieldnames
        
        for row_num, row in enumerate(reader, start=2):
            if row_num in target_rows:
                print(f"\n=== Testing Row {row_num} ===")
                print(f"Name: {row.get('Name', '')}")
                parent_name = row.get("Parent's name", '')
                print(f"Parent's name: {parent_name}")
                print(f"Contact: {row.get('Contact', '')}")
                print(f"Address: {row.get('Address', '')}")
                print(f"Email: {row.get('Email', '')}")
                
                # Test family creation directly
                try:
                    created_families = {}
                    family_doc = create_or_get_beneficiary_family(row, None, created_families, True)
                    if family_doc:
                        print(f"SUCCESS: Family created - {family_doc.family_name}")
                    else:
                        print("FAILED: Family creation returned None")
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
    
    return "Test completed"

if __name__ == "__main__":
    # For direct execution during development
    test_import()
