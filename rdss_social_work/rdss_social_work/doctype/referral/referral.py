# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_days


class Referral(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set referral date if not provided
		if not self.referral_date:
			self.referral_date = today()
		
		# Set referred by if not provided
		if not self.referred_by:
			self.referred_by = frappe.session.user
		
		# Auto-populate beneficiary from case
		if self.case and not self.beneficiary:
			case_doc = frappe.get_doc("Case", self.case)
			self.beneficiary = case_doc.beneficiary
		
		# Set default status for new referrals
		if not self.status:
			self.status = "Pending"
		
		# Set consent date if consent obtained but date not set
		if self.consent_obtained and not self.consent_date:
			self.consent_date = today()
		
		# Set acknowledgment date if acknowledgment received but date not set
		if self.acknowledgment_received and not self.acknowledgment_date:
			self.acknowledgment_date = today()
		
		# Set service start date if service started but date not set
		if self.service_started and not self.service_start_date:
			self.service_start_date = today()
		
		# Auto-set follow-up date based on priority and urgency
		if not self.follow_up_date and self.follow_up_required:
			self.follow_up_date = self.calculate_follow_up_date()
	
	def validate(self):
		"""Validate referral data"""
		# Ensure case exists and is active
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_status in ["Closed", "Transferred"]:
				frappe.throw(f"Cannot create referral for {case_doc.case_status.lower()} case")
		
		# Validate dates
		if self.referral_date and getdate(self.referral_date) > getdate(today()):
			frappe.throw("Referral date cannot be in the future")
		
		if self.referral_sent_date and self.referral_date:
			if getdate(self.referral_sent_date) < getdate(self.referral_date):
				frappe.throw("Referral sent date cannot be before referral date")
		
		if self.acknowledgment_date and self.referral_sent_date:
			if getdate(self.acknowledgment_date) < getdate(self.referral_sent_date):
				frappe.throw("Acknowledgment date cannot be before referral sent date")
		
		if self.service_start_date and self.outcome_date:
			if getdate(self.service_start_date) < getdate(self.outcome_date):
				frappe.throw("Service start date cannot be before outcome date")
		
		# Validate required fields based on status
		if self.status == "Sent":
			if not self.referral_sent_date:
				frappe.throw("Referral sent date is required when status is 'Sent'")
			if not self.referral_method:
				frappe.throw("Referral method is required when status is 'Sent'")
		
		if self.status == "Acknowledged":
			if not self.acknowledgment_received:
				self.acknowledgment_received = 1
			if not self.acknowledgment_date:
				self.acknowledgment_date = today()
		
		if self.status in ["Accepted", "Rejected", "Completed"]:
			if not self.referral_outcome:
				frappe.throw(f"Referral outcome is required when status is '{self.status}'")
			if not self.outcome_date:
				self.outcome_date = today()
		
		# Validate consent requirements for certain referral types
		high_privacy_types = ["Mental Health", "Specialty Care", "Residential Care"]
		if self.service_category in high_privacy_types:
			if not self.consent_obtained:
				frappe.msgprint(
					f"Consent is strongly recommended for {self.service_category} referrals",
					title="Consent Recommended",
					indicator="orange"
				)
		
		# Validate urgency vs priority alignment
		if self.priority == "Urgent" and self.urgency_level in ["Routine", "Soon"]:
			frappe.msgprint(
				"Priority and urgency level may not be aligned",
				title="Priority Mismatch",
				indicator="yellow"
			)
	
	def on_submit(self):
		"""Actions to perform when referral is submitted"""
		# Update status to sent if not already set
		if self.status == "Pending":
			self.status = "Sent"
			if not self.referral_sent_date:
				self.referral_sent_date = today()
		
		# Update case with referral information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Referral submitted: {self.referred_to_organization}')
		
		# Create follow-up task if required
		if self.follow_up_required:
			self.create_follow_up_task()
		
		# Send notifications
		self.send_referral_notification()
	
	def on_cancel(self):
		"""Actions to perform when referral is cancelled"""
		self.status = "Cancelled"
		
		# Notify relevant parties
		self.send_cancellation_notification()
	
	def calculate_follow_up_date(self):
		"""Calculate follow-up date based on priority and urgency"""
		if not self.referral_date:
			return None
		
		base_date = getdate(self.referral_date)
		
		# Determine follow-up timeline based on priority and urgency
		if self.priority == "Urgent" or self.urgency_level == "Emergent":
			return add_days(base_date, 1)  # Next day
		elif self.priority == "High" or self.urgency_level == "Urgent":
			return add_days(base_date, 3)  # 3 days
		elif self.priority == "Medium" or self.urgency_level == "Soon":
			return add_days(base_date, 7)  # 1 week
		else:
			return add_days(base_date, 14)  # 2 weeks
	
	def create_follow_up_task(self):
		"""Create follow-up task for this referral"""
		if not self.follow_up_date:
			return
		
		try:
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Follow up on referral to {self.referred_to_organization} for {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
			todo_doc.reference_type = "Referral"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.referred_by
			todo_doc.owner = self.referred_by
			todo_doc.date = self.follow_up_date
			
			# Set priority based on referral priority
			if self.priority in ["Urgent", "High"]:
				todo_doc.priority = "High"
			elif self.priority == "Medium":
				todo_doc.priority = "Medium"
			else:
				todo_doc.priority = "Low"
			
			todo_doc.status = "Open"
			todo_doc.insert()
			
			self.add_comment('Info', f'Follow-up task created: {todo_doc.name}')
			
		except Exception as e:
			frappe.log_error(f"Error creating follow-up task: {str(e)}")
	
	def send_referral_notification(self):
		"""Send notification when referral is submitted"""
		recipients = [self.referred_by]
		
		# Add case manager to recipients if different
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_manager and case_doc.case_manager != self.referred_by:
				recipients.append(case_doc.case_manager)
		
		subject = f"Referral Submitted: {self.referred_to_organization}"
		
		message = f"""
		<p>Referral <strong>{self.name}</strong> has been submitted.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Referred to:</strong> {self.referred_to_organization}</p>
		<p><strong>Service Category:</strong> {self.service_category or 'Not specified'}</p>
		<p><strong>Priority:</strong> {self.priority}</p>
		<p><strong>Referral Reason:</strong> {frappe.utils.strip_html(self.referral_reason)[:200]}...</p>
		"""
		
		if self.follow_up_date:
			message += f"<p><strong>Follow-up Date:</strong> {self.follow_up_date}</p>"
		
		if self.priority in ["Urgent", "High"]:
			message += "<p><strong style='color: red;'>This is a high priority referral.</strong></p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending referral notification: {str(e)}")
	
	def send_cancellation_notification(self):
		"""Send notification when referral is cancelled"""
		recipients = [self.referred_by]
		
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_manager and case_doc.case_manager != self.referred_by:
				recipients.append(case_doc.case_manager)
		
		subject = f"Referral Cancelled: {self.referred_to_organization}"
		
		message = f"""
		<p>Referral <strong>{self.name}</strong> has been cancelled.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Referred to:</strong> {self.referred_to_organization}</p>
		<p>Please review and create a new referral if needed.</p>
		"""
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending cancellation notification: {str(e)}")
	
	def update_status_from_outcome(self):
		"""Update referral status based on outcome"""
		if not self.referral_outcome:
			return
		
		status_mapping = {
			"Accepted": "Accepted",
			"Rejected": "Rejected",
			"Partially Accepted": "Accepted",
			"Referred Elsewhere": "Completed",
			"No Response": "Pending"
		}
		
		new_status = status_mapping.get(self.referral_outcome)
		if new_status and new_status != self.status:
			self.status = new_status
			if not self.outcome_date:
				self.outcome_date = today()
	
	def get_referral_timeline(self):
		"""Get timeline of referral events"""
		timeline = []
		
		if self.referral_date:
			timeline.append({
				'date': self.referral_date,
				'event': 'Referral Created',
				'details': f'Referred to {self.referred_to_organization}'
			})
		
		if self.referral_sent_date:
			timeline.append({
				'date': self.referral_sent_date,
				'event': 'Referral Sent',
				'details': f'Sent via {self.referral_method or "Unknown method"}'
			})
		
		if self.acknowledgment_date:
			timeline.append({
				'date': self.acknowledgment_date,
				'event': 'Acknowledgment Received',
				'details': 'Referral acknowledged by recipient'
			})
		
		if self.outcome_date:
			timeline.append({
				'date': self.outcome_date,
				'event': 'Outcome Determined',
				'details': f'Outcome: {self.referral_outcome}'
			})
		
		if self.service_start_date:
			timeline.append({
				'date': self.service_start_date,
				'event': 'Service Started',
				'details': 'Service delivery began'
			})
		
		if self.follow_up_date:
			timeline.append({
				'date': self.follow_up_date,
				'event': 'Follow-up Scheduled',
				'details': f'Follow-up via {self.follow_up_method or "TBD"}'
			})
		
		# Sort timeline by date
		timeline.sort(key=lambda x: x['date'])
		return timeline
	
	def get_days_since_referral(self):
		"""Calculate days since referral was made"""
		if not self.referral_date:
			return 0
		
		from frappe.utils import date_diff
		return date_diff(today(), self.referral_date)
	
	def is_overdue(self):
		"""Check if referral follow-up is overdue"""
		if not self.follow_up_date or self.status in ["Completed", "Cancelled", "Rejected"]:
			return False
		
		return getdate(self.follow_up_date) < getdate(today())
	
	def get_referral_metrics(self):
		"""Get metrics for this referral"""
		days_since_referral = self.get_days_since_referral()
		
		metrics = {
			'days_since_referral': days_since_referral,
			'is_overdue': self.is_overdue(),
			'response_time': None,
			'completion_time': None,
			'status_category': self.get_status_category()
		}
		
		# Calculate response time (referral to acknowledgment)
		if self.acknowledgment_date and self.referral_sent_date:
			from frappe.utils import date_diff
			metrics['response_time'] = date_diff(self.acknowledgment_date, self.referral_sent_date)
		
		# Calculate completion time (referral to service start)
		if self.service_start_date and self.referral_date:
			from frappe.utils import date_diff
			metrics['completion_time'] = date_diff(self.service_start_date, self.referral_date)
		
		return metrics
	
	def get_status_category(self):
		"""Categorize status for reporting"""
		if self.status in ["Pending", "Sent"]:
			return "In Progress"
		elif self.status in ["Acknowledged", "Accepted"]:
			return "Active"
		elif self.status == "Completed":
			return "Completed"
		elif self.status in ["Rejected", "Cancelled"]:
			return "Closed"
		else:
			return "Unknown"
	
	def create_follow_up_referral(self, reason):
		"""Create a follow-up referral based on this one"""
		new_referral = frappe.copy_doc(self)
		new_referral.referral_date = today()
		new_referral.referral_source = "Follow-up Referral"
		new_referral.status = "Pending"
		new_referral.referral_sent_date = None
		new_referral.acknowledgment_received = 0
		new_referral.acknowledgment_date = None
		new_referral.referral_outcome = None
		new_referral.outcome_date = None
		new_referral.service_started = 0
		new_referral.service_start_date = None
		
		# Update referral reason to include follow-up context
		new_referral.referral_reason = f"Follow-up to {self.name}: {reason}\n\nOriginal referral reason:\n{self.referral_reason}"
		
		new_referral.insert()
		
		# Link referrals
		self.add_comment('Info', f'Follow-up referral created: {new_referral.name}')
		new_referral.add_comment('Info', f'Follow-up to referral: {self.name}')
		
		return new_referral.name
