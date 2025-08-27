"""
Seed data script for Referral documents in RDSS Social Work Case Management System

This script creates sample referral data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_referral
"""

import frappe
from frappe.utils import today, add_days
import random

def execute():
    """Main function to seed referral data"""
    print("Starting RDSS Social Work referral data seeding...")
    
    # Get existing beneficiaries and cases
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not cases:
        print("No cases found. Please run seed_data.py first.")
        return
    
    # Create sample referrals
    create_sample_referrals(cases)
    
    print("Referral data seeding completed successfully!")

def create_sample_referrals(cases):
    """Create sample referrals for cases"""
    referral_types = [
        "Medical Services", "Therapy Services", "Social Services", 
        "Educational Services", "Vocational Services", "Financial Assistance", 
        "Housing Services", "Transportation", "Respite Care", "Support Groups"
    ]
    
    service_categories = [
        "Primary Care", "Specialty Care", "Mental Health", "Physical Therapy", 
        "Occupational Therapy", "Speech Therapy", "Social Work", "Case Management", 
        "Home Care", "Day Care", "Residential Care"
    ]
    
    referral_sources = ["Initial Assessment", "Follow Up Assessment", "Case Notes", "Family Request", "Provider Recommendation", "Emergency"]
    priorities = ["Low", "Medium", "High", "Urgent"]
    statuses = ["Pending", "Sent", "Acknowledged", "Accepted", "Rejected", "Completed", "Cancelled"]
    urgency_levels = ["Routine", "Soon", "Urgent", "Emergent"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create 1-2 referrals per case
    for i, case in enumerate(cases[:3]):  # Create referrals for first 3 cases
        num_referrals = random.randint(1, 2)
        
        for j in range(num_referrals):
            # Check if referral already exists for this case
            if frappe.db.exists("Referral", {"case": case["name"], "referral_type": referral_types[j]}):
                print(f"Referral already exists for Case: {case['name']}")
                continue
            
            referral = frappe.new_doc("Referral")
            referral.case = case["name"]
            referral.beneficiary = case["beneficiary"]
            referral.referral_date = add_days(today(), -random.randint(1, 20))
            referral.referred_by = random.choice(social_workers)
            referral.referral_source = random.choice(referral_sources)
            referral.priority = random.choice(priorities)
            referral.status = random.choice(statuses)
            referral.referral_type = referral_types[j] if j < len(referral_types) else random.choice(referral_types)
            referral.service_category = random.choice(service_categories)
            referral.referral_reason = f"Referral for {referral.referral_type.lower()} to support {case['beneficiary']} case goals"
            referral.urgency_level = random.choice(urgency_levels)
            referral.expected_outcome = f"Improved {referral.referral_type.lower()} support for beneficiary"
            referral.background_information = f"Beneficiary requires {referral.referral_type.lower()} as part of comprehensive care plan"
            
            # Recipient information
            referral.referred_to_organization = f"{referral.referral_type} Provider Organization"
            referral.referred_to_person = "Dr. Smith" if "Medical" in referral.referral_type else "Provider Specialist"
            referral.contact_person = "Receptionist"
            
            # Set referral outcome if status is Rejected
            if referral.status == "Rejected":
                referral.referral_outcome = "Rejected"
            referral.organization_phone = "+65 1234 5678"
            referral.organization_email = f"info@{referral.referral_type.lower().replace(' ', '')}.com"
            referral.organization_address = "123 Provider Street, Singapore 123456"
            
            # Requirements
            referral.documentation_required = "Medical records, assessment reports"
            referral.consent_obtained = "Yes"
            referral.consent_date = add_days(referral.referral_date, 1)
            referral.special_requirements = "Wheelchair access required"
            referral.accessibility_needs = "Ramp access, wide doorways"
            
            # Communication
            referral.referral_method = "Email"
            referral.referral_sent_date = add_days(referral.referral_date, 2)
            referral.follow_up_required = "Yes" if random.choice([True, False]) else "No"
            referral.acknowledgment_received = "Yes"
            referral.acknowledgment_date = add_days(referral.referral_sent_date, 1)
            
            try:
                referral.insert()
                print(f"Created Referral: {referral.name} for Case: {case['name']}")
            except Exception as e:
                print(f"Error creating referral for case {case['name']}: {str(e)}")
