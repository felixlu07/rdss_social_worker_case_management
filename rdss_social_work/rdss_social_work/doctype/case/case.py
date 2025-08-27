# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, today
from datetime import date


class Case(Document):
	def get_indicator(self):
		"""Return indicator for the list view based on case_priority"""
		if self.case_priority:
			priority_data = frappe.db.get_value("Case Priority", self.case_priority, ["priority_code", "color_code"], as_dict=True)
			if priority_data:
				return (priority_data.priority_code, priority_data.color_code, f"case_priority,=,{self.case_priority}")
		return ("", "gray", "")
	def before_save(self):
		"""Set default values and calculate fields before saving"""
		# Set case opened date if not provided
		if not self.case_opened_date:
			self.case_opened_date = today()
		
		# Set assigned date if not provided
		if not self.assigned_date:
			self.assigned_date = today()
		
		# Set primary social worker if not provided
		if not self.primary_social_worker:
			self.primary_social_worker = frappe.session.user
		
		# Set default status for new cases
		if not self.case_status:
			self.case_status = "Open"
		
		# Calculate case duration
		if self.case_opened_date:
			self.case_duration_days = date_diff(today(), self.case_opened_date)
		
		# Set closure date when status changes to closed
		if self.case_status == "Closed" and not self.actual_closure_date:
			self.actual_closure_date = today()
			if not self.closed_by:
				self.closed_by = frappe.session.user
		
		# Clear closure date if status changes from closed
		if self.case_status != "Closed" and self.actual_closure_date:
			self.actual_closure_date = None
			self.closed_by = None
	
	def validate(self):
		"""Validate case data"""
		# Ensure beneficiary exists
		if self.beneficiary:
			if not frappe.db.exists("Beneficiary", self.beneficiary):
				frappe.throw(f"Beneficiary {self.beneficiary} does not exist")
		
		# Validate dates
		if self.expected_closure_date and self.case_opened_date:
			if getdate(self.expected_closure_date) < getdate(self.case_opened_date):
				frappe.throw("Expected closure date cannot be before case opened date")
		
		# Validate closure requirements
		if self.case_status == "Closed":
			if not self.closure_reason:
				frappe.throw("Closure reason is required when closing a case")
			if not self.closure_summary:
				frappe.msgprint(
					"Consider adding a closure summary for better record keeping",
					title="Closure Summary Recommended",
					indicator="orange"
				)
		
		# Validate risk assessment
		if self.risk_level in ["High Risk", "Critical Risk"] and not self.risk_mitigation_plan:
			frappe.throw("Risk mitigation plan is required for high and critical risk cases")
		
		# Validate service authorization
		if self.service_budget and self.service_budget > 0:
			if not self.funding_source:
				frappe.throw("Funding source is required when service budget is specified")
			if not self.authorized_by:
				frappe.msgprint(
					"Consider specifying who authorized the service budget",
					title="Authorization Recommended",
					indicator="orange"
				)
	
	def on_update(self):
		"""Actions to perform after updating case"""
		# Update case metrics
		self.update_case_metrics()
		
		# Update beneficiary's last activity
		if self.beneficiary:
			beneficiary_doc = frappe.get_doc("Beneficiary", self.beneficiary)
			beneficiary_doc.add_comment('Info', f'Case updated: {self.case_title}')
		
		# Send notifications for status changes
		if self.has_value_changed('case_status'):
			self.send_status_change_notification()
		
		# Send notifications for priority changes
		if self.has_value_changed('priority_level'):
			self.send_priority_change_notification()
	
	def update_case_metrics(self):
		"""Update case metrics based on related records"""
		# Count assessments
		assessments = frappe.db.count('Initial Assessment', {
			'client_name': frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')
		})
		self.db_set('total_assessments', assessments, update_modified=False)
		
		# Update last activity date
		self.db_set('last_activity_date', today(), update_modified=False)
	
	def send_status_change_notification(self):
		"""Send notification when case status changes"""
		# Check if email is configured
		if not frappe.db.get_value("Email Account", {"default_outgoing": 1}):
			frappe.msgprint("Email notifications are disabled. Please setup default Email Account from Settings > Email Account")
			return
			
		if self.case_status == "Closed":
			# Notify supervisor and team
			recipients = [self.primary_social_worker]
			if self.secondary_social_worker:
				recipients.append(self.secondary_social_worker)
			if self.supervisor:
				recipients.append(self.supervisor)
			
			for recipient in recipients:
				frappe.sendmail(
					recipients=[recipient],
					subject=f"Case Closed: {self.case_title}",
					message=f"""
					<p>Case <strong>{self.name}</strong> has been closed.</p>
					<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
					<p><strong>Closure Reason:</strong> {self.closure_reason}</p>
					<p><strong>Closed By:</strong> {self.closed_by}</p>
					"""
				)
	
	def send_priority_change_notification(self):
		"""Send notification when case priority changes"""
		# Check if email is configured
		if not frappe.db.get_value("Email Account", {"default_outgoing": 1}):
			frappe.msgprint("Email notifications are disabled. Please setup default Email Account from Settings > Email Account")
			return
			
		if self.case_priority:
			priority_info = frappe.get_doc("Case Priority", self.case_priority)
			priority_code = priority_info.priority_code
			
			# Notify supervisor for high priority cases (P1, P2, P3)
			if priority_code in ["P1", "P2", "P3"] and self.supervisor:
				frappe.sendmail(
					recipients=[self.supervisor],
					subject=f"High Priority Case: {self.case_title}",
					message=f"""
					<p>Case <strong>{self.name}</strong> has been marked as <strong>{priority_code}</strong> priority.</p>
					<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
					<p><strong>Primary Social Worker:</strong> {self.primary_social_worker}</p>
					<p><strong>Risk Level:</strong> {self.risk_level or 'Not assessed'}</p>
					<p><strong>Appointment Frequency:</strong> Every {priority_info.appointment_frequency_months} month(s)</p>
					"""
				)
	
	def get_case_timeline(self):
		"""Get chronological timeline of case activities"""
		timeline = []
		
		# Add case creation
		timeline.append({
			'date': self.case_opened_date,
			'activity': 'Case Opened',
			'details': f'Case opened by {self.primary_social_worker}',
			'type': 'case_event'
		})
		
		# Add assessments
		assessments = frappe.get_all('Initial Assessment',
			filters={'client_name': frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')},
			fields=['name', 'assessment_date', 'assessed_by'],
			order_by='assessment_date'
		)
		
		for assessment in assessments:
			timeline.append({
				'date': assessment.assessment_date,
				'activity': 'Assessment Completed',
				'details': f'Initial Assessment by {assessment.assessed_by}',
				'type': 'assessment',
				'reference': assessment.name
			})
		
		# Add closure if applicable
		if self.case_status == "Closed" and self.actual_closure_date:
			timeline.append({
				'date': self.actual_closure_date,
				'activity': 'Case Closed',
				'details': f'Closed by {self.closed_by} - Reason: {self.closure_reason}',
				'type': 'case_event'
			})
		
		# Sort by date
		timeline.sort(key=lambda x: x['date'])
		return timeline
	
	def get_overdue_reviews(self):
		"""Check if case review is overdue"""
		if self.next_review_date and getdate(self.next_review_date) < getdate(today()):
			return {
				'overdue': True,
				'days_overdue': date_diff(today(), self.next_review_date),
				'next_review_date': self.next_review_date
			}
		return {'overdue': False}
	
	def create_follow_up_case(self):
		"""Create a follow-up case when current case is closed"""
		if self.case_status != "Closed" or not self.follow_up_required:
			frappe.throw("Follow-up case can only be created for closed cases that require follow-up")
		
		follow_up_case = frappe.new_doc("Case")
		follow_up_case.case_title = f"Follow-up: {self.case_title}"
		follow_up_case.beneficiary = self.beneficiary
		follow_up_case.case_type = "Follow-up"
		follow_up_case.primary_social_worker = self.primary_social_worker
		follow_up_case.case_priority = self.case_priority
		follow_up_case.presenting_issues = f"Follow-up from case {self.name}"
		follow_up_case.case_opened_date = self.follow_up_date or today()
		
		follow_up_case.insert()
		
		# Link the cases
		self.add_comment('Info', f'Follow-up case created: {follow_up_case.name}')
		follow_up_case.add_comment('Info', f'Follow-up from case: {self.name}')
		
		return follow_up_case.name
