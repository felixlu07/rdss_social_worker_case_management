frappe.ui.form.on('Event', {
    refresh: function(frm) {
        // Add custom button for sending calendar invites
        if (!frm.doc.__islocal && frm.doc.docstatus < 2) {
            frm.add_custom_button(__('Send Calendar Invite'), function() {
                send_calendar_invite(frm);
            }, __('Actions'));
            
            // Add update button if Google Calendar event exists
            if (frm.doc.custom_google_calendar_event_id) {
                frm.add_custom_button(__('Update Calendar Event'), function() {
                    update_calendar_event(frm);
                }, __('Actions'));
                
                frm.add_custom_button(__('Delete Calendar Event'), function() {
                    delete_calendar_event(frm);
                }, __('Actions'));
            }
        }
    }
});

function send_calendar_invite(frm) {
    // Validate required fields
    if (!frm.doc.subject) {
        frappe.msgprint(__('Event subject is required'));
        return;
    }
    
    if (!frm.doc.starts_on) {
        frappe.msgprint(__('Event start time is required'));
        return;
    }
    
    if (!frm.doc.ends_on) {
        frappe.msgprint(__('Event end time is required'));
        return;
    }
    
    // Check if there are attendees in the custom field
    if (!frm.doc.custom_google_calendar_attendees || !frm.doc.custom_google_calendar_attendees.trim()) {
        frappe.msgprint(__('Please add email addresses in the Google Calendar Attendees field'));
        return;
    }
    
    // Show confirmation dialog
    frappe.confirm(
        __('This will create a Google Calendar event and send invites to all participants. Continue?'),
        function() {
            frappe.show_alert({
                message: __('Sending calendar invite...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.oauth_calendar_service.send_calendar_invite_oauth',
                args: {
                    event_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();
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
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to send calendar invite'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

function update_calendar_event(frm) {
    frappe.confirm(
        __('This will update the existing Google Calendar event with current details. Continue?'),
        function() {
            frappe.show_alert({
                message: __('Updating calendar event...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.invite_sender.update_calendar_event',
                args: {
                    event_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to update calendar event'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

function delete_calendar_event(frm) {
    frappe.confirm(
        __('This will delete the Google Calendar event. This action cannot be undone. Continue?'),
        function() {
            frappe.show_alert({
                message: __('Deleting calendar event...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'rdss_social_work.rdss_social_work.google_calendar.invite_sender.delete_calendar_event',
                args: {
                    event_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Failed to delete calendar event'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}
