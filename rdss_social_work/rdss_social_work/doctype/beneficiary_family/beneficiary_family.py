# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class BeneficiaryFamily(Document):
	def before_save(self):
		"""Set default values and calculate fields before saving"""
		# Set registration date if not provided
		if not self.registration_date:
			self.registration_date = today()
		
		# Set primary social worker if not provided
		if not self.primary_social_worker:
			self.primary_social_worker = frappe.session.user
		
		# Set default status for new records
		if not self.family_status:
			self.family_status = "Active"
		
		# Update total family members count
		self.update_family_member_count()
	
	def validate(self):
		"""Validate beneficiary family data"""
		# Validate contact information
		if self.primary_email_address:
			self.validate_email()
		
		# Validate phone numbers
		if self.primary_mobile_number:
			self.validate_phone_number(self.primary_mobile_number, "Primary Mobile Number")
		if self.primary_home_number:
			self.validate_phone_number(self.primary_home_number, "Primary Home Number")
		
		# Ensure at least one emergency contact
		if not (self.emergency_contact_1_name and self.emergency_contact_1_phone):
			frappe.msgprint(
				"At least one emergency contact is required for the family",
				title="Emergency Contact Required",
				indicator="orange"
			)
	
	def validate_email(self):
		"""Validate email format"""
		import re
		email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		if not re.match(email_pattern, self.primary_email_address):
			frappe.throw("Please enter a valid email address")
	
	def validate_phone_number(self, phone, field_name):
		"""Validate phone number format"""
		# Remove spaces, dashes, and plus signs for validation
		clean_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
		
		if not clean_phone.isdigit():
			frappe.throw(f"Invalid {field_name} format. Please enter numbers only.")
		
		if len(clean_phone) < 8 or len(clean_phone) > 15:
			frappe.throw(f"{field_name} should be between 8-15 digits")
	
	def update_family_member_count(self):
		"""Update the count of family members"""
		count = frappe.db.count('Beneficiary', {'beneficiary_family': self.name})
		self.total_family_members = count
	
	def on_update(self):
		"""Actions to perform after updating beneficiary family"""
		# Update related records if family name changed
		if self.has_value_changed('family_name'):
			self.update_related_records()
	
	def update_related_records(self):
		"""Update related case records when family details change"""
		# Update cases linked to this family
		cases = frappe.get_all('Case', filters={'beneficiary_family': self.name})
		for case in cases:
			case_doc = frappe.get_doc('Case', case.name)
			case_doc.add_comment('Info', f'Family details updated: {self.family_name}')
	
	def get_family_members(self):
		"""Get all beneficiaries in this family"""
		return frappe.get_all('Beneficiary', 
			filters={'beneficiary_family': self.name},
			fields=['name', 'beneficiary_name', 'current_status', 'primary_diagnosis', 'date_of_birth'],
			order_by='beneficiary_name'
		)
	
	def get_active_cases(self):
		"""Get all active cases for this family"""
		return frappe.get_all('Case', 
			filters={
				'beneficiary_family': self.name,
				'case_status': ['in', ['Open', 'Active', 'In Progress']]
			},
			fields=['name', 'case_title', 'case_status', 'primary_social_worker', 'modified'],
			order_by='modified desc'
		)
	
	def get_family_appointments(self):
		"""Get all appointments for family members"""
		family_members = [member.name for member in self.get_family_members()]
		if not family_members:
			return []
		
		return frappe.get_all('Appointment',
			filters={
				'beneficiary': ['in', family_members],
				'appointment_status': ['in', ['Scheduled', 'Confirmed', 'In Progress']]
			},
			fields=['name', 'beneficiary', 'appointment_date', 'appointment_time', 'appointment_type', 'appointment_status'],
			order_by='appointment_date, appointment_time'
		)
	
	def add_family_member(self, beneficiary_name, relationship=None):
		"""Add a beneficiary to this family"""
		if frappe.db.exists('Beneficiary', {'beneficiary_name': beneficiary_name}):
			beneficiary = frappe.get_doc('Beneficiary', {'beneficiary_name': beneficiary_name})
			beneficiary.beneficiary_family = self.name
			if relationship:
				beneficiary.family_relationship = relationship
			beneficiary.save()
			self.update_family_member_count()
			return beneficiary.name
		else:
			frappe.throw(f"Beneficiary '{beneficiary_name}' does not exist")
	
	def remove_family_member(self, beneficiary_name):
		"""Remove a beneficiary from this family"""
		beneficiary = frappe.get_doc('Beneficiary', beneficiary_name)
		beneficiary.beneficiary_family = None
		beneficiary.family_relationship = None
		beneficiary.save()
		self.update_family_member_count()
	
	def get_family_summary(self):
		"""Get summary information for dashboard display"""
		family_members = self.get_family_members()
		active_cases = self.get_active_cases()
		upcoming_appointments = self.get_family_appointments()
		
		return {
			'total_members': len(family_members),
			'active_cases': len(active_cases),
			'upcoming_appointments': len(upcoming_appointments),
			'family_head': self.family_head,
			'primary_contact': self.primary_mobile_number or self.primary_home_number,
			'status': self.family_status
		}
