"""
Script to run all seeding scripts in the correct order for RDSS Social Work Case Management System

This script executes all seeding files in the proper sequence to populate the system with sample data.

Usage:
    bench execute rdss_social_work.seed_all
"""

import frappe

def execute():
    """Main function to run all seeding scripts in order"""
    print("Starting RDSS Social Work complete data seeding...")
    
    # List of seeding functions to execute in order
    seeding_functions = [
        ("seed_data", "Main seeding script"),
        ("seed_beneficiary_next_of_kin_link", "Beneficiary next of kin links"),
        ("seed_initial_assessment_next_of_kin_link", "Initial assessment next of kin links"),
        ("seed_appointment", "Appointments"),
        ("seed_care_team", "Care teams"),
        ("seed_financial_assessment", "Financial assessments"),
        ("seed_service_plan", "Service plans"),
        ("seed_referral", "Referrals"),
        ("seed_case_notes", "Case notes"),
        ("seed_follow_up_assessment", "Follow-up assessments"),
        ("seed_medical_history", "Medical histories"),
        ("seed_document_attachment", "Document attachments")
    ]
    
    # Execute each seeding function
    for module_name, description in seeding_functions:
        try:
            print(f"\n--- Seeding {description} ---")
            module = frappe.get_module(f"rdss_social_work.{module_name}")
            module.execute()
        except Exception as e:
            print(f"Error running {module_name}: {str(e)}")
            # Continue with other seeding scripts even if one fails
    
    print("\n--- All seeding completed ---")
