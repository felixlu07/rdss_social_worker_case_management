import frappe
from frappe import _
from datetime import datetime, timedelta
import os

def send_appointment_reminders():
    """
    Send appointment reminder notifications 3 days before scheduled appointments.
    This function is designed to be scheduled to run daily.
    """
    # Calculate the date 3 days from now
    target_date = datetime.now().date() + timedelta(days=3)
    
    # Find all appointments scheduled for the target date
    appointments = frappe.get_all(
        "Appointment",
        filters={
            "appointment_date": target_date,
            "docstatus": 1  # Only consider submitted appointments
        },
        fields=["name", "social_worker", "beneficiary", "appointment_date", "appointment_time"]
    )
    
    if not appointments:
        frappe.logger().info(f"No appointments found for {target_date}")
        return
    
    # Get the template path
    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "appointment_reminder_template.html"
    )
    
    # Check if template exists
    if not os.path.exists(template_path):
        frappe.logger().error("Appointment reminder template not found")
        return
    
    # Read the template
    with open(template_path, "r") as template_file:
        template_content = template_file.read()
    
    # Send notifications for each appointment
    for appointment in appointments:
        try:
            # Get the full appointment document
            doc = frappe.get_doc("Appointment", appointment.name)
            
            # Skip if no social worker assigned
            if not doc.social_worker:
                frappe.logger().info(f"No social worker assigned to appointment {doc.name}, skipping notification")
                continue
            
            # Get social worker's email
            social_worker_email = frappe.db.get_value("User", doc.social_worker, "email")
            if not social_worker_email:
                frappe.logger().info(f"No email found for social worker {doc.social_worker}, skipping notification")
                continue
            
            # Get beneficiary name for subject line
            beneficiary_name = frappe.db.get_value("Beneficiary", doc.beneficiary, "beneficiary_name") if doc.beneficiary else "Unknown"
            
            # Format the appointment date for the subject
            appointment_date_str = frappe.utils.get_datetime(doc.appointment_date).strftime('%d %b %Y')
            
            # Render the template with the appointment data
            subject = f"Reminder: Appointment with {beneficiary_name} on {appointment_date_str}"
            
            # Send the email notification
            frappe.sendmail(
                recipients=social_worker_email,
                subject=subject,
                message=frappe.render_template(template_content, {"doc": doc}),
                reference_doctype="Appointment",
                reference_name=doc.name
            )
            
            frappe.logger().info(f"Sent appointment reminder for {doc.name} to {social_worker_email}")
            
        except Exception as e:
            frappe.logger().error(f"Error sending appointment reminder for {appointment.name}: {str(e)}")
    
    frappe.logger().info(f"Processed {len(appointments)} appointment reminders")

def setup_appointment_reminder_scheduler():
    """
    Set up the scheduler for appointment reminders.
    This should be called during app installation or update.
    """
    # Check if the scheduler event already exists
    if not frappe.db.exists("Scheduled Job Type", {"method": "rdss_social_work.rdss_social_work.notifications.appointment_notification.send_appointment_reminders"}):
        # Create a new scheduler event
        job = frappe.new_doc("Scheduled Job Type")
        job.update({
            "method": "rdss_social_work.rdss_social_work.notifications.appointment_notification.send_appointment_reminders",
            "frequency": "Daily",
            "cron_format": "0 8 * * *",  # Run daily at 8:00 AM
            "docstatus": 0,
            "name": "Appointment Reminders",
            "module": "RDSS Social Work"
        })
        job.insert()
        frappe.db.commit()
        frappe.logger().info("Appointment reminder scheduler has been set up")
