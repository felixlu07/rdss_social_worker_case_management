// Copyright (c) 2025, RDSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Initial Assessment', {
	refresh: function(frm) {
		// Make form mobile-friendly
		frm.page.body.addClass('mobile-friendly-form');
		
		// Add custom CSS for better mobile experience
		if (!$('#mobile-form-css').length) {
			$('<style id="mobile-form-css">')
				.text(`
					.mobile-friendly-form .form-section {
						margin-bottom: 20px;
					}
					.mobile-friendly-form .form-column {
						margin-bottom: 15px;
					}
					@media (max-width: 768px) {
						.mobile-friendly-form .form-grid {
							overflow-x: auto;
						}
						.mobile-friendly-form .btn {
							width: 100%;
							margin-bottom: 10px;
						}
						.mobile-friendly-form .form-control {
							font-size: 16px; /* Prevents zoom on iOS */
						}
					}
				`)
				.appendTo('head');
		}
		
		// Set default values
		if (frm.is_new()) {
			frm.set_value('assessment_date', frappe.datetime.get_today());
			frm.set_value('assessed_by', frappe.session.user);
		}
		
		// Add quick action buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('Print Assessment'), function() {
				frappe.utils.print(
					frm.doctype,
					frm.docname,
					null,
					null,
					null,
					'Initial Assessment Print Format'
				);
			});
			
			frm.add_custom_button(__('Create Follow-up'), function() {
				frappe.new_doc('Initial Assessment', {
					'client_name': frm.doc.client_name,
					'bc_nric_no': frm.doc.bc_nric_no,
					'age_category': frm.doc.age_category
				});
			});
		}
		
		// Progress indicator
		add_progress_indicator(frm);
	},
	
	client_name: function(frm) {
		// Auto-generate case number based on client name
		if (frm.doc.client_name && !frm.doc.case_no) {
			let initials = frm.doc.client_name.split(' ').map(name => name.charAt(0)).join('');
			let date = frappe.datetime.get_today().replace(/-/g, '');
			frm.set_value('case_no', `${initials}-${date}`);
		}
	},
	
	medicine_compliance: function(frm) {
		// Show/hide reason field based on compliance
		if (frm.doc.medicine_compliance === 'Irregular') {
			frm.set_df_property('medicine_compliance_reason', 'reqd', 1);
		} else {
			frm.set_df_property('medicine_compliance_reason', 'reqd', 0);
			frm.set_value('medicine_compliance_reason', '');
		}
	},
	
	assessment_decision: function(frm) {
		// Handle conditional fields based on assessment decision
		if (frm.doc.assessment_decision === 'Reject') {
			frm.set_df_property('reject_reason', 'reqd', 1);
			frm.set_df_property('refer_to', 'reqd', 0);
			frm.set_value('refer_to', '');
		} else if (frm.doc.assessment_decision === 'Refer to') {
			frm.set_df_property('refer_to', 'reqd', 1);
			frm.set_df_property('reject_reason', 'reqd', 0);
			frm.set_value('reject_reason', '');
		} else {
			frm.set_df_property('reject_reason', 'reqd', 0);
			frm.set_df_property('refer_to', 'reqd', 0);
			frm.set_value('reject_reason', '');
			frm.set_value('refer_to', '');
		}
		
		// Auto-set decision date if not already set
		if (frm.doc.assessment_decision && !frm.doc.decision_date_of_assessment) {
			frm.set_value('decision_date_of_assessment', frappe.datetime.get_today());
		}
		
		// Auto-set decision assessed by if not already set
		if (frm.doc.assessment_decision && !frm.doc.decision_assessed_by) {
			frm.set_value('decision_assessed_by', frappe.session.user);
		}
	},
	
	before_save: function(frm) {
		// Validate required ADL assessments
		validate_adl_completion(frm);
	}
});

frappe.ui.form.on('Initial Assessment Next of Kin Link', {
	next_of_kin: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.next_of_kin) {
			// Auto-populate relationship context from linked Next of Kin record
			frappe.db.get_doc('Next of Kin', row.next_of_kin).then(doc => {
				if (doc.relationship_to_beneficiary) {
					frappe.model.set_value(cdt, cdn, 'relationship_context', doc.relationship_to_beneficiary);
				}
			});
		}
	}
});

function add_progress_indicator(frm) {
	// Calculate completion percentage
	let total_fields = 0;
	let completed_fields = 0;
	
	// Count required fields
	frm.meta.fields.forEach(field => {
		if (field.reqd || ['mobility', 'washing_bathing', 'dressing', 'feeding', 'toileting', 'transferring'].includes(field.fieldname)) {
			total_fields++;
			if (frm.doc[field.fieldname]) {
				completed_fields++;
			}
		}
	});
	
	// Check if next of kin is provided
	if (frm.doc.next_of_kin_contacts && frm.doc.next_of_kin_contacts.length > 0) {
		completed_fields++;
	}
	total_fields++;
	
	let percentage = Math.round((completed_fields / total_fields) * 100);
	
	// Add progress bar
	if (!frm.progress_area) {
		frm.progress_area = $(`
			<div class="progress-indicator" style="margin: 15px 0;">
				<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
					<span>Assessment Completion</span>
					<span class="progress-text">${percentage}%</span>
				</div>
				<div class="progress" style="height: 8px;">
					<div class="progress-bar" role="progressbar" 
						 style="width: ${percentage}%; background-color: ${percentage === 100 ? '#28a745' : '#007bff'};">
					</div>
				</div>
			</div>
		`).insertAfter(frm.toolbar);
	} else {
		frm.progress_area.find('.progress-text').text(`${percentage}%`);
		frm.progress_area.find('.progress-bar').css({
			'width': `${percentage}%`,
			'background-color': percentage === 100 ? '#28a745' : '#007bff'
		});
	}
}

function validate_adl_completion(frm) {
	let adl_fields = ['mobility', 'washing_bathing', 'dressing', 'feeding', 'toileting', 'transferring'];
	let missing_adl = [];
	
	adl_fields.forEach(field => {
		if (!frm.doc[field]) {
			missing_adl.push(frm.meta.get_field(field).label);
		}
	});
	
	if (missing_adl.length > 0) {
		frappe.msgprint({
			title: __('ADL Assessment Incomplete'),
			message: __('Please complete assessment for: {0}', [missing_adl.join(', ')]),
			indicator: 'orange'
		});
		return false;
	}
	return true;
}
