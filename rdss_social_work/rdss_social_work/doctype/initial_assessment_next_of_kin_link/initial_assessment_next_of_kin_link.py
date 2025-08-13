# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InitialAssessmentNextofKinLink(Document):
	def validate(self):
		"""Validate the next of kin link"""
		# Ensure only one primary contact per assessment
		if self.is_primary_contact:
			parent_doc = self.get_parent_doc()
			if parent_doc:
				for row in parent_doc.next_of_kin_contacts:
					if row.name != self.name and row.is_primary_contact:
						frappe.throw("Only one primary contact is allowed per assessment")
		
		# Ensure contact priority is unique within the assessment
		if self.contact_priority and self.contact_priority != "4 - Other":
			parent_doc = self.get_parent_doc()
			if parent_doc:
				for row in parent_doc.next_of_kin_contacts:
					if (row.name != self.name and 
						row.contact_priority == self.contact_priority and 
						row.contact_priority != "4 - Other"):
						frappe.throw(f"Contact priority '{self.contact_priority}' is already assigned to another contact")
	
	def get_parent_doc(self):
		"""Get the parent Initial Assessment document"""
		if hasattr(self, 'parent') and self.parent:
			return frappe.get_doc("Initial Assessment", self.parent)
		return None
