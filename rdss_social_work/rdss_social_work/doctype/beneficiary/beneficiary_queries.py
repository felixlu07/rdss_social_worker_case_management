#!/usr/bin/env python3
"""
Server-side query methods for Beneficiary DocType
Bypasses client-side field permission issues
"""

import frappe

@frappe.whitelist()
def get_beneficiary_cases(beneficiary_name):
    """Get cases for a beneficiary"""
    return frappe.get_list(
        'Case',
        filters={'beneficiary': beneficiary_name},
        fields=['name', 'case_title', 'case_status', 'case_priority', 'case_opened_date', 'primary_social_worker'],
        order_by='case_opened_date desc'
    )

@frappe.whitelist()
def get_beneficiary_closed_cases(beneficiary_name):
    """Get closed cases for a beneficiary"""
    return frappe.get_list(
        'Case',
        filters={
            'beneficiary': beneficiary_name,
            'case_status': ['in', ['Closed', 'Completed']]
        },
        fields=['name', 'case_title', 'case_status', 'case_opened_date', 'actual_closure_date', 'primary_social_worker'],
        order_by='actual_closure_date desc',
        limit=10
    )

@frappe.whitelist()
def get_beneficiary_appointments(beneficiary_name, upcoming=True):
    """Get appointments for a beneficiary"""
    if upcoming:
        filters = {
            'beneficiary': beneficiary_name,
            'appointment_date': ['>=', frappe.utils.today()]
        }
        order_by = 'appointment_date asc'
    else:
        filters = {
            'beneficiary': beneficiary_name,
            'appointment_date': ['<', frappe.utils.today()]
        }
        order_by = 'appointment_date desc'
    
    return frappe.get_list(
        'Appointment',
        filters=filters,
        fields=['name', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status', 'social_worker', 'case'],
        order_by=order_by,
        limit=20
    )

@frappe.whitelist()
def get_beneficiary_assessments(beneficiary_name):
    """Get assessments for a beneficiary"""
    # Get Initial Assessments by client_name
    initial = frappe.get_list(
        'Initial Assessment',
        filters={'client_name': beneficiary_name},
        fields=['name', 'assessment_date', 'assessed_by', 'case_no'],
        order_by='assessment_date desc'
    )
    
    # Get Follow Up Assessments by beneficiary field
    follow_up = frappe.get_list(
        'Follow Up Assessment',
        filters={'beneficiary': beneficiary_name},
        fields=['name', 'assessment_date', 'assessed_by', 'assessment_type', 'case'],
        order_by='assessment_date desc'
    )
    
    return {'initial': initial, 'follow_up': follow_up}

@frappe.whitelist()
def get_beneficiary_service_plans(beneficiary_name):
    """Get service plans for a beneficiary"""
    return frappe.get_list(
        'Service Plan',
        filters={'beneficiary': beneficiary_name},
        fields=['name', 'plan_title', 'effective_date', 'expiry_date', 'plan_status', 'primary_social_worker'],
        order_by='effective_date desc'
    )

@frappe.whitelist()
def get_beneficiary_documents(beneficiary_name):
    """Get documents for a beneficiary"""
    return frappe.get_list(
        'Document Attachment',
        filters={'beneficiary': beneficiary_name},
        fields=['name', 'document_title', 'document_type', 'upload_date', 'uploaded_by'],
        order_by='upload_date desc',
        limit=50
    )

@frappe.whitelist()
def get_beneficiary_family_info(beneficiary_name):
    """Get family information for a beneficiary"""
    try:
        # Get the beneficiary document to find family link
        beneficiary = frappe.get_doc('Beneficiary', beneficiary_name)
        
        if not beneficiary.beneficiary_family:
            return {'family': None, 'family_members': []}
            
        # Get family document
        family = frappe.get_doc('Beneficiary Family', beneficiary.beneficiary_family)
        
        # Get all family members
        family_members = frappe.get_list(
            'Beneficiary',
            filters={'beneficiary_family': beneficiary.beneficiary_family},
            fields=['name', 'beneficiary_name', 'family_relationship', 'age', 'gender', 'current_status', 'primary_diagnosis'],
            order_by='family_relationship asc'
        )
        
        return {
            'family': {
                'name': family.name,
                'family_name': family.family_name,
                'family_head': family.family_head,
                'family_status': family.family_status,
                'registration_date': family.registration_date,
                'primary_address_line_1': family.primary_address_line_1,
                'primary_postal_code': family.primary_postal_code,
                'primary_mobile_number': family.primary_mobile_number,
                'primary_email_address': family.primary_email_address,
                'emergency_contact_1_name': family.emergency_contact_1_name,
                'emergency_contact_1_relationship': family.emergency_contact_1_relationship,
                'emergency_contact_1_phone': family.emergency_contact_1_phone
            },
            'family_members': family_members
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting family info for {beneficiary_name}: {str(e)}", "Family Info Error")
        return {'family': None, 'family_members': []}
