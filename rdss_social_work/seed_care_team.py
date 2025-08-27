"""
Seed data script for Care Team documents in RDSS Social Work Case Management System

This script creates sample care team data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_care_team
"""

import frappe
from frappe.utils import today
import random

def execute():
    """Main function to seed care team data"""
    print("Starting RDSS Social Work care team data seeding...")
    
    # Get existing beneficiaries and cases
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not beneficiaries or not cases:
        print("No beneficiaries or cases found. Please run seed_data.py first.")
        return
    
    # Create sample care teams
    create_sample_care_teams(beneficiaries, cases)
    
    print("Care team data seeding completed successfully!")

def create_sample_care_teams(beneficiaries, cases):
    """Create sample care teams for beneficiaries"""
    team_statuses = ["Active", "Inactive", "Transitioning", "Disbanded"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create one care team per case
    for i, case in enumerate(cases[:3]):  # Create care teams for first 3 cases
        # Check if care team already exists for this case
        if frappe.db.exists("Care Team", {"case": case["name"]}):
            print(f"Care team already exists for Case: {case['name']}")
            continue
        
        care_team = frappe.new_doc("Care Team")
        care_team.beneficiary = case["beneficiary"]
        care_team.case = case["name"]
        care_team.team_name = f"Care Team for {case['beneficiary']}"
        care_team.team_lead = random.choice(social_workers)
        care_team.formation_date = today()
        care_team.team_status = "Active"
        
        # Team composition
        care_team.primary_social_worker = social_workers[0]
        care_team.case_manager = social_workers[0]
        care_team.supervisor = social_workers[1]
        
        # External providers
        care_team.healthcare_providers = "General Hospital, Specialist Clinic"
        care_team.community_partners = "Community Center, Support Group"
        care_team.family_members = "Immediate Family"
        
        # Coordination
        care_team.meeting_frequency = "Weekly"
        care_team.primary_communication_method = "Mixed Methods"
        care_team.coordination_platform = "Case Management System"
        
        # Roles and responsibilities
        care_team.team_roles = "Social Worker: Case management, Specialist: Medical care, Family: Support"
        care_team.decision_making_process = "Collaborative decision making with beneficiary involvement"
        care_team.escalation_procedures = "Escalate to supervisor for complex issues"
        
        # Care planning
        care_team.care_goals = "Improve quality of life, maintain independence"
        care_team.service_coordination = "Coordinate medical appointments, therapy sessions"
        care_team.treatment_protocols = "Follow hospital treatment plan"
        
        try:
            care_team.insert()
            print(f"Created Care Team: {care_team.name} for Case: {case['name']}")
        except Exception as e:
            print(f"Error creating care team for case {case['name']}: {str(e)}")
