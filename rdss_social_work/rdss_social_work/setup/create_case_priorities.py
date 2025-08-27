import frappe
import json
import os

def create_case_priorities():
    """Create the initial Case Priority records"""
    print("Creating Case Priority records...")
    
    # Path to the fixtures file
    fixtures_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        "rdss_social_work", 
        "fixtures",
        "case_priority.json"
    )
    
    # Load the fixtures data
    with open(fixtures_path, 'r') as f:
        priorities = json.load(f)
    
    # Create each priority record
    for priority in priorities:
        # Check if record already exists
        if not frappe.db.exists("Case Priority", {"priority_code": priority["priority_code"]}):
            doc = frappe.new_doc("Case Priority")
            doc.priority_code = priority["priority_code"]
            doc.priority_name = priority["priority_name"]
            doc.appointment_frequency_months = priority["appointment_frequency_months"]
            doc.description = priority["description"]
            doc.color_code = priority["color_code"]
            doc.insert()
            print(f"Created Case Priority: {priority['priority_code']} - {priority['priority_name']}")
        else:
            print(f"Case Priority {priority['priority_code']} already exists")
    
    frappe.db.commit()
    print("Case Priority records created successfully")

def execute():
    """Execute the script"""
    create_case_priorities()

if __name__ == "__frappe__.utils.bench_helper":
    execute()
