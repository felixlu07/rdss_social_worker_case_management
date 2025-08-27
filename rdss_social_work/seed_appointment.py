"""
Seed data script for Appointment documents in RDSS Social Work Case Management System

This script creates sample appointment data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_appointment
"""

import frappe
from frappe.utils import today, add_days, add_months, nowtime
import random

def execute():
    """Main function to seed appointment data"""
    print("Starting RDSS Social Work appointment data seeding...")
    
    # Get existing cases and beneficiaries
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not cases:
        print("No cases found. Please run seed_data.py first to create cases.")
        return
    
    # Create sample appointments
    create_sample_appointments(cases)
    
    print("Appointment data seeding completed successfully!")

def create_sample_appointments(cases):
    """Create sample appointments for cases"""
    appointment_types = [
        "Initial Assessment", "Follow Up Assessment", "Case Review", 
        "Service Planning", "Crisis Intervention", "Family Meeting", 
        "Home Visit", "Office Visit", "Phone Consultation", "Video Call"
    ]
    
    appointment_statuses = [
        "Scheduled", "Confirmed", "In Progress", "Completed", 
        "Cancelled", "No Show", "Rescheduled"
    ]
    
    appointment_categories = [
        "Routine", "Urgent", "Emergency", "Follow-up", 
        "Assessment", "Planning", "Crisis"
    ]
    
    priorities = ["Low", "Medium", "High", "Urgent"]
    location_types = [
        "Office", "Home Visit", "Community Center", "Hospital", 
        "School", "Phone", "Video Call", "Other"
    ]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    for i, case in enumerate(cases[:3]):  # Create appointments for first 3 cases
        # Create 2-3 appointments per case
        num_appointments = random.randint(2, 3)
        
        for j in range(num_appointments):
            # Ensure appointments are not scheduled in the past
            appointment_date = add_days(today(), random.randint(0, 30))
            
            appointment = frappe.new_doc("Appointment")
            appointment.case = case["name"]
            appointment.beneficiary = case["beneficiary"]
            appointment.appointment_date = appointment_date
            appointment.appointment_time = "09:00:00" if j % 2 == 0 else "14:00:00"
            appointment.appointment_type = random.choice(appointment_types)
            appointment.appointment_status = random.choice(appointment_statuses)
            appointment.scheduled_by = random.choice(social_workers)
            appointment.duration_minutes = 60 if j % 2 == 0 else 90
            appointment.purpose = f"{appointment.appointment_type} for {case['beneficiary']}"
            appointment.appointment_category = random.choice(appointment_categories)
            appointment.priority = random.choice(priorities)
            appointment.location_type = random.choice(location_types)
            appointment.appointment_location = "Main Office" if appointment.location_type == "Office" else f"{appointment.location_type} Location"
            appointment.social_worker = random.choice(social_workers)
            appointment.attendees = f"{case['beneficiary']}, Social Worker"
            
            # Set cancellation reason if appointment is cancelled
            if appointment.appointment_status == "Cancelled":
                appointment.cancellation_reason = "Client Request"
            
            # Set no show reason if appointment is No Show
            if appointment.appointment_status == "No Show":
                appointment.no_show_reason = "Forgot Appointment"
            
            # Set appointment outcome if appointment is completed
            if appointment.appointment_status == "Completed":
                appointment.appointment_outcome = "Completed as Planned"
                appointment.attendance_status = "Attended"
            
            try:
                appointment.insert()
                print(f"Created Appointment: {appointment.name} for Case: {case['name']}")
            except Exception as e:
                print(f"Error creating appointment for case {case['name']}: {str(e)}")
