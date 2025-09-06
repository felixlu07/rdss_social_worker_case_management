import frappe

def check_events():
    """Check the events that were imported"""
    
    # Count total events
    total_events = frappe.db.count('Event')
    
    # Get a sample of events
    events = frappe.get_all('Event', 
                           fields=['name', 'subject', 'starts_on', 'status'],
                           limit=5)
    
    result = f"Total events in system: {total_events}\n\n"
    result += "Sample of events:\n"
    
    for event in events:
        result += f"- {event.name}: {event.subject} ({event.starts_on}) - {event.status}\n"
    
    return result

if __name__ == "__main__":
    print(check_events())
