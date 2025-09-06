import frappe
from frappe.model.document import Document
from frappe.utils import now

class SupportSchemeApplication(Document):
    def validate(self):
        # Validate beneficiary email matches user email for portal users
        if frappe.session.user != "Administrator" and not frappe.has_permission("Support Scheme Application", "write"):
            beneficiary_email = frappe.db.get_value("Beneficiary", self.beneficiary, "email_address")
            if beneficiary_email != frappe.session.user:
                frappe.throw("You can only create applications for your registered email address.")
    
    def before_submit(self):
        self.submitted_by = frappe.session.user
        self.submitted_date = now()
        self.application_status = "Submitted"
    
    def on_submit(self):
        # Notify Head of Admin about new application
        self.notify_admin_review()
    
    def notify_admin_review(self):
        # Get users with Head of Admin role
        admin_users = frappe.get_all("Has Role", 
            filters={"role": "Head of Admin", "parenttype": "User"},
            fields=["parent"]
        )
        
        for admin in admin_users:
            frappe.sendmail(
                recipients=[admin.parent],
                subject=f"New Support Scheme Application - {self.name}",
                message=f"""
                A new support scheme application has been submitted:
                
                Application ID: {self.name}
                Beneficiary: {self.beneficiary_name}
                Scheme Type: {self.scheme_type}
                Application Date: {self.application_date}
                
                Please review and approve/reject this application.
                """
            )
    
    def approve_by_admin(self):
        if not frappe.has_permission("Support Scheme Application", "write") or not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Head of Admin"}):
            frappe.throw("Only Head of Admin can approve applications at this stage.")
        
        self.reviewed_by_admin = frappe.session.user
        self.admin_review_date = now()
        self.application_status = "Admin Approved"
        self.save()
        
        # Notify RDSS Director
        self.notify_director_review()
    
    def notify_director_review(self):
        # Get users with RDSS Director role
        director_users = frappe.get_all("Has Role",
            filters={"role": "RDSS Director", "parenttype": "User"},
            fields=["parent"]
        )
        
        for director in director_users:
            frappe.sendmail(
                recipients=[director.parent],
                subject=f"Support Scheme Application for Final Approval - {self.name}",
                message=f"""
                A support scheme application has been approved by Admin and requires your final approval:
                
                Application ID: {self.name}
                Beneficiary: {self.beneficiary_name}
                Scheme Type: {self.scheme_type}
                Admin Approved By: {self.reviewed_by_admin}
                Admin Review Date: {self.admin_review_date}
                
                Please provide final approval/rejection.
                """
            )
    
    def approve_by_director(self, approved_amount=None):
        if not frappe.has_permission("Support Scheme Application", "write") or not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "RDSS Director"}):
            frappe.throw("Only RDSS Director can provide final approval.")
        
        self.approved_by_director = frappe.session.user
        self.director_approval_date = now()
        self.application_status = "Approved"
        if approved_amount:
            self.approved_amount = approved_amount
        self.save()
        
        # Notify beneficiary of approval
        self.notify_beneficiary_approval()
    
    def reject_application(self, rejection_reason, rejected_by_role="Head of Admin"):
        if rejected_by_role == "Head of Admin":
            if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Head of Admin"}):
                frappe.throw("Only Head of Admin can reject at this stage.")
            self.reviewed_by_admin = frappe.session.user
            self.admin_review_date = now()
        elif rejected_by_role == "RDSS Director":
            if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "RDSS Director"}):
                frappe.throw("Only RDSS Director can reject at this stage.")
            self.approved_by_director = frappe.session.user
            self.director_approval_date = now()
        
        self.application_status = "Rejected"
        self.rejection_reason = rejection_reason
        self.save()
        
        # Notify beneficiary of rejection
        self.notify_beneficiary_rejection()
    
    def notify_beneficiary_approval(self):
        if self.beneficiary_email:
            frappe.sendmail(
                recipients=[self.beneficiary_email],
                subject=f"Support Scheme Application Approved - {self.name}",
                message=f"""
                Dear {self.beneficiary_name},
                
                Your support scheme application has been approved!
                
                Application ID: {self.name}
                Scheme Type: {self.scheme_type}
                Approved Amount: ${self.approved_amount or 'To be determined'}
                
                You will be contacted regarding the next steps.
                
                Best regards,
                RDSS Team
                """
            )
    
    def notify_beneficiary_rejection(self):
        if self.beneficiary_email:
            frappe.sendmail(
                recipients=[self.beneficiary_email],
                subject=f"Support Scheme Application Update - {self.name}",
                message=f"""
                Dear {self.beneficiary_name},
                
                We regret to inform you that your support scheme application requires revision.
                
                Application ID: {self.name}
                Scheme Type: {self.scheme_type}
                Reason: {self.rejection_reason}
                
                Please contact us for more information or to resubmit your application.
                
                Best regards,
                RDSS Team
                """
            )

@frappe.whitelist()
def get_beneficiary_applications():
    """Get applications for the current beneficiary user"""
    user_email = frappe.session.user
    beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user_email}, "name")
    
    if not beneficiary:
        return []
    
    applications = frappe.get_all("Support Scheme Application",
        filters={"beneficiary": beneficiary},
        fields=["name", "scheme_type", "application_date", "application_status", "approved_amount"],
        order_by="creation desc"
    )
    
    return applications

@frappe.whitelist()
def admin_approve_application(application_name):
    """Admin approval method"""
    doc = frappe.get_doc("Support Scheme Application", application_name)
    doc.approve_by_admin()
    return {"status": "success", "message": "Application approved by admin"}

@frappe.whitelist()
def director_approve_application(application_name, approved_amount=None):
    """Director approval method"""
    doc = frappe.get_doc("Support Scheme Application", application_name)
    doc.approve_by_director(approved_amount)
    return {"status": "success", "message": "Application approved by director"}

@frappe.whitelist()
def reject_application(application_name, rejection_reason, rejected_by_role="Head of Admin"):
    """Reject application method"""
    doc = frappe.get_doc("Support Scheme Application", application_name)
    doc.reject_application(rejection_reason, rejected_by_role)
    return {"status": "success", "message": "Application rejected"}

def validate_beneficiary_access(doc, method=None):
    """Validate that the user has access to this beneficiary's application"""
    if frappe.session.user == "Administrator" or frappe.has_permission("Support Scheme Application", "write"):
        return
        
    # For regular beneficiary users, check if they own this application
    beneficiary_email = frappe.db.get_value("Beneficiary", doc.beneficiary, "email_address")
    if beneficiary_email != frappe.session.user:
        frappe.throw("You can only access applications for your registered email address.")

# def has_permission(doc, user=None, permission_type=None):
#     """Custom permission check for Support Scheme Applications"""
#     if not user:
#         user = frappe.session.user
#     
#     # Allow administrators and staff full access
#     if user == "Administrator":
#         return True
#     
#     # Check if user has admin roles
#     user_roles = frappe.get_roles(user)
#     admin_roles = ["System Manager", "Social Worker", "Head of Admin", "RDSS Director"]
#     if any(role in user_roles for role in admin_roles):
#         return True
#     
#     # For beneficiaries, only allow access to their own applications
#     if "Beneficiary" in user_roles:
#         if doc:
#             beneficiary_email = frappe.db.get_value("Beneficiary", doc.beneficiary, "email_address")
#             return beneficiary_email == user
#         else:
#             # For list view, return True and let the query filter handle it
#             return True
#     
#     return False

# def get_permission_query_conditions(user=None):
#     """Return query conditions for Support Scheme Applications based on user permissions"""
#     if not user:
#         user = frappe.session.user
#     
#     # Allow administrators and staff to see all
#     if user == "Administrator":
#         return ""
#     
#     user_roles = frappe.get_roles(user)
#     admin_roles = ["System Manager", "Social Worker", "Head of Admin", "RDSS Director"]
#     if any(role in user_roles for role in admin_roles):
#         return ""
#     
#     # For beneficiaries, only show their own applications
#     if "Beneficiary" in user_roles:
#         beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user}, "name")
#         if beneficiary:
#             return f"`tabSupport Scheme Application`.beneficiary = '{beneficiary}'"
#     
#     # Default: no access
#     return "1=0"
