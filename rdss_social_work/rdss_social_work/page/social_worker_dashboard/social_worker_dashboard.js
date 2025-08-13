frappe.pages['social-worker-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Social Worker Dashboard',
        single_column: true
    });

    page.main.html(frappe.render_template("social_worker_dashboard"));
    
    // Load dashboard data
    load_dashboard_data();
    
    // Refresh every 5 minutes
    setInterval(load_dashboard_data, 300000);
};

function load_dashboard_data() {
    frappe.call({
        method: "rdss_social_work.rdss_social_work.page.social_worker_dashboard.social_worker_dashboard.get_dashboard_data",
        callback: function(r) {
            if (r.message) {
                update_dashboard(r.message);
            }
        }
    });
}

function update_dashboard(data) {
    // Update stats
    $("#active-cases").text(data.stats.active_cases);
    $("#today-appointments").text(data.stats.today_appointments);
    $("#pending-tasks").text(data.stats.pending_tasks);
    $("#month-visits").text(data.stats.this_month_visits);
    
    // Update today's schedule
    var schedule_html = "";
    if (data.today_appointments.length === 0) {
        schedule_html = "<div class='text-muted'>No appointments scheduled for today</div>";
    } else {
        data.today_appointments.forEach(function(apt) {
            schedule_html += `
                <div class="schedule-item">
                    <div class="schedule-time">${apt.appointment_time}</div>
                    <div class="schedule-details">
                        <strong>${apt.beneficiary}</strong><br>
                        <small>${apt.appointment_type} - ${apt.purpose}</small>
                    </div>
                    <div class="schedule-actions">
                        <button class="btn btn-sm btn-primary" onclick="open_appointment('${apt.name}')">View</button>
                    </div>
                </div>
            `;
        });
    }
    $("#today-schedule").html(schedule_html);
    
    // Update pending tasks
    var tasks_html = "";
    if (data.pending_tasks.length === 0) {
        tasks_html = "<div class='text-muted'>No pending tasks</div>";
    } else {
        data.pending_tasks.forEach(function(task) {
            var priority_class = task.priority === "High" ? "label-danger" : "label-warning";
            tasks_html += `
                <div class="task-item">
                    <div class="task-details">
                        <strong>${task.type}</strong><br>
                        <small>${task.beneficiary} - Due: ${task.due_date}</small>
                        <span class="label ${priority_class}">${task.priority}</span>
                    </div>
                    <div class="task-actions">
                        <button class="btn btn-sm btn-success" onclick="complete_task('${task.type}', '${task.name}')">Complete</button>
                    </div>
                </div>
            `;
        });
    }
    $("#pending-tasks").html(tasks_html);
    
    // Update case alerts
    var alerts_html = "";
    if (data.case_alerts.length === 0) {
        alerts_html = "<div class='text-muted'>No urgent cases</div>";
    } else {
        data.case_alerts.forEach(function(alert) {
            var priority_class = alert.priority === "Critical" ? "alert-danger" : "alert-warning";
            alerts_html += `
                <div class="alert ${priority_class} alert-sm">
                    <strong>${alert.beneficiary}</strong><br>
                    <small>Priority: ${alert.priority} | Status: ${alert.case_status}</small>
                    <button class="btn btn-sm btn-default pull-right" onclick="open_case('${alert.name}')">View Case</button>
                </div>
            `;
        });
    }
    $("#case-alerts").html(alerts_html);
    
    // Update recent activity
    var activity_html = "";
    if (data.recent_activity.length === 0) {
        activity_html = "<div class='text-muted'>No recent activity</div>";
    } else {
        data.recent_activity.forEach(function(activity) {
            activity_html += `
                <div class="activity-item">
                    <div class="activity-details">
                        <strong>${activity.beneficiary}</strong><br>
                        <small>${activity.visit_type} on ${activity.visit_date}</small>
                    </div>
                    <div class="activity-actions">
                        <button class="btn btn-sm btn-default" onclick="open_case_notes('${activity.name}')">View</button>
                    </div>
                </div>
            `;
        });
    }
    $("#recent-activity").html(activity_html);
}

function open_appointment(name) {
    frappe.set_route("Form", "Appointment", name);
}

function open_case(name) {
    frappe.set_route("Form", "Case", name);
}

function open_case_notes(name) {
    frappe.set_route("Form", "Case Notes", name);
}

function complete_task(task_type, task_name) {
    frappe.call({
        method: "rdss_social_work.rdss_social_work.page.social_worker_dashboard.social_worker_dashboard.mark_task_complete",
        args: {
            task_type: task_type,
            task_name: task_name
        },
        callback: function(r) {
            if (r.message.success) {
                frappe.show_alert({message: r.message.message, indicator: 'green'});
                load_dashboard_data(); // Refresh data
            } else {
                frappe.show_alert({message: r.message.message, indicator: 'red'});
            }
        }
    });
}
