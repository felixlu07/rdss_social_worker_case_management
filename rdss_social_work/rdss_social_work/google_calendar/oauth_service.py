import frappe
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class GoogleOAuthService:
    def __init__(self):
        self.calendar_service = None
        self.scopes = [
            'https://www.googleapis.com/auth/calendar'
        ]
        self._initialize_services()
    
    def _get_credentials_path(self):
        """Get path to store OAuth credentials in the site's private directory
        to prevent committing tokens into the app repository."""
        return frappe.get_site_path("private", "google_oauth_tokens.json")
    
    def _get_client_config(self):
        """Get OAuth client configuration"""
        # You'll need to create OAuth 2.0 credentials in Google Cloud Console
        return {
            "web": {
                "client_id": frappe.conf.get('google_oauth_client_id'),
                "client_secret": frappe.conf.get('google_oauth_client_secret'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"https://erp.rdss.org.sg/api/method/rdss_social_work.rdss_social_work.api.oauth_callback"]
            }
        }
    
    def _initialize_services(self):
        """Initialize Google services using OAuth credentials"""
        try:
            credentials = self._get_valid_credentials()
            if credentials:
                self.calendar_service = build('calendar', 'v3', credentials=credentials)
                self.gmail_service = build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            # Avoid noisy Error Logs if creds are missing/invalid; initialization can happen after auth
            try:
                frappe.logger().info(f"OAuth services not initialized yet: {str(e)}")
            except Exception:
                pass
    
    def _get_valid_credentials(self):
        """Get valid OAuth credentials, refresh if needed"""
        creds_path = self._get_credentials_path()
        creds = None
        
        # Load existing credentials
        if os.path.exists(creds_path):
            try:
                creds = Credentials.from_authorized_user_file(creds_path, self.scopes)
            except Exception as e:
                # Token file exists but is invalid (e.g., missing refresh_token)
                # Log as a warning (not an error) to avoid noisy Error Logs; this is expected when re-auth is needed
                try:
                    frappe.logger().warning(f"Invalid OAuth token file at {creds_path}: {str(e)}")
                except Exception:
                    pass
                try:
                    os.remove(creds_path)
                except Exception:
                    pass
                creds = None
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(creds_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds if creds and creds.valid else None
    
    def get_authorization_url(self):
        """Get OAuth authorization URL for user to visit"""
        client_config = self._get_client_config()
        if not client_config["web"]["client_id"]:
            frappe.throw("Google OAuth client ID not configured")
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=client_config["web"]["redirect_uris"][0]
        )
        
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store flow state for callback
        frappe.cache().set_value("google_oauth_flow_state", state, expires_in_sec=600)
        
        return auth_url
    
    def handle_oauth_callback(self, code, state):
        """Handle OAuth callback and store credentials"""
        try:
            # Verify state
            stored_state = frappe.cache().get_value("google_oauth_flow_state")
            if state != stored_state:
                frappe.throw("Invalid OAuth state")
            
            client_config = self._get_client_config()
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=client_config["web"]["redirect_uris"][0],
                state=state
            )
            
            # Exchange code for credentials
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Save credentials
            creds_path = self._get_credentials_path()
            os.makedirs(os.path.dirname(creds_path), exist_ok=True)
            with open(creds_path, 'w') as token:
                token.write(creds.to_json())
            
            # Initialize services
            self._initialize_services()
            
            return True
            
        except Exception as e:
            frappe.log_error(f"OAuth callback failed: {str(e)}")
            return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self._get_valid_credentials() is not None
    
    def create_calendar_event(self, event_data):
        """Create calendar event with OAuth credentials"""
        if not self.is_authenticated():
            frappe.throw("Google OAuth authentication required")
        
        try:
            # Validate and clean data
            subject = event_data.get('subject', '')[:100]  # Limit title length
            description = event_data.get('description', '')[:1000]  # Limit description
            location = event_data.get('location', '')[:100]  # Limit location
            
            # Validate start/end times
            start_time = event_data.get('starts_on')
            end_time = event_data.get('ends_on')
            
            if end_time <= start_time:
                frappe.throw("Event end time must be after start time")
            
            # Convert ERPNext event to Google Calendar format
            calendar_event = {
                'summary': subject,
                'description': description,
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
                'location': location,
            }
            
            # Create event with sendUpdates to send invites
            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=calendar_event,
                sendUpdates='all'  # This works with OAuth
            ).execute()
            
            return event.get('id')
            
        except Exception as e:
            frappe.throw(f"Calendar creation failed: {str(e)}")

    def update_calendar_event(self, event_id, event_data):
        """Update an existing calendar event using OAuth credentials"""
        if not self.is_authenticated():
            frappe.throw("Google OAuth authentication required")

        try:
            # Prepare body similar to create
            subject = event_data.get('subject', '')[:100]
            description = event_data.get('description', '')[:1000]
            location = event_data.get('location', '')[:100]

            calendar_event = {
                'summary': subject,
                'description': description,
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
                'location': location,
            }

            updated = self.calendar_service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=calendar_event,
                sendUpdates='all'
            ).execute()

            return updated.get('id')

        except Exception as e:
            frappe.throw(f"Calendar update failed: {str(e)}")

    def delete_calendar_event(self, event_id):
        """Delete an existing calendar event using OAuth credentials"""
        if not self.is_authenticated():
            frappe.throw("Google OAuth authentication required")

        try:
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            return True
        except Exception as e:
            frappe.throw(f"Calendar deletion failed: {str(e)}")
    
    def _format_datetime(self, dt):
        """Format datetime for Google Calendar API"""
        from datetime import datetime, timezone
        
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        elif not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.isoformat()


@frappe.whitelist(allow_guest=True)
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        code = frappe.form_dict.get('code')
        state = frappe.form_dict.get('state')
        
        if not code:
            frappe.throw("No authorization code received")
        
        oauth_service = GoogleOAuthService()
        success = oauth_service.handle_oauth_callback(code, state)
        
        if success:
            return """
            <html>
                <body>
                    <h2>✅ Google Calendar Authorization Successful!</h2>
                    <p>You can now close this window and return to ERPNext.</p>
                    <script>window.close();</script>
                </body>
            </html>
            """
        else:
            frappe.throw("OAuth authorization failed")
            
    except Exception as e:
        frappe.log_error(f"OAuth callback error: {str(e)}")
        return f"""
        <html>
            <body>
                <h2>❌ Authorization Failed</h2>
                <p>Error: {str(e)}</p>
            </body>
        </html>
        """


@frappe.whitelist()
def get_oauth_status():
    """Check OAuth authentication status"""
    oauth_service = GoogleOAuthService()
    return {
        'authenticated': oauth_service.is_authenticated()
    }


@frappe.whitelist()
def start_oauth_flow():
    """Start OAuth authorization flow"""
    try:
        oauth_service = GoogleOAuthService()
        auth_url = oauth_service.get_authorization_url()
        return {
            'status': 'success',
            'auth_url': auth_url
        }
    except Exception as e:
        frappe.log_error(f"OAuth flow start failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
