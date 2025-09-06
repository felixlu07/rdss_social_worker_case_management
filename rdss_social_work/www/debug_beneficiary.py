import frappe
from frappe import _

def get_context(context):
    context.title = "Beneficiary Debug"
    context.debug_msg = "Context function is working"
    
    # Get current user info
    context.current_user = frappe.session.user
    context.is_guest = frappe.session.user == "Guest"
    
    if not context.is_guest:
        try:
            # Get user roles
            context.user_roles = frappe.get_roles(frappe.session.user)
            
            # Check if Beneficiary role exists
            context.beneficiary_role_exists = frappe.db.exists("Role", "Beneficiary")
            
            # Check if user has Beneficiary role
            context.has_beneficiary_role = frappe.db.exists("Has Role", {
                "parent": frappe.session.user,
                "role": "Beneficiary"
            })
            
            # Check beneficiary record with direct SQL query since get_value is failing
            beneficiary_data = frappe.db.sql("""
                SELECT name, beneficiary_name, email_address 
                FROM tabBeneficiary 
                WHERE email_address = %s
            """, (frappe.session.user,), as_dict=True)
            
            context.beneficiary_record = beneficiary_data[0] if beneficiary_data else None
            
            # Check permissions
            context.can_read_beneficiary = frappe.has_permission("Beneficiary", "read")
            context.can_read_application = frappe.has_permission("Support Scheme Application", "read")
            
            # Get role permissions
            try:
                context.beneficiary_perms = frappe.get_all("Custom DocPerm", 
                    filters={"parent": "Beneficiary", "role": "Beneficiary"},
                    fields=["read", "write", "create", "delete"])
            except:
                context.beneficiary_perms = []
            
            try:
                context.application_perms = frappe.get_all("Custom DocPerm", 
                    filters={"parent": "Support Scheme Application", "role": "Beneficiary"},
                    fields=["read", "write", "create", "delete"])
            except:
                context.application_perms = []
                
        except Exception as e:
            frappe.log_error(f"Error in debug context: {str(e)}")
            context.error = str(e)
    
    return context
