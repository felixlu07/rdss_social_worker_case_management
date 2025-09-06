import frappe

def get_permission_query_conditions(user):
    """Permission query conditions for beneficiary data isolation"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if user in ["Administrator"] or "System Manager" in frappe.get_roles(user):
        return ""
    
    # Social Workers, Head of Admin, and RDSS Director have full access
    user_roles = frappe.get_roles(user)
    if any(role in user_roles for role in ["Social Worker", "Head of Admin", "RDSS Director"]):
        return ""
    
    # Beneficiaries can only see their own records
    if "Beneficiary" in user_roles:
        beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user}, "name")
        if beneficiary:
            return f"`tabSupport Scheme Application`.beneficiary = '{beneficiary}'"
    
    # Default: no access
    return "1=0"

def has_permission(doc, user):
    """Check if user has permission to access document"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if user in ["Administrator"] or "System Manager" in frappe.get_roles(user):
        return True
    
    # Social Workers, Head of Admin, and RDSS Director have full access
    user_roles = frappe.get_roles(user)
    if any(role in user_roles for role in ["Social Worker", "Head of Admin", "RDSS Director"]):
        return True
    
    # Beneficiaries can only access their own records
    if "Beneficiary" in user_roles:
        if doc.doctype == "Support Scheme Application":
            beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user}, "name")
            return doc.beneficiary == beneficiary
        elif doc.doctype == "Beneficiary":
            return doc.email_address == user
        elif doc.doctype in ["Medical Intervention Scheme"]:
            beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user}, "name")
            return doc.beneficiary == beneficiary
    
    return False
