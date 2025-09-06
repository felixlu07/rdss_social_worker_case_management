import frappe

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

if __name__ == "__main__":
    print(clear_events())
