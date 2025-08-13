import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now_datetime
import json

@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard data for social worker"""
    user = frappe.session.user
    
    # Get today's appointments
    today_appointments = frappe.get_all("Appointment", 
        filters={
            "social_worker": user,
            "appointment_date": today(),
            "appointment_status": ["in", ["Scheduled", "Confirmed"]]
        },
        fields=["name", "appointment_time", "beneficiary", "appointment_type", "purpose"],
        order_by="appointment_time"
    )
    
    # Get pending tasks (overdue assessments, follow-ups)
    pending_tasks = []
    
    # Overdue follow-up assessments
    overdue_followups = frappe.get_all("Follow Up Assessment",
        filters={
            "social_worker": user,
            "assessment_date": ["<", today()],
            "docstatus": 0
        },
        fields=["name", "case", "beneficiary", "assessment_date"],
        limit=10
    )
    
    for task in overdue_followups:
        pending_tasks.append({
            "type": "Follow-up Assessment",
            "name": task.name,
            "case": task.case,
            "beneficiary": task.beneficiary,
            "due_date": task.assessment_date,
            "priority": "High"
        })
    
    # Upcoming appointments (next 7 days)
    upcoming_appointments = frappe.get_all("Appointment",
        filters={
            "social_worker": user,
            "appointment_date": ["between", [today(), add_days(today(), 7)]],
            "appointment_status": ["in", ["Scheduled", "Confirmed"]]
        },
        fields=["name", "appointment_date", "appointment_time", "beneficiary", "appointment_type"],
        order_by="appointment_date, appointment_time",
        limit=10
    )
    
    # Case alerts (urgent cases, approaching deadlines)
    case_alerts = frappe.get_all("Case",
        filters={
            "social_worker": user,
            "case_status": ["in", ["Active", "Under Review"]],
            "priority": ["in", ["High", "Critical"]]
        },
        fields=["name", "beneficiary", "priority", "case_status", "creation"],
        limit=5
    )
    
    # Quick stats
    stats = {
        "active_cases": frappe.db.count("Case", {"social_worker": user, "case_status": "Active"}),
        "today_appointments": len(today_appointments),
        "pending_tasks": len(pending_tasks),
        "this_month_visits": frappe.db.count("Case Notes", {
            "social_worker": user,
            "visit_date": [">=", getdate(today()).replace(day=1)]
        })
    }
    
    # Recent activity
    recent_notes = frappe.get_all("Case Notes",
        filters={"social_worker": user},
        fields=["name", "case", "beneficiary", "visit_date", "visit_type"],
        order_by="creation desc",
        limit=5
    )
    
    return {
        "today_appointments": today_appointments,
        "pending_tasks": pending_tasks,
        "upcoming_appointments": upcoming_appointments,
        "case_alerts": case_alerts,
        "stats": stats,
        "recent_activity": recent_notes
    }

@frappe.whitelist()
def mark_task_complete(task_type, task_name):
    """Mark a task as complete"""
    try:
        if task_type == "Follow-up Assessment":
            doc = frappe.get_doc("Follow Up Assessment", task_name)
            doc.submit()
            return {"success": True, "message": "Task marked as complete"}
    except Exception as e:
        return {"success": False, "message": str(e)}
