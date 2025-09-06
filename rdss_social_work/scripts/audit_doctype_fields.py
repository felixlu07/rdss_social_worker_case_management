#!/usr/bin/env python3
"""
Comprehensive DocType Field Auditor
Systematically audits all DocType fields and generates correct field mappings for JavaScript queries
"""

import frappe
import json

def audit_all_doctype_fields():
    """
    Audit all DocType fields and generate comprehensive field mappings
    """
    
    # DocTypes we need to audit based on JavaScript usage
    doctypes_to_audit = [
        'Beneficiary',
        'Beneficiary Family', 
        'Case',
        'Service Plan',
        'Document Attachment',
        'Initial Assessment',
        'Follow Up Assessment'
    ]
    
    results = {}
    
    for doctype in doctypes_to_audit:
        print(f"\n=== Auditing {doctype} ===")
        
        try:
            # Get DocType meta
            meta = frappe.get_meta(doctype)
            
            # Get all field names
            all_fields = [field.fieldname for field in meta.fields if field.fieldname]
            
            # Get database table columns
            table_name = f"tab{doctype}"
            db_columns = frappe.db.sql(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()
            """, (table_name,), as_list=True)
            
            db_column_names = [col[0] for col in db_columns]
            
            # Store results
            results[doctype] = {
                'meta_fields': all_fields,
                'db_columns': db_column_names,
                'common_fields': list(set(all_fields) & set(db_column_names)),
                'meta_only': list(set(all_fields) - set(db_column_names)),
                'db_only': list(set(db_column_names) - set(all_fields))
            }
            
            print(f"Meta fields: {len(all_fields)}")
            print(f"DB columns: {len(db_column_names)}")
            print(f"Common: {len(results[doctype]['common_fields'])}")
            
            # Print key fields for queries
            key_fields = ['name', 'beneficiary', 'case', 'document_title', 'document_name', 
                         'plan_title', 'plan_name', 'case_title', 'case_priority', 'priority_level',
                         'case_status', 'plan_status', 'status', 'relationship_to_family', 
                         'family_relationship', 'assessment_date', 'assessed_by']
            
            available_key_fields = [f for f in key_fields if f in db_column_names]
            print(f"Available key fields: {available_key_fields}")
            
        except Exception as e:
            print(f"Error auditing {doctype}: {str(e)}")
            results[doctype] = {'error': str(e)}
    
    return results

def generate_field_mappings():
    """
    Generate correct field mappings for JavaScript queries
    """
    
    print("\n=== GENERATING FIELD MAPPINGS ===")
    
    mappings = {
        'Case': {
            'query_fields': ['name', 'case_title', 'case_status', 'case_priority', 'case_opened_date', 'primary_social_worker'],
            'note': 'Use case_priority (not priority_level) for queries'
        },
        'Service Plan': {
            'query_fields': ['name', 'plan_title', 'effective_date', 'expiry_date', 'plan_status', 'primary_social_worker'],
            'note': 'Use plan_title, plan_status, effective_date, expiry_date'
        },
        'Document Attachment': {
            'query_fields': ['name', 'document_title', 'document_type', 'upload_date', 'uploaded_by'],
            'note': 'Use document_title (not document_name)'
        },
        'Beneficiary': {
            'query_fields': ['name', 'beneficiary_name', 'family_relationship', 'gender', 'date_of_birth', 'current_status'],
            'note': 'Use family_relationship (not relationship_to_family)'
        },
        'Initial Assessment': {
            'query_fields': ['name', 'assessment_date', 'assessed_by', 'case_no', 'beneficiary'],
            'note': 'Filter by client_name or beneficiary field'
        },
        'Follow Up Assessment': {
            'query_fields': ['name', 'assessment_date', 'assessed_by', 'assessment_type', 'case', 'beneficiary'],
            'note': 'Filter by beneficiary field'
        }
    }
    
    for doctype, mapping in mappings.items():
        print(f"\n{doctype}:")
        print(f"  Fields: {mapping['query_fields']}")
        print(f"  Note: {mapping['note']}")
    
    return mappings

def check_html_field_wrappers():
    """
    Check available HTML field wrappers in Beneficiary DocType
    """
    
    print("\n=== CHECKING HTML FIELD WRAPPERS ===")
    
    try:
        meta = frappe.get_meta('Beneficiary')
        html_fields = [field.fieldname for field in meta.fields 
                      if field.fieldtype == 'HTML' and field.fieldname]
        
        print(f"Available HTML fields in Beneficiary: {html_fields}")
        
        # Check which ones are missing from current JS
        js_html_fields = [
            'initial_assessments_html',
            'follow_up_assessments_html', 
            'current_service_plans_html',
            'document_attachments_html',
            'active_cases_html',
            'closed_cases_html'
        ]
        
        missing_fields = [f for f in js_html_fields if f not in html_fields]
        print(f"Missing HTML fields (need to use existing ones): {missing_fields}")
        
        return html_fields, missing_fields
        
    except Exception as e:
        print(f"Error checking HTML fields: {str(e)}")
        return [], []

if __name__ == "__main__":
    print("Starting comprehensive DocType field audit...")
    
    # Audit all fields
    audit_results = audit_all_doctype_fields()
    
    # Generate mappings
    field_mappings = generate_field_mappings()
    
    # Check HTML wrappers
    html_fields, missing_html = check_html_field_wrappers()
    
    print("\n" + "="*50)
    print("AUDIT COMPLETE")
    print("="*50)
    
    print(f"\nSave this output and use it to fix all JavaScript queries at once!")
