"""
Seed data script for Medical History documents in RDSS Social Work Case Management System

This script creates sample medical history data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_medical_history
"""

import frappe
from frappe.utils import today, add_days
import random

def execute():
    """Main function to seed medical history data"""
    print("Starting RDSS Social Work medical history data seeding...")
    
    # Get existing beneficiaries and cases
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not beneficiaries or not cases:
        print("No beneficiaries or cases found. Please run seed_data.py first.")
        return
    
    # Create sample medical histories
    create_sample_medical_histories(beneficiaries, cases)
    
    print("Medical history data seeding completed successfully!")

def create_sample_medical_histories(beneficiaries, cases):
    """Create sample medical histories for beneficiaries"""
    diagnosis_statuses = ["Confirmed", "Provisional", "Rule Out", "History Of", "Suspected"]
    severity_levels = ["Mild", "Moderate", "Severe", "Critical"]
    mobility_statuses = ["Fully Mobile", "Ambulatory with Assistance", "Wheelchair Dependent", "Bedridden"]
    cognitive_statuses = ["Normal", "Mild Impairment", "Moderate Impairment", "Severe Impairment"]
    communication_abilities = ["Normal", "Mild Difficulty", "Moderate Difficulty", "Severe Difficulty", "Non-verbal"]
    sensory_impairments = ["None", "Hearing Impaired", "Vision Impaired", "Both"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create one medical history per case
    for i, case in enumerate(cases[:3]):  # Create medical histories for first 3 cases
        # Check if medical history already exists for this case
        if frappe.db.exists("Medical History", {"case": case["name"]}):
            print(f"Medical history already exists for Case: {case['name']}")
            continue
        
        medical_history = frappe.new_doc("Medical History")
        medical_history.beneficiary = case["beneficiary"]
        medical_history.case = case["name"]
        medical_history.record_date = add_days(today(), -20)
        medical_history.recorded_by = random.choice(social_workers)
        medical_history.source_of_information = "Medical Records"
        medical_history.verification_status = "Verified"
        
        # Primary diagnosis
        medical_history.primary_diagnosis = "Rare Genetic Disorder" if random.choice([True, False]) else "Neurological Condition"
        medical_history.diagnosis_date = add_days(today(), -365)
        medical_history.diagnosing_physician = "Dr. Sarah Johnson"
        medical_history.icd_code = "Q99.9" if "Genetic" in medical_history.primary_diagnosis else "G99.9"
        medical_history.diagnosis_status = random.choice(diagnosis_statuses)
        medical_history.severity_level = random.choice(severity_levels)
        
        # Secondary conditions
        medical_history.secondary_diagnoses = "Mild scoliosis" if random.choice([True, False]) else "None"
        medical_history.comorbidities = "Asthma" if random.choice([True, False]) else "None"
        medical_history.complications = "None" if random.choice([True, False]) else "Minor respiratory issues"
        medical_history.genetic_conditions = "Family history of genetic disorders" if random.choice([True, False]) else "None"
        medical_history.rare_disorders = medical_history.primary_diagnosis if "Rare" in medical_history.primary_diagnosis else "None"
        medical_history.syndrome_details = "Associated syndrome symptoms" if "Syndrome" in medical_history.primary_diagnosis else "None"
        
        # Current medications
        medical_history.current_medications = "Multivitamins, Pain management medication"
        medical_history.medication_allergies = "Penicillin" if random.choice([True, False]) else "None"
        medical_history.adverse_reactions = "Mild rash" if random.choice([True, False]) else "None"
        medical_history.medication_compliance = "Good" if random.choice([True, False]) else "Fair"
        medical_history.pharmacy_information = "Local pharmacy" if random.choice([True, False]) else "Hospital pharmacy"
        medical_history.medication_management = "Family Assisted"
        
        # Medical procedures
        medical_history.surgeries_performed = "Spinal correction surgery" if random.choice([True, False]) else "None"
        medical_history.planned_procedures = "None" if random.choice([True, False]) else "Upcoming specialist consultation"
        medical_history.medical_devices = "Wheelchair" if random.choice([True, False]) else "None"
        medical_history.assistive_equipment = "Walking frame" if random.choice([True, False]) else "None"
        medical_history.prosthetics_orthotics = "Back brace" if random.choice([True, False]) else "None"
        medical_history.equipment_maintenance = "Regular maintenance required" if random.choice([True, False]) else "None"
        
        # Hospitalizations
        medical_history.recent_hospitalizations = "None" if random.choice([True, False]) else "One admission for respiratory infection"
        medical_history.emergency_visits = "None" if random.choice([True, False]) else "One ER visit"
        medical_history.admission_history = "No significant history" if random.choice([True, False]) else "One previous admission"
        medical_history.discharge_summaries = "All discharge summaries available" if random.choice([True, False]) else "Recent summary pending"
        medical_history.follow_up_care = "Regular specialist appointments"
        medical_history.readmission_risk = "Low" if random.choice([True, False]) else "Moderate"
        
        # Healthcare providers
        medical_history.primary_care_physician = "Dr. Michael Chen"
        medical_history.specialists = "Neurologist, Orthopedic Surgeon, Geneticist"
        medical_history.healthcare_team = "Multidisciplinary team approach"
        medical_history.preferred_hospital = "General Hospital"
        medical_history.insurance_provider = "Integrated Shield Plan"
        medical_history.medical_record_number = f"MR{random.randint(10000, 99999)}"
        
        # Functional status
        medical_history.mobility_status = random.choice(mobility_statuses)
        medical_history.cognitive_status = random.choice(cognitive_statuses)
        medical_history.communication_abilities = random.choice(communication_abilities)
        medical_history.sensory_impairments = random.choice(sensory_impairments)
        medical_history.behavioral_concerns = "None" if random.choice([True, False]) else "Occasional anxiety"
        medical_history.developmental_milestones = "Delayed in motor skills" if random.choice([True, False]) else "Age-appropriate"
        
        # Care requirements
        medical_history.daily_care_needs = "Assistance with mobility and personal care"
        medical_history.nursing_care_required = "Yes" if random.choice([True, False]) else "No"
        medical_history.therapy_services = "Physical therapy, Occupational therapy"
        medical_history.respite_care_needs = "Yes" if random.choice([True, False]) else "No"
        medical_history.emergency_protocols = "Contact primary physician, then emergency services"
        medical_history.care_coordination = "Social worker coordinates with medical team"
        
        # Prognosis
        medical_history.prognosis = "Good"
        medical_history.life_expectancy = "Normal" if random.choice([True, False]) else "Slightly reduced"
        medical_history.disease_progression = "Slowly Progressive" if random.choice([True, False]) else "Stable"
        medical_history.quality_of_life = "Good" if random.choice([True, False]) else "Fair"
        medical_history.treatment_goals = "Maintain current function, prevent complications"
        medical_history.advance_directives = "None" if random.choice([True, False]) else "Living will in place"
        
        try:
            medical_history.insert()
            print(f"Created Medical History: {medical_history.name} for Case: {case['name']}")
        except Exception as e:
            print(f"Error creating medical history for case {case['name']}: {str(e)}")
