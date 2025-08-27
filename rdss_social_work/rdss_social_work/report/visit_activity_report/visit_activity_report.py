import frappe
from frappe import _
from frappe.utils import today, add_months, getdate, formatdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "social_worker",
            "label": _("Social Worker"),
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "fieldname": "visit_date",
            "label": _("Visit Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "beneficiary",
            "label": _("Beneficiary"),
            "fieldtype": "Link",
            "options": "Beneficiary",
            "width": 150
        },
        {
            "fieldname": "visit_type",
            "label": _("Visit Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "visit_purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "visit_duration",
            "label": _("Duration"),
            "fieldtype": "Duration",
            "width": 120
        },
        {
            "fieldname": "case_link",
            "label": _("Case"),
            "fieldtype": "Link",
            "options": "Case",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = []
    values = []
    
    if filters.get("social_worker"):
        conditions.append("cn.social_worker = %s")
        values.append(filters.get("social_worker"))
    
    if filters.get("from_date"):
        conditions.append("cn.visit_date >= %s")
        values.append(filters.get("from_date"))
        
    if filters.get("to_date"):
        conditions.append("cn.visit_date <= %s")
        values.append(filters.get("to_date"))
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    query = f"""
        SELECT 
            cn.social_worker,
            cn.visit_date,
            cn.beneficiary,
            cn.visit_type,
            cn.visit_purpose,
            cn.visit_duration,
            cn.case as case_link
        FROM `tabCase Notes` cn
        {where_clause}
        ORDER BY cn.visit_date DESC, cn.social_worker
    """
    
    data = frappe.db.sql(query, values, as_dict=True)
    return data
