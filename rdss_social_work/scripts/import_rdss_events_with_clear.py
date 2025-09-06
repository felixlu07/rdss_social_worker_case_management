import frappe
import csv
import os
from datetime import datetime, timedelta
from frappe.utils import getdate, get_datetime, nowtime

def clear_events():
    """Delete all existing events from the system"""
    
    # Get all events
    events = frappe.get_all('Event', fields=['name'])
    
    # Count before deletion
    total_before = len(events)
    
    # Delete each event
    deleted_count = 0
    errors = []
    
    for event in events:
        try:
            frappe.delete_doc('Event', event.name, force=True)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Error deleting {event.name}: {str(e)}")
    
    # Commit the changes
    frappe.db.commit()
    
    # Count after deletion
    remaining = frappe.db.count('Event')
    
    result = f"Events before deletion: {total_before}\n"
    result += f"Events deleted: {deleted_count}\n"
    result += f"Events remaining: {remaining}\n"
    
    if errors:
        result += "\nErrors encountered:\n"
        for error in errors:
            result += f"- {error}\n"
    
    return result

def import_rdss_events(clear_existing=True, debug=False):
    """Import RDSS events from CSV file to Event doctype"""
    
    result_messages = []
    
    # Clear existing events if requested
    if clear_existing:
        clear_result = clear_events()
        result_messages.append(clear_result)
        
    if debug:
        frappe.log_error("Starting RDSS event import", "RDSS Event Import")
    
    # Path to the CSV file
    csv_file_path = os.path.join(
        frappe.get_app_path('rdss_social_work'),
        'public',
        'rdss-events.csv'
    )
    
    if debug:
        frappe.log_error(f"CSV file path: {csv_file_path}", "RDSS Event Import")
        frappe.log_error(f"File exists: {os.path.exists(csv_file_path)}", "RDSS Event Import")
    
    # Category mapping from CSV to Event doctype
    category_mapping = {
        'Family Event': 'Event',
        'Educational Outreach': 'Event',
        'Fundraising Event': 'Event',
        'Educational Forum': 'Event',
        'Appreciation Event': 'Event',
        'Sibling Support': 'Event',
        'Corporate Collaboration': 'Event',
        'Caregiver Support': 'Event',
        'Youth Program': 'Event',
        'Advocacy Event': 'Event',
        'Webinar': 'Event',
        'Fundraising Campaign': 'Event',
        'TBD': 'Event',
        # Default to 'Other' for any unmapped categories
        'default': 'Other'
    }
    
    # Status mapping from CSV to Event doctype
    status_mapping = {
        'Completed': 'Completed',
        'Registration Open': 'Open',
        'Planned': 'Open',
        'Venue Booked': 'Open',
        'Registered': 'Open',
        # Default to 'Open' for any unmapped statuses
        'default': 'Open'
    }
    
    # Counter for successful and failed imports
    success_count = 0
    error_count = 0
    
    # List to store error messages
    errors = []
    
    try:
        with open(csv_file_path, 'r') as file:
            content = file.read()
            if debug:
                frappe.log_error(f"CSV content first 200 chars: {content[:200]}", "RDSS Event Import")
            
            # Reset file pointer to beginning
            file.seek(0)
            
            # Read the CSV file and clean up column names
            reader = csv.reader(file)
            headers = next(reader)
            
            # Clean up header names - remove BOM and trim spaces
            clean_headers = []
            for header in headers:
                # Remove BOM if present
                if header.startswith('\ufeff'):
                    header = header[1:]
                # Remove trailing/leading spaces
                header = header.strip()
                clean_headers.append(header)
                
            if debug:
                # Log only the first few headers to avoid truncation
                frappe.log_error(f"Cleaned headers sample: {clean_headers[:3]}...", "RDSS Event Import")
            
            # Create a list of dictionaries with clean keys
            rows = []
            for row in reader:
                if len(row) == len(clean_headers):
                    row_dict = {clean_headers[i]: row[i].strip() for i in range(len(row))}
                    rows.append(row_dict)
                    
            if debug:
                frappe.log_error(f"Number of rows in CSV: {len(rows)}", "RDSS Event Import")
                if rows:
                    # Log only a few key fields from the first row to avoid truncation
                    sample_data = {k: rows[0].get(k, '') for k in ['Event_ID', 'Title'] if k in rows[0]}
                    frappe.log_error(f"First row sample: {sample_data}", "RDSS Event Import")
            
            # Use the cleaned rows for processing
            reader = rows
            
            for row_index, row in enumerate(reader):
                if debug:
                    frappe.log_error(f"Processing row {row_index}: {row.get('Event_ID', 'No ID')}", "RDSS Event Import")
                # Skip empty rows
                if not row.get('Event_ID'):
                    if debug:
                        frappe.log_error(f"Skipping row {row_index} - no Event_ID", "RDSS Event Import")
                    continue
                    
                if debug:
                    frappe.log_error(f"Processing event: {row.get('Title')}", "RDSS Event Import")
                
                try:
                    # Create event document
                    event = frappe.new_doc('Event')
                    
                    # Basic fields
                    title = row.get('Title', '')
                    if debug:
                        frappe.log_error(f"Setting subject to: {title}", "RDSS Event Import")
                    event.subject = title
                    
                    # Map event category
                    csv_category = row.get('Category', '').strip()
                    event.event_category = category_mapping.get(csv_category, category_mapping['default'])
                    
                    # Set event type to Public
                    event.event_type = 'Public'
                    
                    # Map status
                    csv_status = row.get('Status', '').strip()
                    event.status = status_mapping.get(csv_status, status_mapping['default'])
                    
                    # Handle date and time
                    event_date = row.get('Date', '').strip()
                    start_time = row.get('Start_Time', '').strip()
                    end_time = row.get('End_Time', '').strip()
                    
                    # Check if it's an all-day event
                    all_day = False
                    if start_time.lower() == 'all day' or start_time.lower() == 'tbd':
                        all_day = True
                    
                    event.all_day = all_day
                    
                    # Parse date
                    if event_date and event_date.lower() != 'tbd':
                        try:
                            # Handle special cases like '2025-12-TBD'
                            if 'tbd' in event_date.lower():
                                # Use the first day of the mentioned month
                                parts = event_date.split('-')
                                if len(parts) >= 2:
                                    event_date = f"{parts[0]}-{parts[1]}-01"
                            
                            parsed_date = getdate(event_date)
                            
                            # Set start datetime
                            if all_day:
                                event.starts_on = datetime.combine(parsed_date, datetime.min.time())
                                # For all-day events, end time is end of day
                                event.ends_on = datetime.combine(parsed_date, datetime.max.time())
                            else:
                                # Parse start time
                                if start_time and start_time.lower() != 'tbd':
                                    try:
                                        start_dt = datetime.strptime(start_time, '%H:%M')
                                        event.starts_on = datetime.combine(
                                            parsed_date, 
                                            start_dt.time()
                                        )
                                    except ValueError:
                                        # Default to 9 AM if time format is invalid
                                        event.starts_on = datetime.combine(
                                            parsed_date, 
                                            datetime.strptime('09:00', '%H:%M').time()
                                        )
                                else:
                                    # Default to 9 AM if time is not provided
                                    event.starts_on = datetime.combine(
                                        parsed_date, 
                                        datetime.strptime('09:00', '%H:%M').time()
                                    )
                                
                                # Parse end time
                                if end_time and end_time.lower() != 'tbd':
                                    try:
                                        end_dt = datetime.strptime(end_time, '%H:%M')
                                        event.ends_on = datetime.combine(
                                            parsed_date, 
                                            end_dt.time()
                                        )
                                    except ValueError:
                                        # Default to start time + 1 hour if time format is invalid
                                        if event.starts_on:
                                            event.ends_on = event.starts_on + timedelta(hours=1)
                                else:
                                    # Default to start time + 1 hour if end time is not provided
                                    if event.starts_on:
                                        event.ends_on = event.starts_on + timedelta(hours=1)
                        except Exception as e:
                            frappe.log_error(f"Error parsing date for event {row.get('Event_ID')}: {str(e)}")
                            # Use current date as fallback
                            event.starts_on = datetime.now()
                            event.ends_on = event.starts_on + timedelta(hours=1)
                    else:
                        # Use current date as fallback
                        event.starts_on = datetime.now()
                        event.ends_on = event.starts_on + timedelta(hours=1)
                    
                    # Build description with additional fields
                    description_parts = []
                    
                    # Add Event ID
                    description_parts.append(f"<p><strong>Event ID:</strong> {row.get('Event_ID', '')}</p>")
                    
                    # Add Target Audience
                    if row.get('Target_Audience'):
                        description_parts.append(f"<p><strong>Target Audience:</strong> {row.get('Target_Audience', '')}</p>")
                    
                    # Add Purpose
                    if row.get('Purpose'):
                        description_parts.append(f"<p><strong>Purpose:</strong> {row.get('Purpose', '')}</p>")
                    
                    # Add Location
                    if row.get('Location'):
                        description_parts.append(f"<p><strong>Location:</strong> {row.get('Location', '')}</p>")
                    
                    # Add Budget
                    if row.get('Budget') and row.get('Budget').lower() != 'tbd':
                        description_parts.append(f"<p><strong>Budget:</strong> ${row.get('Budget', '')}</p>")
                    
                    # Add Partner Organization
                    if row.get('Partner_Organization'):
                        description_parts.append(f"<p><strong>Partner Organization:</strong> {row.get('Partner_Organization', '')}</p>")
                    
                    # Add Duration Hours
                    if row.get('Duration_Hours') and row.get('Duration_Hours').lower() != 'tbd':
                        description_parts.append(f"<p><strong>Duration (Hours):</strong> {row.get('Duration_Hours', '')}</p>")
                    
                    # Add Attendees
                    if row.get('Attendees') and row.get('Attendees').lower() != 'tbd':
                        description_parts.append(f"<p><strong>Number of Attendees:</strong> {row.get('Attendees', '')}</p>")
                    
                    # Add Feedback Rating
                    if row.get('Feedback_Rating') and row.get('Feedback_Rating').lower() != 'tbd':
                        description_parts.append(f"<p><strong>Feedback Rating:</strong> {row.get('Feedback_Rating', '')}</p>")
                    
                    # Add Notes
                    if row.get('Notes'):
                        description_parts.append(f"<p><strong>Notes:</strong> {row.get('Notes', '')}</p>")
                    
                    # Set description
                    event.description = "\n".join(description_parts)
                    
                    # Save the event
                    event.insert()
                    
                    # Add dummy participant if attendees count is available
                    attendees_count = row.get('Attendees', '').strip()
                    if attendees_count and attendees_count.lower() != 'tbd' and attendees_count.isdigit():
                        try:
                            count = int(attendees_count)
                            if count > 0:
                                # Add a note about attendees in the event
                                frappe.db.set_value('Event', event.name, 'description', 
                                                  event.description + f"\n<p><strong>Note:</strong> This event has {count} attendees.</p>")
                        except ValueError:
                            pass
                    
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"Error importing event {row.get('Event_ID')}: {str(e)}"
                    frappe.log_error(error_msg, "RDSS Event Import Error")
                    errors.append(error_msg)
                    error_count += 1
        
        # Print summary
        summary = f"Import complete. Successfully imported {success_count} events. {error_count} events failed."
        if errors:
            summary += "\n\nErrors:"
            for error in errors:
                summary += f"\n- {error}"
        
        result_messages.append(summary)
        return "\n\n".join(result_messages)
        
    except Exception as e:
        error_msg = f"Error in RDSS event import: {str(e)}"
        frappe.log_error(f"{error_msg}\nTraceback: {frappe.get_traceback()}", "RDSS Event Import Error")
        result_messages.append(f"Import failed: {error_msg}")
        return "\n\n".join(result_messages)

if __name__ == "__main__":
    import_rdss_events()
