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


@frappe.whitelist()
def update_calendar_event_oauth(event_name):
    """
    Update an existing Google Calendar event using OAuth
    """
    try:
        event_doc = frappe.get_doc("Event", event_name)

        google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
        if not google_event_id:
            frappe.throw("No Google Calendar event found for this ERPNext event")

        attendees = []
        if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
            attendees = [email.strip() for email in event_doc.custom_google_calendar_attendees.split(',') if email.strip()]

        event_data = {
            'subject': event_doc.subject,
            'description': event_doc.description or '',
            'starts_on': event_doc.starts_on,
            'ends_on': event_doc.ends_on,
            'location': getattr(event_doc, 'location', ''),
            'attendees': ','.join(attendees)
        }

        oauth_service = GoogleOAuthService()

        if not oauth_service.is_authenticated():
            auth_url = oauth_service.get_authorization_url()
            return {
                'status': 'auth_required',
                'message': 'Google authorization required',
                'auth_url': auth_url
            }

        oauth_service.update_calendar_event(google_event_id, event_data)

        return {
            'status': 'success',
            'message': f'Calendar event updated for {len(attendees)} attendees'
        }

    except Exception as e:
        error_msg = str(e)[:80]
        frappe.log_error(f"OAuth update failed: {error_msg}")
        frappe.throw(f"Calendar event update failed: {error_msg}")


@frappe.whitelist()
def delete_calendar_event_oauth(event_name):
    """
    Delete an existing Google Calendar event using OAuth
    """
    try:
        event_doc = frappe.get_doc("Event", event_name)

        google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
        if not google_event_id:
            return {'status': 'success', 'message': 'No Google Calendar event to delete'}

        oauth_service = GoogleOAuthService()

        if not oauth_service.is_authenticated():
            auth_url = oauth_service.get_authorization_url()
            return {
                'status': 'auth_required',
                'message': 'Google authorization required',
                'auth_url': auth_url
            }

        oauth_service.delete_calendar_event(google_event_id)

        return {
            'status': 'success',
            'message': 'Calendar event deleted successfully'
        }

    except Exception as e:
        error_msg = str(e)[:80]
        frappe.log_error(f"OAuth deletion failed: {error_msg}")
        return {
            'status': 'error',
            'message': f'Failed to delete calendar event: {error_msg}'
        }


@frappe.whitelist()
def send_mass_calendar_invites_oauth(event_names):
    """
    Send calendar invites for multiple events using OAuth authentication
    """
    if isinstance(event_names, str):
        event_names = frappe.parse_json(event_names)
    
    if not event_names or not isinstance(event_names, list):
        frappe.throw("No events selected")
    
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
    
    results = {
        'success': [],
        'failed': []
    }
    
    for event_name in event_names:
        try:
            # Get event document
            event_doc = frappe.get_doc("Event", event_name)
            
            # Skip if already has Google Calendar event ID
            if hasattr(event_doc, 'custom_google_calendar_event_id') and event_doc.custom_google_calendar_event_id:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event already has a Google Calendar event'
                })
                continue
            
            # Validate required fields
            if not event_doc.subject:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event subject is required'
                })
                continue
            
            if not event_doc.starts_on:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event start time is required'
                })
                continue
            
            if not event_doc.ends_on:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event end time is required'
                })
                continue
            
            # Get attendees from custom Google Calendar attendees field
            attendees = []
            if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
                attendees = [
                    email.strip() 
                    for email in event_doc.custom_google_calendar_attendees.split(',') 
                    if email.strip()
                ]
            
            if not attendees:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'No attendees specified in Google Calendar Attendees field'
                })
                continue
            
            # Prepare event data
            event_data = {
                'subject': event_doc.subject,
                'description': event_doc.description or '',
                'starts_on': event_doc.starts_on,
                'ends_on': event_doc.ends_on,
                'location': getattr(event_doc, 'location', ''),
                'attendees': ','.join(attendees)
            }
            
            # Create calendar event with invites
            calendar_event_id = oauth_service.create_calendar_event(event_data)
            
            # Update ERPNext event with Google Calendar event ID
            event_doc.db_set('custom_google_calendar_event_id', calendar_event_id, update_modified=False)
            
            results['success'].append({
                'name': event_name,
                'attendees': len(attendees)
            })
            
        except Exception as e:
            error_msg = str(e)
            short_error = error_msg[:80]  # Shortened version for UI
            
            # Detailed logging with full stack trace
            frappe.log_error(
                message=f"Mass OAuth invite failed for {event_name}: {error_msg}",
                title=f"Calendar Invite Error - {event_name}"
            )
            
            results['failed'].append({
                'name': event_name,
                'reason': short_error,
                'event_id': event_name  # Include event ID for reference
            })
    
    # Prepare response
    success_count = len(results['success'])
    failed_count = len(results['failed'])
    total_count = success_count + failed_count
    
    if success_count == total_count:
        return {
            'status': 'success',
            'message': f'Calendar invites sent for all {success_count} events',
            'results': results
        }
    elif success_count > 0:
        return {
            'status': 'partial_success',
            'message': f'Calendar invites sent for {success_count} out of {total_count} events',
            'results': results
        }
    else:
        return {
            'status': 'error',
            'message': f'Failed to send calendar invites for all {total_count} events',
            'results': results
        }


@frappe.whitelist()
def update_mass_calendar_events_oauth(event_names):
    """
    Update Google Calendar events for multiple events using OAuth authentication
    """
    if isinstance(event_names, str):
        event_names = frappe.parse_json(event_names)
    
    if not event_names or not isinstance(event_names, list):
        frappe.throw("No events selected")
    
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
    
    results = {
        'success': [],
        'failed': []
    }
    
    for event_name in event_names:
        try:
            # Get event document
            event_doc = frappe.get_doc("Event", event_name)
            
            # Check if event has Google Calendar event ID
            google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
            if not google_event_id:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'No Google Calendar event found for this ERPNext event'
                })
                continue
            
            # Validate required fields
            if not event_doc.subject:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event subject is required'
                })
                continue
            
            if not event_doc.starts_on:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event start time is required'
                })
                continue
            
            if not event_doc.ends_on:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'Event end time is required'
                })
                continue
            
            # Get attendees from custom Google Calendar attendees field
            attendees = []
            if hasattr(event_doc, 'custom_google_calendar_attendees') and event_doc.custom_google_calendar_attendees:
                attendees = [
                    email.strip() 
                    for email in event_doc.custom_google_calendar_attendees.split(',') 
                    if email.strip()
                ]
            
            if not attendees:
                results['failed'].append({
                    'name': event_name,
                    'reason': 'No attendees specified in Google Calendar Attendees field'
                })
                continue
            
            # Prepare event data
            event_data = {
                'subject': event_doc.subject,
                'description': event_doc.description or '',
                'starts_on': event_doc.starts_on,
                'ends_on': event_doc.ends_on,
                'location': getattr(event_doc, 'location', ''),
                'attendees': ','.join(attendees)
            }
            
            # Update calendar event
            oauth_service.update_calendar_event(google_event_id, event_data)
            
            results['success'].append({
                'name': event_name,
                'attendees': len(attendees)
            })
            
        except Exception as e:
            error_msg = str(e)
            short_error = error_msg[:80]  # Shortened version for UI
            
            # Detailed logging with full stack trace
            frappe.log_error(
                message=f"Mass OAuth update failed for {event_name}: {error_msg}",
                title=f"Calendar Update Error - {event_name}"
            )
            
            results['failed'].append({
                'name': event_name,
                'reason': short_error,
                'event_id': event_name,  # Include event ID for reference
                'google_event_id': google_event_id  # Include Google Calendar event ID
            })
    
    # Prepare response
    success_count = len(results['success'])
    failed_count = len(results['failed'])
    total_count = success_count + failed_count
    
    if success_count == total_count:
        return {
            'status': 'success',
            'message': f'Calendar events updated for all {success_count} events',
            'results': results
        }
    elif success_count > 0:
        return {
            'status': 'partial_success',
            'message': f'Calendar events updated for {success_count} out of {total_count} events',
            'results': results
        }
    else:
        return {
            'status': 'error',
            'message': f'Failed to update calendar events for all {total_count} events',
            'results': results
        }


@frappe.whitelist()
def delete_mass_calendar_events_oauth(event_names):
    """
    Delete Google Calendar events for multiple events using OAuth authentication
    """
    if isinstance(event_names, str):
        event_names = frappe.parse_json(event_names)
    
    if not event_names or not isinstance(event_names, list):
        frappe.throw("No events selected")
    
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
    
    results = {
        'success': [],
        'skipped': [],
        'failed': []
    }
    
    for event_name in event_names:
        try:
            # Get event document
            event_doc = frappe.get_doc("Event", event_name)
            
            # Check if event has Google Calendar event ID
            google_event_id = getattr(event_doc, 'custom_google_calendar_event_id', None)
            if not google_event_id:
                results['skipped'].append({
                    'name': event_name,
                    'reason': 'No Google Calendar event to delete'
                })
                continue
            
            # Delete calendar event
            oauth_service.delete_calendar_event(google_event_id)
            
            # Clear Google Calendar event ID from ERPNext event
            event_doc.db_set('custom_google_calendar_event_id', None, update_modified=False)
            
            results['success'].append({
                'name': event_name
            })
            
        except Exception as e:
            error_msg = str(e)
            short_error = error_msg[:80]  # Shortened version for UI
            
            # Detailed logging with full stack trace
            frappe.log_error(
                message=f"Mass OAuth deletion failed for {event_name}: {error_msg}",
                title=f"Calendar Delete Error - {event_name}"
            )
            
            results['failed'].append({
                'name': event_name,
                'reason': short_error,
                'event_id': event_name,  # Include event ID for reference
                'google_event_id': google_event_id if 'google_event_id' in locals() else None  # Include Google Calendar event ID if available
            })
    
    # Prepare response
    success_count = len(results['success'])
    skipped_count = len(results['skipped'])
    failed_count = len(results['failed'])
    total_count = success_count + skipped_count + failed_count
    
    if success_count + skipped_count == total_count:
        return {
            'status': 'success',
            'message': f'Calendar events deleted for all {success_count} events' + 
                      (f' ({skipped_count} skipped)' if skipped_count > 0 else ''),
            'results': results
        }
    elif success_count > 0:
        return {
            'status': 'partial_success',
            'message': f'Calendar events deleted for {success_count} out of {total_count} events' + 
                      (f' ({skipped_count} skipped)' if skipped_count > 0 else ''),
            'results': results
        }
    else:
        return {
            'status': 'error',
            'message': f'Failed to delete calendar events for all {total_count - skipped_count} events' + 
                      (f' ({skipped_count} skipped)' if skipped_count > 0 else ''),
            'results': results
        }
