import frappe
from frappe import _

def get_context(context):
    context.title = "Beneficiary Portal"
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        context.show_access_issue = True
        context.access_message = "Please log in to access the beneficiary portal."
        return context
    
    # Check if user has Beneficiary role
    user_roles = frappe.get_roles(frappe.session.user)
    if "Beneficiary" not in user_roles:
        context.show_access_issue = True
        context.access_message = "You do not have permission to access this portal. Please contact support."
        return context
    
    try:
        # Get complete beneficiary data
        beneficiary_data = frappe.db.sql("""
            SELECT name, beneficiary_name, email_address, primary_diagnosis, 
                   current_status, date_of_birth, gender, mobile_number,
                   address_line_1, address_line_2, postal_code, severity_level,
                   emergency_contact_1_name, emergency_contact_1_phone
            FROM tabBeneficiary 
            WHERE email_address = %s
        """, (frappe.session.user,), as_dict=True)
        
        if not beneficiary_data:
            context.show_access_issue = True
            context.access_message = f"Unable to load beneficiary information for {frappe.session.user}. Please ensure you are logged in with a valid beneficiary account."
            return context
        
        context.beneficiary = beneficiary_data[0]
        
        # Get recent applications with correct field names
        try:
            applications = frappe.get_all("Support Scheme Application",
                filters={"beneficiary": context.beneficiary["name"]},
                fields=["name", "application_date", "scheme_type", "application_status", "approved_amount"],
                order_by="creation desc",
                limit=10
            )
            context.recent_applications = applications
            
            # Create a mapping of existing applications by scheme type for restriction logic
            context.existing_scheme_applications = {}
            for app in applications:
                context.existing_scheme_applications[app.scheme_type] = {
                    "name": app.name,
                    "status": app.application_status,
                    "can_cancel": app.application_status in ["Draft", "Submitted", "Under Admin Review"]
                }
            
            # Get application statistics
            context.total_applications = len(frappe.get_all("Support Scheme Application", 
                filters={"beneficiary": context.beneficiary["name"]}))
            context.approved_applications = len(frappe.get_all("Support Scheme Application", 
                filters={"beneficiary": context.beneficiary["name"], "application_status": "Approved"}))
            context.pending_applications = len(frappe.get_all("Support Scheme Application", 
                filters={"beneficiary": context.beneficiary["name"], "application_status": ["in", ["Draft", "Submitted", "Under Admin Review", "Under Director Review"]]}))
        except Exception as e:
            frappe.log_error(f"Error loading applications: {str(e)}")
            # If applications lookup fails, set defaults
            context.recent_applications = []
            context.existing_scheme_applications = {}
            context.total_applications = 0
            context.approved_applications = 0
            context.pending_applications = 0
        
        # Get upcoming appointments
        try:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            appointments = frappe.db.sql("""
                SELECT name, appointment_date, appointment_time, appointment_type, 
                       appointment_status, purpose, location_type, appointment_location,
                       social_worker, duration_minutes, special_instructions
                FROM tabAppointment 
                WHERE beneficiary = %s 
                AND appointment_date >= %s
                AND appointment_status IN ('Scheduled', 'Confirmed')
                ORDER BY appointment_date ASC, appointment_time ASC
                LIMIT 3
            """, (context.beneficiary["name"], today), as_dict=True)
            
            # Get social worker names
            for appointment in appointments:
                if appointment.social_worker:
                    social_worker_name = frappe.db.get_value("User", appointment.social_worker, "full_name")
                    appointment.social_worker_name = social_worker_name or appointment.social_worker
                else:
                    appointment.social_worker_name = "Not assigned"
            
            context.upcoming_appointments = appointments
            
        except Exception as e:
            frappe.log_error(f"Error loading appointments: {str(e)}")
            context.upcoming_appointments = []

        # Add available support schemes
        context.schemes = [
            {
                "name": "Medical Intervention Support",
                "description": "Financial assistance for medical treatments and interventions",
                "deadline": "30 April",
                "route": "/medical_intervention_application"
            },
            {
                "name": "Power for Life Subsidy (PLS)",
                "description": "Up to $100 per month for beneficiary using ventilator on long term basis",
                "deadline": "30 April",
                "route": "/power-for-life-application"
            },
            {
                "name": "Special Formula Subsidy (SFS)",
                "description": "$100 per month per beneficiary who needs unique formula as part of their dietary requirements",
                "deadline": "30 April",
                "route": "/special-formula-application"
            },
            {
                "name": "Optical / Dental Subsidy (ODS)",
                "description": "$600 (Dental) $600 (Optical) per beneficiary for each financial year",
                "deadline": "30 April",
                "route": "/optical-dental-application"
            },
            {
                "name": "Therapy Support Subsidy (TSS)",
                "description": "Up to $1,800 per beneficiary for each financial year",
                "deadline": "30 April",
                "route": "/therapy-support-application"
            },
            {
                "name": "Vital Support Subsidy (VSS)",
                "description": "Up to $10,000 per beneficiary within 5 years",
                "deadline": "30 April",
                "route": "/vital-support-application"
            }
        ]
        
        context.show_access_issue = False
        
    except Exception as e:
        frappe.log_error(f"Error loading beneficiary portal: {str(e)}")
        context.show_access_issue = True
        context.access_message = f"An error occurred while loading your information: {str(e)}"
    
    return context
