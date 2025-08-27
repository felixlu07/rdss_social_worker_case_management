import frappe
from rdss_social_work.rdss_social_work.google_calendar.oauth_service import GoogleOAuthService

@frappe.whitelist(allow_guest=True)
def oauth_callback():
    """Handle Google OAuth callback"""
    code = frappe.form_dict.get('code')
    state = frappe.form_dict.get('state')
    
    if not code:
        frappe.throw("Authorization code not received")
    
    oauth_service = GoogleOAuthService()
    result = oauth_service.handle_oauth_callback(code, state)
    
    # Redirect to a success page or return success message
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/app/event"
    
    return result
