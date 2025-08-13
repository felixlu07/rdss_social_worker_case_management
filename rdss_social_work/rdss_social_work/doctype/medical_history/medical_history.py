# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class MedicalHistory(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set record date if not provided
		if not self.record_date:
			self.record_date = today()
		
		# Set recorded by if not provided
		if not self.recorded_by:
			self.recorded_by = frappe.session.user
		
		# Auto-populate case from beneficiary if not provided
		if self.beneficiary and not self.case:
			# Get the most recent active case for this beneficiary
			active_case = frappe.db.get_value(
				"Case",
				{"beneficiary": self.beneficiary, "case_status": ["not in", ["Closed", "Transferred"]]},
				"name",
				order_by="creation desc"
			)
			if active_case:
				self.case = active_case
		
		# Set default verification status
		if not self.verification_status:
			if self.source_of_information in ["Medical Records", "Physician Report", "Hospital Discharge"]:
				self.verification_status = "Verified"
			else:
				self.verification_status = "Needs Verification"
	
	def validate(self):
		"""Validate medical history data"""
		# Validate diagnosis date
		if self.diagnosis_date and getdate(self.diagnosis_date) > getdate(today()):
			frappe.throw("Diagnosis date cannot be in the future")
		
		# Validate record date
		if self.record_date and getdate(self.record_date) > getdate(today()):
			frappe.throw("Record date cannot be in the future")
		
		# Validate ICD code format if provided
		if self.icd_code:
			self.validate_icd_code()
		
		# Validate medication allergies vs current medications
		if self.medication_allergies and self.current_medications:
			self.check_medication_conflicts()
		
		# Validate severity level for certain conditions
		if self.primary_diagnosis and self.severity_level == "Critical":
			if not self.emergency_protocols:
				frappe.msgprint(
					"Emergency protocols should be documented for critical conditions",
					title="Emergency Protocols Recommended",
					indicator="orange"
				)
		
		# Validate care requirements
		if self.nursing_care_required or self.respite_care_needs:
			if not self.daily_care_needs:
				frappe.throw("Daily care needs must be documented when nursing or respite care is required")
	
	def on_submit(self):
		"""Actions to perform when medical history is submitted"""
		# Update beneficiary with key medical information
		if self.beneficiary:
			self.update_beneficiary_medical_info()
		
		# Update case with medical history information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Medical History updated: {self.primary_diagnosis}')
		
		# Create alerts for critical conditions
		if self.severity_level == "Critical" or self.prognosis in ["Poor", "Terminal"]:
			self.create_medical_alert()
		
		# Send notifications to healthcare team
		self.send_medical_update_notification()
	
	def validate_icd_code(self):
		"""Validate ICD code format"""
		import re
		
		# Basic ICD-10 format validation (simplified)
		icd_pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'
		
		if not re.match(icd_pattern, self.icd_code.upper()):
			frappe.msgprint(
				"ICD code format may be incorrect. Expected format: A00 or A00.0",
				title="ICD Code Format",
				indicator="yellow"
			)
	
	def check_medication_conflicts(self):
		"""Check for potential medication conflicts with allergies"""
		if not self.medication_allergies or not self.current_medications:
			return
		
		allergies = [allergy.strip().lower() for allergy in self.medication_allergies.split(',')]
		medications = self.current_medications.lower()
		
		conflicts = []
		for allergy in allergies:
			if allergy in medications:
				conflicts.append(allergy)
		
		if conflicts:
			frappe.msgprint(
				f"Potential medication conflicts detected: {', '.join(conflicts)}",
				title="Medication Conflict Alert",
				indicator="red"
			)
	
	def update_beneficiary_medical_info(self):
		"""Update beneficiary with key medical information"""
		try:
			beneficiary_doc = frappe.get_doc("Beneficiary", self.beneficiary)
			
			# Update primary diagnosis if not set or if this is more recent
			if not beneficiary_doc.primary_medical_condition or (
				self.record_date and getdate(self.record_date) > getdate(beneficiary_doc.modified)
			):
				beneficiary_doc.primary_medical_condition = self.primary_diagnosis
			
			# Update rare disorder information
			if self.rare_disorders:
				beneficiary_doc.rare_disorder_details = self.rare_disorders
			
			# Update care level based on functional status
			if self.mobility_status in ["Wheelchair Dependent", "Bedridden"]:
				beneficiary_doc.care_level = "High"
			elif self.cognitive_status in ["Moderate Impairment", "Severe Impairment"]:
				beneficiary_doc.care_level = "High"
			elif self.nursing_care_required:
				beneficiary_doc.care_level = "High"
			
			beneficiary_doc.save()
			
		except Exception as e:
			frappe.log_error(f"Error updating beneficiary medical info: {str(e)}")
	
	def create_medical_alert(self):
		"""Create medical alert for critical conditions"""
		try:
			# Create a ToDo as medical alert
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"MEDICAL ALERT: {self.primary_diagnosis} - {self.severity_level or self.prognosis}"
			todo_doc.reference_type = "Medical History"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.recorded_by
			
			# Assign to case manager or primary social worker
			if self.case:
				case_doc = frappe.get_doc("Case", self.case)
				todo_doc.owner = case_doc.case_manager or case_doc.assigned_social_worker
			else:
				todo_doc.owner = self.recorded_by
			
			todo_doc.date = today()
			todo_doc.priority = "High"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating medical alert: {str(e)}")
	
	def send_medical_update_notification(self):
		"""Send notification about medical history update"""
		if not self.case:
			return
		
		case_doc = frappe.get_doc("Case", self.case)
		recipients = [self.recorded_by]
		
		# Add case team to recipients
		if case_doc.case_manager and case_doc.case_manager != self.recorded_by:
			recipients.append(case_doc.case_manager)
		
		if case_doc.assigned_social_worker and case_doc.assigned_social_worker not in recipients:
			recipients.append(case_doc.assigned_social_worker)
		
		if case_doc.supervisor:
			recipients.append(case_doc.supervisor)
		
		# Determine urgency
		urgency = "Normal"
		if self.severity_level == "Critical" or self.prognosis in ["Poor", "Terminal"]:
			urgency = "High"
		
		subject = f"Medical History Updated: {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
		
		message = f"""
		<p>Medical History <strong>{self.name}</strong> has been updated.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Primary Diagnosis:</strong> {self.primary_diagnosis}</p>
		<p><strong>Severity:</strong> {self.severity_level or 'Not specified'}</p>
		<p><strong>Prognosis:</strong> {self.prognosis or 'Not specified'}</p>
		"""
		
		if self.medication_allergies:
			message += f"<p><strong>Medication Allergies:</strong> {self.medication_allergies}</p>"
		
		if self.emergency_protocols:
			message += f"<p><strong>Emergency Protocols:</strong> {self.emergency_protocols}</p>"
		
		if urgency == "High":
			message += "<p><strong style='color: red;'>This medical update requires immediate attention.</strong></p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending medical update notification: {str(e)}")
	
	def get_medication_summary(self):
		"""Get summary of current medications"""
		if not self.current_medications:
			return {"total_medications": 0, "compliance_status": "N/A"}
		
		# Simple medication count (assuming each line is a medication)
		med_lines = [line.strip() for line in self.current_medications.split('\n') if line.strip()]
		
		return {
			"total_medications": len(med_lines),
			"compliance_status": self.medication_compliance or "Not assessed",
			"allergies_count": len(self.medication_allergies.split(',')) if self.medication_allergies else 0,
			"management_type": self.medication_management or "Not specified"
		}
	
	def get_care_complexity_score(self):
		"""Calculate care complexity score based on medical factors"""
		score = 0
		
		# Severity level scoring
		severity_scores = {
			"Mild": 1,
			"Moderate": 2,
			"Severe": 3,
			"Critical": 4
		}
		score += severity_scores.get(self.severity_level, 0)
		
		# Functional status scoring
		if self.mobility_status in ["Wheelchair Dependent", "Bedridden"]:
			score += 2
		elif self.mobility_status == "Ambulatory with Assistance":
			score += 1
		
		if self.cognitive_status in ["Severe Impairment"]:
			score += 3
		elif self.cognitive_status in ["Moderate Impairment"]:
			score += 2
		elif self.cognitive_status in ["Mild Impairment"]:
			score += 1
		
		# Care requirements scoring
		if self.nursing_care_required:
			score += 2
		if self.respite_care_needs:
			score += 1
		
		# Prognosis scoring
		prognosis_scores = {
			"Terminal": 4,
			"Poor": 3,
			"Fair": 2,
			"Good": 1,
			"Excellent": 0
		}
		score += prognosis_scores.get(self.prognosis, 0)
		
		# Categorize complexity
		if score >= 10:
			complexity = "Very High"
		elif score >= 7:
			complexity = "High"
		elif score >= 4:
			complexity = "Moderate"
		elif score >= 2:
			complexity = "Low"
		else:
			complexity = "Minimal"
		
		return {
			"score": score,
			"complexity": complexity,
			"factors": self.get_complexity_factors()
		}
	
	def get_complexity_factors(self):
		"""Get factors contributing to care complexity"""
		factors = []
		
		if self.severity_level in ["Severe", "Critical"]:
			factors.append(f"High severity condition: {self.primary_diagnosis}")
		
		if self.mobility_status in ["Wheelchair Dependent", "Bedridden"]:
			factors.append(f"Limited mobility: {self.mobility_status}")
		
		if self.cognitive_status in ["Moderate Impairment", "Severe Impairment"]:
			factors.append(f"Cognitive impairment: {self.cognitive_status}")
		
		if self.nursing_care_required:
			factors.append("Requires nursing care")
		
		if self.medication_compliance in ["Poor", "Non-compliant"]:
			factors.append("Poor medication compliance")
		
		if self.prognosis in ["Poor", "Terminal"]:
			factors.append(f"Poor prognosis: {self.prognosis}")
		
		if self.readmission_risk in ["High", "Very High"]:
			factors.append(f"High readmission risk")
		
		return factors
	
	def get_healthcare_team_summary(self):
		"""Get summary of healthcare team"""
		team_summary = {
			"primary_care": self.primary_care_physician or "Not assigned",
			"specialists": [],
			"total_providers": 0
		}
		
		if self.specialists:
			team_summary["specialists"] = [spec.strip() for spec in self.specialists.split('\n') if spec.strip()]
		
		# Count total providers
		providers = 0
		if self.primary_care_physician:
			providers += 1
		providers += len(team_summary["specialists"])
		
		team_summary["total_providers"] = providers
		
		return team_summary
	
	def create_medication_review_reminder(self):
		"""Create reminder for medication review"""
		if not self.current_medications:
			return
		
		try:
			# Create reminder for 6 months from now
			from frappe.utils import add_months
			review_date = add_months(today(), 6)
			
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Medication Review Due: {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
			todo_doc.reference_type = "Medical History"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.recorded_by
			todo_doc.owner = self.recorded_by
			todo_doc.date = review_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating medication review reminder: {str(e)}")
