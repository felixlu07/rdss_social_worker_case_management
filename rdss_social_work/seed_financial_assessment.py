"""
Seed data script for Financial Assessment documents in RDSS Social Work Case Management System

This script creates sample financial assessment data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_financial_assessment
"""

import frappe
from frappe.utils import today, add_days
import random

def execute():
    """Main function to seed financial assessment data"""
    print("Starting RDSS Social Work financial assessment data seeding...")
    
    # Get existing beneficiaries and cases
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not beneficiaries or not cases:
        print("No beneficiaries or cases found. Please run seed_data.py first.")
        return
    
    # Create sample financial assessments
    create_sample_financial_assessments(beneficiaries, cases)
    
    print("Financial assessment data seeding completed successfully!")

def create_sample_financial_assessments(beneficiaries, cases):
    """Create sample financial assessments for beneficiaries"""
    assessment_types = [
        "Initial Financial Assessment", "Annual Review", "Change in Circumstances", 
        "Benefit Application", "Crisis Assessment"
    ]
    
    employment_statuses = ["Employed", "Unemployed", "Self-employed", "Retired", "Student"]
    financial_stability_ratings = ["Very Stable", "Stable", "Moderately Stable", "Unstable", "Very Unstable"]
    poverty_statuses = ["Below Poverty Line", "Near Poverty Line", "Above Poverty Line"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create one financial assessment per case
    for i, case in enumerate(cases[:3]):  # Create assessments for first 3 cases
        # Check if financial assessment already exists for this case
        if frappe.db.exists("Financial Assessment", {"case": case["name"]}):
            print(f"Financial assessment already exists for Case: {case['name']}")
            continue
        
        financial_assessment = frappe.new_doc("Financial Assessment")
        financial_assessment.beneficiary = case["beneficiary"]
        financial_assessment.case = case["name"]
        financial_assessment.assessment_date = add_days(today(), -10)
        financial_assessment.assessed_by = random.choice(social_workers)
        financial_assessment.assessment_type = random.choice(assessment_types)
        financial_assessment.assessment_period = "Last 3 Months"
        
        # Household information
        financial_assessment.household_size = random.randint(2, 5)
        financial_assessment.household_composition = "Beneficiary and family members"
        financial_assessment.primary_income_earner = "Parent"
        financial_assessment.dependents_count = financial_assessment.household_size - 1
        financial_assessment.household_head = "Parent"
        financial_assessment.marital_status = "Married"
        
        # Income information
        financial_assessment.monthly_gross_income = random.randint(3000, 8000)
        financial_assessment.monthly_net_income = int(financial_assessment.monthly_gross_income * 0.8)
        financial_assessment.primary_income_source = "Employment"
        financial_assessment.secondary_income_sources = "Part-time work"
        financial_assessment.government_benefits = 500
        
        # Expenses
        financial_assessment.monthly_housing_cost = 1200
        financial_assessment.monthly_utilities = 200
        financial_assessment.monthly_food_expenses = 800
        financial_assessment.monthly_transportation = 300
        financial_assessment.monthly_medical_expenses = 400
        financial_assessment.monthly_other_expenses = 500
        
        # Assets
        financial_assessment.savings_amount = random.randint(5000, 20000)
        financial_assessment.checking_account_balance = 2000
        financial_assessment.investments = 10000
        financial_assessment.property_owned = "HDB Flat"
        
        # Debts
        financial_assessment.total_debt_amount = 200000
        financial_assessment.monthly_debt_payments = 1500
        financial_assessment.mortgage_balance = 180000
        
        # Insurance
        financial_assessment.health_insurance = "Yes"
        financial_assessment.health_insurance_provider = "Integrated Shield Plan"
        
        # Financial assistance
        financial_assessment.current_assistance_programs = "CHAS, ComCare"
        financial_assessment.assistance_amount_monthly = 300
        financial_assessment.assistance_eligibility = "Eligible for additional support"
        
        # Financial management
        financial_assessment.budgeting_skills = "Fair"
        financial_assessment.financial_literacy_level = "Moderate"
        financial_assessment.banking_access = "Full Access"
        financial_assessment.financial_decision_maker = "Parent"
        
        # Assessment results
        financial_assessment.financial_stability_rating = "Stable"
        financial_assessment.poverty_level_status = random.choice(poverty_statuses)
        financial_assessment.financial_stress_level = "Moderate"
        financial_assessment.immediate_financial_needs = "Utility bill assistance, medical expense support"
        financial_assessment.long_term_financial_goals = "Increase savings, reduce debt"
        
        # Recommendations
        financial_assessment.financial_recommendations = "Connect with financial counseling services"
        financial_assessment.assistance_recommendations = "Apply for additional government assistance"
        financial_assessment.referrals_needed = "Financial counseling agency"
        financial_assessment.priority_actions = "Immediate utility bill assistance"
        financial_assessment.follow_up_timeline = "3 months"
        financial_assessment.next_assessment_date = add_days(today(), 90)
        
        try:
            financial_assessment.insert()
            print(f"Created Financial Assessment: {financial_assessment.name} for Case: {case['name']}")
        except Exception as e:
            print(f"Error creating financial assessment for case {case['name']}: {str(e)}")
