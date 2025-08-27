"""
Seed data script for Case Notes documents in RDSS Social Work Case Management System

This script creates sample case notes data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_case_notes
"""

import frappe
from frappe.utils import today, add_days, nowtime
import random

def execute():
    """Main function to seed case notes data"""
    print("Starting RDSS Social Work case notes data seeding...")
    
    # Get existing beneficiaries and cases
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not cases:
        print("No cases found. Please run seed_data.py first.")
        return
    
    # Create sample case notes
    create_sample_case_notes(cases)
    
    print("Case notes data seeding completed successfully!")

def create_sample_case_notes(cases):
    """Create sample case notes for cases"""
    visit_types = [
        "Home Visit", "Office Visit", "Phone Call", "Video Call", 
        "Community Visit", "Hospital Visit", "School Visit", "Emergency Visit", 
        "Follow-up Call"
    ]
    
    visit_purposes = [
        "Routine Check-in", "Assessment", "Crisis Intervention", "Service Coordination", 
        "Advocacy", "Education/Training", "Resource Provision", "Follow-up", "Case Review"
    ]
    
    client_moods = ["Cooperative", "Engaged", "Withdrawn", "Anxious", "Agitated", "Depressed", "Confused", "Hostile"]
    visit_outcomes = ["Successful", "Partially Successful", "Unsuccessful", "Rescheduled", "Cancelled", "Emergency Response"]
    client_satisfactions = ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
    goals_status = ["Fully Met", "Partially Met", "Not Met"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create 2-3 case notes per case
    for i, case in enumerate(cases[:3]):  # Create case notes for first 3 cases
        num_notes = random.randint(2, 3)
        
        for j in range(num_notes):
            visit_date = add_days(today(), -random.randint(1, 30))
            
            case_note = frappe.new_doc("Case Notes")
            case_note.case = case["name"]
            case_note.beneficiary = case["beneficiary"]
            case_note.visit_date = visit_date
            case_note.visit_time = "09:00:00" if j % 2 == 0 else "14:00:00"
            case_note.visit_type = random.choice(visit_types)
            # case_note.visit_duration = 1800 if j % 2 == 0 else 3600  # 30 or 60 minutes in seconds
            case_note.location = "Home" if "Home" in case_note.visit_type else "Office"
            case_note.social_worker = random.choice(social_workers)
            case_note.beneficiary_present = 1
            case_note.family_members_present = "Parent" if random.choice([True, False]) else ""
            case_note.other_attendees = "Support worker" if random.choice([True, False]) else ""
            case_note.interpreter_used = 0
            case_note.visit_purpose = random.choice(visit_purposes)
            case_note.observations = f"Beneficiary appears {random.choice(client_moods).lower()} during visit. Discussed ongoing support needs and progress toward goals."
            case_note.discussion_topics = "Support services, family dynamics, medical appointments"
            case_note.client_mood_behavior = random.choice(client_moods)
            case_note.environmental_observations = "Home environment appears stable and well-maintained"
            
            # Assessment
            case_note.progress_since_last_visit = "Beneficiary reports continued progress with daily activities"
            case_note.goals_addressed = "Independence in daily living, family relationships"
            case_note.new_concerns_identified = "None reported" if random.choice([True, False]) else "Minor transportation issues"
            case_note.risk_factors_observed = "No significant risks observed"
            case_note.safety_concerns = "None identified"
            
            # Actions and interventions
            case_note.actions_taken = "Provided resource information, scheduled follow-up appointment"
            case_note.referrals_made = "None" if random.choice([True, False]) else "Occupational therapy referral"
            case_note.resources_provided = "Information pamphlets, contact numbers"
            case_note.follow_up_required = "Yes" if random.choice([True, False]) else "No"
            case_note.next_steps = "Continue monitoring progress, schedule next visit"
            case_note.next_visit_date = add_days(visit_date, 14)
            
            # Documentation
            case_note.documents_reviewed = "Service plan, medical reports"
            case_note.documents_provided = "Resource list, appointment cards"
            case_note.consent_obtained = "Yes"
            case_note.confidentiality_discussed = "Yes"
            
            # Outcome
            case_note.visit_outcome = random.choice(visit_outcomes)
            case_note.client_satisfaction = random.choice(client_satisfactions)
            case_note.goals_met = random.choice(goals_status)
            case_note.barriers_encountered = "None" if random.choice([True, False]) else "Transportation challenges"
            case_note.recommendations = "Continue current support approach, monitor progress"
            
            # Administrative
            # case_note.travel_time = 1800  # 30 minutes in seconds
            case_note.mileage = 15 if "Home" in case_note.visit_type else 0
            case_note.expenses = 10.50 if "Home" in case_note.visit_type else 0
            case_note.supervisor_review_required = 0
            case_note.priority_follow_up = 0
            
            try:
                case_note.insert()
                print(f"Created Case Note: {case_note.name} for Case: {case['name']}")
            except Exception as e:
                print(f"Error creating case note for case {case['name']}: {str(e)}")
