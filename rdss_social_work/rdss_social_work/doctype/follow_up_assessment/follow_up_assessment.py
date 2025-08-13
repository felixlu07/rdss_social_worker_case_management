# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, date_diff, get_datetime


class FollowUpAssessment(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set assessment date if not provided
		if not self.assessment_date:
			self.assessment_date = today()
		
		# Set assessed by if not provided
		if not self.assessed_by:
			self.assessed_by = frappe.session.user
		
		# Auto-populate beneficiary from case
		if self.case and not self.beneficiary:
			case_doc = frappe.get_doc("Case", self.case)
			self.beneficiary = case_doc.beneficiary
		
		# Calculate time since last assessment
		if self.previous_assessment:
			self.calculate_time_since_last_assessment()
		
		# Auto-calculate next assessment date based on follow-up timeline
		if self.follow_up_timeline and not self.next_assessment_date:
			self.next_assessment_date = self.calculate_next_assessment_date()
	
	def validate(self):
		"""Validate follow-up assessment data"""
		# Ensure case exists and is active
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_status in ["Closed", "Transferred"]:
				frappe.throw(f"Cannot create follow-up assessment for {case_doc.case_status.lower()} case")
		
		# Validate assessment date
		if self.assessment_date and getdate(self.assessment_date) > getdate(today()):
			frappe.throw("Assessment date cannot be in the future")
		
		# Validate next assessment date
		if self.next_assessment_date and self.assessment_date:
			if getdate(self.next_assessment_date) <= getdate(self.assessment_date):
				frappe.throw("Next assessment date must be after current assessment date")
		
		# Ensure required fields based on assessment outcome
		if self.assessment_outcome == "Refer to Other Agency":
			if not self.referrals_recommended:
				frappe.throw("Referrals must be specified when referring to other agency")
		
		if self.assessment_outcome in ["Increase Services", "Change Services"]:
			if not self.service_recommendations:
				frappe.throw("Service recommendations are required for this assessment outcome")
		
		# Validate risk level changes
		if self.current_risk_level == "Critical Risk":
			if not self.safety_concerns_current:
				frappe.throw("Safety concerns must be documented for critical risk cases")
			if not self.priority_actions:
				frappe.throw("Priority actions must be specified for critical risk cases")
	
	def on_submit(self):
		"""Actions to perform when follow-up assessment is submitted"""
		# Update case with assessment information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			
			# Update case risk level if changed
			if self.current_risk_level:
				case_doc.risk_level = self.current_risk_level
			
			# Add comment to case
			case_doc.add_comment('Info', f'Follow-up Assessment completed: {self.assessment_outcome}')
			
			# Update case status based on assessment outcome
			if self.assessment_outcome == "Discharge":
				case_doc.case_status = "Closed"
				case_doc.closure_date = self.assessment_date
				case_doc.closure_reason = "Discharged after follow-up assessment"
			elif self.assessment_outcome == "Refer to Other Agency":
				case_doc.case_status = "Transferred"
			
			case_doc.save()
		
		# Create referrals if recommended
		if self.referrals_recommended and self.assessment_outcome == "Refer to Other Agency":
			self.create_referrals()
		
		# Schedule next assessment if specified
		if self.next_assessment_date:
			self.schedule_next_assessment()
		
		# Send notifications
		self.send_assessment_notification()
	
	def calculate_time_since_last_assessment(self):
		"""Calculate time elapsed since previous assessment"""
		if not self.previous_assessment:
			return
		
		try:
			# Try to get from Initial Assessment first
			prev_doc = frappe.get_doc("Initial Assessment", self.previous_assessment)
			prev_date = prev_doc.assessment_date
		except:
			try:
				# Try Follow-up Assessment
				prev_doc = frappe.get_doc("Follow-up Assessment", self.previous_assessment)
				prev_date = prev_doc.assessment_date
			except:
				return
		
		if prev_date and self.assessment_date:
			days_diff = date_diff(self.assessment_date, prev_date)
			
			if days_diff < 30:
				self.time_since_last_assessment = f"{days_diff} days"
			elif days_diff < 365:
				months = days_diff // 30
				remaining_days = days_diff % 30
				if remaining_days > 0:
					self.time_since_last_assessment = f"{months} months, {remaining_days} days"
				else:
					self.time_since_last_assessment = f"{months} months"
			else:
				years = days_diff // 365
				remaining_days = days_diff % 365
				months = remaining_days // 30
				if months > 0:
					self.time_since_last_assessment = f"{years} years, {months} months"
				else:
					self.time_since_last_assessment = f"{years} years"
	
	def calculate_next_assessment_date(self):
		"""Calculate next assessment date based on follow-up timeline"""
		if not self.follow_up_timeline or not self.assessment_date:
			return None
		
		base_date = getdate(self.assessment_date)
		
		if self.follow_up_timeline == "1 week":
			return frappe.utils.add_days(base_date, 7)
		elif self.follow_up_timeline == "2 weeks":
			return frappe.utils.add_days(base_date, 14)
		elif self.follow_up_timeline == "1 month":
			return frappe.utils.add_months(base_date, 1)
		elif self.follow_up_timeline == "3 months":
			return frappe.utils.add_months(base_date, 3)
		elif self.follow_up_timeline == "6 months":
			return frappe.utils.add_months(base_date, 6)
		elif self.follow_up_timeline == "1 year":
			return frappe.utils.add_months(base_date, 12)
		
		return None
	
	def create_referrals(self):
		"""Create referral documents based on recommendations"""
		if not self.referrals_recommended:
			return
		
		# Split referrals by line and create individual referral documents
		referral_lines = self.referrals_recommended.split('\n')
		
		for line in referral_lines:
			line = line.strip()
			if line:
				try:
					referral_doc = frappe.new_doc("Referral")
					referral_doc.case = self.case
					referral_doc.beneficiary = self.beneficiary
					referral_doc.referral_date = self.assessment_date
					referral_doc.referred_by = self.assessed_by
					referral_doc.referral_reason = f"Follow-up assessment recommendation: {line}"
					referral_doc.referral_source = "Follow-up Assessment"
					referral_doc.priority = "Medium"  # Default priority
					referral_doc.status = "Pending"
					referral_doc.insert()
					
					# Link referral to this assessment
					self.add_comment('Info', f'Referral created: {referral_doc.name}')
					
				except Exception as e:
					frappe.log_error(f"Error creating referral: {str(e)}")
	
	def schedule_next_assessment(self):
		"""Schedule next assessment as a reminder/task"""
		if not self.next_assessment_date:
			return
		
		# Create a ToDo for the next assessment
		try:
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Follow-up Assessment due for {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
			todo_doc.reference_type = "Case"
			todo_doc.reference_name = self.case
			todo_doc.assigned_by = self.assessed_by
			todo_doc.owner = self.assessed_by
			todo_doc.date = self.next_assessment_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error scheduling next assessment: {str(e)}")
	
	def send_assessment_notification(self):
		"""Send notification about completed assessment"""
		if not self.case:
			return
		
		case_doc = frappe.get_doc("Case", self.case)
		recipients = [self.assessed_by]
		
		# Add case manager and supervisor to recipients
		if case_doc.case_manager and case_doc.case_manager != self.assessed_by:
			recipients.append(case_doc.case_manager)
		
		if case_doc.supervisor:
			recipients.append(case_doc.supervisor)
		
		# Determine urgency based on assessment outcome and risk level
		urgency = "Normal"
		if self.current_risk_level == "Critical Risk" or self.assessment_outcome in ["Discharge", "Refer to Other Agency"]:
			urgency = "High"
		
		subject = f"Follow-up Assessment Completed: {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
		
		message = f"""
		<p>Follow-up Assessment <strong>{self.name}</strong> has been completed.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Assessment Date:</strong> {self.assessment_date}</p>
		<p><strong>Assessment Outcome:</strong> {self.assessment_outcome}</p>
		<p><strong>Overall Progress:</strong> {self.overall_progress or 'Not specified'}</p>
		<p><strong>Current Risk Level:</strong> {self.current_risk_level or 'Not assessed'}</p>
		"""
		
		if self.priority_actions:
			message += f"<p><strong>Priority Actions:</strong> {self.priority_actions}</p>"
		
		if self.next_assessment_date:
			message += f"<p><strong>Next Assessment Due:</strong> {self.next_assessment_date}</p>"
		
		if urgency == "High":
			message += "<p><strong style='color: red;'>This assessment requires immediate attention.</strong></p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending assessment notification: {str(e)}")
	
	def get_comparison_data(self):
		"""Get comparison data with previous assessment"""
		if not self.previous_assessment:
			return None
		
		try:
			# Try to get from Initial Assessment first
			prev_doc = frappe.get_doc("Initial Assessment", self.previous_assessment)
			prev_type = "Initial Assessment"
		except:
			try:
				# Try Follow-up Assessment
				prev_doc = frappe.get_doc("Follow-up Assessment", self.previous_assessment)
				prev_type = "Follow-up Assessment"
			except:
				return None
		
		# Compare functional abilities
		functional_comparison = {}
		functional_fields = [
			'mobility_current', 'washing_bathing_current', 'dressing_current',
			'feeding_current', 'toileting_current', 'transferring_current',
			'housekeeping_current', 'cognitive_ability_current'
		]
		
		for field in functional_fields:
			current_val = getattr(self, field, None)
			
			# Map field names for Initial Assessment
			if prev_type == "Initial Assessment":
				prev_field = field.replace('_current', '')
				prev_val = getattr(prev_doc, prev_field, None)
			else:
				prev_val = getattr(prev_doc, field, None)
			
			if current_val and prev_val:
				functional_comparison[field] = {
					'previous': prev_val,
					'current': current_val,
					'changed': current_val != prev_val
				}
		
		return {
			'previous_assessment_type': prev_type,
			'previous_assessment_date': prev_doc.assessment_date,
			'functional_comparison': functional_comparison,
			'time_elapsed': self.time_since_last_assessment
		}
	
	def get_progress_indicators(self):
		"""Get progress indicators for dashboard display"""
		indicators = {
			'overall_status': 'stable',
			'risk_status': 'low',
			'service_status': 'adequate',
			'alerts': []
		}
		
		# Determine overall status
		if self.overall_progress in ['Excellent Progress', 'Good Progress']:
			indicators['overall_status'] = 'improving'
		elif self.overall_progress == 'Regression':
			indicators['overall_status'] = 'declining'
		
		# Determine risk status
		if self.current_risk_level in ['High Risk', 'Critical Risk']:
			indicators['risk_status'] = 'high'
			indicators['alerts'].append('High risk level requires immediate attention')
		elif self.current_risk_level == 'Moderate Risk':
			indicators['risk_status'] = 'moderate'
		
		# Determine service status
		if self.service_satisfaction in ['Dissatisfied', 'Very Dissatisfied']:
			indicators['service_status'] = 'poor'
			indicators['alerts'].append('Service satisfaction is low')
		elif self.additional_services_needed:
			indicators['service_status'] = 'needs_improvement'
		
		# Add specific alerts
		if self.caregiver_stress_level in ['High', 'Critical']:
			indicators['alerts'].append('Caregiver stress level is concerning')
		
		if self.respite_care_needed:
			indicators['alerts'].append('Respite care is needed')
		
		if self.home_safety_current in ['Major Concerns', 'Unsafe']:
			indicators['alerts'].append('Home safety concerns identified')
		
		return indicators
