import frappe

def check_events_detailed():
    """Check the events in detail to understand what's happening"""
    
    # Count total events
    total_events = frappe.db.count('Event')
    
    # Get all events
    events = frappe.get_all('Event', 
                           fields=['name', 'subject', 'starts_on', 'status', 'event_type', 'event_category'],
                           order_by='name desc')
    
    result = f"Total events in system: {total_events}\n\n"
    result += "Events by status:\n"
    
    # Count events by status
    status_counts = {}
    for event in events:
        status = event.status
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    for status, count in status_counts.items():
        result += f"- {status}: {count}\n"
    
    result += "\nEvents by category:\n"
    
    # Count events by category
    category_counts = {}
    for event in events:
        category = event.event_category
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    for category, count in category_counts.items():
        result += f"- {category}: {count}\n"
    
    result += "\nEvents by type:\n"
    
    # Count events by type
    type_counts = {}
    for event in events:
        event_type = event.event_type
        if event_type not in type_counts:
            type_counts[event_type] = 0
        type_counts[event_type] += 1
    
    for event_type, count in type_counts.items():
        result += f"- {event_type}: {count}\n"
    
    result += "\nList of all events:\n"
    for event in events:
        result += f"- {event.name}: {event.subject} ({event.starts_on}) - {event.status}\n"
    
    return result

if __name__ == "__main__":
    print(check_events_detailed())
