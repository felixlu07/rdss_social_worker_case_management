#!/usr/bin/env python3
"""
Test Case Query to identify the exact permission issue
"""

import frappe

def test_case_query():
    """Test Case query with beneficiary filter"""
    
    try:
        # Test the exact query from JavaScript
        result = frappe.get_list(
            'Case',
            filters={'beneficiary': 'BEN-2025-01557'},
            fields=['name', 'case_title', 'case_status', 'case_priority', 'case_opened_date', 'primary_social_worker']
        )
        print(f"SUCCESS: Found {len(result)} cases")
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        
        # Test if beneficiary field exists and is accessible
        try:
            meta = frappe.get_meta('Case')
            beneficiary_field = meta.get_field('beneficiary')
            print(f"Beneficiary field exists: {beneficiary_field is not None}")
            if beneficiary_field:
                print(f"Field properties: {beneficiary_field.as_dict()}")
        except Exception as meta_error:
            print(f"Meta error: {str(meta_error)}")
            
        # Test direct SQL query
        try:
            sql_result = frappe.db.sql("""
                SELECT name, case_title, case_status, case_priority, case_opened_date, primary_social_worker 
                FROM `tabCase` 
                WHERE beneficiary = %s 
                LIMIT 5
            """, ('BEN-2025-01557',), as_dict=True)
            print(f"Direct SQL works: Found {len(sql_result)} records")
        except Exception as sql_error:
            print(f"SQL error: {str(sql_error)}")
            
        return None

if __name__ == "__main__":
    test_case_query()
