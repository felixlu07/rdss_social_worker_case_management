import frappe
from .calendar_service import GoogleCalendarService


@frappe.whitelist()
def test_google_calendar_connection():
    """
    Test function to verify Google Calendar API connection
    """
    try:
        # Initialize the service
        calendar_service = GoogleCalendarService()
        
        # Try to list calendars to test connection
        calendars_result = calendar_service.calendar_service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        primary_calendar = None
        for calendar in calendars:
            if calendar.get('primary'):
                primary_calendar = calendar
                break
        
        if primary_calendar:
            return {
                'status': 'success',
                'message': f'Successfully connected to Google Calendar',
                'calendar_name': primary_calendar.get('summary', 'Primary Calendar'),
                'calendar_id': primary_calendar.get('id')
            }
        else:
            return {
                'status': 'error',
                'message': 'No primary calendar found'
            }
            
    except Exception as e:
        frappe.log_error(f"Google Calendar connection test failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }
