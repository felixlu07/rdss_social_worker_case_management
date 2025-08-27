frappe.ui.form.on('Appointment', {
    refresh: function(frm) {
        // Auto-populate beneficiary when case is selected
        if (frm.doc.case && !frm.doc.beneficiary) {
            frappe.db.get_value('Case', frm.doc.case, 'beneficiary')
                .then(r => {
                    if (r.message && r.message.beneficiary) {
                        frm.set_value('beneficiary', r.message.beneficiary);
                    }
                });
        }
        
        // Add custom buttons based on appointment status
        add_appointment_custom_buttons(frm);
        
        // Show/hide post-visit fields based on status
        toggle_post_visit_fields(frm);
        
        // Add case notes table at the top of the form
        add_case_notes_section(frm);
    },
    
    case: function(frm) {
        // Auto-populate beneficiary when case is selected
        if (frm.doc.case) {
            frappe.db.get_value('Case', frm.doc.case, 'beneficiary')
                .then(r => {
                    if (r.message && r.message.beneficiary) {
                        frm.set_value('beneficiary', r.message.beneficiary);
                    }
                });
        }
    },
    
    appointment_status: function(frm) {
        toggle_post_visit_fields(frm);
    },
    
    appointment_outcome: function(frm) {
        // Auto-populate actual times when marking as completed
        if (frm.doc.appointment_outcome === 'Completed as Planned' && !frm.doc.actual_start_time) {
            frm.set_value('actual_start_time', frm.doc.appointment_time);
            
            // Set end time to 1 hour after start time if duration is specified
            if (frm.doc.duration_minutes) {
                let start_time = frappe.datetime.str_to_obj(frm.doc.appointment_time);
                let end_time = new Date(start_time.getTime() + (frm.doc.duration_minutes * 60000));
                frm.set_value('actual_end_time', frappe.datetime.obj_to_str(end_time));
            }
        }
    }
});

function add_appointment_custom_buttons(frm) {
    if (!frm.is_new()) {
        // Add button to create case note from appointment - available regardless of appointment status
        // If case note already exists, show view button
        if (frm.doc.case_note) {
            frm.add_custom_button(__('View Case Note'), function() {
                frappe.set_route('Form', 'Case Notes', frm.doc.case_note);
            }, __('Case Documentation'));
        } else {
            // Otherwise show create button
            frm.add_custom_button(__('Create Case Note'), function() {
                frappe.call({
                    method: 'rdss_social_work.rdss_social_work.doctype.appointment.appointment.create_case_note_from_appointment',
                    args: {
                        appointment_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route('Form', 'Case Notes', r.message.name);
                        }
                    }
                });
            }, __('Case Documentation')).addClass('btn-primary');
        }
        
        // Add button to view all case notes for this case
        frm.add_custom_button(__('View All Case Notes'), function() {
            frappe.route_options = {
                'case': frm.doc.case
            };
            frappe.set_route('List', 'Case Notes');
        }, __('Case Documentation'));
        
        // Add button to create follow-up assessment
        if (frm.doc.appointment_outcome === 'Completed as Planned') {
            frm.add_custom_button(__('Create Follow-up Assessment'), function() {
                frappe.new_doc('Follow Up Assessment', {
                    case: frm.doc.case,
                    beneficiary: frm.doc.beneficiary,
                    assessment_date: frm.doc.appointment_date,
                    assessed_by: frm.doc.social_worker,
                                        previous_appointment: frm.doc.name
                });
            }, __('Create'));
        }
        
        // Add button to schedule next appointment
        frm.add_custom_button(__('Schedule Next Appointment'), function() {
            frappe.new_doc('Appointment', {
                case: frm.doc.case,
                beneficiary: frm.doc.beneficiary,
                social_worker: frm.doc.social_worker,
                appointment_type: frm.doc.appointment_type
            });
        }, __('Create'));
        
        // Navigation to case is now handled through other UI elements
    }
}

function toggle_post_visit_fields(frm) {
    // Show post-visit fields only when appointment is completed or has outcome
    let show_post_visit = frm.doc.appointment_status === 'Completed' || 
                         frm.doc.appointment_outcome === 'Completed as Planned' ||
                         frm.doc.appointment_outcome === 'Partially Completed';
    
    // Toggle visibility of post-visit documentation fields
    frm.toggle_display(['appointment_notes', 'private_notes', 'attachments_section', 
                       'voice_notes', 'visit_photos', 'supporting_documents', 
                       'action_items', 'referrals_made'], show_post_visit);
    
    // Make appointment notes mandatory for completed visits
    frm.toggle_reqd('appointment_notes', show_post_visit);
}

// Custom function to handle voice note upload
frappe.ui.form.on('Appointment', 'voice_notes', function(frm) {
    if (frm.doc.voice_notes) {
        // Show success message when voice note is uploaded
        frappe.show_alert({
            message: __('Voice note uploaded successfully'),
            indicator: 'green'
        });
        
        // Auto-add note about voice recording
        let current_notes = frm.doc.appointment_notes || '';
        if (!current_notes.includes('Voice recording attached')) {
            let voice_note_text = '\n\n[Voice recording attached - ' + 
                                 frappe.datetime.now_datetime() + ']';
            frm.set_value('appointment_notes', current_notes + voice_note_text);
        }
    }
});

// Custom function to handle visit photos
frappe.ui.form.on('Appointment', 'visit_photos', function(frm) {
    if (frm.doc.visit_photos) {
        frappe.show_alert({
            message: __('Visit photo uploaded successfully'),
            indicator: 'green'
        });
        
        // Auto-add note about photo
        let current_notes = frm.doc.appointment_notes || '';
        if (!current_notes.includes('Visit photo attached')) {
            let photo_note_text = '\n\n[Visit photo attached - ' + 
                                frappe.datetime.now_datetime() + ']';
            frm.set_value('appointment_notes', current_notes + photo_note_text);
        }
    }
});

// Function to add case notes section to the form using the HTML field in the tab
function add_case_notes_section(frm) {
    if (!frm.doc.case || frm.is_new()) return;
    
    // Use the HTML field wrapper instead of relying on a fixed DOM id
    const notes_wrapper = $(frm.fields_dict['case_notes_html'].wrapper);

    setTimeout(() => {
        // Add header with action button
        let header = $(`
            <div class="case-notes-header" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid var(--border-color); background-color: var(--fg-color);">
                <h6 class="case-notes-title" style="margin: 0; font-weight: 600; color: var(--text-color);">Case Notes for this Appointment</h6>
                <button class="btn btn-sm btn-primary" onclick="create_new_case_note('${frm.doc.case}', '${frm.doc.beneficiary}', '${frm.doc.name}')">
                    <i class="fa fa-plus"></i> New Case Note
                </button>
            </div>
        `);
        
        // Add container for case notes table
        let container = $(`
            <div class="case-notes-container" style="padding: 0 15px;">
                <div id="case-notes-table" style="margin-top: 15px;">Loading case notes...</div>
                <div id="case-notes-pagination" style="padding: 15px 0; text-align: center;"></div>
            </div>
        `);
        
        // Append the content to the HTML container
        notes_wrapper.empty().append(header).append(container);
        
        // Load the case notes data
        load_case_notes_table(frm, 1);
        
        // Activate the Case Notes tab if it exists
        if (frm.layout && frm.layout.tabs) {
            // Use the standard Frappe method to activate a tab
            frm.set_df_property('case_notes_tab', 'hidden', 0);
            frm.refresh_field('case_notes_tab');
            frm.scroll_to_field('case_notes_tab');
        }
    }, 100);
}

function load_case_notes_table(frm, page = 1) {
    const page_length = 3; // Show only 3 rows per page
    
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Case Notes',
            filters: [
                ['Case Notes', 'related_appointment', '=', frm.doc.name]
            ],
            // minimal debug
            fields: ['name', 'visit_date', 'visit_type', 'social_worker', 'visit_outcome', 'related_appointment'],
            order_by: 'visit_date desc, modified desc',
            limit_page_length: page_length,
            limit_start: (page - 1) * page_length
        },
        callback: function(r) {
            let table_html = '';
            
            if (r.message && r.message.length) {
                let rows = '';
                r.message.forEach(note => {
                    rows += `
                    <tr>
                        <td><a href="#Form/Case Notes/${note.name}" class="text-primary">${note.name}</a></td>
                        <td>${note.visit_date || ''}</td>
                        <td>${note.visit_type || ''}</td>
                        <td>${note.social_worker || ''}</td>
                        <td>
                            <span class="indicator ${getOutcomeIndicator(note.visit_outcome)}">
                                ${note.visit_outcome || 'Not Specified'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-xs btn-primary" onclick="frappe.set_route('Form', 'Case Notes', '${note.name}')">
                                <i class="fa fa-eye"></i> View
                            </button>
                        </td>
                    </tr>`;
                });
                
                table_html = `
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Social Worker</th>
                                <th>Outcome</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>`;
                
                // Get total count for pagination
                frappe.call({
                    method: 'frappe.client.get_count',
                    args: {
                        doctype: 'Case Notes',
                        filters: [
                            ['Case Notes', 'related_appointment', '=', frm.doc.name]
                        ]
                    },
                    callback: function(count_r) {
                        const total_pages = Math.ceil(count_r.message / page_length);
                        render_pagination(frm, page, total_pages);
                    }
                });
            } else {
                table_html = `
                <div class="no-result text-muted" style="padding: 30px 0; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 10px;">
                        <i class="fa fa-clipboard-list"></i>
                    </div>
                    <p>No case notes found for this appointment.</p>
                    <button class="btn btn-primary btn-sm" onclick="create_new_case_note('${frm.doc.case}', '${frm.doc.beneficiary}', '${frm.doc.name}')">
                        <i class="fa fa-plus"></i> Create Case Note
                    </button>
                </div>`;
                $('#case-notes-pagination').html('');
            }
            
            $('#case-notes-table').html(table_html);
        }
    });
}

// Helper function to get indicator color based on outcome
function getOutcomeIndicator(outcome) {
    if (!outcome) return 'gray';
    
    outcome = outcome.toLowerCase();
    if (outcome.includes('successful') || outcome.includes('completed')) {
        return 'green';
    } else if (outcome.includes('partial')) {
        return 'orange';
    } else if (outcome.includes('unsuccessful') || outcome.includes('failed')) {
        return 'red';
    } else if (outcome.includes('reschedule')) {
        return 'blue';
    } else {
        return 'gray';
    }
}

function render_pagination(frm, current_page, total_pages) {
    if (total_pages <= 1) {
        $('#case-notes-pagination').html('');
        return;
    }
    
    // Create a more modern pagination with page info
    let pagination_html = `
    <div class="case-notes-pagination">
        <div class="pagination-info" style="margin-bottom: 10px; color: var(--text-muted); font-size: 0.9em;">
            Showing page ${current_page} of ${total_pages}
        </div>
        <div class="pagination-controls">
    `;
    
    // Previous button
    pagination_html += `
        <button class="btn btn-sm ${current_page === 1 ? 'btn-default disabled' : 'btn-default'}" 
            ${current_page > 1 ? `onclick="load_case_notes_table(cur_frm, ${current_page - 1})"` : ''}
            style="margin-right: 5px;">
            <i class="fa fa-chevron-left"></i>
        </button>
    `;
    
    // Page numbers with ellipsis for many pages
    if (total_pages <= 5) {
        // Show all page numbers if 5 or fewer
        for (let i = 1; i <= total_pages; i++) {
            pagination_html += `
                <button class="btn btn-sm ${i === current_page ? 'btn-primary' : 'btn-default'}" 
                    onclick="load_case_notes_table(cur_frm, ${i})" style="margin: 0 2px;">
                    ${i}
                </button>
            `;
        }
    } else {
        // Show limited page numbers with ellipsis for many pages
        // Always show first page
        pagination_html += `
            <button class="btn btn-sm ${1 === current_page ? 'btn-primary' : 'btn-default'}" 
                onclick="load_case_notes_table(cur_frm, 1)" style="margin: 0 2px;">
                1
            </button>
        `;
        
        // Show ellipsis if current page is more than 3
        if (current_page > 3) {
            pagination_html += `<span style="margin: 0 5px;">...</span>`;
        }
        
        // Show current page and surrounding pages
        for (let i = Math.max(2, current_page - 1); i <= Math.min(total_pages - 1, current_page + 1); i++) {
            if (i !== 1 && i !== total_pages) { // Skip first and last pages as they're handled separately
                pagination_html += `
                    <button class="btn btn-sm ${i === current_page ? 'btn-primary' : 'btn-default'}" 
                        onclick="load_case_notes_table(cur_frm, ${i})" style="margin: 0 2px;">
                        ${i}
                    </button>
                `;
            }
        }
        
        // Show ellipsis if current page is less than total_pages - 2
        if (current_page < total_pages - 2) {
            pagination_html += `<span style="margin: 0 5px;">...</span>`;
        }
        
        // Always show last page
        pagination_html += `
            <button class="btn btn-sm ${total_pages === current_page ? 'btn-primary' : 'btn-default'}" 
                onclick="load_case_notes_table(cur_frm, ${total_pages})" style="margin: 0 2px;">
                ${total_pages}
            </button>
        `;
    }
    
    // Next button
    pagination_html += `
        <button class="btn btn-sm ${current_page === total_pages ? 'btn-default disabled' : 'btn-default'}" 
            ${current_page < total_pages ? `onclick="load_case_notes_table(cur_frm, ${current_page + 1})"` : ''}
            style="margin-left: 5px;">
            <i class="fa fa-chevron-right"></i>
        </button>
    `;
    
    pagination_html += '</div></div>';
    $('#case-notes-pagination').html(pagination_html);
}

// Make this function globally accessible by attaching it to window
window.create_new_case_note = function(case_id, beneficiary, appointment_name) {
    // Get appointment details to populate visit_date
    frappe.db.get_doc('Appointment', appointment_name)
        .then(appointment => {
            frappe.new_doc('Case Notes', {
                'case': case_id,
                'beneficiary': beneficiary,
                'related_appointment': appointment_name,
                'visit_date': appointment.appointment_date
            });
        });
};
