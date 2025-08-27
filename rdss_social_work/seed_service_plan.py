"""
Seed data script for Service Plan documents in RDSS Social Work Case Management System

This script creates sample service plan data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_service_plan
"""

import frappe
from frappe.utils import today, add_days, add_months
import random

def execute():
    """Main function to seed service plan data"""
    print("Starting RDSS Social Work service plan data seeding...")
    
    # Get existing beneficiaries and cases
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not beneficiaries or not cases:
        print("No beneficiaries or cases found. Please run seed_data.py first.")
        return
    
    # Create sample service plans
    create_sample_service_plans(cases)
    
    print("Service plan data seeding completed successfully!")

def create_sample_service_plans(cases):
    """Create sample service plans for cases"""
    plan_types = [
        "Initial Service Plan", "Revised Service Plan", "Crisis Intervention Plan", 
        "Transition Plan", "Discharge Plan", "Family Support Plan", "Individual Support Plan"
    ]
    
    plan_statuses = ["Draft", "Active", "Under Review", "Revised", "Completed", "Cancelled"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create one service plan per case
    for i, case in enumerate(cases[:3]):  # Create service plans for first 3 cases
        # Check if service plan already exists for this case
        if frappe.db.exists("Service Plan", {"case": case["name"]}):
            print(f"Service plan already exists for Case: {case['name']}")
            continue
        
        service_plan = frappe.new_doc("Service Plan")
        service_plan.plan_title = f"Service Plan for {case['beneficiary']}"
        service_plan.case = case["name"]
        service_plan.beneficiary = case["beneficiary"]
        service_plan.plan_type = random.choice(plan_types)
        service_plan.plan_date = add_days(today(), -15)
        service_plan.plan_status = "Active"
        service_plan.effective_date = add_days(today(), -10)
        service_plan.review_date = add_months(today(), 3)
        service_plan.expiry_date = add_months(today(), 12)
        
        # Planning team
        service_plan.primary_social_worker = social_workers[0]
        service_plan.case_manager = social_workers[0]
        service_plan.supervisor = social_workers[1]
        service_plan.beneficiary_involvement = "Fully Involved"
        service_plan.family_involvement = "Partially Involved"
        service_plan.other_professionals = "Medical Specialist, Therapist"
        
        # Assessment summary
        service_plan.presenting_needs = "Daily living support, medical care coordination, family support"
        service_plan.strengths_identified = "Family support, resilience, motivation to improve"
        service_plan.risk_factors = "Financial stress, limited support network"
        service_plan.priority_concerns = "Medical appointment adherence, financial stability"
        service_plan.cultural_considerations = "Language preferences, family dynamics"
        
        # Goals and objectives
        service_plan.primary_goal = "Improve quality of life and independence"
        service_plan.secondary_goals = "Enhance family relationships, secure stable housing"
        service_plan.measurable_objectives = "Attend 80% of medical appointments, maintain stable housing"
        service_plan.target_outcomes = "Beneficiary reports improved satisfaction with daily life"
        service_plan.success_indicators = "Regular attendance at appointments, stable housing"
        
        # Services
        service_plan.services_to_be_provided = "Case management, medical care coordination, family support services"
        service_plan.service_frequency = "Weekly"
        service_plan.service_duration = "6-12 months"
        service_plan.service_providers = "Social worker, medical specialist, community support services"
        service_plan.service_location = "Multiple Locations"
        service_plan.transportation_needs = "Assistance with medical appointments"
        
        # Resources
        service_plan.internal_resources = "Social work team, case management services"
        service_plan.external_resources = "Community support services, medical providers"
        service_plan.equipment_needed = "Mobility aids, communication devices"
        service_plan.funding_source = "Government Grant"
        service_plan.estimated_cost = 5000.00
        service_plan.budget_approved = "Yes"
        
        # Timeline
        service_plan.implementation_start_date = add_days(today(), -5)
        service_plan.milestone_dates = "3-month review, 6-month review, annual review"
        service_plan.review_schedule = "Monthly"
        service_plan.expected_completion_date = add_months(today(), 12)
        service_plan.progress_monitoring = "Monthly check-ins, quarterly reviews"
        
        # Responsibilities
        service_plan.social_worker_responsibilities = "Case management, care coordination, advocacy"
        service_plan.beneficiary_responsibilities = "Attend appointments, communicate needs, participate in planning"
        service_plan.family_responsibilities = "Provide support, participate in family meetings"
        service_plan.agency_responsibilities = "Provide services, maintain communication"
        
        # Monitoring and evaluation
        service_plan.progress_indicators = "Appointment attendance, goal achievement"
        service_plan.evaluation_methods = "Regular assessments, feedback collection"
        service_plan.reporting_schedule = "Monthly"
        service_plan.quality_measures = "Service satisfaction, outcome achievement"
        service_plan.outcome_measurement = "Goal attainment scaling, beneficiary feedback"
        
        # Contingency
        service_plan.barriers_anticipated = "Financial constraints, transportation issues"
        service_plan.contingency_plans = "Access emergency funds, arrange transportation support"
        service_plan.crisis_procedures = "Contact crisis intervention team, emergency protocols"
        service_plan.emergency_contacts = "Crisis hotline, emergency social worker"
        service_plan.escalation_procedures = "Supervisor notification, management review"
        
        # Approval
        service_plan.plan_developed_by = social_workers[0]
        service_plan.plan_approved_by = social_workers[1]
        service_plan.approval_date = add_days(today(), -3)
        service_plan.beneficiary_consent = "Yes"
        service_plan.consent_date = add_days(today(), -3)
        service_plan.next_review_by = social_workers[0]
        
        try:
            service_plan.insert()
            print(f"Created Service Plan: {service_plan.name} for Case: {case['name']}")
        except Exception as e:
            print(f"Error creating service plan for case {case['name']}: {str(e)}")
