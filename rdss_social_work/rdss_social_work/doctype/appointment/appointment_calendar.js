frappe.views.calendar["Appointment"] = {
	field_map: {
		"start": "appointment_date",
		"end": "appointment_date", 
		"id": "name",
		"title": "purpose",
		"allDay": false
	},
	gantt: false,
	get_events_method: "frappe.desk.calendar.get_events",
	filters: [
		{
			"fieldname": "appointment_status",
			"fieldtype": "Select",
			"label": __("Status"),
			"options": "\nScheduled\nConfirmed\nIn Progress\nCompleted\nCancelled\nNo Show\nRescheduled"
		},
		{
			"fieldname": "social_worker", 
			"fieldtype": "Link",
			"label": __("Social Worker"),
			"options": "User"
		},
		{
			"fieldname": "appointment_type",
			"fieldtype": "Select", 
			"label": __("Type"),
			"options": "\nInitial Assessment\nFollow Up Assessment\nCase Review\nService Planning\nCrisis Intervention\nFamily Meeting\nHome Visit\nOffice Visit\nPhone Consultation\nVideo Call\nOther"
		}
	],
	get_css_class: function(data) {
		if (data.appointment_status === "Cancelled" || data.appointment_status === "No Show") {
			return "danger";
		} else if (data.appointment_status === "Completed") {
			return "success";
		} else if (data.appointment_status === "In Progress") {
			return "warning";
		} else if (data.appointment_status === "Confirmed") {
			return "info";
		}
		return "";
	},
	get_events: function(start, end, filters, callback) {
		frappe.call({
			method: "frappe.desk.calendar.get_events",
			args: {
				doctype: "Appointment",
				start: start,
				end: end,
				field_map: {
					"start": "appointment_date",
					"end": "appointment_date",
					"id": "name", 
					"title": "purpose",
					"allDay": false
				},
				filters: filters
			},
			callback: function(r) {
				var events = r.message || [];
				// Process events to add time and duration
				events = events.map(function(event) {
					if (event.appointment_time && event.duration_minutes) {
						// Combine date and time for proper start datetime
						var start_datetime = moment(event.start + " " + event.appointment_time);
						event.start = start_datetime.format();
						
						// Calculate end time based on duration
						var end_datetime = start_datetime.clone().add(event.duration_minutes || 60, 'minutes');
						event.end = end_datetime.format();
						
						// Enhanced title with beneficiary and time
						if (event.beneficiary) {
							event.title = event.beneficiary + " - " + (event.purpose || "Appointment");
						}
						event.title += " (" + moment(event.appointment_time, "HH:mm:ss").format("HH:mm") + ")";
					}
					return event;
				});
				callback(events);
			}
		});
	}
};
