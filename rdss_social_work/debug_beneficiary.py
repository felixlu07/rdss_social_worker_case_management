import frappe

def debug_beneficiary_access():
    """Debug beneficiary access issues"""
    print("=== Beneficiary Access Debug ===")
    
    # Check current user
    print(f"Current user: {frappe.session.user}")
    
    # Check user roles
    if frappe.session.user != "Guest":
        user_roles = frappe.get_roles(frappe.session.user)
        print(f"User roles: {user_roles}")
        
        # Check if Beneficiary role exists
        beneficiary_role = frappe.db.exists("Role", "Beneficiary")
        print(f"Beneficiary role exists: {beneficiary_role}")
        
        # Check if user has Beneficiary role
        has_beneficiary_role = frappe.db.exists("Has Role", {
            "parent": frappe.session.user,
            "role": "Beneficiary"
        })
        print(f"User has Beneficiary role: {has_beneficiary_role}")
        
        # Check beneficiary record
        beneficiary = frappe.db.get_value("Beneficiary", 
            {"email_address": frappe.session.user}, 
            ["name", "beneficiary_name"], as_dict=True)
        print(f"Beneficiary record: {beneficiary}")
        
        # Check permissions
        can_read_beneficiary = frappe.has_permission("Beneficiary", "read")
        can_read_application = frappe.has_permission("Support Scheme Application", "read")
        print(f"Can read Beneficiary: {can_read_beneficiary}")
        print(f"Can read Support Scheme Application: {can_read_application}")
        
        # Check role permissions for Beneficiary doctype
        role_permissions = frappe.get_all("Custom DocPerm", 
            filters={"parent": "Beneficiary", "role": "Beneficiary"},
            fields=["read", "write", "create", "delete"])
        print(f"Beneficiary role permissions on Beneficiary doctype: {role_permissions}")
        
        # Check role permissions for Support Scheme Application doctype
        app_permissions = frappe.get_all("Custom DocPerm", 
            filters={"parent": "Support Scheme Application", "role": "Beneficiary"},
            fields=["read", "write", "create", "delete"])
        print(f"Beneficiary role permissions on Support Scheme Application: {app_permissions}")
    
    print("=== End Debug ===")

if __name__ == "__main__":
    debug_beneficiary_access()
