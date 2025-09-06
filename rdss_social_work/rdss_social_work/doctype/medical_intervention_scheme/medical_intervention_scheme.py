import frappe
from frappe.model.document import Document

class MedicalInterventionScheme(Document):
    def validate(self):
        # Calculate total amount from item details
        total = 0
        if self.item_details_table:
            for item in self.item_details_table:
                if item.amount:
                    total += item.amount
        self.total_amount_requested = total
    
    def before_submit(self):
        self.status = "Submitted"
