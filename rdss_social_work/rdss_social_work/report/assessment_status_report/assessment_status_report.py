import frappe
from frappe import _
from frappe.utils import today, add_days, getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "assessment_type",
            "label": _("Assessment Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "case",
            "label": _("Case"),
            "fieldtype": "Link",
            "options": "Case",
            "width": 120
        },
        {
            "fieldname": "beneficiary",
            "label": _("Beneficiary"),
            "fieldtype": "Link",
            "options": "Beneficiary",
            "width": 150
        },
        {
            "fieldname": "social_worker",
            "label": _("Social Worker"),
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "fieldname": "due_date",
            "label": _("Due Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "days_overdue",
            "label": _("Days Overdue"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "priority",
            "label": _("Priority"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    data = []
    
    # Get pending Initial Assessments
    initial_assessments = frappe.get_all("Initial Assessment",
        filters={"docstatus": 0},
        fields=["name", "case", "beneficiary", "social_worker", "assessment_date", "priority"]
    )
    
    for assessment in initial_assessments:
        days_overdue = 0
        if assessment.assessment_date and getdate(assessment.assessment_date) < getdate(today()):
            days_overdue = (getdate(today()) - getdate(assessment.assessment_date)).days
            
        data.append({
            "assessment_type": "Initial Assessment",
            "case": assessment.case,
            "beneficiary": assessment.beneficiary,
            "social_worker": assessment.social_worker,
            "due_date": assessment.assessment_date,
            "status": "Overdue" if days_overdue > 0 else "Pending",
            "days_overdue": days_overdue if days_overdue > 0 else 0,
            "priority": assessment.priority or "Medium"
        })
    
    # Get pending Follow-up Assessments
    followup_assessments = frappe.get_all("Follow Up Assessment",
        filters={"docstatus": 0},
        fields=["name", "case", "beneficiary", "social_worker", "assessment_date", "priority"]
    )
    
    for assessment in followup_assessments:
        days_overdue = 0
        if assessment.assessment_date and getdate(assessment.assessment_date) < getdate(today()):
            days_overdue = (getdate(today()) - getdate(assessment.assessment_date)).days
            
        data.append({
            "assessment_type": "Follow-up Assessment",
            "case": assessment.case,
            "beneficiary": assessment.beneficiary,
            "social_worker": assessment.social_worker,
            "due_date": assessment.assessment_date,
            "status": "Overdue" if days_overdue > 0 else "Pending",
            "days_overdue": days_overdue if days_overdue > 0 else 0,
            "priority": assessment.priority or "Medium"
        })
    
    # Sort by days overdue (descending) and then by due date
    data.sort(key=lambda x: (-x["days_overdue"], x["due_date"] or ""))
    
    return data
