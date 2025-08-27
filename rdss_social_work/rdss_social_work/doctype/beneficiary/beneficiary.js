frappe.ui.form.on('Beneficiary', {
    refresh: function(frm) {
        // Calculate age from date of birth
        if (frm.doc.date_of_birth) {
            frm.set_value('age', calculate_age(frm.doc.date_of_birth));
        }
        
        // Load related data in tabs
        if (!frm.is_new()) {
            load_cases_data(frm);
            load_appointments_data(frm);
            load_assessments_data(frm);
            load_services_data(frm);
            load_documents_data(frm);
        }
        
        // Add custom buttons
        add_custom_buttons(frm);
    },
    
    date_of_birth: function(frm) {
        if (frm.doc.date_of_birth) {
            frm.set_value('age', calculate_age(frm.doc.date_of_birth));
        }
    },
    
    postal_code: function(frm) {
        if (frm.doc.postal_code && frm.doc.postal_code.trim()) {
            // Show notification that we're geocoding
            frappe.show_alert({
                message: __('Updating location coordinates for postal code: {0}', [frm.doc.postal_code]),
                indicator: 'blue'
            }, 3);
            
            // Call geocoding API
            geocode_postal_code(frm, frm.doc.postal_code);
        }
    },
    
    // Ensure tabs work correctly by handling tab changes
    onload: function(frm) {
        // Initialize HTML containers for tabs
        initialize_tab_containers(frm);
        
        // Force refresh on tab change to ensure content loads correctly
        $('.form-tabs .nav-link').on('shown.bs.tab', function(e) {
            if (!frm.is_new()) {
                const tab = $(e.target).attr('data-target');
                if (tab === '#cases') {
                    load_cases_data(frm);
                } else if (tab === '#appointments') {
                    load_appointments_data(frm);
                } else if (tab === '#assessments') {
                    load_assessments_data(frm);
                } else if (tab === '#services') {
                    load_services_data(frm);
                } else if (tab === '#documents') {
                    load_documents_data(frm);
                }
            }
        });
        
        // Trigger loading of the first visible tab
        if (!frm.is_new()) {
            const activeTab = $('.form-tabs .nav-link.active');
            if (activeTab.length) {
                activeTab.trigger('shown.bs.tab');
            } else {
                load_cases_data(frm);
            }
        }
    }
});

function add_custom_buttons(frm) {
    if (!frm.is_new()) {
        // Add button to create new case
        frm.add_custom_button(__('New Case'), function() {
            frappe.new_doc('Case', {
                beneficiary: frm.doc.name
            });
        }, __('Create'));
        
        // Add button to schedule appointment
        frm.add_custom_button(__('Schedule Appointment'), function() {
            frappe.new_doc('Appointment', {
                beneficiary: frm.doc.name
            });
        }, __('Create'));
        
        // Add button to create initial assessment
        frm.add_custom_button(__('Initial Assessment'), function() {
            frappe.new_doc('Initial Assessment', {
                client_name: frm.doc.beneficiary_name,
                bc_nric_no: frm.doc.bc_nric_no
            });
        }, __('Create'));
        
        // Add button to create follow-up assessment
        frm.add_custom_button(__('Follow-up Assessment'), function() {
            frappe.new_doc('Follow Up Assessment', {
                beneficiary: frm.doc.name
            });
        }, __('Create'));
    }
}

function load_cases_data(frm) {
    // Load active cases
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Case',
            filters: {
                beneficiary: frm.doc.name
            },
            fields: ['name', 'case_title', 'case_status', 'case_priority', 'case_opened_date', 'primary_social_worker'],
            order_by: 'case_opened_date desc'
        },
        callback: function(r) {
            if (r.message) {
                render_cases_table(frm, r.message, 'active_cases_html', 'Active Cases');
            }
        }
    });
    
    // Load closed cases
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Case',
            filters: {
                beneficiary: frm.doc.name
            },
            fields: ['name', 'case_title', 'case_status', 'case_opened_date', 'actual_closure_date', 'primary_social_worker'],
            order_by: 'actual_closure_date desc',
            limit: 10
        },
        callback: function(r) {
            if (r.message) {
                render_cases_table(frm, r.message, 'closed_cases_html', 'Case History');
            }
        }
    });
}

function load_appointments_data(frm) {
    // Load upcoming appointments
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Appointment',
            filters: {
                beneficiary: frm.doc.name,
                appointment_date: ['>=', frappe.datetime.get_today()]
            },
            fields: ['name', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status', 'social_worker', 'case'],
            order_by: 'appointment_date asc'
        },
        callback: function(r) {
            if (r.message) {
                render_appointments_table(frm, r.message, 'upcoming_appointments_html', 'Upcoming Appointments');
            }
        }
    });
    
    // Load appointment history
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Appointment',
            filters: {
                beneficiary: frm.doc.name,
                appointment_date: ['<', frappe.datetime.get_today()]
            },
            fields: ['name', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status', 'social_worker', 'case'],
            order_by: 'appointment_date desc',
            limit: 20
        },
        callback: function(r) {
            if (r.message) {
                render_appointments_table(frm, r.message, 'appointment_history_html', 'Appointment History');
            }
        }
    });
}

function load_assessments_data(frm) {
    // Load initial assessments - note: linking by client_name since no beneficiary link field exists
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Initial Assessment',
            filters: {
                client_name: frm.doc.beneficiary_name
            },
            fields: ['name', 'assessment_date', 'assessed_by', 'case_no'],
            order_by: 'assessment_date desc'
        },
        callback: function(r) {
            if (r.message) {
                render_assessments_table(frm, r.message, 'initial_assessments_html', 'Initial Assessments');
            }
        }
    });
    
    // Load follow-up assessments
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Follow Up Assessment',
            filters: {
                beneficiary: frm.doc.name
            },
            fields: ['name', 'assessment_date', 'assessed_by', 'assessment_type', 'case'],
            order_by: 'assessment_date desc'
        },
        callback: function(r) {
            if (r.message) {
                render_assessments_table(frm, r.message, 'follow_up_assessments_html', 'Follow-up Assessments');
            }
        }
    });
}

function load_services_data(frm) {
    // First, get only the names to avoid field permission issues
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Service Plan',
            filters: {
                beneficiary: frm.doc.name
            },
            fields: ['name'],
            limit: 50
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                // Fetch full docs for each service plan
                let service_plans = [];
                let completed = 0;
                
                r.message.forEach(function(item) {
                    frappe.model.with_doc('Service Plan', item.name, function() {
                        let doc = frappe.model.get_doc('Service Plan', item.name);
                        if (doc) {
                            service_plans.push(doc);
                        }
                        
                        completed++;
                        if (completed === r.message.length) {
                            // Filter for active/in progress services if we want to
                            const filtered_plans = service_plans.filter(plan => 
                                ['Active', 'In Progress'].includes(plan.status || ''));
                                
                            render_services_table(frm, filtered_plans, 'current_service_plans_html', 'Current Service Plans');
                        }
                    });
                });
            } else {
                render_services_table(frm, [], 'current_service_plans_html', 'Current Service Plans');
            }
        }
    });
}

function load_documents_data(frm) {
    // First, get only the names to avoid field permission issues
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Document Attachment',
            filters: {
                beneficiary: frm.doc.name
            },
            fields: ['name'],
            limit: 50
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                // Fetch full docs for each document
                let documents = [];
                let completed = 0;
                
                r.message.forEach(function(item) {
                    frappe.model.with_doc('Document Attachment', item.name, function() {
                        let doc = frappe.model.get_doc('Document Attachment', item.name);
                        if (doc) {
                            documents.push(doc);
                        }
                        
                        completed++;
                        if (completed === r.message.length) {
                            // Sort by upload date if available
                            documents.sort(function(a, b) {
                                if (a.upload_date && b.upload_date) {
                                    return new Date(b.upload_date) - new Date(a.upload_date);
                                }
                                return 0;
                            });
                            
                            render_documents_table(frm, documents, 'document_attachments_html', 'Document Attachments');
                        }
                    });
                });
            } else {
                render_documents_table(frm, [], 'document_attachments_html', 'Document Attachments');
            }
        }
    });
}

function render_cases_table(frm, data, field_name, title) {
    // Get container ID for the field
    const container_id = {
        'active_cases_html': 'active-cases-container',
        'closed_cases_html': 'closed-cases-container'
    }[field_name] || field_name;
    
    let html = `<div class="table-responsive">
        <h5>${title}</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Case ID</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Opened Date</th>
                    <th>Social Worker</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    data.forEach(function(case_doc) {
        html += `<tr>
            <td><a href="/app/case/${case_doc.name}">${case_doc.name}</a></td>
            <td>${case_doc.case_title || ''}</td>
            <td><span class="indicator ${get_status_color(case_doc.case_status)}">${case_doc.case_status || ''}</span></td>
            <td>${case_doc.case_priority || ''}</td>
            <td>${frappe.datetime.str_to_user(case_doc.case_opened_date) || ''}</td>
            <td>${case_doc.primary_social_worker || ''}</td>
            <td>
                <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Case', '${case_doc.name}')">View</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    if (data.length === 0) {
        html = `<div><h5>${title}</h5><p class="text-muted">No cases found.</p></div>`;
    }
    
    // Insert HTML into the correct container
    insert_html(frm, field_name, container_id, html);
}

function render_appointments_table(frm, data, field_name, title) {
    // Get container ID for the field
    const container_id = {
        'upcoming_appointments_html': 'upcoming-appointments-container',
        'appointment_history_html': 'appointment-history-container'
    }[field_name] || field_name;
    
    let html = `<div class="table-responsive">
        <h5>${title}</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Appointment ID</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Status/Outcome</th>
                    <th>Social Worker</th>
                    <th>Case</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    data.forEach(function(apt) {
        html += `<tr>
            <td><a href="/app/appointment/${apt.name}">${apt.name}</a></td>
            <td>${frappe.datetime.str_to_user(apt.appointment_date) || ''}</td>
            <td>${apt.appointment_time || ''}</td>
            <td>${apt.appointment_type || ''}</td>
            <td>${apt.appointment_status || apt.appointment_outcome || ''}</td>
            <td>${apt.social_worker || ''}</td>
            <td><a href="/app/case/${apt.case}">${apt.case || ''}</a></td>
            <td>
                <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Appointment', '${apt.name}')">View</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    if (data.length === 0) {
        html = `<div><h5>${title}</h5><p class="text-muted">No appointments found.</p></div>`;
    }
    
    // Insert HTML into the correct container
    insert_html(frm, field_name, container_id, html);
}

function render_assessments_table(frm, data, field_name, title) {
    // Get container ID for the field
    const container_id = {
        'initial_assessments_html': 'initial-assessments-container',
        'follow_up_assessments_html': 'follow-up-assessments-container'
    }[field_name] || field_name;
    
    let html = `<div class="table-responsive">
        <h5>${title}</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Assessment ID</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Assessed By</th>
                    <th>Case</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    data.forEach(function(assessment) {
        let doctype = field_name.includes('initial') ? 'Initial Assessment' : 'Follow Up Assessment';
        html += `<tr>
            <td><a href="/app/${doctype.toLowerCase().replace(' ', '-')}/${assessment.name}">${assessment.name}</a></td>
            <td>${frappe.datetime.str_to_user(assessment.assessment_date) || ''}</td>
            <td>${assessment.assessment_type || 'Initial'}</td>
            <td>${assessment.assessed_by || ''}</td>
            <td><a href="/app/case/${assessment.case_no || assessment.case}">${assessment.case_no || assessment.case || ''}</a></td>
            <td>
                <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', '${doctype}', '${assessment.name}')">View</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    if (data.length === 0) {
        html = `<div><h5>${title}</h5><p class="text-muted">No assessments found.</p></div>`;
    }
    
    // Insert HTML into the correct container
    insert_html(frm, field_name, container_id, html);
}

function render_services_table(frm, data, field_name, title) {
    // Get container ID for the field
    const container_id = {
        'current_service_plans_html': 'current-service-plans-container',
        'past_service_plans_html': 'past-service-plans-container'
    }[field_name] || field_name;

    let html = `<div class="table-responsive">
        <h5>${title}</h5>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Service Plan ID</th>
                    <th>Plan Name</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Status</th>
                    <th>Social Worker</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (data.length === 0) {
        html += `<tr><td colspan="7" class="text-center">No service plans found</td></tr>`;
    } else {
        data.forEach(function(service) {
            html += `<tr>
                <td><a href="/app/service-plan/${service.name}">${service.name}</a></td>
                <td>${service.plan_name || service.name}</td>
                <td>${service.start_date ? frappe.datetime.str_to_user(service.start_date) : '-'}</td>
                <td>${service.end_date ? frappe.datetime.str_to_user(service.end_date) : '-'}</td>
                <td><span class="indicator ${get_status_color(service.status)}">${service.status || ''}</span></td>
                <td>${service.assigned_social_worker || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Service Plan', '${service.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    insert_html(frm, field_name, container_id, html);
}

function render_documents_table(frm, data, field_name, title) {
    // Get container ID for the field
    const container_id = {
        'document_attachments_html': 'document-attachments-container'
    }[field_name] || field_name;
    
    let html = `<div class="table-responsive">
        <h5>${title}</h5>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Document Name</th>
                    <th>Type</th>
                    <th>Upload Date</th>
                    <th>Uploaded By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (data.length === 0) {
        html += `<tr><td colspan="5" class="text-center">No documents found</td></tr>`;
    } else {
        data.forEach(function(doc) {
            html += `<tr>
                <td><a href="/app/document-attachment/${doc.name}">${doc.document_name || doc.name}</a></td>
                <td>${doc.document_type || ''}</td>
                <td>${doc.upload_date ? frappe.datetime.str_to_user(doc.upload_date) : '-'}</td>
                <td>${doc.uploaded_by || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Document Attachment', '${doc.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    insert_html(frm, field_name, container_id, html);
}

// Helper function to insert HTML into the correct container
function insert_html(frm, field_name, container_id, html) {
    const $wrapper = frm.fields_dict[field_name].$wrapper;
    const $container = $wrapper.find('#' + container_id);
    
    if ($container.length) {
        $container.html(html);
    } else {
        $wrapper.html('<div id="' + container_id + '">' + html + '</div>');
    }
}

// Initialize containers for all tab content
function initialize_tab_containers(frm) {
    // Ensure all HTML fields have container divs
    const html_fields = [
        { field: 'active_cases_html', container: 'active-cases-container' },
        { field: 'closed_cases_html', container: 'closed-cases-container' },
        { field: 'upcoming_appointments_html', container: 'upcoming-appointments-container' },
        { field: 'appointment_history_html', container: 'appointment-history-container' },
        { field: 'initial_assessments_html', container: 'initial-assessments-container' },
        { field: 'follow_up_assessments_html', container: 'follow-up-assessments-container' },
        { field: 'current_service_plans_html', container: 'current-service-plans-container' },
        { field: 'document_attachments_html', container: 'document-attachments-container' }
    ];
    
    html_fields.forEach(function(item) {
        if (frm.fields_dict[item.field]) {
            const $wrapper = frm.fields_dict[item.field].$wrapper;
            const $container = $wrapper.find('#' + item.container);
            
            if (!$container.length) {
                $wrapper.html('<div id="' + item.container + '"><p class="text-muted">Loading...</p></div>');
            }
        }
    });
}

function get_status_color(status) {
    const status_colors = {
        'Active': 'green',
        'Open': 'blue',
        'In Progress': 'orange',
        'Under Review': 'yellow',
        'Completed': 'green',
        'Closed': 'gray',
        'Cancelled': 'red'
    };
    return status_colors[status] || 'blue';
}

// Custom function to calculate age from date of birth
function calculate_age(dob) {
    if (!dob) return 0;
    
    const birth_date = new Date(dob);
    const today = new Date();
    
    let age = today.getFullYear() - birth_date.getFullYear();
    const month_diff = today.getMonth() - birth_date.getMonth();
    
    if (month_diff < 0 || (month_diff === 0 && today.getDate() < birth_date.getDate())) {
        age--;
    }
    
    return age;
}

// Geocoding function for postal code changes
function geocode_postal_code(frm, postal_code) {
    frappe.call({
        method: 'rdss_social_work.geocoding_utils.geocode_address_api',
        args: {
            address_line_1: frm.doc.address_line_1 || 'Singapore',
            address_line_2: frm.doc.address_line_2,
            postal_code: postal_code,
            country: 'Singapore'
        },
        callback: function(r) {
            if (r.message) {
                // Update geolocation field with the returned GeoJSON
                frm.set_value('geolocation', r.message);
                
                // Show success notification
                frappe.show_alert({
                    message: __('Location coordinates updated successfully!'),
                    indicator: 'green'
                }, 3);
            } else {
                // Show error notification
                frappe.show_alert({
                    message: __('Could not geocode postal code: {0}. Please check if it\'s valid.', [postal_code]),
                    indicator: 'red'
                }, 5);
            }
        },
        error: function(r) {
            // Show error notification
            frappe.show_alert({
                message: __('Error updating location coordinates. Please try again.'),
                indicator: 'red'
            }, 5);
            console.error('Geocoding error:', r);
        }
    });
}
