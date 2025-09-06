frappe.listview_settings['Event'] = {
    onload: function(listview) {
        // Add custom buttons for calendar operations
        listview.page.add_action_item(__('Send Calendar Invites'), function() {
            send_mass_calendar_invites(listview);
        });
        
        listview.page.add_action_item(__('Update Calendar Events'), function() {
            update_mass_calendar_events(listview);
        });
        
        listview.page.add_action_item(__('Delete Calendar Events'), function() {
            delete_mass_calendar_events(listview);
        });
    }
};

function send_mass_calendar_invites(listview) {
    // Get selected events
    const selected_docs = listview.get_checked_items();
    
    // Check if any events are selected
    if (selected_docs.length === 0) {
        frappe.msgprint(__('Please select at least one event'));
        return;
    }
    
    // Collect names of selected events
    const event_names = selected_docs.map(doc => doc.name);
    
    // Show confirmation dialog with count
    frappe.confirm(
        __(`This will create Google Calendar events and send invites for ${selected_docs.length} selected event(s). Continue?`),
        function() {
            frappe.show_alert({
                message: __('Sending calendar invites...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.oauth_calendar_service.send_mass_calendar_invites_oauth',
                args: {
                    event_names: event_names
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        listview.refresh();
                    } else if (r.message && r.message.status === 'partial_success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'yellow'
                        });
                        listview.refresh();
                    } else if (r.message && r.message.status === 'auth_required') {
                        // Show OAuth authorization dialog
                        frappe.confirm(
                            __('Google authorization required to send calendar invites. Click OK to authorize.'),
                            function() {
                                window.open(r.message.auth_url, 'google_auth', 'width=500,height=600');
                                frappe.show_alert({
                                    message: __('Please complete authorization in the popup window, then try again.'),
                                    indicator: 'blue'
                                });
                            }
                        );
                    } else {
                        frappe.show_alert({
                            message: __('Failed to send calendar invites'),
                            indicator: 'red'
                        });
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to send calendar invites'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

function update_mass_calendar_events(listview) {
    // Get selected events
    const selected_docs = listview.get_checked_items();
    
    // Check if any events are selected
    if (selected_docs.length === 0) {
        frappe.msgprint(__('Please select at least one event'));
        return;
    }
    
    // Collect names of selected events
    const event_names = selected_docs.map(doc => doc.name);
    
    // Show confirmation dialog with count
    frappe.confirm(
        __(`This will update Google Calendar events for ${selected_docs.length} selected event(s). Continue?`),
        function() {
            frappe.show_alert({
                message: __('Updating calendar events...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.oauth_calendar_service.update_mass_calendar_events_oauth',
                args: {
                    event_names: event_names
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        listview.refresh();
                    } else if (r.message && r.message.status === 'partial_success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'yellow'
                        });
                        listview.refresh();
                    } else if (r.message && r.message.status === 'auth_required') {
                        // Show OAuth authorization dialog
                        frappe.confirm(
                            __('Google authorization required to update calendar events. Click OK to authorize.'),
                            function() {
                                window.open(r.message.auth_url, 'google_auth', 'width=500,height=600');
                                frappe.show_alert({
                                    message: __('Please complete authorization in the popup window, then try again.'),
                                    indicator: 'blue'
                                });
                            }
                        );
                    } else {
                        frappe.show_alert({
                            message: __('Failed to update calendar events'),
                            indicator: 'red'
                        });
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to update calendar events'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

function delete_mass_calendar_events(listview) {
    // Get selected events
    const selected_docs = listview.get_checked_items();
    
    // Check if any events are selected
    if (selected_docs.length === 0) {
        frappe.msgprint(__('Please select at least one event'));
        return;
    }
    
    // Collect names of selected events
    const event_names = selected_docs.map(doc => doc.name);
    
    // Show confirmation dialog with count
    frappe.confirm(
        __(`This will delete Google Calendar events for ${selected_docs.length} selected event(s). This action cannot be undone. Continue?`),
        function() {
            frappe.show_alert({
                message: __('Deleting calendar events...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.oauth_calendar_service.delete_mass_calendar_events_oauth',
                args: {
                    event_names: event_names
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        listview.refresh();
                    } else if (r.message && r.message.status === 'partial_success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'yellow'
                        });
                        listview.refresh();
                        
                        // Show detailed error dialog for partial success
                        if (r.message.results && r.message.results.failed && r.message.results.failed.length > 0) {
                            setTimeout(() => {
                                show_calendar_errors('Calendar Delete Errors', r.message.results.failed);
                            }, 1000);
                        }
                    } else if (r.message && r.message.status === 'auth_required') {
                        // Show OAuth authorization dialog
                        frappe.confirm(
                            __('Google authorization required to delete calendar events. Click OK to authorize.'),
                            function() {
                                window.open(r.message.auth_url, 'google_auth', 'width=500,height=600');
                                frappe.show_alert({
                                    message: __('Please complete authorization in the popup window, then try again.'),
                                    indicator: 'blue'
                                });
                            }
                        );
                    } else {
                        frappe.show_alert({
                            message: __('Failed to delete calendar events'),
                            indicator: 'red'
                        });
                        
                        // Show detailed error dialog for complete failure
                        if (r.message && r.message.results && r.message.results.failed && r.message.results.failed.length > 0) {
                            setTimeout(() => {
                                show_calendar_errors('Calendar Delete Errors', r.message.results.failed);
                            }, 1000);
                        }
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to delete calendar events'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

/**
 * Shows a dialog with detailed error information for calendar operations
 * @param {string} title - Dialog title
 * @param {Array} errors - Array of error objects
 */
function show_calendar_errors(title, errors) {
    if (!errors || !errors.length) return;
    
    // Create HTML table for errors
    let error_html = '<div style="max-height: 300px; overflow-y: auto;">';
    error_html += '<table class="table table-bordered">';
    error_html += '<thead><tr><th>Event</th><th>Error</th></tr></thead>';
    error_html += '<tbody>';
    
    errors.forEach(err => {
        const event_name = err.name || 'Unknown';
        const reason = err.reason || 'Unknown error';
        
        error_html += `<tr>
            <td><a href="#Form/Event/${event_name}">${event_name}</a></td>
            <td>${reason}</td>
        </tr>`;
    });
    
    error_html += '</tbody></table></div>';
    
    // Create and show dialog
    const d = new frappe.ui.Dialog({
        title: __(title),
        fields: [{
            fieldtype: 'HTML',
            fieldname: 'error_html',
            options: error_html
        }],
        primary_action_label: __('View Error Logs'),
        primary_action: function() {
            frappe.set_route('List', 'Error Log', {
                filters: {
                    'method': ['like', '%calendar%']
                }
            });
            d.hide();
        }
    });
    
    d.show();
}
