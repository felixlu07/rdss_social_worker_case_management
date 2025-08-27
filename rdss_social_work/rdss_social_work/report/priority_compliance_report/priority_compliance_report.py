import frappe
from frappe import _
from frappe.utils import today, getdate, add_months

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"fieldname": "beneficiary", "label": _("Beneficiary"), "fieldtype": "Link", "options": "Beneficiary", "width": 180},
        {"fieldname": "case", "label": _("Case"), "fieldtype": "Link", "options": "Case", "width": 150},
        {"fieldname": "priority_code", "label": _("Priority"), "fieldtype": "Data", "width": 80},
        {"fieldname": "frequency", "label": _("Frequency (Months)"), "fieldtype": "Int", "width": 120},
        {"fieldname": "last_visit", "label": _("Last Appointment"), "fieldtype": "Date", "width": 110},
        {"fieldname": "next_visit", "label": _("Next Appointment"), "fieldtype": "Date", "width": 110},
        {"fieldname": "due_date", "label": _("Due By"), "fieldtype": "Date", "width": 110},
        {"fieldname": "days_overdue", "label": _("Days Overdue"), "fieldtype": "Int", "width": 100},
        {"fieldname": "status", "label": _("Compliance Status"), "fieldtype": "Data", "width": 150},
    ]

def get_data():
    today_date = getdate(today())

    # Fetch active cases with their appointment frequency
    cases = frappe.db.get_all(
        "Case",
        filters={"case_status": ["not in", ["Closed", "Transferred"]]},
        fields=["name", "beneficiary", "case_priority", "appointment_frequency"]
    )

    data = []
    for case in cases:
        frequency = case.appointment_frequency or 0

        last_visit = frappe.db.get_value(
            "Appointment",
            {
                "beneficiary": case.beneficiary,
                "appointment_date": ("<=", today_date),
                "appointment_status": ["not in", ["Cancelled", "No Show"]]
            },
            "max(appointment_date)"
        )

        next_visit = frappe.db.get_value(
            "Appointment",
            {
                "beneficiary": case.beneficiary,
                "appointment_date": (">", today_date),
                "appointment_status": ["not in", ["Cancelled", "No Show"]]
            },
            "min(appointment_date)"
        )

        # Compute due date based on last_visit & frequency
        due_date = None
        days_overdue = 0
        status = "Compliant"
        if frequency and last_visit:
            due_date = add_months(getdate(last_visit), frequency)
            if today_date > due_date:
                status = "Overdue"
                days_overdue = (today_date - getdate(due_date)).days
        elif frequency:
            # No past appointment found
            status = "Overdue"
            days_overdue = 9999  # signifies missing entirely

        # If there is a future appointment within frequency window, mark compliant
        if next_visit and frequency:
            if getdate(next_visit) <= add_months(today_date, frequency):
                status = "Scheduled"
                days_overdue = 0

        data.append({
            "beneficiary": case.beneficiary,
            "case": case.name,
            "priority_code": case.case_priority,
            "frequency": frequency,
            "last_visit": last_visit,
            "next_visit": next_visit,
            "due_date": due_date,
            "days_overdue": days_overdue,
            "status": status,
        })

    # Sort: Overdue first by days_overdue desc, then Scheduled, then Compliant
    def sort_key(d):
        if d["status"] == "Overdue":
            return (0, -d["days_overdue"])
        elif d["status"] == "Scheduled":
            return (1, 0)
        return (2, 0)

    data.sort(key=sort_key)
    return data
