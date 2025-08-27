"""
Seed data script for Beneficiary documents in RDSS Social Work Case Management System

This script creates sample beneficiary data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_beneficiary
"""

import frappe
from frappe.utils import today, add_years, add_months
import random

def execute():
    """Main function to seed beneficiary data"""
    print("Starting RDSS Social Work beneficiary data seeding...")
    
    # Create sample beneficiaries
    create_sample_beneficiaries()
    
    print("Beneficiary data seeding completed successfully!")

def create_sample_beneficiaries():
    """Create 10 sample beneficiaries with diverse characteristics"""
    
    # Sample data for realistic beneficiaries
    names = [
        "Ahmad bin Ibrahim",
        "Tan Mei Ling",
        "Rajesh Kumar",
        "Sarah Lim Wei Ting",
        "Mohammed Ali Hassan",
        "Chong Siew Hua",
        "Krishna Priya",
        "James Wong Chee Keong",
        "Noor Aisyah bte Abdullah",
        "David Chen Wei Ming"
    ]
    
    genders = ["Male", "Female", "Other", "Prefer not to say"]
    
    # Rare disorders/diseases
    primary_diagnoses = [
        "Spinal Muscular Atrophy Type 1",
        "Duchenne Muscular Dystrophy",
        "Huntington's Disease",
        "Cystic Fibrosis",
        "Tay-Sachs Disease",
        "Gaucher Disease Type 1",
        "Fabry Disease",
        "Pompe Disease",
        "Niemann-Pick Disease Type C",
        "Wilson's Disease"
    ]
    
    severity_levels = ["Mild", "Moderate", "Severe", "Critical"]
    
    living_arrangements = [
        "Lives Alone", "With Family", "With Caregiver", 
        "Assisted Living", "Nursing Home", "Other"
    ]
    
    independence_levels = [
        "Fully Independent", "Partially Independent", 
        "Requires Assistance", "Fully Dependent"
    ]
    
    languages = ["English", "Mandarin", "Malay", "Tamil", "Other"]
    
    # Addresses in Singapore
    addresses = [
        {"address": "Blk 123 Ang Mo Kio Ave 3 #08-215", "postal": "560123"},
        {"address": "Blk 456 Bedok North St 3 #12-345", "postal": "460456"},
        {"address": "Blk 789 Choa Chu Kang Loop #05-678", "postal": "680789"},
        {"address": "Blk 234 Jurong West St 21 #10-234", "postal": "640234"},
        {"address": "Blk 567 Tampines St 32 #03-567", "postal": "520567"},
        {"address": "Blk 891 Yishun Ring Rd #07-891", "postal": "760891"},
        {"address": "Blk 345 Punggol Field #15-345", "postal": "820345"},
        {"address": "Blk 678 Sengkang East Way #02-678", "postal": "540678"},
        {"address": "Blk 901 Hougang Ave 8 #11-901", "postal": "530901"},
        {"address": "Blk 432 Bukit Batok West Ave 6 #09-432", "postal": "650432"}
    ]
    
    # Create 10 beneficiaries
    for i in range(10):
        beneficiary = frappe.new_doc("Beneficiary")
        
        # Basic information
        beneficiary.naming_series = "BEN-.YYYY.-"
        beneficiary.beneficiary_name = names[i]
        beneficiary.bc_nric_no = f"S{i+1:08d}X"  # Unique NRIC format
        
        # Date of birth - varied ages from 5 to 75 years old
        age = random.randint(5, 75)
        beneficiary.date_of_birth = add_years(today(), -age)
        
        # Gender
        beneficiary.gender = genders[i % 4]
        
        # Registration date (within last 2 years)
        beneficiary.registration_date = add_months(today(), -random.randint(1, 24))
        
        # Current status
        beneficiary.current_status = "Active"
        
        # Contact information
        beneficiary.address_line_1 = addresses[i]["address"]
        beneficiary.postal_code = addresses[i]["postal"]
        beneficiary.mobile_number = f"8{i+1:07d}{random.randint(1000, 9999)}"
        beneficiary.email_address = f"{names[i].lower().replace(' ', '.')}@email.com"
        beneficiary.preferred_contact_method = random.choice(["Mobile", "Email", "Home Phone"])
        
        # Rare disorder information
        beneficiary.primary_diagnosis = primary_diagnoses[i]
        beneficiary.diagnosis_date = add_months(today(), -random.randint(3, 36))
        beneficiary.severity_level = random.choice(severity_levels)
        
        # Additional medical details
        beneficiary.secondary_conditions = random.choice([
            "Mild cognitive impairment",
            "Mobility issues",
            "Speech delays",
            "Feeding difficulties",
            "Sleep disorders",
            "Behavioral challenges"
        ]) if random.random() > 0.3 else ""
        
        beneficiary.genetic_counseling_received = random.choice([0, 1])
        beneficiary.specialist_doctor = f"Dr. {random.choice(['Tan', 'Lim', 'Raj', 'Wong', 'Lee'])} {random.choice(['Kumar', 'Mei', 'Seng', 'Hui', 'Ming'])}"
        beneficiary.hospital_clinic = random.choice([
            "KK Women's and Children's Hospital",
            "National University Hospital",
            "Singapore General Hospital",
            "Tan Tock Seng Hospital",
            "Changi General Hospital"
        ])
        
        # Medical summary
        beneficiary.current_medications = random.choice([
            "Enzyme replacement therapy",
            "Physical therapy medications",
            "Symptomatic treatment",
            "Multivitamin supplements",
            "Pain management medications"
        ]) if random.random() > 0.2 else ""
        
        beneficiary.known_allergies = random.choice([
            "Penicillin allergy",
            "Latex allergy",
            "Food allergies",
            "No known allergies"
        ]) if random.random() > 0.5 else ""
        
        beneficiary.medical_devices_equipment = random.choice([
            "Wheelchair",
            "Walker",
            "Feeding tube",
            "Oxygen concentrator",
            "CPAP machine"
        ]) if random.random() > 0.4 else ""
        
        beneficiary.mobility_aids = random.choice([
            "Manual wheelchair",
            "Electric wheelchair",
            "Walking frame",
            "Crutches",
            "Cane"
        ]) if random.random() > 0.6 else ""
        
        # Care level
        beneficiary.care_level = random.choice(severity_levels)
        beneficiary.care_hours_per_day = random.randint(2, 12)
        beneficiary.living_arrangement = random.choice(living_arrangements)
        beneficiary.independence_level = random.choice(independence_levels)
        
        # Emergency contacts
        beneficiary.emergency_contact_1_name = f"{random.choice(['Father', 'Mother', 'Spouse', 'Sibling'])} {names[i].split()[-1]}"
        beneficiary.emergency_contact_1_relationship = random.choice(["Father", "Mother", "Spouse", "Sibling", "Adult Child"])
        beneficiary.emergency_contact_1_phone = f"9{i+1:07d}{random.randint(1000, 9999)}"
        
        beneficiary.emergency_contact_2_name = f"{random.choice(['Uncle', 'Aunt', 'Cousin', 'Friend'])} {random.choice(['Tan', 'Lim', 'Raj', 'Wong'])}"
        beneficiary.emergency_contact_2_relationship = random.choice(["Uncle", "Aunt", "Cousin", "Friend", "Neighbor"])
        beneficiary.emergency_contact_2_phone = f"6{i+1:07d}{random.randint(1000, 9999)}"
        
        # Preferences
        beneficiary.preferred_language = random.choice(languages)
        beneficiary.communication_preferences = random.choice([
            "Direct Communication",
            "Through Family",
            "Through Caregiver",
            "Written Communication"
        ])
        
        # Additional notes
        beneficiary.additional_notes = f"Sample beneficiary #{i+1} created for demonstration purposes."
        beneficiary.internal_notes = f"Seed data created on {today()}"
        
        try:
            beneficiary.insert()
            print(f"Created Beneficiary: {beneficiary.name} - {beneficiary.beneficiary_name}")
        except Exception as e:
            print(f"Error creating beneficiary {names[i]}: {str(e)}")

if __name__ == "__main__":
    execute()
