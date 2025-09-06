#!/usr/bin/env python3
"""
Server-side query methods for Beneficiary Family DocType
Bypasses client-side field permission issues
"""

import frappe

@frappe.whitelist()
def get_family_members(family_name):
    """Get all family members for a family"""
    return frappe.get_list(
        'Beneficiary',
        filters={'beneficiary_family': family_name},
        fields=['name', 'beneficiary_name', 'gender', 'date_of_birth', 'beneficiary_status', 'mobile_number', 'email_address'],
        order_by='beneficiary_name asc'
    )

@frappe.whitelist()
def get_family_cases(family_name):
    """Get all cases for family members"""
    # First get all family members
    family_members = frappe.get_list(
        'Beneficiary',
        filters={'beneficiary_family': family_name},
        fields=['name'],
        pluck='name'
    )
    
    if not family_members:
        return []
    
    # Get cases for all family members
    return frappe.get_list(
        'Case',
        filters={'beneficiary': ['in', family_members]},
        fields=['name', 'case_title', 'case_status', 'case_priority', 'case_opened_date', 'beneficiary', 'primary_social_worker'],
        order_by='case_opened_date desc'
    )

@frappe.whitelist()
def get_family_appointments(family_name):
    """Get all appointments for family members"""
    # First get all family members
    family_members = frappe.get_list(
        'Beneficiary',
        filters={'beneficiary_family': family_name},
        fields=['name'],
        pluck='name'
    )
    
    if not family_members:
        return []
    
    # Get appointments for all family members
    return frappe.get_list(
        'Appointment',
        filters={'beneficiary': ['in', family_members]},
        fields=['name', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status', 'beneficiary', 'assigned_social_worker'],
        order_by='appointment_date desc, appointment_time desc'
    )

@frappe.whitelist()
def get_family_case_notes(family_name):
    """Get all case notes for family members"""
    # First get all family members
    family_members = frappe.get_list(
        'Beneficiary',
        filters={'beneficiary_family': family_name},
        fields=['name'],
        pluck='name'
    )
    
    if not family_members:
        return []
    
    # Get cases for family members first
    family_cases = frappe.get_list(
        'Case',
        filters={'beneficiary': ['in', family_members]},
        fields=['name'],
        pluck='name'
    )
    
    if not family_cases:
        return []
    
    # Get case notes for all family cases
    return frappe.get_list(
        'Case Note',
        filters={'case': ['in', family_cases]},
        fields=['name', 'note_date', 'note_type', 'note_content', 'case', 'created_by'],
        order_by='note_date desc, creation desc'
    )
