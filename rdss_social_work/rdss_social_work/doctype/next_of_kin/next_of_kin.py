# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff
from datetime import date


class NextofKin(Document):
	def before_save(self):
		"""Set default values and calculate fields before saving"""
		# Calculate age from date of birth
		if self.date_of_birth:
			self.age = self.calculate_age(self.date_of_birth)
		
		# Set consent date if not provided
		if not self.consent_date and (self.consent_to_contact or self.consent_to_share_information):
			self.consent_date = frappe.utils.today()
		
		# Set consent given by if not provided
		if not self.consent_given_by and (self.consent_to_contact or self.consent_to_share_information):
			self.consent_given_by = frappe.session.user
	
	def validate(self):
		"""Validate next of kin data"""
		# Validate contact information
		if self.email_address:
			self.validate_email()
		
		# Validate phone numbers
		if self.mobile_number:
			self.validate_phone_number(self.mobile_number, "Mobile Number")
		if self.home_number:
			self.validate_phone_number(self.home_number, "Home Number")
		if self.work_number:
			self.validate_phone_number(self.work_number, "Work Number")
		
		# Validate BC/NRIC format if provided
		if self.bc_nric_no:
			self.validate_bc_nric()
		
		# Ensure primary caregiver has appropriate availability
		if self.is_primary_caregiver and self.caregiver_availability in ["Not Available", "Emergency Only"]:
			frappe.msgprint(
				"Primary caregiver should have more availability than 'Not Available' or 'Emergency Only'",
				title="Caregiver Availability Warning",
				indicator="orange"
			)
		
		# Validate emergency contact requirements
		if self.emergency_contact_priority == "Primary" and self.consent_to_emergency_contact != "Yes":
			frappe.throw("Primary emergency contact must consent to emergency contact")
	
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
	
	def get_linked_beneficiaries(self):
		"""Get all beneficiaries linked to this next of kin"""
		# This will be implemented when we create the linking mechanism
		# For now, return empty list
		return []
	
	def get_contact_history(self):
		"""Get contact history for this next of kin"""
		# This will be implemented when we create case notes system
		return []
	
	def is_available_now(self):
		"""Check if the contact is available based on their preferences"""
		from datetime import datetime
		
		current_hour = datetime.now().hour
		
		if self.best_time_to_contact == "Morning (9am-12pm)":
			return 9 <= current_hour < 12
		elif self.best_time_to_contact == "Afternoon (12pm-6pm)":
			return 12 <= current_hour < 18
		elif self.best_time_to_contact == "Evening (6pm-9pm)":
			return 18 <= current_hour < 21
		elif self.best_time_to_contact == "Anytime":
			return True
		else:
			return False  # Weekends Only or Emergency Only
	
	def get_preferred_contact_info(self):
		"""Get the preferred contact information based on preferences"""
		contact_methods = {
			"Mobile": self.mobile_number,
			"Home Phone": self.home_number,
			"Work Phone": self.work_number,
			"Email": self.email_address
		}
		
		return contact_methods.get(self.preferred_contact_method, self.mobile_number)
