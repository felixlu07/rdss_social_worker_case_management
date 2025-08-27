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
		
		// Auto-populate beneficiary from case if case is selected first
		if (frm.doc.case && !frm.doc.beneficiary) {
			frappe.db.get_value('Case', frm.doc.case, 'beneficiary')
				.then(r => {
					if (r.message && r.message.beneficiary) {
						frm.set_value('beneficiary', r.message.beneficiary);
					}
				});
		}
		
		// Add quick action buttons
		if (!frm.is_new()) {
			// Add navigation buttons to related records
			if (frm.doc.beneficiary) {
				frm.add_custom_button(__('View Beneficiary'), function() {
					frappe.set_route('Form', 'Beneficiary', frm.doc.beneficiary);
				}, __('Navigate'));
			}
			
			if (frm.doc.case) {
				frm.add_custom_button(__('View Case'), function() {
					frappe.set_route('Form', 'Case', frm.doc.case);
				}, __('Navigate'));
			}
			
			// Add follow-up assessment button
			frm.add_custom_button(__('Create Follow-up Assessment'), function() {
				frappe.new_doc('Follow-up Assessment', {
					beneficiary: frm.doc.beneficiary,
					case: frm.doc.case,
					initial_assessment: frm.doc.name,
					assessment_date: frappe.datetime.get_today()
				});
			}, __('Actions'));
			
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
	
	case: function(frm) {
		// Auto-populate beneficiary when case is selected
		if (frm.doc.case && !frm.doc.beneficiary) {
			frappe.db.get_value('Case', frm.doc.case, 'beneficiary')
				.then(r => {
					if (r.message && r.message.beneficiary) {
						frm.set_value('beneficiary', r.message.beneficiary);
					}
				});
		}
	},
	
	beneficiary: function(frm) {
		// Auto-populate case if there's an active case for the beneficiary
		if (frm.doc.beneficiary && !frm.doc.case) {
			frappe.db.get_list('Case', {
				filters: {
					beneficiary: frm.doc.beneficiary
				},
				fields: ['name', 'case_title'],
				limit: 1,
				order_by: 'creation desc'
			}).then(r => {
				if (r && r.length > 0) {
					frm.set_value('case', r[0].name);
				}
			});
		}

		// Auto-fetch additional fields from beneficiary
		if (frm.doc.beneficiary) {
			frappe.db.get_value('Beneficiary', frm.doc.beneficiary, ['beneficiary_name', 'bc_nric_no'])
				.then(r => {
					if (r.message) {
						// client_name is now fetch_from, but we'll ensure bc_nric_no is also populated
						if (r.message.bc_nric_no) {
							frm.set_value('bc_nric_no', r.message.bc_nric_no);
						}
					}
				});
		}
	},
	
	// Removed auto-generation of case_no from client_name function
	client_name: function(frm) {
		// No longer auto-generating case_no to prevent incorrect values
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
	// Use a simpler approach to avoid DOM fragment issues
	try {
		// Calculate completion percentage
		let total_fields = 0;
		let completed_fields = 0;
		
		// Count required fields - safely check if fields exist
		if (frm.meta && frm.meta.fields) {
			frm.meta.fields.forEach(field => {
				if (field.reqd || ['mobility', 'washing_bathing', 'dressing', 'feeding', 'toileting', 'transferring'].includes(field.fieldname)) {
					total_fields++;
					if (frm.doc && frm.doc[field.fieldname]) {
						completed_fields++;
					}
				}
			});
		}
		
		// Check if next of kin is provided
		if (frm.doc && frm.doc.next_of_kin_contacts && frm.doc.next_of_kin_contacts.length > 0) {
			completed_fields++;
		}
		total_fields++;
		
		let percentage = Math.round((completed_fields / total_fields) * 100);
		
		// Create progress indicator HTML
		const progressHtml = 
			'<div class="progress-indicator" style="margin: 15px 0;">' +
				'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">' +
					'<span>Assessment Completion</span>' +
					'<span class="progress-text">' + percentage + '%</span>' +
				'</div>' +
				'<div class="progress" style="height: 8px;">' +
					'<div class="progress-bar" role="progressbar" ' +
						'style="width: ' + percentage + '%; background-color: ' + (percentage === 100 ? '#28a745' : '#007bff') + ';">' +
					'</div>' +
				'</div>' +
			'</div>';
		
		// Add progress bar
		if (!frm.progress_area) {
			// Create a simple div and append it
			frm.progress_area = $('<div>').html(progressHtml);
			
			// Check if toolbar exists before inserting
			if (frm.toolbar && frm.toolbar.length) {
				frm.progress_area.insertAfter(frm.toolbar);
			} else {
				// Fallback to page-form if toolbar doesn't exist
				frm.progress_area.prependTo(frm.page.body.find('.page-form'));
			}
		} else {
			// Update existing progress area
			frm.progress_area.html(progressHtml);
		}
	} catch (e) {
		// Silently fail if there's an error - don't break form functionality
		console.error('Error in progress indicator:', e);
	}
}

function validate_adl_completion(frm) {
	try {
		let adl_fields = ['mobility', 'washing_bathing', 'dressing', 'feeding', 'toileting', 'transferring'];
		let missing_adl = [];
		
		// Use field labels directly instead of trying to get them from meta
		const field_labels = {
			'mobility': 'Mobility',
			'washing_bathing': 'Washing/Bathing',
			'dressing': 'Dressing',
			'feeding': 'Feeding',
			'toileting': 'Toileting',
			'transferring': 'Transferring'
		};
		
		adl_fields.forEach(field => {
			if (!frm.doc[field]) {
				missing_adl.push(field_labels[field] || field);
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
	} catch (e) {
		console.error('Error in ADL validation:', e);
		return true; // Don't block saving if there's an error in validation
	}
}
