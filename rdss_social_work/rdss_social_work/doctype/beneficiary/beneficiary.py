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
		
		# Validate beneficiary family is required
		if not self.beneficiary_family:
			frappe.throw("Beneficiary Family is required. Please select or create a family first.")
	
	def validate(self):
		"""Validate beneficiary data"""
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
		
		# Update family member count when beneficiary family changes
		if self.has_value_changed('beneficiary_family'):
			self.update_family_member_counts()
	
	def update_related_records(self):
		"""Update related case records when beneficiary details change"""
		# Update cases linked to this beneficiary
		cases = frappe.get_all('Case', filters={'beneficiary': self.name})
		for case in cases:
			case_doc = frappe.get_doc('Case', case.name)
			case_doc.add_comment('Info', f'Beneficiary details updated: {self.beneficiary_name}')
	
	def update_family_member_counts(self):
		"""Update family member counts for old and new families"""
		# Update old family if it exists
		old_family = self.get_doc_before_save()
		if old_family and old_family.beneficiary_family:
			old_family_doc = frappe.get_doc('Beneficiary Family', old_family.beneficiary_family)
			old_family_doc.update_family_member_count()
			old_family_doc.save()
		
		# Update new family
		if self.beneficiary_family:
			new_family_doc = frappe.get_doc('Beneficiary Family', self.beneficiary_family)
			new_family_doc.update_family_member_count()
			new_family_doc.save()
	
	def get_family_cases(self):
		"""Get all cases for this beneficiary's family"""
		if not self.beneficiary_family:
			return []
		
		return frappe.get_all('Case', 
			filters={
				'beneficiary_family': self.beneficiary_family,
				'case_status': ['in', ['Open', 'Active', 'In Progress']]
			},
			fields=['name', 'case_title', 'case_status', 'primary_social_worker', 'modified']
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
