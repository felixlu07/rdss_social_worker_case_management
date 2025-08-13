# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InitialAssessment(Document):
	def before_save(self):
		"""Set default values and validate data before saving"""
		if not self.assessment_date:
			self.assessment_date = frappe.utils.today()
		
		if not self.assessed_by:
			self.assessed_by = frappe.session.user
	
	def validate(self):
		"""Validate the assessment data"""
		# Ensure at least one next of kin is provided
		if not self.next_of_kin_contacts:
			frappe.throw("At least one Next-of-Kin contact is required")
		
		# Validate that required ADL assessments are completed
		adl_fields = [
			'mobility', 'washing_bathing', 'dressing', 
			'feeding', 'toileting', 'transferring'
		]
		
		missing_adl = []
		for field in adl_fields:
			if not self.get(field):
				missing_adl.append(field.replace('_', ' ').title())
		
		if missing_adl:
			frappe.msgprint(
				f"Please complete ADL assessment for: {', '.join(missing_adl)}",
				title="ADL Assessment Incomplete",
				indicator="orange"
			)
		
		# Validate assessment decision fields
		if self.assessment_decision:
			if self.assessment_decision == 'Reject' and not self.reject_reason:
				frappe.throw("Please provide a reason for rejection")
			
			if self.assessment_decision == 'Refer to' and not self.refer_to:
				frappe.throw("Please specify who to refer to")
			
			# Auto-set decision date and assessed by if not provided
			if not self.decision_date_of_assessment:
				self.decision_date_of_assessment = frappe.utils.today()
			
			if not self.decision_assessed_by:
				self.decision_assessed_by = frappe.session.user
	
	def on_submit(self):
		"""Actions to perform when assessment is submitted"""
		frappe.msgprint(
			f"Initial Assessment for {self.client_name} has been submitted successfully",
			title="Assessment Submitted",
			indicator="green"
		)
