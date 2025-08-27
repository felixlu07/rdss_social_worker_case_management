import frappe
from .oauth_service import GoogleOAuthService


@frappe.whitelist()
def send_calendar_invite_oauth(event_name):
    """
    Send calendar invite using OAuth authentication (as yourself)
    """
    try:
        # Get event document
        event_doc = frappe.get_doc("Event", event_name)
        
        # Validate required fields
        if not event_doc.subject:
            frappe.throw("Event subject is required")
        
        if not event_doc.starts_on:
            frappe.throw("Event start time is required")
        
        if not event_doc.ends_on:
            frappe.throw("Event end time is required. Please set both start and end times in the Event form.")
        
        # Get attendees from custom Google Calendar attendees field
        attendees = []
        if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
            attendees = [
                email.strip() 
                for email in event_doc.custom_google_calendar_attendees.split(',') 
                if email.strip()
            ]
        
        if not attendees:
            frappe.throw("Please add email addresses in the Google Calendar Attendees field")
        
        # Prepare event data
        event_data = {
            'subject': event_doc.subject,
            'description': event_doc.description or '',
            'starts_on': event_doc.starts_on,
            'ends_on': event_doc.ends_on,
            'location': getattr(event_doc, 'location', ''),
            'attendees': ','.join(attendees)
        }
        
        # Initialize OAuth service
        oauth_service = GoogleOAuthService()
        
        # Check if authenticated
        if not oauth_service.is_authenticated():
            # Return auth URL for user to visit
            auth_url = oauth_service.get_authorization_url()
            return {
                'status': 'auth_required',
                'message': 'Google authorization required',
                'auth_url': auth_url
            }
        
        # Create calendar event with invites
        calendar_event_id = oauth_service.create_calendar_event(event_data)
        
        # Update ERPNext event with Google Calendar event ID
        event_doc.db_set('custom_google_calendar_event_id', calendar_event_id, update_modified=False)
        
        return {
            'status': 'success',
            'message': f'Calendar invite sent to {len(attendees)} attendees',
            'google_event_id': calendar_event_id
        }
        
    except Exception as e:
        error_msg = str(e)[:80]  # Limit error message length
        frappe.log_error(f"OAuth invite failed: {error_msg}")
        frappe.throw(f"Calendar invite failed: {error_msg}")
