frappe.ui.form.on('Beneficiary Family', {
    refresh: function(frm) {
        // Load all tab data
        if (!frm.is_new()) {
            load_family_members(frm);
            load_family_cases(frm);
            load_family_appointments(frm);
            load_family_case_notes(frm);
        }
    },
    
    onload: function(frm) {
        // Initialize HTML containers for tabs
        initialize_family_tab_containers(frm);
        
        // Force refresh on tab change to ensure content loads correctly
        $('.form-tabs .nav-link').on('shown.bs.tab', function(e) {
            if (!frm.is_new()) {
                const tab = $(e.target).attr('data-target');
                if (tab === '#case-management') {
                    load_family_cases(frm);
                } else if (tab === '#appointments') {
                    load_family_appointments(frm);
                } else if (tab === '#case-notes') {
                    load_family_case_notes(frm);
                } else if (tab === '#family-members') {
                    load_family_members(frm);
                }
            }
        });
    }
});

function load_family_members(frm) {
    frappe.call({
        method: 'rdss_social_work.rdss_social_work.doctype.beneficiary_family.beneficiary_family_queries.get_family_members',
        args: { family_name: frm.doc.name },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                render_family_members_table(frm, r.message);
            } else {
                render_family_members_table(frm, []);
            }
        }
    });
}

function render_family_members_table(frm, members) {
    let html = `<div class="table-responsive">
        <h5>Family Members (${members.length})</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Relationship</th>
                    <th>Gender</th>
                    <th>Date of Birth</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (members.length === 0) {
        html += `<tr><td colspan="6" class="text-center text-muted">No family members found</td></tr>`;
    } else {
        members.forEach(function(member) {
            html += `<tr>
                <td><a href="/app/beneficiary/${member.name}">${member.beneficiary_name}</a></td>
                <td>${member.family_relationship || ''}</td>
                <td>${member.gender || ''}</td>
                <td>${member.date_of_birth ? frappe.datetime.str_to_user(member.date_of_birth) : ''}</td>
                <td><span class="indicator ${get_status_color(member.current_status)}">${member.current_status || ''}</span></td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Beneficiary', '${member.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    // Insert into family members container
    const $wrapper = frm.fields_dict.family_members_html.$wrapper;
    if ($wrapper) {
        $wrapper.html(html);
    }
}

function load_family_cases(frm) {
    frappe.call({
        method: 'rdss_social_work.rdss_social_work.doctype.beneficiary_family.beneficiary_family_queries.get_family_cases',
        args: { family_name: frm.doc.name },
        callback: function(r) {
            render_family_cases_table(frm, r.message || []);
        }
    });
}

function load_family_appointments(frm) {
    frappe.call({
        method: 'rdss_social_work.rdss_social_work.doctype.beneficiary_family.beneficiary_family_queries.get_family_appointments',
        args: { family_name: frm.doc.name },
        callback: function(r) {
            render_family_appointments_table(frm, r.message || []);
        }
    });
}

function load_family_case_notes(frm) {
    frappe.call({
        method: 'rdss_social_work.rdss_social_work.doctype.beneficiary_family.beneficiary_family_queries.get_family_case_notes',
        args: { family_name: frm.doc.name },
        callback: function(r) {
            render_family_case_notes_table(frm, r.message || []);
        }
    });
}

function render_family_cases_table(frm, cases) {
    let html = `<div class="table-responsive">
        <h5>Family Cases (${cases.length})</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Case ID</th>
                    <th>Title</th>
                    <th>Beneficiary</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Opened Date</th>
                    <th>Social Worker</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (cases.length === 0) {
        html += `<tr><td colspan="8" class="text-center text-muted">No cases found for this family</td></tr>`;
    } else {
        cases.forEach(function(case_doc) {
            html += `<tr>
                <td><a href="/app/case/${case_doc.name}">${case_doc.name}</a></td>
                <td>${case_doc.case_title || ''}</td>
                <td><a href="/app/beneficiary/${case_doc.beneficiary}">${case_doc.beneficiary}</a></td>
                <td><span class="indicator ${get_status_color(case_doc.case_status)}">${case_doc.case_status || ''}</span></td>
                <td><span class="indicator ${get_priority_color(case_doc.case_priority)}">${case_doc.case_priority || ''}</span></td>
                <td>${case_doc.case_opened_date ? frappe.datetime.str_to_user(case_doc.case_opened_date) : ''}</td>
                <td>${case_doc.primary_social_worker || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Case', '${case_doc.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    const $wrapper = frm.fields_dict.family_cases_html.$wrapper;
    if ($wrapper) {
        $wrapper.html(html);
    }
}

function render_family_appointments_table(frm, appointments) {
    let html = `<div class="table-responsive">
        <h5>Family Appointments (${appointments.length})</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Appointment ID</th>
                    <th>Beneficiary</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Social Worker</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (appointments.length === 0) {
        html += `<tr><td colspan="8" class="text-center text-muted">No appointments found for this family</td></tr>`;
    } else {
        appointments.forEach(function(apt) {
            html += `<tr>
                <td><a href="/app/appointment/${apt.name}">${apt.name}</a></td>
                <td><a href="/app/beneficiary/${apt.beneficiary}">${apt.beneficiary}</a></td>
                <td>${apt.appointment_date ? frappe.datetime.str_to_user(apt.appointment_date) : ''}</td>
                <td>${apt.appointment_time || ''}</td>
                <td>${apt.appointment_type || ''}</td>
                <td><span class="indicator ${get_status_color(apt.appointment_status)}">${apt.appointment_status || ''}</span></td>
                <td>${apt.social_worker || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Appointment', '${apt.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    const $wrapper = frm.fields_dict.family_appointments_html.$wrapper;
    if ($wrapper) {
        $wrapper.html(html);
    }
}

function render_family_case_notes_table(frm, cases) {
    let html = `<div class="table-responsive">
        <h5>Family Case Notes (${cases.length})</h5>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Case ID</th>
                    <th>Title</th>
                    <th>Beneficiary</th>
                    <th>Status</th>
                    <th>Opened Date</th>
                    <th>Social Worker</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
    
    if (cases.length === 0) {
        html += `<tr><td colspan="7" class="text-center text-muted">No case notes found for this family</td></tr>`;
    } else {
        cases.forEach(function(case_doc) {
            html += `<tr>
                <td><a href="/app/case/${case_doc.name}">${case_doc.name}</a></td>
                <td>${case_doc.case_title || ''}</td>
                <td><a href="/app/beneficiary/${case_doc.beneficiary}">${case_doc.beneficiary}</a></td>
                <td><span class="indicator ${get_status_color(case_doc.case_status)}">${case_doc.case_status || ''}</span></td>
                <td>${case_doc.case_opened_date ? frappe.datetime.str_to_user(case_doc.case_opened_date) : ''}</td>
                <td>${case_doc.primary_social_worker || ''}</td>
                <td>
                    <button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'Case', '${case_doc.name}')">View</button>
                </td>
            </tr>`;
        });
    }
    
    html += '</tbody></table></div>';
    
    const $wrapper = frm.fields_dict.family_case_notes_html.$wrapper;
    if ($wrapper) {
        $wrapper.html(html);
    }
}

function initialize_family_tab_containers(frm) {
    const html_fields = [
        { field: 'family_members_html', container: 'family-members-container' },
        { field: 'family_cases_html', container: 'family-cases-container' },
        { field: 'family_appointments_html', container: 'family-appointments-container' },
        { field: 'family_case_notes_html', container: 'family-case-notes-container' }
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

function get_priority_color(priority) {
    const priority_colors = {
        'High': 'red',
        'Medium': 'orange', 
        'Low': 'green'
    };
    return priority_colors[priority] || 'blue';
}

function get_status_color(status) {
    const status_colors = {
        'Active': 'green',
        'Inactive': 'red',
        'Transferred': 'orange',
        'On Hold': 'yellow',
        'Open': 'blue',
        'In Progress': 'orange',
        'Completed': 'green',
        'Closed': 'gray',
        'Cancelled': 'red'
    };
    return status_colors[status] || 'blue';
}
