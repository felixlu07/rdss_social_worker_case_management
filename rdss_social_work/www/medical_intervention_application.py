import frappe
from frappe import _

def get_context(context):
    context.title = "Medical Intervention Application"
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        context.show_access_issue = True
        context.access_message = "Please log in to access this page."
        return context
    
    # Check if user has Beneficiary role
    user_roles = frappe.get_roles(frappe.session.user)
    if "Beneficiary" not in user_roles:
        context.show_access_issue = True
        context.access_message = "Access denied. You need Beneficiary role to access this page."
        return context
    
    try:
        # Get beneficiary record using direct SQL query
        beneficiary_data = frappe.db.sql("""
            SELECT name, beneficiary_name, email_address 
            FROM tabBeneficiary 
            WHERE email_address = %s
        """, (frappe.session.user,), as_dict=True)
        
        if not beneficiary_data:
            context.show_access_issue = True
            context.access_message = "No beneficiary record found for your account. Please contact support."
            return context
        
        context.beneficiary = beneficiary_data[0]
        
        # Check for existing Medical Intervention applications
        existing_applications = frappe.get_all("Support Scheme Application",
            filters={
                "beneficiary": context.beneficiary["name"],
                "scheme_type": "Medical Intervention Scheme (MIS)"
            },
            fields=["name", "application_date", "application_status", "approved_amount"],
            order_by="creation desc"
        )
        
        # Check if there's already an active application
        active_application = None
        for app in existing_applications:
            if app.application_status in ["Draft", "Submitted", "Under Admin Review", "Under Director Review", "Approved"]:
                active_application = app
                break
        
        if active_application:
            context.show_form = False
            context.show_access_issue = True
            context.existing_application = active_application
            if active_application.application_status == "Approved":
                context.access_message = f"You already have an approved Medical Intervention application (Status: {active_application.application_status}). Only one application per scheme is allowed."
            else:
                context.access_message = f"You already have a pending Medical Intervention application (Status: {active_application.application_status}). Please wait for it to be processed or cancel it to submit a new one."
        else:
            context.show_form = True
            context.show_access_issue = False
        
        context.existing_applications = existing_applications
        
    except Exception as e:
        frappe.log_error(f"Error in medical intervention context: {str(e)}")
        context.show_form = False
        context.show_access_issue = True
        context.access_message = f"An error occurred: {str(e)}"
        context.beneficiary = None
        context.existing_applications = []
    
    return context
