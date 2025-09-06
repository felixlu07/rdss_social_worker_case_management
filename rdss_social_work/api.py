import frappe
from frappe import _
from frappe.utils import now

@frappe.whitelist()
def create_mis_application(data, submit=False):
    """Create Medical Intervention Scheme application"""
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        # Validate beneficiary access
        user_email = frappe.session.user
        beneficiary_email = frappe.db.get_value("Beneficiary", data.get("beneficiary"), "email_address")
        
        if user_email != beneficiary_email and not frappe.has_permission("Support Scheme Application", "write"):
            frappe.throw(_("Access Denied"))
        
        # Create Medical Intervention Scheme document
        mis_doc = frappe.new_doc("Medical Intervention Scheme")
        
        # Set basic fields
        for field in ["beneficiary", "application_date", "main_medical_diagnosis", "nature_of_support", 
                     "nature_of_disability", "duration_of_disability", "reimbursement_type",
                     "preferred_payment_method", "paynow_mobile", "paynow_name", 
                     "bank_transfer_details", "bank_account_name", "assessor_name",
                     "health_institution", "designation", "contact_number", "email_address",
                     "endorsement_date", "additional_notes"]:
            if data.get(field):
                mis_doc.set(field, data.get(field))
        
        # Set checkboxes
        for checkbox in ["medical_consumables", "medical_equipment", "medication", "consultation", "surgery"]:
            mis_doc.set(checkbox, data.get(checkbox, 0))
        
        # Add item details
        if data.get("item_details_table"):
            for item in data.get("item_details_table"):
                mis_doc.append("item_details_table", item)
        
        mis_doc.insert()
        
        # Create corresponding Support Scheme Application
        app_doc = frappe.new_doc("Support Scheme Application")
        app_doc.beneficiary = data.get("beneficiary")
        app_doc.scheme_type = "Medical Intervention Scheme (MIS)"
        app_doc.application_date = data.get("application_date")
        app_doc.medical_intervention_details = f"MIS Application: {mis_doc.name}"
        
        # Ensure the beneficiary user is set as the owner
        app_doc.insert(ignore_permissions=True)
        
        # Set the correct owner to the beneficiary's email
        frappe.db.set_value("Support Scheme Application", app_doc.name, "owner", user_email)
        
        # Create User Permission to allow beneficiary to access this specific application
        user_perm = frappe.new_doc("User Permission")
        user_perm.user = user_email
        user_perm.allow = "Support Scheme Application"
        user_perm.for_value = app_doc.name
        user_perm.insert(ignore_permissions=True)
        
        frappe.db.commit()
        
        if submit:
            app_doc.submit()
        
        return {"status": "success", "application_id": app_doc.name, "mis_id": mis_doc.name}
        
    except Exception as e:
        frappe.log_error(f"Error creating MIS application: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_beneficiary_profile():
    """Get current beneficiary's profile information"""
    user_email = frappe.session.user
    beneficiary = frappe.db.get_value("Beneficiary", {"email_address": user_email}, 
        ["name", "beneficiary_name", "primary_diagnosis", "current_status", "email_address",
         "mobile_number", "address_line_1", "address_line_2", "postal_code"], as_dict=True)
    
    if not beneficiary:
        frappe.throw(_("No beneficiary record found"))
    
    return beneficiary

@frappe.whitelist()
def create_beneficiary_user(email, beneficiary_name, password):
    """Create user account for beneficiary during signup"""
    try:
        # Check if beneficiary exists with this email
        beneficiary = frappe.db.get_value("Beneficiary", {"email_address": email}, "name")
        
        if not beneficiary:
            frappe.throw(_("No beneficiary record found with this email address"))
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            frappe.throw(_("User account already exists for this email"))
        
        # Create user
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = beneficiary_name
        user.enabled = 1
        user.new_password = password
        user.send_welcome_email = 0
        
        # Add Beneficiary role
        user.append("roles", {"role": "Beneficiary"})
        
        user.insert(ignore_permissions=True)
        
        # Ensure role is properly assigned
        frappe.db.commit()
        
        # Double-check role assignment
        if not frappe.db.exists("Has Role", {"parent": email, "role": "Beneficiary"}):
            # Force add the role if it wasn't added
            role_doc = frappe.new_doc("Has Role")
            role_doc.parent = email
            role_doc.parenttype = "User"
            role_doc.parentfield = "roles"
            role_doc.role = "Beneficiary"
            role_doc.insert(ignore_permissions=True)
            frappe.db.commit()
        
        return {"status": "success", "message": "Account created successfully"}
        
    except Exception as e:
        frappe.log_error(f"Error creating beneficiary user: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def validate_beneficiary_email(email):
    """Validate if email belongs to a registered beneficiary"""
    beneficiary = frappe.db.get_value("Beneficiary", {"email_address": email}, "beneficiary_name")
    
    if beneficiary:
        return {"status": "success", "beneficiary_name": beneficiary}
    else:
        return {"status": "error", "message": "No beneficiary found with this email address"}

@frappe.whitelist()
def debug_user_beneficiary_match():
    """Debug user and beneficiary record matching"""
    try:
        current_user = frappe.session.user
        
        # Get all beneficiary records
        all_beneficiaries = frappe.get_all("Beneficiary", 
            fields=["name", "beneficiary_name", "email_address"])
        
        # Get user info
        user_info = frappe.get_doc("User", current_user)
        
        return {
            "status": "success",
            "current_user": current_user,
            "user_email": user_info.email,
            "user_first_name": user_info.first_name,
            "all_beneficiaries": all_beneficiaries,
            "matching_beneficiary": frappe.db.get_value("Beneficiary", 
                {"email_address": current_user}, 
                ["name", "beneficiary_name", "email_address"], as_dict=True)
        }
    except Exception as e:
        frappe.log_error(f"Error in debug_user_beneficiary_match: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=False)
def fix_beneficiary_role():
    """Fix beneficiary role assignment for current user"""
    try:
        email = frappe.session.user
        
        # Check if user exists
        if not frappe.db.exists("User", email):
            return {"status": "error", "message": f"User {email} does not exist"}
        
        # Check if beneficiary record exists using direct SQL
        beneficiary = frappe.db.sql("""
            SELECT beneficiary_name 
            FROM tabBeneficiary 
            WHERE email_address = %s
        """, (email,), as_dict=True)
        
        if not beneficiary:
            return {"status": "error", "message": "No beneficiary record found for this email"}
        
        # Check if user already has Beneficiary role
        has_role = frappe.db.exists("Has Role", {"parent": email, "role": "Beneficiary"})
        if has_role:
            return {"status": "success", "message": "User already has Beneficiary role"}
        
        # Add Beneficiary role
        role_doc = frappe.new_doc("Has Role")
        role_doc.parent = email
        role_doc.parenttype = "User"
        role_doc.parentfield = "roles"
        role_doc.role = "Beneficiary"
        role_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {"status": "success", "message": "Beneficiary role added successfully"}
        
    except Exception as e:
        frappe.log_error(f"Error fixing beneficiary role: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def create_or_link_beneficiary_record(beneficiary_name=None, beneficiary_id=None):
    """Create a new beneficiary record or link existing one to current user"""
    try:
        current_user = frappe.session.user
        
        if beneficiary_id:
            # Link existing beneficiary record
            if not frappe.db.exists("Beneficiary", beneficiary_id):
                return {"status": "error", "message": "Beneficiary record not found"}
            
            # Update the email address
            frappe.db.set_value("Beneficiary", beneficiary_id, "email_address", current_user)
            frappe.db.commit()
            
            return {"status": "success", "message": f"Linked beneficiary record {beneficiary_id} to {current_user}"}
        
        elif beneficiary_name:
            # Create new beneficiary record
            beneficiary = frappe.new_doc("Beneficiary")
            beneficiary.beneficiary_name = beneficiary_name
            beneficiary.email_address = current_user
            beneficiary.current_status = "Active"
            beneficiary.primary_diagnosis = "To be updated"
            beneficiary.insert(ignore_permissions=True)
            
            return {"status": "success", "message": f"Created new beneficiary record for {current_user}"}
        
        else:
            return {"status": "error", "message": "Either beneficiary_name or beneficiary_id is required"}
            
    except Exception as e:
        frappe.log_error(f"Error creating/linking beneficiary record: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_scheme_applications(scheme_type=None):
    """Get applications for admin/director review"""
    if not (frappe.has_permission("Support Scheme Application", "read") and 
            (frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Head of Admin"}) or
             frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "RDSS Director"}))):
        frappe.throw(_("Access Denied"))
    
    filters = {}
    if scheme_type:
        filters["scheme_type"] = scheme_type
    
    applications = frappe.get_all("Support Scheme Application",
        filters=filters,
        fields=["name", "beneficiary", "beneficiary_name", "scheme_type", 
               "application_date", "application_status", "approved_amount"],
        order_by="creation desc"
    )
    
    return applications

@frappe.whitelist()
def cancel_application(application_name):
    """Cancel a support scheme application if it's not yet approved"""
    try:
        # Get the application
        app_doc = frappe.get_doc("Support Scheme Application", application_name)
        
        # Check if current user is the beneficiary who submitted this application
        user_email = frappe.session.user
        beneficiary_email = frappe.db.get_value("Beneficiary", app_doc.beneficiary, "email_address")
        
        if user_email != beneficiary_email and not frappe.has_permission("Support Scheme Application", "write"):
            frappe.throw(_("Access Denied: You can only cancel your own applications"))
        
        # Check if application can be cancelled
        if app_doc.application_status in ["Approved"]:
            frappe.throw(_("Cannot cancel an approved application"))
        
        # Check if application is not in a cancellable state
        if app_doc.application_status not in ["Draft", "Submitted", "Under Admin Review"]:
            frappe.throw(_("Application cannot be cancelled at this stage"))
        
        # Cancel the application by setting docstatus to 2 (cancelled)
        app_doc.cancel()
        
        return {"status": "success", "message": "Application cancelled successfully"}
        
    except Exception as e:
        frappe.log_error(f"Error cancelling application: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def fix_application_ownership():
    """Fix ownership of existing Support Scheme Applications to match beneficiary emails"""
    try:
        if not frappe.has_permission("Support Scheme Application", "write"):
            frappe.throw(_("Access Denied"))
        
        # Get all Support Scheme Applications
        applications = frappe.get_all("Support Scheme Application", 
            fields=["name", "beneficiary", "owner"])
        
        fixed_count = 0
        for app in applications:
            # Get beneficiary email
            beneficiary_email = frappe.db.get_value("Beneficiary", app.beneficiary, "email_address")
            
            if beneficiary_email:
                # Update owner to beneficiary email if needed
                if beneficiary_email != app.owner:
                    frappe.db.set_value("Support Scheme Application", app.name, "owner", beneficiary_email)
                    fixed_count += 1
                
                # Check if User Permission exists, create if not
                existing_perm = frappe.db.exists("User Permission", {
                    "user": beneficiary_email,
                    "allow": "Support Scheme Application",
                    "for_value": app.name
                })
                
                if not existing_perm:
                    user_perm = frappe.new_doc("User Permission")
                    user_perm.user = beneficiary_email
                    user_perm.allow = "Support Scheme Application"
                    user_perm.for_value = app.name
                    user_perm.insert(ignore_permissions=True)
                    fixed_count += 1
        
        frappe.db.commit()
        
        return {
            "status": "success", 
            "message": f"Fixed ownership for {fixed_count} applications",
            "fixed_count": fixed_count,
            "total_applications": len(applications)
        }
        
    except Exception as e:
        frappe.log_error(f"Error fixing application ownership: {str(e)}")
        return {"status": "error", "message": str(e)}
