import frappe
import json
import os

def execute():
    """Create the initial Case Priority records"""
    print("Creating Case Priority records...")
    
    priorities = [
        {
            "priority_code": "P1",
            "priority_name": "Critical Priority",
            "appointment_frequency_months": 1,
            "description": "<p>Highest priority level requiring monthly appointments. Cases with immediate risk or urgent needs that require constant monitoring.</p>",
            "color_code": "red"
        },
        {
            "priority_code": "P2",
            "priority_name": "High Priority",
            "appointment_frequency_months": 1,
            "description": "<p>High priority level requiring monthly appointments. Cases with significant needs that require regular monitoring.</p>",
            "color_code": "orange"
        },
        {
            "priority_code": "P3",
            "priority_name": "Medium Priority",
            "appointment_frequency_months": 3,
            "description": "<p>Medium priority level requiring quarterly appointments (every 3 months). Cases with moderate needs that require periodic monitoring.</p>",
            "color_code": "yellow"
        },
        {
            "priority_code": "P4",
            "priority_name": "Standard Priority",
            "appointment_frequency_months": 6,
            "description": "<p>Standard priority level requiring semi-annual appointments (every 6 months). Cases with lower needs that require less frequent monitoring.</p>",
            "color_code": "blue"
        },
        {
            "priority_code": "P5",
            "priority_name": "Low Priority",
            "appointment_frequency_months": 12,
            "description": "<p>Low priority level requiring annual appointments. Cases with minimal needs that require basic annual check-ins.</p>",
            "color_code": "green"
        },
        {
            "priority_code": "P6",
            "priority_name": "Maintenance Priority",
            "appointment_frequency_months": 12,
            "description": "<p>Maintenance level requiring annual appointments. Cases that are stable and only need routine annual check-ins.</p>",
            "color_code": "gray"
        }
    ]
    
    # Create each priority record
    for priority in priorities:
        # Check if record already exists
        if not frappe.db.exists("Case Priority", {"priority_code": priority["priority_code"]}):
            doc = frappe.get_doc({
                "doctype": "Case Priority",
                "priority_code": priority["priority_code"],
                "priority_name": priority["priority_name"],
                "appointment_frequency_months": priority["appointment_frequency_months"],
                "description": priority["description"],
                "color_code": priority["color_code"]
            })
            doc.insert()
            print(f"Created Case Priority: {priority['priority_code']} - {priority['priority_name']}")
        else:
            print(f"Case Priority {priority['priority_code']} already exists")
    
    frappe.db.commit()
    print("Case Priority records created successfully")
