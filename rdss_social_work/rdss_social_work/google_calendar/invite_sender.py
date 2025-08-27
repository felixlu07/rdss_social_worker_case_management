import frappe
from .calendar_service import GoogleCalendarService


@frappe.whitelist()
def send_calendar_invite(event_name):
    """
    Main method to send calendar invite for an ERPNext Event
    Called from custom button on Event doctype
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
            frappe.throw("Event end time is required")
        
        # Get attendees from custom Google Calendar attendees field
        attendees = []
        if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
            # Split by comma and clean up emails
            attendees = [
                email.strip() 
                for email in event_doc.custom_google_calendar_attendees.split(',') 
                if email.strip()
            ]
        
        # Prepare event data
        event_data = {
            'subject': event_doc.subject,
            'description': event_doc.description or '',
            'starts_on': event_doc.starts_on,
            'ends_on': event_doc.ends_on,
            'location': getattr(event_doc, 'location', ''),
            'attendees': ','.join(attendees)
        }
        
        # Initialize Google Calendar service
        calendar_service = GoogleCalendarService()
        
        # Create calendar event (this automatically sends invites)
        calendar_event_id = calendar_service.create_calendar_event(event_data)
        
        # Update ERPNext event with Google Calendar event ID
        event_doc.db_set('custom_google_calendar_event_id', calendar_event_id, update_modified=False)
        
        # Log success
        frappe.msgprint(
            f"Calendar invite sent successfully to {len(attendees)} attendees. "
            f"Google Calendar Event ID: {calendar_event_id}",
            title="Success"
        )
        
        return {
            'status': 'success',
            'message': f'Calendar invite sent to {len(attendees)} attendees',
            'google_event_id': calendar_event_id
        }
        
    except Exception as e:
        frappe.log_error(f"Calendar invite sending failed: {str(e)}")
        frappe.throw(f"Failed to send calendar invite: {str(e)}")


@frappe.whitelist()
def update_calendar_event(event_name):
    """
    Update existing Google Calendar event when ERPNext event is modified
    """
    try:
        event_doc = frappe.get_doc("Event", event_name)
        
        # Check if Google Calendar event ID exists
        google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
        if not google_event_id:
            frappe.throw("No Google Calendar event found for this ERPNext event")
        
        # Get attendees from custom Google Calendar attendees field
        attendees = []
        if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
            # Split by comma and clean up emails
            attendees = [
                email.strip() 
                for email in event_doc.custom_google_calendar_attendees.split(',') 
                if email.strip()
            ]
        
        # Prepare updated event data
        event_data = {
            'subject': event_doc.subject,
            'description': event_doc.description or '',
            'starts_on': event_doc.starts_on,
            'ends_on': event_doc.ends_on,
            'location': getattr(event_doc, 'location', ''),
            'attendees': ','.join(attendees)
        }
        
        # Initialize Google Calendar service
        calendar_service = GoogleCalendarService()
        
        # Update the existing calendar event
        updated_event = calendar_service.update_calendar_event(google_event_id, event_data)
        
        frappe.msgprint(
            f"Google Calendar event updated successfully for {len(attendees)} attendees.",
            title="Success"
        )
        
        return {
            'status': 'success',
            'message': f'Calendar event updated for {len(attendees)} attendees'
        }
        
    except Exception as e:
        frappe.log_error(f"Calendar event update failed: {str(e)}")
        frappe.throw(f"Failed to update calendar event: {str(e)}")


@frappe.whitelist()
def delete_calendar_event(event_name):
    """
    Delete Google Calendar event when ERPNext event is deleted
    """
    try:
        event_doc = frappe.get_doc("Event", event_name)
        
        # Check if Google Calendar event ID exists
        google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
        if not google_event_id:
            return {'status': 'success', 'message': 'No Google Calendar event to delete'}
        
        # Initialize Google Calendar service
        calendar_service = GoogleCalendarService()
        
        # Delete the calendar event
        calendar_service.delete_calendar_event(google_event_id)
        
        frappe.msgprint("Google Calendar event deleted successfully.", title="Success")
        
        return {
            'status': 'success',
            'message': 'Calendar event deleted successfully'
        }
        
    except Exception as e:
        frappe.log_error(f"Calendar event deletion failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to delete calendar event: {str(e)}'
        }
