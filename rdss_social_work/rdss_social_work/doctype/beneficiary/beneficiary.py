# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff
from datetime import date


class Beneficiary(Document):
	def before_save(self):
		"""Set default values and calculate fields before saving"""
		# Set registration date if not provided
		if not self.registration_date:
			self.registration_date = frappe.utils.today()
		
		# Set initial social worker if not provided
		if not self.initial_social_worker:
			self.initial_social_worker = frappe.session.user
		
		# Calculate age from date of birth
		if self.date_of_birth:
			self.age = self.calculate_age(self.date_of_birth)
		
		# Set default status for new records
		if not self.current_status:
			self.current_status = "Active"
	
	def validate(self):
		"""Validate beneficiary data"""
		# Validate BC/NRIC format (basic validation)
		if self.bc_nric_no:
			self.validate_bc_nric()
		
		# Validate contact information
		if self.email_address:
			self.validate_email()
		
		# Validate phone numbers
		if self.mobile_number:
			self.validate_phone_number(self.mobile_number, "Mobile Number")
		if self.home_number:
			self.validate_phone_number(self.home_number, "Home Number")
		
		# Ensure at least one emergency contact
		if not (self.emergency_contact_1_name and self.emergency_contact_1_phone):
			frappe.msgprint(
				"At least one emergency contact is required",
				title="Emergency Contact Required",
				indicator="orange"
			)
	
	def calculate_age(self, birth_date):
		"""Calculate age from date of birth"""
		if not birth_date:
			return None
		
		today = date.today()
		birth_date = getdate(birth_date)
		
		age = today.year - birth_date.year
		if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
			age -= 1
		
		return age
	
	def validate_bc_nric(self):
		"""Basic validation for BC/NRIC format"""
		bc_nric = self.bc_nric_no.upper().strip()
		
		# Basic format check (simplified)
		if len(bc_nric) < 8 or len(bc_nric) > 12:
			frappe.throw("BC/NRIC format appears invalid. Please check the format.")
	
	def validate_email(self):
		"""Validate email format"""
		import re
		email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		if not re.match(email_pattern, self.email_address):
			frappe.throw("Please enter a valid email address")
	
	def validate_phone_number(self, phone, field_name):
		"""Validate phone number format"""
		# Remove spaces, dashes, and plus signs for validation
		clean_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
		
		if not clean_phone.isdigit():
			frappe.throw(f"Invalid {field_name} format. Please enter numbers only.")
		
		if len(clean_phone) < 8 or len(clean_phone) > 15:
			frappe.throw(f"{field_name} should be between 8-15 digits")
	
	def on_update(self):
		"""Actions to perform after updating beneficiary"""
		# Update related records if name changed
		if self.has_value_changed('beneficiary_name'):
			self.update_related_records()
	
	def update_related_records(self):
		"""Update related case records when beneficiary details change"""
		# Update cases linked to this beneficiary
		cases = frappe.get_all('Case', filters={'beneficiary': self.name})
		for case in cases:
			case_doc = frappe.get_doc('Case', case.name)
			case_doc.add_comment('Info', f'Beneficiary details updated: {self.beneficiary_name}')
	
	def get_active_cases(self):
		"""Get all active cases for this beneficiary"""
		return frappe.get_all('Case', 
			filters={
				'beneficiary': self.name,
				'case_status': ['in', ['Open', 'Active', 'In Progress']]
			},
			fields=['name', 'case_status', 'assigned_social_worker', 'modified']
		)
	
	def get_latest_assessment(self):
		"""Get the most recent assessment for this beneficiary"""
		assessments = frappe.get_all('Initial Assessment',
			filters={'client_name': self.beneficiary_name},
			fields=['name', 'assessment_date', 'assessed_by'],
			order_by='assessment_date desc',
			limit=1
		)
		return assessments[0] if assessments else None
