# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CasePriority(Document):
    def get_indicator(self):
        """Return indicator color for list view based on color_code field"""
        return (self.priority_code, self.color_code, f"priority_code,=,{self.priority_code}")
    
    def validate(self):
        """Validate priority code format (P1-P6)"""
        if not self.priority_code:
            return
            
        if not (self.priority_code.startswith('P') and len(self.priority_code) == 2 and self.priority_code[1:].isdigit()):
            frappe.throw("Priority Code must be in the format P1, P2, P3, etc.")
            
        priority_number = int(self.priority_code[1:])
        if priority_number < 1 or priority_number > 6:
            frappe.throw("Priority Code must be between P1 and P6")
