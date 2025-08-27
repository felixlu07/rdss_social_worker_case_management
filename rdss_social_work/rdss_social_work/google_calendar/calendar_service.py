import frappe
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class GoogleCalendarService:
    def __init__(self):
        self.calendar_service = None
        self.gmail_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google Calendar and Gmail services using service account credentials"""
        try:
            # Get credentials from site config
            service_account_json = frappe.conf.get('google_service_account_json')
            if not service_account_json:
                frappe.throw("Google service account credentials not configured in site config")
            
            # Parse credentials
            if isinstance(service_account_json, str):
                # If it's a file path
                if service_account_json.endswith('.json'):
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_json,
                        scopes=[
                            'https://www.googleapis.com/auth/calendar',
                            'https://www.googleapis.com/auth/gmail.send'
                        ]
                    )
                else:
                    # If it's JSON string
                    service_account_info = json.loads(service_account_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        service_account_info,
                        scopes=[
                            'https://www.googleapis.com/auth/calendar',
                            'https://www.googleapis.com/auth/gmail.send'
                        ]
                    )
            
            # Build Calendar service only (Gmail sending will be handled differently)
            self.calendar_service = build('calendar', 'v3', credentials=credentials)
            self.gmail_service = None  # Will use SMTP instead
            
        except Exception as e:
            frappe.log_error(f"Failed to initialize Google services: {str(e)}")
            frappe.throw(f"Google Calendar service initialization failed: {str(e)}")
    
    def create_calendar_event(self, event_data):
        """Create a calendar event and return event ID"""
        try:
            # Convert ERPNext event to Google Calendar format
            calendar_event = {
                'summary': event_data.get('subject'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': self._format_datetime(event_data.get('starts_on')),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': self._format_datetime(event_data.get('ends_on')),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': email.strip()} 
                    for email in event_data.get('attendees', '').split(',') 
                    if email.strip()
                ],
                'location': event_data.get('location', ''),
            }
            
            # Create event without sendUpdates to avoid service account restrictions
            sender_email = frappe.conf.get('google_sender_email')
            calendar_id = sender_email if sender_email else 'primary'
            
            event = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=calendar_event
                # Note: sendUpdates removed - service accounts can't send invites without domain delegation
            ).execute()
            
            return event.get('id')
            
        except Exception as e:
            frappe.log_error(f"Failed to create calendar event: {str(e)}")
            frappe.throw(f"Failed to create calendar event: {str(e)}")
    
    def _format_datetime(self, dt):
        """Format datetime for Google Calendar API"""
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        elif not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.isoformat()
    
    def send_calendar_invite_email(self, event_data, calendar_event_id):
        """Send calendar invite via Gmail (alternative method)"""
        try:
            sender_email = frappe.conf.get('google_sender_email')
            if not sender_email:
                frappe.throw("Google sender email not configured in site config")
            
            attendees = [
                email.strip() 
                for email in event_data.get('attendees', '').split(',') 
                if email.strip()
            ]
            
            for attendee_email in attendees:
                # Create email with calendar invite
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = attendee_email
                msg['Subject'] = f"Calendar Invite: {event_data.get('subject')}"
                
                # Email body
                body = f"""
                You're invited to: {event_data.get('subject')}
                
                When: {event_data.get('starts_on')} - {event_data.get('ends_on')}
                Where: {event_data.get('location', 'Not specified')}
                
                Description:
                {event_data.get('description', '')}
                
                Google Calendar Event ID: {calendar_event_id}
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Send via Gmail API
                raw_message = {'raw': msg.as_string().encode('utf-8')}
                self.gmail_service.users().messages().send(
                    userId='me',
                    body=raw_message
                ).execute()
            
            return True
            
        except Exception as e:
            frappe.log_error(f"Failed to send calendar invite emails: {str(e)}")
            return False
    
    def update_calendar_event(self, event_id, event_data):
        """Update existing calendar event"""
        try:
            # Get existing event
            existing_event = self.calendar_service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update event data
            existing_event.update({
                'summary': event_data.get('subject'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': self._format_datetime(event_data.get('starts_on')),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': self._format_datetime(event_data.get('ends_on')),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': email.strip()} 
                    for email in event_data.get('attendees', '').split(',') 
                    if email.strip()
                ],
                'location': event_data.get('location', ''),
            })
            
            # Update event without sendUpdates
            sender_email = frappe.conf.get('google_sender_email')
            calendar_id = sender_email if sender_email else 'primary'
            
            updated_event = self.calendar_service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            return updated_event
            
        except Exception as e:
            frappe.log_error(f"Failed to update calendar event: {str(e)}")
            frappe.throw(f"Failed to update calendar event: {str(e)}")
    
    def delete_calendar_event(self, event_id):
        """Delete calendar event"""
        try:
            sender_email = frappe.conf.get('google_sender_email')
            calendar_id = sender_email if sender_email else 'primary'
            
            self.calendar_service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return True
            
        except Exception as e:
            frappe.log_error(f"Failed to delete calendar event: {str(e)}")
            frappe.throw(f"Failed to delete calendar event: {str(e)}")
