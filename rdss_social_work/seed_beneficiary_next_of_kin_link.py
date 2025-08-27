"""
Seed data script for Beneficiary Next of Kin Link documents in RDSS Social Work Case Management System

This script creates sample beneficiary next of kin link data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_beneficiary_next_of_kin_link
"""

import frappe
import random

def execute():
    """Create sample beneficiary next of kin links for demo purposes"""
    print("Starting RDSS Social Work beneficiary next of kin link data seeding...")
    
    # Get existing beneficiaries and next of kin
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    next_of_kin_list = frappe.get_all("Next of Kin", fields=["name"])
    
    if not beneficiaries or not next_of_kin_list:
        print("No beneficiaries or next of kin found. Please run seed_data.py first.")
        return
    
    # Relationship types for next of kin
    relationship_types = ["Parent", "Spouse", "Child", "Sibling", "Grandparent", 
                         "Grandchild", "Other Family", "Friend", "Caregiver", "Guardian", "Other"]
    
    # Create sample links
    create_sample_beneficiary_next_of_kin_links(beneficiaries, next_of_kin_list, relationship_types)
    
    print("Beneficiary next of kin link data seeding completed successfully!")

def create_sample_beneficiary_next_of_kin_links(beneficiaries, next_of_kin_list, relationship_types):
    """Create sample beneficiary next of kin links as child table entries"""
    
    # Create links for beneficiaries
    for i, beneficiary in enumerate(beneficiaries[:3]):  # Create links for first 3 beneficiaries
        num_links = random.randint(1, 2)
        
        # Get the beneficiary document
        beneficiary_doc = frappe.get_doc("Beneficiary", beneficiary["name"])
        
        # Check if links already exist
        if beneficiary_doc.next_of_kin_relationships:
            print(f"Beneficiary next of kin links already exist for Beneficiary: {beneficiary['name']}")
            continue
        
        # Add new links to the beneficiary document
        for j in range(num_links):
            if j < len(next_of_kin_list):
                link = beneficiary_doc.append("next_of_kin_relationships")
                link.next_of_kin = next_of_kin_list[j]["name"]
                link.relationship_type = relationship_types[j] if j < len(relationship_types) else random.choice(relationship_types)
                link.is_primary_caregiver = 1 if j == 0 else 0  # First link is primary caregiver
                link.is_emergency_contact = 1 if j == 0 else (1 if random.choice([True, False]) else 0)
                link.is_authorized_contact = 1 if j == 0 else (1 if random.choice([True, False]) else 0)
                link.notes = f"{link.relationship_type} relationship with beneficiary"
        
        try:
            beneficiary_doc.save()
            print(f"Created {num_links} Beneficiary Next of Kin Links for Beneficiary: {beneficiary['name']}")
        except Exception as e:
            print(f"Error creating beneficiary next of kin links for beneficiary {beneficiary['name']}: {str(e)}")
