"""
Seed data script for Follow-up Assessment documents in RDSS Social Work Case Management System

This script creates sample follow-up assessment data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_follow_up_assessment
"""

import frappe
from frappe.utils import today, add_days
import random

def execute():
    """Main function to seed follow-up assessment data"""
    print("Starting RDSS Social Work follow-up assessment data seeding...")
    
    # Get existing beneficiaries, cases, and initial assessments
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    initial_assessments = frappe.get_all("Initial Assessment", fields=["name", "case_no"])
    
    if not cases:
        print("No cases found. Please run seed_data.py first.")
        return
    
    # Create sample follow-up assessments
    create_sample_follow_up_assessments(cases, initial_assessments)
    
    print("Follow-up assessment data seeding completed successfully!")

def create_sample_follow_up_assessments(cases, initial_assessments):
    """Create sample follow-up assessments for cases"""
    assessment_types = [
        "Scheduled Review", "Unscheduled Review", "Crisis Assessment", 
        "Discharge Assessment", "Annual Review", "Service Change Assessment"
    ]
    
    assessment_reasons = [
        "Routine Follow-up", "Condition Change", "Service Review", 
        "Family Request", "Provider Concern", "Emergency"
    ]
    
    change_levels = ["Significant Improvement", "Slight Improvement", "No Change", "Slight Decline", "Significant Decline"]
    mobility_levels = ["Independent", "Requires Assistance", "Requires Supervision", "Dependent"]
    health_statuses = ["Good", "Fair", "Poor"]
    risk_levels = ["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create one follow-up assessment per case
    for i, case in enumerate(cases[:3]):  # Create assessments for first 3 cases
        # Check if follow-up assessment already exists for this case
        if frappe.db.exists("Follow Up Assessment", {"case": case["name"]}):
            print(f"Follow-up assessment already exists for Case: {case['name']}")
            continue
        
        follow_up = frappe.new_doc("Follow Up Assessment")
        follow_up.case = case["name"]
        follow_up.beneficiary = case["beneficiary"]
        follow_up.assessment_type = random.choice(assessment_types)
        follow_up.assessment_date = add_days(today(), -5)
        follow_up.assessed_by = random.choice(social_workers)
        follow_up.assessment_reason = random.choice(assessment_reasons)
        
        # Link to initial assessment if available
        if initial_assessments and i < len(initial_assessments):
            follow_up.previous_assessment = initial_assessments[i]["name"]
            follow_up.time_since_last_assessment = "3 months"
        
        # Changes since last assessment
        follow_up.overall_condition_change = random.choice(change_levels)
        follow_up.functional_status_change = random.choice(change_levels)
        follow_up.medical_status_change = random.choice(change_levels)
        follow_up.social_status_change = random.choice(change_levels)
        follow_up.environmental_changes = "Stable home environment" if random.choice([True, False]) else "Minor changes in living situation"
        follow_up.service_needs_change = "No Change" if random.choice([True, False]) else "Increased Slightly"
        
        # Current functional abilities
        follow_up.mobility_current = random.choice(mobility_levels)
        follow_up.washing_bathing_current = random.choice(mobility_levels)
        follow_up.dressing_current = random.choice(mobility_levels)
        follow_up.feeding_current = "Independent"
        follow_up.toileting_current = random.choice(mobility_levels)
        follow_up.transferring_current = random.choice(mobility_levels)
        follow_up.housekeeping_current = random.choice(mobility_levels)
        follow_up.cognitive_ability_current = "Normal" if random.choice([True, False]) else "Mild Impairment"
        
        # Current health status
        follow_up.medical_conditions_current = "Stable medical condition"
        follow_up.medications_current = "Continuing prescribed medications"
        follow_up.recent_hospitalizations = "None" if random.choice([True, False]) else "One brief admission"
        follow_up.health_concerns_new = "None reported" if random.choice([True, False]) else "Minor respiratory issues"
        follow_up.pain_level = random.choice(["No Pain", "Mild Pain", "Moderate Pain", "Severe Pain"])
        follow_up.mental_health_status = "Good"
        
        # Current support services
        follow_up.services_currently_receiving = "Case management, medical care coordination"
        follow_up.service_satisfaction = "Satisfied" if random.choice([True, False]) else "Neutral"
        follow_up.services_working_well = "Medical appointments, family support"
        follow_up.services_not_working = "None" if random.choice([True, False]) else "Transportation delays"
        follow_up.additional_services_needed = "None" if random.choice([True, False]) else "Occupational therapy"
        follow_up.service_gaps_identified = "None" if random.choice([True, False]) else "Transportation support"
        
        # Caregiver assessment
        follow_up.primary_caregiver_current = "Parent"
        follow_up.caregiver_stress_level = "Low" if random.choice([True, False]) else "Moderate"
        follow_up.caregiver_support_needs = "Respite care" if random.choice([True, False]) else "None"
        follow_up.caregiver_training_needs = "Medical procedure training" if random.choice([True, False]) else "None"
        follow_up.respite_care_needed = "Yes" if random.choice([True, False]) else "No"
        follow_up.family_dynamics_changes = "Stable family relationships"
        
        # Environmental assessment
        follow_up.home_safety_current = "Safe"
        follow_up.accessibility_issues = "None" if random.choice([True, False]) else "Minor accessibility concerns"
        follow_up.equipment_functioning = "All Working Well"
        follow_up.environmental_hazards = "None identified"
        follow_up.home_modifications_needed = "None" if random.choice([True, False]) else "Grab bars in bathroom"
        follow_up.transportation_issues = "None" if random.choice([True, False]) else "Occasional delays"
        
        # Goals progress
        follow_up.previous_goals_status = "Making progress toward goals"
        follow_up.goals_achieved = "Independence in daily activities"
        follow_up.goals_partially_achieved = "Improved family communication"
        follow_up.goals_not_achieved = "None" if random.choice([True, False]) else "Transportation independence"
        follow_up.barriers_to_goals = "None" if random.choice([True, False]) else "Financial constraints"
        follow_up.new_goals_identified = "Enhance community participation" if random.choice([True, False]) else "None"
        
        # Risk assessment
        follow_up.current_risk_level = random.choice(risk_levels)
        follow_up.risk_factors_current = "None" if random.choice([True, False]) else "Financial stress"
        follow_up.safety_concerns_current = "None identified"
        follow_up.risk_changes = "Risk Unchanged" if random.choice([True, False]) else "Risk Increased"
        follow_up.protective_factors = "Strong family support, stable housing"
        
        # Recommendations
        follow_up.service_recommendations = "Continue current services, monitor progress"
        follow_up.care_plan_changes = "None required" if random.choice([True, False]) else "Add occupational therapy"
        follow_up.referrals_recommended = "None" if random.choice([True, False]) else "Community support services"
        follow_up.priority_actions = "Monitor medical appointments, provide family support"
        follow_up.follow_up_timeline = "3 months"
        follow_up.next_assessment_date = add_days(today(), 90)
        
        # Outcome
        follow_up.assessment_outcome = "Continue Current Services"
        follow_up.overall_progress = "Good Progress"
        follow_up.quality_of_life_rating = "Good" if random.choice([True, False]) else "Fair"
        follow_up.client_satisfaction_current = "Satisfied" if random.choice([True, False]) else "Neutral"
        follow_up.family_satisfaction = "Satisfied"
        
        try:
            follow_up.insert()
            follow_up.submit()
            print(f"Created and submitted Follow-up Assessment: {follow_up.name} for Case: {case['name']}")
        except Exception as e:
            print(f"Error creating follow-up assessment for case {case['name']}: {str(e)}")
