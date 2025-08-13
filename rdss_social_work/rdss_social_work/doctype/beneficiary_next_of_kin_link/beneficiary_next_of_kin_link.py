# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BeneficiaryNextofKinLink(Document):
	def validate(self):
		"""Validate the beneficiary-next of kin relationship"""
		# Ensure only one primary caregiver per beneficiary
		if self.is_primary_caregiver:
			parent_doc = self.get_parent_doc()
			if parent_doc:
				for row in parent_doc.next_of_kin_relationships:
					if row.name != self.name and row.is_primary_caregiver:
						frappe.throw("Only one primary caregiver is allowed per beneficiary")
		
		# Auto-populate relationship type from Next of Kin record if not set
		if not self.relationship_type and self.next_of_kin:
			next_of_kin_doc = frappe.get_doc("Next of Kin", self.next_of_kin)
			if next_of_kin_doc.relationship_to_beneficiary:
				self.relationship_type = next_of_kin_doc.relationship_to_beneficiary
	
	def get_parent_doc(self):
		"""Get the parent Beneficiary document"""
		if hasattr(self, 'parent') and self.parent:
			return frappe.get_doc("Beneficiary", self.parent)
		return None
