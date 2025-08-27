"""
Seed data script for RDSS Social Work Case Management System

This script creates sample data for demonstration purposes.

Additional seeding files have been created for each document type:
- seed_appointment.py
- seed_care_team.py
- seed_financial_assessment.py
- seed_service_plan.py
- seed_referral.py
- seed_case_notes.py
- seed_follow_up_assessment.py
- seed_medical_history.py
- seed_document_attachment.py
- seed_beneficiary_next_of_kin_link.py
- seed_initial_assessment_next_of_kin_link.py

Usage:
    bench execute rdss_social_work.seed_data
"""

import frappe
from frappe.utils import today, add_days, add_months
import random

def execute():
    """Main function to seed all data"""
    print("Starting RDSS Social Work data seeding...")
    
    # Create sample data
    create_sample_users()
    create_sample_next_of_kin()
    beneficiaries = create_sample_beneficiaries()
    cases = create_sample_cases(beneficiaries)
    create_sample_initial_assessments(beneficiaries, cases)
    
    print("Data seeding completed successfully!")
    print("\nDemo accounts created:")
    print("- Social Worker: social_worker@example.com (password: social123)")
    print("- Supervisor: supervisor@example.com (password: supervisor123)")

def create_sample_users():
    """Create sample social worker and supervisor accounts"""
    # Create social worker
    if not frappe.db.exists("User", "social_worker@example.com"):
        social_worker = frappe.new_doc("User")
        social_worker.email = "social_worker@example.com"
        social_worker.first_name = "Social"
        social_worker.last_name = "Worker"
        social_worker.send_welcome_email = 0
        social_worker.new_password = "SocialWorker123!"
        social_worker.insert()
        social_worker.add_roles("Social Worker")
        
    # Create supervisor
    if not frappe.db.exists("User", "supervisor@example.com"):
        supervisor = frappe.new_doc("User")
        supervisor.email = "supervisor@example.com"
        supervisor.first_name = "Case"
        supervisor.last_name = "Supervisor"
        supervisor.send_welcome_email = 0
        supervisor.new_password = "Supervisor123!"
        supervisor.insert()
        supervisor.add_roles("Social Worker", "Social Work Supervisor")

def create_sample_next_of_kin():
    """Create sample next of kin contacts"""
    next_of_kin_data = [
        {
            "contact_name": "Tan Mei Ling",
            "relationship_to_beneficiary": "Parent",
            "age": 48,
            "gender": "Female",
            "date_of_birth": "1975-03-15",
            "bc_nric_no": "S7512345C",
            "occupation": "Administrative Assistant",
            "mobile_number": "+65 9123 4567",
            "email_address": "tanmeiling@example.com",
            "address_line_1": "Blk 123 Hougang Ave 4",
            "address_line_2": "#05-89",
            "postal_code": "530123",
            "is_primary_caregiver": 1,
            "caregiver_availability": "Full-time (24/7)",
            "consent_to_contact": "Yes",
            "consent_to_share_information": "Yes",
            "consent_to_emergency_contact": "Yes",
            "emergency_contact_priority": "Primary",
            "available_24_7": 1
        },
        {
            "contact_name": "Lim Wei Jun",
            "relationship_to_beneficiary": "Parent",
            "age": 50,
            "gender": "Male",
            "date_of_birth": "1973-07-22",
            "bc_nric_no": "S7312345D",
            "occupation": "Delivery Driver",
            "mobile_number": "+65 8765 4321",
            "email_address": "limweijun@example.com",
            "address_line_1": "Blk 123 Hougang Ave 4",
            "address_line_2": "#05-89",
            "postal_code": "530123",
            "is_primary_caregiver": 0,
            "caregiver_availability": "Part-time (4-8 hours)",
            "consent_to_contact": "Yes",
            "consent_to_share_information": "Yes",
            "consent_to_emergency_contact": "Yes",
            "emergency_contact_priority": "Secondary",
            "available_24_7": 0
        }
    ]
    
    for nok_data in next_of_kin_data:
        if not frappe.db.exists("Next of Kin", {"contact_name": nok_data["contact_name"]}):
            nok = frappe.new_doc("Next of Kin")
            nok.update(nok_data)
            nok.insert()
            print(f"Created Next of Kin: {nok.contact_name}")

def create_sample_beneficiaries():
    """Create sample beneficiaries"""
    beneficiaries = []
    
    beneficiary_data = [
        {
            "beneficiary_name": "Tan Zi Wei",
            "bc_nric_no": "S0812345B",
            "date_of_birth": "2008-05-12",
            "age": 17,
            "gender": "Male",
            "registration_date": add_days(today(), -180),
            "current_status": "Active",
            "address_line_1": "Blk 123 Hougang Ave 4",
            "address_line_2": "#12-345",
            "postal_code": "530123",
            "mobile_number": "+65 9123 4567",
            "primary_diagnosis": "Orthopaedic",
            "diagnosis_date": "2010-03-15",
            "severity_level": "Moderate",
            "specialist_doctor": "Dr. Lim Hui Ling",
            "hospital_clinic": "KK Women's and Children's Hospital",
            "current_medications": "Corticosteroids, Heart medications",
            "known_allergies": "Penicillin",
            "care_level": "Level 3 - High Support",
        }
    ]
    
    # Get existing next of kin
    next_of_kin_list = frappe.get_all("Next of Kin", fields=["name", "contact_name"])
    
    for ben_data in beneficiary_data:
        if not frappe.db.exists("Beneficiary", {"bc_nric_no": ben_data["bc_nric_no"]}):
            beneficiary = frappe.new_doc("Beneficiary")
            beneficiary.update(ben_data)
            
            # Link to Next of Kin
            if next_of_kin_list:
                # Add a relationship to the first Next of Kin
                beneficiary.append("next_of_kin_relationships", {
                    "next_of_kin": next_of_kin_list[0]['name'],
                    "relationship_type": "Parent",
                    "is_primary_caregiver": 1,
                    "is_emergency_contact": 1,
                    "is_authorized_contact": 1
                })
            
            beneficiary.insert()
            beneficiaries.append(beneficiary)
            print(f"Created Beneficiary: {beneficiary.beneficiary_name}")
    
    return beneficiaries

def create_sample_cases(beneficiaries):
    """Create sample cases for beneficiaries"""
    cases = []
    
    case_types = [
        "Initial Assessment",
        "Ongoing Support",
        "Family Support",
        "Crisis Intervention",
        "Resource Coordination"
    ]
    priorities = ["Low", "Medium", "High", "Urgent"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    for i, beneficiary in enumerate(beneficiaries):
        if not frappe.db.exists("Case", {"beneficiary": beneficiary.name}):
            case = frappe.new_doc("Case")
            case.case_title = f"Case for {beneficiary.beneficiary_name}"
            case.beneficiary = beneficiary.name
            case.case_type = random.choice(case_types)
            case.priority_level = random.choice(priorities)
            case.case_opened_date = add_days(beneficiary.registration_date, 7)
            case.case_status = "Open"
            case.primary_social_worker = social_workers[i % len(social_workers)]
            case.supervisor = social_workers[(i + 1) % len(social_workers)]
            case.assigned_date = add_days(case.case_opened_date, 1)
            case.presenting_issues = "Beneficiary requires ongoing support services for rare disorder management"
            case.case_goals = "Improve quality of life, maintain independence, coordinate care services"
            
            # Set risk level based on priority
            if case.priority_level == "Low":
                case.risk_level = "Low Risk"
            elif case.priority_level == "Medium":
                case.risk_level = "Moderate Risk"
            elif case.priority_level == "High":
                case.risk_level = "High Risk"
            elif case.priority_level == "Urgent":
                case.risk_level = "High Risk"
            else:  # Critical
                case.risk_level = "Critical Risk"
            
            # Add risk mitigation plan for high and critical risk cases
            if case.risk_level in ["High Risk", "Critical Risk"]:
                case.risk_mitigation_plan = "Regular check-ins with beneficiary, emergency contact information verified, safety plan in place, 24/7 support available"
            
            case.service_budget = 2000.00 if i % 2 == 0 else 1500.00
            case.funding_source = "Government Grant"
            case.authorization_date = case.case_opened_date
            case.insert()
            cases.append(case)
            print(f"Created Case: {case.name} for {beneficiary.beneficiary_name}")
    
    return cases

def create_sample_initial_assessments(beneficiaries, cases):
    """Create sample initial assessments"""
    for i, (beneficiary, case) in enumerate(zip(beneficiaries, cases)):
        if not frappe.db.exists("Initial Assessment", {"beneficiary": beneficiary.name}):
            assessment = frappe.new_doc("Initial Assessment")
            assessment.case_no = case.name
            assessment.client_name = beneficiary.beneficiary_name
            assessment.bc_nric_no = beneficiary.bc_nric_no
            assessment.age_category = "Below Age 21" if beneficiary.age < 21 else "Adult"
            assessment.assessment_date = add_days(beneficiary.registration_date, 5)
            assessment.assessed_by = "social_worker@example.com"
            assessment.institution_ssa = "Rare Disorder Society of Singapore"
            
            # Get Next of Kin for this beneficiary
            next_of_kin_list = frappe.get_all("Next of Kin", filters={}, fields=["name"])
            
            # Link to existing Next of Kin
            if next_of_kin_list:
                # Add the first Next of Kin as a contact
                assessment.append("next_of_kin_contacts", {
                    "next_of_kin": next_of_kin_list[0]['name'],
                    "relationship_context": "Primary caregiver and emergency contact",
                    "is_primary_contact": 1,
                    "is_emergency_contact": 1,
                    "contact_priority": "1 - First Contact"
                })
            
            # Community services
            assessment.befriending = 1
            assessment.counselling = 1
            assessment.medical_escort_school_escort = 1 if beneficiary.age < 18 else 0
            assessment.transport = 1
            assessment.financial_aid = 1
            
            # Functional abilities
            assessment.mobility = "Requires help/supervision" if i % 2 == 0 else "Independent – No help is required"
            assessment.washing_bathing = "Requires help/supervision"
            assessment.dressing = "Requires help/supervision" if i % 2 == 0 else "Independent – No help is required"
            assessment.feeding = "Independent – No help is required"
            assessment.toileting = "Requires help/supervision"
            assessment.transferring = "Requires help/supervision"
            
            # Health status
            assessment.medical_conditions = beneficiary.primary_diagnosis
            assessment.hearing_status = "Good"
            assessment.vision_status = "Good"
            
            # Allergies
            assessment.medicine_allergy = beneficiary.known_allergies
            
            # Financial
            assessment.financial_source = "Employment" if beneficiary.age >= 18 else "Parents"
            assessment.monthly_household_income = 4000.00 if i % 2 == 0 else 6000.00
            
            # Emergency contact
            assessment.emergency_contact_name = "Tan Mei Ling"
            assessment.emergency_contact_relationship = "Mother"
            assessment.emergency_contact_mobile_no = "+65 9123 4567"
            
            # Assessment decision
            assessment.assessment_decision = "Accept"
            
            assessment.insert()
            assessment.submit()
            print(f"Created and submitted Initial Assessment: {assessment.name}")
