# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime


class CaseNotes(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set visit date if not provided
		if not self.visit_date:
			self.visit_date = today()
		
		# Set social worker if not provided
		if not self.social_worker:
			self.social_worker = frappe.session.user
		
		# Auto-populate beneficiary from case
		if self.case and not self.beneficiary:
			case_doc = frappe.get_doc("Case", self.case)
			self.beneficiary = case_doc.beneficiary
		
		# Set default location for home visits
		if self.visit_type == "Home Visit" and not self.location:
			if self.beneficiary:
				beneficiary_doc = frappe.get_doc("Beneficiary", self.beneficiary)
				if beneficiary_doc.address_line_1:
					self.location = f"{beneficiary_doc.address_line_1}, {beneficiary_doc.postal_code}"
	
	def validate(self):
		"""Validate case notes data"""
		# Ensure case exists and is active
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_status in ["Closed", "Transferred"]:
				frappe.msgprint(
					f"Warning: Adding notes to a {case_doc.case_status.lower()} case",
					title="Case Status Warning",
					indicator="orange"
				)
		
		# Validate visit duration
		if self.visit_duration and self.visit_duration.total_seconds() > 8 * 3600:  # 8 hours
			frappe.msgprint(
				"Visit duration seems unusually long. Please verify.",
				title="Duration Check",
				indicator="orange"
			)
		
		# Ensure required fields for specific visit types
		if self.visit_type == "Phone Call" and not self.visit_duration:
			frappe.msgprint(
				"Consider recording call duration for phone visits",
				title="Duration Recommended",
				indicator="blue"
			)
		
		# Check for safety concerns
		if self.safety_concerns:
			self.supervisor_review_required = 1
			self.priority_follow_up = 1
		
		# Check for high-risk observations
		risk_keywords = ["crisis", "emergency", "danger", "harm", "suicide", "abuse"]
		if self.observations:
			obs_lower = self.observations.lower()
			if any(keyword in obs_lower for keyword in risk_keywords):
				self.supervisor_review_required = 1
				self.priority_follow_up = 1
				frappe.msgprint(
					"High-risk keywords detected. Supervisor review and priority follow-up have been flagged.",
					title="Risk Alert",
					indicator="red"
				)
	
	def on_update(self):
		"""Actions to perform after updating case notes"""
		# Update case's last contact date
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.db_set('last_contact_date', self.visit_date, update_modified=False)
			case_doc.db_set('last_activity_date', today(), update_modified=False)
			
			# Update case metrics
			total_visits = frappe.db.count('Case Notes', {'case': self.case})
			case_doc.db_set('total_visits', total_visits, update_modified=False)
		
		# Send notifications for priority follow-ups
		if self.priority_follow_up:
			self.send_priority_notification()
		
		# Send notifications for supervisor review
		if self.supervisor_review_required:
			self.send_supervisor_notification()
	
	def send_priority_notification(self):
		"""Send notification for priority follow-up cases"""
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			recipients = [case_doc.primary_social_worker]
			
			if case_doc.secondary_social_worker:
				recipients.append(case_doc.secondary_social_worker)
			
			frappe.sendmail(
				recipients=recipients,
				subject=f"Priority Follow-up Required: {case_doc.case_title}",
				message=f"""
				<p>A priority follow-up has been flagged for case <strong>{case_doc.name}</strong>.</p>
				<p><strong>Visit Date:</strong> {self.visit_date}</p>
				<p><strong>Visit Type:</strong> {self.visit_type}</p>
				<p><strong>Next Steps:</strong> {self.next_steps or 'Not specified'}</p>
				<p><strong>Next Visit Date:</strong> {self.next_visit_date or 'Not scheduled'}</p>
				<p>Please review and take appropriate action.</p>
				"""
			)
	
	def send_supervisor_notification(self):
		"""Send notification to supervisor for review"""
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.supervisor:
				frappe.sendmail(
					recipients=[case_doc.supervisor],
					subject=f"Supervisor Review Required: {case_doc.case_title}",
					message=f"""
					<p>Supervisor review has been requested for case <strong>{case_doc.name}</strong>.</p>
					<p><strong>Social Worker:</strong> {self.social_worker}</p>
					<p><strong>Visit Date:</strong> {self.visit_date}</p>
					<p><strong>Visit Type:</strong> {self.visit_type}</p>
					<p><strong>Safety Concerns:</strong> {self.safety_concerns or 'None specified'}</p>
					<p><strong>Risk Factors:</strong> {self.risk_factors_observed or 'None specified'}</p>
					<p>Please review the case notes and provide guidance.</p>
					"""
				)
	
	def get_previous_visit(self):
		"""Get the previous visit for this case"""
		previous_visits = frappe.get_all('Case Notes',
			filters={
				'case': self.case,
				'visit_date': ['<', self.visit_date],
				'name': ['!=', self.name]
			},
			fields=['name', 'visit_date', 'visit_type', 'social_worker'],
			order_by='visit_date desc',
			limit=1
		)
		return previous_visits[0] if previous_visits else None
	
	def get_next_visit(self):
		"""Get the next scheduled visit for this case"""
		next_visits = frappe.get_all('Case Notes',
			filters={
				'case': self.case,
				'visit_date': ['>', self.visit_date],
				'name': ['!=', self.name]
			},
			fields=['name', 'visit_date', 'visit_type', 'social_worker'],
			order_by='visit_date asc',
			limit=1
		)
		return next_visits[0] if next_visits else None
	
	def calculate_visit_frequency(self):
		"""Calculate average visit frequency for this case"""
		visits = frappe.get_all('Case Notes',
			filters={'case': self.case},
			fields=['visit_date'],
			order_by='visit_date'
		)
		
		if len(visits) < 2:
			return None
		
		from frappe.utils import date_diff
		total_days = date_diff(visits[-1].visit_date, visits[0].visit_date)
		avg_days_between_visits = total_days / (len(visits) - 1)
		
		return avg_days_between_visits
	
	def get_visit_summary(self):
		"""Get a summary of this visit for reporting"""
		return {
			'case': self.case,
			'beneficiary': self.beneficiary,
			'visit_date': self.visit_date,
			'visit_type': self.visit_type,
			'duration': self.visit_duration,
			'outcome': self.visit_outcome,
			'follow_up_required': self.follow_up_required,
			'next_visit_date': self.next_visit_date,
			'priority_follow_up': self.priority_follow_up,
			'supervisor_review_required': self.supervisor_review_required
		}
