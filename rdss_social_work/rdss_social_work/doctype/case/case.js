frappe.ui.form.on('Case', {
    refresh: function(frm) {
        // Load related data in tabs
        if (!frm.is_new()) {
            load_case_appointments(frm);
            load_case_assessments(frm);
            load_case_timeline(frm);
            check_appointment_frequency(frm);
        }
        
        // Add custom buttons
        add_case_custom_buttons(frm);
        
        // Display priority badge
        set_priority_indicator(frm);
    },
    
    case_priority: function(frm) {
        // Update priority badge when priority changes
        set_priority_indicator(frm);
    },
    
    beneficiary: function(frm) {
        // Auto-populate beneficiary details when beneficiary is selected
        if (frm.doc.beneficiary) {
            frappe.db.get_value('Beneficiary', frm.doc.beneficiary, 'beneficiary_name')
                .then(r => {
                    if (r.message && r.message.beneficiary_name) {
                        frm.set_value('case_title', `Case for ${r.message.beneficiary_name}`);
                    }
                });
        }
    }
});

function add_case_custom_buttons(frm) {
    if (!frm.is_new()) {
        // Add button to schedule appointment
        frm.add_custom_button(__('Schedule Appointment'), function() {
            frappe.new_doc('Appointment', {
                case: frm.doc.name,
                beneficiary: frm.doc.beneficiary
            });
        }, __('Create'));
        
        // Add button to create initial assessment
        frm.add_custom_button(__('Initial Assessment'), function() {
            frappe.new_doc('Initial Assessment', {
                case_no: frm.doc.name,
                beneficiary: frm.doc.beneficiary
            });
        }, __('Create'));
        
        // Add button to create follow-up assessment
        frm.add_custom_button(__('Follow-up Assessment'), function() {
            frappe.new_doc('Follow Up Assessment', {
                case: frm.doc.name,
                beneficiary: frm.doc.beneficiary
            });
        }, __('Create'));
        
        // Add button to create service plan
        frm.add_custom_button(__('Service Plan'), function() {
            frappe.new_doc('Service Plan', {
                beneficiary: frm.doc.beneficiary,
                case: frm.doc.name
            });
        }, __('Create'));
    }
}

function load_case_appointments(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Appointment',
            filters: {
                case: frm.doc.name
            },
            fields: ['name', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status', 'appointment_outcome', 'social_worker'],
            order_by: 'appointment_date desc'
        },
        callback: function(r) {
            if (r.message) {
                render_case_appointments_table(frm, r.message);
            }
        }
    });
}

function load_case_assessments(frm) {
    // Load initial assessments
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Initial Assessment',
            filters: {
                case_no: frm.doc.name
            },
            fields: ['name', 'assessment_date', 'assessed_by', 'client_name'],
            order_by: 'assessment_date desc'
        },
        callback: function(r) {
            let initial_assessments = r.message || [];
            
            // Load follow-up assessments
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Follow Up Assessment',
                    filters: {
                        case: frm.doc.name
                    },
                    fields: ['name', 'assessment_date', 'assessed_by', 'assessment_type'],
                    order_by: 'assessment_date desc'
                },
                callback: function(r2) {
                    let followup_assessments = r2.message || [];
                    render_case_assessments_table(frm, initial_assessments, followup_assessments);
                }
            });
        }
    });
}

function load_case_timeline(frm) {
    // Create a comprehensive timeline of all case activities
    let timeline_data = [];
    
    // Get appointments
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Appointment',
            filters: {
                case: frm.doc.name
            },
            fields: ['name', 'appointment_date', 'appointment_type', 'appointment_status', 'appointment_outcome'],
            order_by: 'appointment_date desc'
        },
        callback: function(r) {
            if (r.message) {
                r.message.forEach(function(apt) {
                    timeline_data.push({
                        date: apt.appointment_date,
                        type: 'Appointment',
                        title: `${apt.appointment_type} Appointment`,
                        status: apt.appointment_status || apt.appointment_outcome,
                        link: `/app/appointment/${apt.name}`,
                        id: apt.name
                    });
                });
            }
            
            // Get assessments and render timeline
            get_assessments_for_timeline(frm, timeline_data);
        }
    });
}

function get_assessments_for_timeline(frm, timeline_data) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Initial Assessment',
            filters: {
                case_no: frm.doc.name
            },
            fields: ['name', 'assessment_date'],
            order_by: 'assessment_date desc'
        },
        callback: function(r) {
            if (r.message) {
                r.message.forEach(function(assessment) {
                    timeline_data.push({
                        date: assessment.assessment_date,
                        type: 'Assessment',
                        title: 'Initial Assessment',
                        status: 'Completed',
                        link: `/app/initial-assessment/${assessment.name}`,
                        id: assessment.name
                    });
                });
            }
            
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Follow Up Assessment',
                    filters: {
                        case: frm.doc.name
                    },
                    fields: ['name', 'assessment_date', 'assessment_type'],
                    order_by: 'assessment_date desc'
                },
                callback: function(r2) {
                    if (r2.message) {
                        r2.message.forEach(function(assessment) {
                            timeline_data.push({
                                date: assessment.assessment_date,
                                type: 'Assessment',
                                title: `${assessment.assessment_type} Assessment`,
                                status: 'Completed',
                                link: `/app/follow-up-assessment/${assessment.name}`,
                                id: assessment.name
                            });
                        });
                    }
                    
                    // Sort timeline by date and render
                    timeline_data.sort((a, b) => new Date(b.date) - new Date(a.date));
                    render_case_timeline(frm, timeline_data);
                }
            });
        }
    });
}

function render_case_appointments_table(frm, data) {
    let html = `<div class="table-responsive">
        <h5>Case Appointments</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Appointment ID</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Status/Outcome</th>
                    <th>Social Worker</th>
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
            <td>
                <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Appointment', '${apt.name}')">View</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    if (data.length === 0) {
        html = '<div><h5>Case Appointments</h5><p class="text-muted">No appointments found for this case.</p></div>';
    }
    
    frm.fields_dict.case_appointments_html.$wrapper.html(html);
}

function render_case_assessments_table(frm, initial_assessments, followup_assessments) {
    let html = `<div class="table-responsive">
        <h5>Case Assessments</h5>`;
    
    if (initial_assessments.length > 0) {
        html += `<h6>Initial Assessments</h6>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Assessment ID</th>
                    <th>Date</th>
                    <th>Assessed By</th>
                    <th>Client Name</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
        
        initial_assessments.forEach(function(assessment) {
            html += `<tr>
                <td><a href="/app/initial-assessment/${assessment.name}">${assessment.name}</a></td>
                <td>${frappe.datetime.str_to_user(assessment.assessment_date) || ''}</td>
                <td>${assessment.assessed_by || ''}</td>
                <td>${assessment.client_name || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Initial Assessment', '${assessment.name}')">View</button>
                </td>
            </tr>`;
        });
        
        html += '</tbody></table>';
    }
    
    if (followup_assessments.length > 0) {
        html += `<h6>Follow-up Assessments</h6>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Assessment ID</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Assessed By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
        
        followup_assessments.forEach(function(assessment) {
            html += `<tr>
                <td><a href="/app/follow-up-assessment/${assessment.name}">${assessment.name}</a></td>
                <td>${frappe.datetime.str_to_user(assessment.assessment_date) || ''}</td>
                <td>${assessment.assessment_type || ''}</td>
                <td>${assessment.assessed_by || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Follow Up Assessment', '${assessment.name}')">View</button>
                </td>
            </tr>`;
        });
        
        html += '</tbody></table>';
    }
    
    html += '</div>';
    
    if (initial_assessments.length === 0 && followup_assessments.length === 0) {
        html = '<div><h5>Case Assessments</h5><p class="text-muted">No assessments found for this case.</p></div>';
    }
    
    frm.fields_dict.case_assessments_html.$wrapper.html(html);
}

function render_case_timeline(frm, timeline_data) {
    let html = `<div class="timeline-container">
        <h5>Case Timeline</h5>`;
    
    if (timeline_data.length > 0) {
        html += '<div class="timeline">';
        
        timeline_data.forEach(function(item, index) {
            html += `<div class="timeline-item">
                <div class="timeline-marker ${get_timeline_color(item.type)}"></div>
                <div class="timeline-content">
                    <div class="timeline-date">${frappe.datetime.str_to_user(item.date)}</div>
                    <div class="timeline-title">
                        <a href="${item.link}">${item.title}</a>
                        <span class="badge badge-${get_status_badge_color(item.status)}">${item.status}</span>
                    </div>
                    <div class="timeline-type">${item.type} - ${item.id}</div>
                </div>
            </div>`;
        });
        
        html += '</div>';
    } else {
        html += '<p class="text-muted">No timeline data available for this case.</p>';
    }
    
    html += `</div>
    <style>
        .timeline { position: relative; padding-left: 30px; }
        .timeline-item { position: relative; margin-bottom: 20px; }
        .timeline-marker { 
            position: absolute; 
            left: -35px; 
            top: 5px; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            border: 2px solid #fff;
            box-shadow: 0 0 0 2px #ddd;
        }
        .timeline-marker.appointment { background-color: #007bff; }
        .timeline-marker.assessment { background-color: #28a745; }
        .timeline-content { background: #f8f9fa; padding: 10px; border-radius: 4px; }
        .timeline-date { font-size: 12px; color: #6c757d; }
        .timeline-title { font-weight: bold; margin: 5px 0; }
        .timeline-type { font-size: 12px; color: #6c757d; }
    </style>`;
    
    frm.fields_dict.case_timeline_html.$wrapper.html(html);
}

function get_timeline_color(type) {
    return type.toLowerCase();
}

function get_status_badge_color(status) {
    const status_colors = {
        'Completed': 'success',
        'Scheduled': 'primary',
        'Cancelled': 'danger',
        'No Show': 'warning'
    };
    return status_colors[status] || 'secondary';
}

function set_priority_indicator(frm) {
    if (!frm.doc.case_priority) return;
    
    frappe.db.get_doc('Case Priority', frm.doc.case_priority)
        .then(priority => {
            if (priority) {
                // Set the indicator color in the form header with both code and name
                const priorityLabel = `${priority.priority_code} - ${priority.priority_name}`;
                frm.page.set_indicator(priorityLabel, priority.color_code);
                
                // Add priority info to the form dashboard
                if (frm.dashboard) {
                    frm.dashboard.add_comment(__(`Priority: ${priorityLabel}`), 'blue');
                    frm.dashboard.add_comment(
                        __(`Appointment Frequency: Every ${priority.appointment_frequency_months} month(s)`), 
                        'blue'
                    );
                }
            }
        });
}

function check_appointment_frequency(frm) {
    if (!frm.doc.case_priority) return;
    
    frappe.db.get_doc('Case Priority', frm.doc.case_priority)
        .then(priority => {
            if (priority && frm.doc.last_contact_date) {
                let lastContact = frappe.datetime.str_to_obj(frm.doc.last_contact_date);
                let today = frappe.datetime.now_date();
                let months = frappe.datetime.month_diff(today, lastContact);
                
                let requiredFrequency = priority.appointment_frequency_months;
                
                if (months >= requiredFrequency) {
                    frm.dashboard.set_headline_alert(
                        `<div class="alert alert-danger">
                            <strong>Appointment Overdue!</strong> Based on priority ${priority.priority_code}, 
                            an appointment was due ${months - requiredFrequency + 1} month(s) ago.
                            <button class="btn btn-xs btn-primary ml-2" 
                                onclick="frappe.new_doc('Appointment', {case: '${frm.doc.name}', beneficiary: '${frm.doc.beneficiary}'})">
                                Schedule Now
                            </button>
                        </div>`
                    );
                } else if (months >= requiredFrequency - 1) {
                    frm.dashboard.set_headline_alert(
                        `<div class="alert alert-warning">
                            <strong>Appointment Due Soon!</strong> Based on priority ${priority.priority_code}, 
                            an appointment will be due in ${requiredFrequency - months} month(s).
                            <button class="btn btn-xs btn-primary ml-2" 
                                onclick="frappe.new_doc('Appointment', {case: '${frm.doc.name}', beneficiary: '${frm.doc.beneficiary}'})">
                                Schedule Now
                            </button>
                        </div>`
                    );
                }
            }
        });
}
