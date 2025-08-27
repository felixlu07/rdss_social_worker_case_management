"""
Delete demo data script for RDSS Social Work Case Management System

This script deletes all sample data created by the seed_data.py script.
Use with caution - this will remove all demo data from the system.

Usage:
    bench execute rdss_social_work.delete_demo_data

Author: Cascade AI Assistant
Date: 2025-08-13
"""

import frappe

def execute():
    """Main function to delete all demo data"""
    print("Starting RDSS Social Work demo data deletion...")
    
    # Delete data in correct order to respect dependencies
    delete_document_attachments()
    delete_care_teams()
    delete_financial_assessments()
    delete_medical_histories()
    delete_appointments()
    delete_referrals()
    delete_case_notes()
    delete_service_plans()
    delete_follow_up_assessments()
    delete_initial_assessments()
    delete_cases()
    delete_beneficiaries()
    delete_next_of_kin()
    delete_sample_users()
    
    print("Demo data deletion completed successfully!")

def delete_document_attachments():
    """Delete sample document attachments"""
    docs = frappe.get_all("Document Attachment", filters={
        "document_title": ["like", "%Tan Zi Wei%"],
        "document_title": ["like", "%Ng Su Ling%"]
    })
    
    for doc in docs:
        frappe.delete_doc("Document Attachment", doc.name, ignore_permissions=True)
    print(f"Deleted {len(docs)} Document Attachments")

def delete_care_teams():
    """Delete sample care teams"""
    teams = frappe.get_all("Care Team", filters={
        "care_goals": ["like", "%Coordinate care services%"]
    })
    
    for team in teams:
        doc = frappe.get_doc("Care Team", team.name)
        if doc.docstatus == 1:  # Submitted
            doc.cancel()
        frappe.delete_doc("Care Team", team.name, ignore_permissions=True)
    print(f"Deleted {len(teams)} Care Teams")

def delete_financial_assessments():
    """Delete sample financial assessments"""
    assessments = frappe.get_all("Financial Assessment", filters={
        "assessed_by": "social_worker@example.com"
    })
    
    for assessment in assessments:
        frappe.delete_doc("Financial Assessment", assessment.name, ignore_permissions=True)
    print(f"Deleted {len(assessments)} Financial Assessments")

def delete_medical_histories():
    """Delete sample medical histories"""
    histories = frappe.get_all("Medical History", filters={
        "recorded_by": "social_worker@example.com"
    })
    
    for history in histories:
        frappe.delete_doc("Medical History", history.name, ignore_permissions=True)
    print(f"Deleted {len(histories)} Medical Histories")

def delete_appointments():
    """Delete sample appointments"""
    appointments = frappe.get_all("Appointment", filters={
        "purpose": ["like", "%Regular case review%"]
    })
    
    for appointment in appointments:
        frappe.delete_doc("Appointment", appointment.name, ignore_permissions=True)
    print(f"Deleted {len(appointments)} Appointments")

def delete_referrals():
    """Delete sample referrals"""
    referrals = frappe.get_all("Referral", filters={
        "referral_source": "RDSS Social Work Department"
    })
    
    for referral in referrals:
        frappe.delete_doc("Referral", referral.name, ignore_permissions=True)
    print(f"Deleted {len(referrals)} Referrals")

def delete_case_notes():
    """Delete sample case notes"""
    notes = frappe.get_all("Case Notes", filters={
        "observations": ["like", "%Beneficiary appears stable%"]
    })
    
    for note in notes:
        frappe.delete_doc("Case Notes", note.name, ignore_permissions=True)
    print(f"Deleted {len(notes)} Case Notes")

def delete_service_plans():
    """Delete sample service plans"""
    plans = frappe.get_all("Service Plan", filters={
        "plan_status": "Active"
    })
    
    for plan in plans:
        doc = frappe.get_doc("Service Plan", plan.name)
        if doc.docstatus == 1:  # Submitted
            doc.cancel()
        frappe.delete_doc("Service Plan", plan.name, ignore_permissions=True)
    print(f"Deleted {len(plans)} Service Plans")

def delete_follow_up_assessments():
    """Delete sample follow-up assessments"""
    assessments = frappe.get_all("Follow Up Assessment", filters={
        "assessed_by": "social_worker@example.com"
    })
    
    for assessment in assessments:
        doc = frappe.get_doc("Follow Up Assessment", assessment.name)
        if doc.docstatus == 1:  # Submitted
            doc.cancel()
        frappe.delete_doc("Follow Up Assessment", assessment.name, ignore_permissions=True)
    print(f"Deleted {len(assessments)} Follow Up Assessments")

def delete_initial_assessments():
    """Delete sample initial assessments"""
    assessments = frappe.get_all("Initial Assessment", filters={
        "institution_ssa": "Rare Disorder Society of Singapore"
    })
    
    for assessment in assessments:
        doc = frappe.get_doc("Initial Assessment", assessment.name)
        if doc.docstatus == 1:  # Submitted
            doc.cancel()
        frappe.delete_doc("Initial Assessment", assessment.name, ignore_permissions=True)
    print(f"Deleted {len(assessments)} Initial Assessments")

def delete_cases():
    """Delete sample cases"""
    cases = frappe.get_all("Case", filters={
        "case_title": ["like", "%Case for %"]
    })
    
    for case in cases:
        doc = frappe.get_doc("Case", case.name)
        if doc.docstatus == 1:  # Submitted
            doc.cancel()
        frappe.delete_doc("Case", case.name, ignore_permissions=True)
    print(f"Deleted {len(cases)} Cases")

def delete_beneficiaries():
    """Delete sample beneficiaries"""
    beneficiaries = frappe.get_all("Beneficiary", filters={
        "beneficiary_name": ["in", ["Tan Zi Wei", "Ng Su Ling"]]
    })
    
    for beneficiary in beneficiaries:
        frappe.delete_doc("Beneficiary", beneficiary.name, ignore_permissions=True)
    print(f"Deleted {len(beneficiaries)} Beneficiaries")

def delete_next_of_kin():
    """Delete sample next of kin"""
    next_of_kin = frappe.get_all("Next of Kin", filters={
        "contact_name": ["in", ["Tan Mei Ling", "Lim Wei Jun"]]
    })
    
    for nok in next_of_kin:
        frappe.delete_doc("Next of Kin", nok.name, ignore_permissions=True)
    print(f"Deleted {len(next_of_kin)} Next of Kin records")

def delete_sample_users():
    """Delete sample users (social worker and supervisor)"""
    # Note: We're not actually deleting the users for safety reasons
    # but we could clear their demo data if needed
    print("Note: Demo users (social_worker@example.com and supervisor@example.com) retained for safety")
    print("Their passwords remain unchanged: SocialWorker123! and Supervisor123! respectively")
