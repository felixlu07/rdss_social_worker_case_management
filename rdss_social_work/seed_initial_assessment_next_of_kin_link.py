"""
Seed data script for Initial Assessment Next of Kin Link documents in RDSS Social Work Case Management System

This script creates sample initial assessment next of kin link data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_initial_assessment_next_of_kin_link
"""

import frappe
import random

def execute():
    """Main function to seed initial assessment next of kin link data"""
    print("Starting RDSS Social Work initial assessment next of kin link data seeding...")
    
    # Get existing initial assessments and next of kin
    initial_assessments = frappe.get_all("Initial Assessment", fields=["name"])
    next_of_kin_list = frappe.get_all("Next of Kin", fields=["name"])
    
    if not initial_assessments or not next_of_kin_list:
        print("No initial assessments or next of kin found. Please run seed_data.py first.")
        return
    
    # Create sample initial assessment next of kin links
    create_sample_initial_assessment_next_of_kin_links(initial_assessments, next_of_kin_list)
    
    print("Initial assessment next of kin link data seeding completed successfully!")

def create_sample_initial_assessment_next_of_kin_links(initial_assessments, next_of_kin_list):
    """Create sample initial assessment next of kin links"""
    contact_priorities = ["1 - First Contact", "2 - Second Contact", "3 - Third Contact"]
    
    # Create links for initial assessments
    for i, assessment in enumerate(initial_assessments[:3]):  # Create links for first 3 assessments
        # Create 1-2 links per assessment
        num_links = random.randint(1, 2)
        
        for j in range(num_links):
            # Check if link already exists
            if frappe.db.exists("Initial Assessment Next of Kin Link", 
                              {"parent": assessment["name"], 
                               "next_of_kin": next_of_kin_list[j]["name"] if j < len(next_of_kin_list) else next_of_kin_list[0]["name"]}):
                print(f"Initial assessment next of kin link already exists for Assessment: {assessment['name']}")
                continue
            
            link = frappe.new_doc("Initial Assessment Next of Kin Link")
            link.parent = assessment["name"]
            link.parenttype = "Initial Assessment"
            link.parentfield = "next_of_kin_contacts"
            link.next_of_kin = next_of_kin_list[j]["name"] if j < len(next_of_kin_list) else next_of_kin_list[0]["name"]
            link.relationship_context = f"{next_of_kin_list[j]['name']} is the primary caregiver" if j == 0 else f"{next_of_kin_list[j]['name']} is a family member"
            link.is_primary_contact = 1 if j == 0 else 0
            link.is_emergency_contact = 1 if j == 0 else (1 if random.choice([True, False]) else 0)
            link.contact_priority = contact_priorities[j] if j < len(contact_priorities) else random.choice(contact_priorities)
            link.notes = f"Contact for {assessment['name']} assessment"
            
            try:
                link.insert()
                print(f"Created Initial Assessment Next of Kin Link: {link.name} for Assessment: {assessment['name']}")
            except Exception as e:
                print(f"Error creating initial assessment next of kin link for assessment {assessment['name']}: {str(e)}")
