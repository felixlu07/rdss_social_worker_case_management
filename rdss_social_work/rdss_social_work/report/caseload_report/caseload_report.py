import frappe
from frappe import _
from frappe.utils import today, add_months, getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "primary_social_worker",
            "label": _("Social Worker"),
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "fieldname": "active_cases",
            "label": _("Active Cases"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "new_cases_this_month",
            "label": _("New Cases (This Month)"),
            "fieldtype": "Int", 
            "width": 150
        },
        {
            "fieldname": "closed_cases_this_month",
            "label": _("Closed Cases (This Month)"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "pending_assessments",
            "label": _("Pending Assessments"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "overdue_followups",
            "label": _("Overdue Follow-ups"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "appointments_this_week",
            "label": _("Appointments (This Week)"),
            "fieldtype": "Int",
            "width": 150
        }
    ]

def get_data(filters):
    data = []
    
    # Get all social workers
    social_workers = frappe.get_all("User", 
        filters={"role_profile_name": ["like", "%Social Worker%"]},
        fields=["name", "full_name"]
    )
    
    if not social_workers:
        # Fallback: get users who have cases assigned
        social_workers = frappe.db.sql("""
            SELECT DISTINCT primary_social_worker as name, primary_social_worker as full_name
            FROM `tabCase` 
            WHERE primary_social_worker IS NOT NULL
        """, as_dict=True)
    
    month_start = getdate(today()).replace(day=1)
    week_start = add_months(today(), 0, as_date=True)  # This week
    
    for worker in social_workers:
        if not worker.name:
            continue
            
        # Active cases
        active_cases = frappe.db.count("Case", {
            "primary_social_worker": worker.name,
            "case_status": "Active"
        })
        
        # New cases this month
        new_cases = frappe.db.count("Case", {
            "primary_social_worker": worker.name,
            "creation": [">=", month_start]
        })
        
        # Closed cases this month
        closed_cases = frappe.db.count("Case", {
            "primary_social_worker": worker.name,
            "case_status": "Closed",
            "modified": [">=", month_start]
        })
        
        # Pending initial assessments
        pending_assessments = frappe.db.count("Initial Assessment", {
            "assessed_by": worker.name,
            "docstatus": 0
        })
        
        # Overdue follow-ups
        overdue_followups = frappe.db.count("Follow Up Assessment", {
            "assessed_by": worker.name,
            "assessment_date": ["<", today()],
            "docstatus": 0
        })
        
        # Appointments this week
        appointments_week = frappe.db.count("Appointment", {
            "primary_social_worker": worker.name,
            "appointment_date": [">=", week_start],
            "appointment_status": ["in", ["Scheduled", "Confirmed"]]
        })
        
        if active_cases > 0 or new_cases > 0 or appointments_week > 0:
            data.append({
                "primary_social_worker": worker.name,
                "active_cases": active_cases,
                "new_cases_this_month": new_cases,
                "closed_cases_this_month": closed_cases,
                "pending_assessments": pending_assessments,
                "overdue_followups": overdue_followups,
                "appointments_this_week": appointments_week
            })
    
    return data
