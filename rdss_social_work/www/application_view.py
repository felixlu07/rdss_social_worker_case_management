import frappe
from frappe import _

def get_context(context):
    context["title"] = "Application Details"
    context["show_error"] = False
    
    # Get application ID from URL
    application_id = frappe.form_dict.get('id')
    if not application_id:
        context["show_error"] = True
        context["error_message"] = "No application ID provided in URL"
        return context
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        context["show_error"] = True
        context["error_message"] = "Please log in to view application details"
        return context
    
    try:
        # Test if application exists first
        if not frappe.db.exists("Support Scheme Application", application_id):
            context["show_error"] = True
            context["error_message"] = f"Application {application_id} not found"
            return context
        
        # Get basic application data
        app_data = frappe.db.get_value("Support Scheme Application", application_id, 
            ["name", "beneficiary", "scheme_type", "application_date", "application_status"], 
            as_dict=True)
        
        if not app_data:
            context["show_error"] = True
            context["error_message"] = "Could not retrieve application data"
            return context
        
        # Test if beneficiary exists
        if not frappe.db.exists("Beneficiary", app_data.beneficiary):
            context["show_error"] = True
            context["error_message"] = f"Beneficiary {app_data.beneficiary} not found"
            return context
        
        # Get basic beneficiary data
        beneficiary_data = frappe.db.get_value("Beneficiary", app_data.beneficiary,
            ["name", "beneficiary_name", "email_address"], as_dict=True)
        
        if not beneficiary_data:
            context["show_error"] = True
            context["error_message"] = "Could not retrieve beneficiary data"
            return context
        
        # Simple permission check
        user_email = frappe.session.user
        if user_email != beneficiary_data.email_address and user_email != "Administrator":
            context["show_error"] = True
            context["error_message"] = f"Access denied. User: {user_email}, Beneficiary: {beneficiary_data.email_address}"
            return context
        
        # Success - set the data
        context["application"] = app_data
        context["beneficiary"] = beneficiary_data
        context["show_error"] = False
        
    except Exception as e:
        context["show_error"] = True
        context["error_message"] = f"Exception: {str(e)}"
        frappe.log_error(f"Application view error: {str(e)}", "Application View")
    
    return context
