# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, get_time, add_days, get_datetime, time_diff_in_hours


class Appointment(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set scheduled by if not provided
		if not self.scheduled_by:
			self.scheduled_by = frappe.session.user
		
		# Set social worker if not provided
		if not self.social_worker:
			self.social_worker = frappe.session.user
		
		# Auto-populate beneficiary from case
		if self.case and not self.beneficiary:
			case_doc = frappe.get_doc("Case", self.case)
			self.beneficiary = case_doc.beneficiary
		
		# Set default status for new appointments
		if not self.appointment_status:
			self.appointment_status = "Scheduled"
		
		# Set default duration if not provided
		if not self.duration_minutes:
			duration_mapping = {
				"Phone Consultation": 30,
				"Video Call": 45,
				"Office Visit": 60,
				"Home Visit": 90,
				"Initial Assessment": 120,
				"Follow-up Assessment": 90,
				"Family Meeting": 90,
				"Crisis Intervention": 60
			}
			self.duration_minutes = duration_mapping.get(self.appointment_type, 60)
		
		# Set reminder date if reminder sent but date not set
		if self.reminder_sent and not self.reminder_date:
			self.reminder_date = today()
		
		# Auto-calculate follow-up date if required
		if self.follow_up_required and not self.follow_up_date:
			self.follow_up_date = add_days(self.appointment_date, 7)  # Default 1 week
	
	def on_submit(self):
		"""Create tasks when appointment is confirmed"""
		self.create_appointment_tasks()
	
	def create_appointment_tasks(self):
		"""Auto-create tasks for appointment preparation and follow-up"""
		# Create preparation task (1 day before appointment)
		if self.preparation_required:
			prep_date = add_days(self.appointment_date, -1)
			if prep_date >= getdate(today()):
				frappe.get_doc({
					"doctype": "ToDo",
					"description": f"Prepare for appointment with {self.beneficiary} - {self.purpose}",
					"reference_type": "Appointment",
					"reference_name": self.name,
					"assigned_by": frappe.session.user,
					"owner": self.social_worker,
					"date": prep_date,
					"priority": "Medium",
					"status": "Open"
				}).insert()
		
		# Create reminder task (same day as appointment)
		frappe.get_doc({
			"doctype": "ToDo", 
			"description": f"Appointment reminder: {self.beneficiary} at {self.appointment_time}",
			"reference_type": "Appointment",
			"reference_name": self.name,
			"assigned_by": frappe.session.user,
			"owner": self.social_worker,
			"date": self.appointment_date,
			"priority": "High" if self.priority in ["High", "Critical"] else "Medium",
			"status": "Open"
		}).insert()
		
		# Create follow-up task if required
		if self.follow_up_required and self.follow_up_date:
			frappe.get_doc({
				"doctype": "ToDo",
				"description": f"Follow-up required for {self.beneficiary} after appointment",
				"reference_type": "Appointment", 
				"reference_name": self.name,
				"assigned_by": frappe.session.user,
				"owner": self.social_worker,
				"date": self.follow_up_date,
				"priority": "Medium",
				"status": "Open"
			}).insert()
	
	def validate(self):
		"""Validate appointment data"""
		# Ensure case exists and is active
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_status in ["Closed", "Transferred"]:
				frappe.throw(f"Cannot create appointment for {case_doc.case_status.lower()} case")
		
		# Validate appointment date and time
		if self.appointment_date and getdate(self.appointment_date) < getdate(today()):
			if self.appointment_status == "Scheduled":
				frappe.throw("Cannot schedule appointment in the past")
		
		# Validate actual times
		if self.actual_start_time and self.actual_end_time:
			if get_time(self.actual_end_time) <= get_time(self.actual_start_time):
				frappe.throw("Actual end time must be after start time")
		
		# Validate status-specific requirements
		if self.appointment_status == "Completed":
			if not self.appointment_outcome:
				frappe.throw("Appointment outcome is required for completed appointments")
			if not self.attendance_status:
				frappe.throw("Attendance status is required for completed appointments")
		
		if self.appointment_status == "No Show":
			self.attendance_status = "No Show"
			if not self.no_show_reason:
				frappe.throw("No show reason is required")
		
		if self.appointment_status == "Cancelled":
			self.attendance_status = "Cancelled"
			if not self.cancellation_reason:
				frappe.throw("Cancellation reason is required")
		
		if self.appointment_status == "Rescheduled":
			self.attendance_status = "Rescheduled"
			if not self.rescheduled_to:
				frappe.msgprint(
					"Please link the rescheduled appointment",
					title="Rescheduled Appointment",
					indicator="orange"
				)
		
		# Validate interpreter requirements
		if self.interpreter_required and not self.interpreter_language:
			frappe.throw("Interpreter language is required when interpreter is needed")
		
		# Check for scheduling conflicts
		self.check_scheduling_conflicts()
	
	def on_submit(self):
		"""Actions to perform when appointment is submitted"""
		# Update status to confirmed if scheduled
		if self.appointment_status == "Scheduled":
			self.appointment_status = "Confirmed"
		
		# Update case with appointment information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Appointment scheduled: {self.appointment_type} on {self.appointment_date}')
		
		# Send appointment confirmation
		self.send_appointment_confirmation()
		
		# Create reminder task
		self.create_reminder_task()
	
	def on_cancel(self):
		"""Actions to perform when appointment is cancelled"""
		self.appointment_status = "Cancelled"
		
		# Send cancellation notification
		self.send_cancellation_notification()
	
	def check_scheduling_conflicts(self):
		"""Check for scheduling conflicts with other appointments"""
		if not self.social_worker or not self.appointment_date or not self.appointment_time:
			return
		
		# Calculate appointment end time
		from frappe.utils import add_to_date
		start_datetime = get_datetime(f"{self.appointment_date} {self.appointment_time}")
		end_datetime = add_to_date(start_datetime, minutes=self.duration_minutes or 60)
		
		# Check for overlapping appointments
		overlapping = frappe.db.sql("""
			SELECT name, appointment_type, appointment_time, duration_minutes
			FROM `tabAppointment`
			WHERE social_worker = %s
			AND appointment_date = %s
			AND appointment_status NOT IN ('Cancelled', 'No Show', 'Completed')
			AND name != %s
			AND (
				(appointment_time <= %s AND ADDTIME(appointment_time, SEC_TO_TIME(IFNULL(duration_minutes, 60) * 60)) > %s)
				OR (appointment_time < %s AND ADDTIME(appointment_time, SEC_TO_TIME(IFNULL(duration_minutes, 60) * 60)) >= %s)
			)
		""", (self.social_worker, self.appointment_date, self.name or "", 
			  self.appointment_time, self.appointment_time, end_datetime.time(), end_datetime.time()))
		
		if overlapping:
			conflict_details = []
			for conflict in overlapping:
				conflict_details.append(f"{conflict[1]} at {conflict[2]}")
			
			frappe.msgprint(
				f"Scheduling conflict detected with: {', '.join(conflict_details)}",
				title="Scheduling Conflict",
				indicator="red"
			)
	
	def create_reminder_task(self):
		"""Create reminder task for appointment"""
		if self.appointment_status not in ["Scheduled", "Confirmed"]:
			return
		
		# Create reminder 1 day before appointment
		reminder_date = add_days(self.appointment_date, -1)
		
		try:
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Appointment reminder: {self.appointment_type} with {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')} on {self.appointment_date} at {self.appointment_time}"
			todo_doc.reference_type = "Appointment"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.scheduled_by
			todo_doc.owner = self.social_worker
			todo_doc.date = reminder_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating appointment reminder: {str(e)}")
	
	def send_appointment_confirmation(self):
		"""Send appointment confirmation notification"""
		recipients = [self.social_worker]
		
		if self.scheduled_by != self.social_worker:
			recipients.append(self.scheduled_by)
		
		# Add case manager if different
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_manager and case_doc.case_manager not in recipients:
				recipients.append(case_doc.case_manager)
		
		subject = f"Appointment Confirmed: {self.appointment_type}"
		
		message = f"""
		<p>Appointment <strong>{self.name}</strong> has been confirmed.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Type:</strong> {self.appointment_type}</p>
		<p><strong>Date:</strong> {self.appointment_date}</p>
		<p><strong>Time:</strong> {self.appointment_time}</p>
		<p><strong>Duration:</strong> {self.duration_minutes} minutes</p>
		<p><strong>Location:</strong> {self.appointment_location or self.location_type}</p>
		"""
		
		if self.special_instructions:
			message += f"<p><strong>Special Instructions:</strong> {self.special_instructions}</p>"
		
		if self.interpreter_required:
			message += f"<p><strong>Interpreter Required:</strong> {self.interpreter_language}</p>"
		
		if self.transportation_needed:
			message += "<p><strong>Transportation assistance needed</strong></p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending appointment confirmation: {str(e)}")
	
	def send_cancellation_notification(self):
		"""Send appointment cancellation notification"""
		recipients = [self.social_worker, self.scheduled_by]
		
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_manager and case_doc.case_manager not in recipients:
				recipients.append(case_doc.case_manager)
		
		subject = f"Appointment Cancelled: {self.appointment_type}"
		
		message = f"""
		<p>Appointment <strong>{self.name}</strong> has been cancelled.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Original Date/Time:</strong> {self.appointment_date} at {self.appointment_time}</p>
		<p><strong>Reason:</strong> {self.cancellation_reason or 'Not specified'}</p>
		"""
		
		if self.rescheduled_to:
			message += f"<p><strong>Rescheduled to:</strong> {self.rescheduled_to}</p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending cancellation notification: {str(e)}")
	
	def mark_completed(self, outcome=None, notes=None):
		"""Mark appointment as completed"""
		self.appointment_status = "Completed"
		self.attendance_status = "Attended"
		
		if outcome:
			self.appointment_outcome = outcome
		
		if notes:
			self.appointment_notes = notes
		
		if not self.actual_start_time:
			self.actual_start_time = self.appointment_time
		
		if not self.actual_end_time:
			# Calculate end time based on duration
			from frappe.utils import add_to_date
			start_datetime = get_datetime(f"{self.appointment_date} {self.actual_start_time}")
			end_datetime = add_to_date(start_datetime, minutes=self.duration_minutes or 60)
			self.actual_end_time = end_datetime.time()
		
		self.save()
		
		# Create case notes if this was a significant appointment
		if self.appointment_type in ["Initial Assessment", "Follow-up Assessment", "Home Visit", "Crisis Intervention"]:
			self.create_case_notes()
	
	def create_case_notes(self):
		"""Create case notes from completed appointment"""
		if not self.case or self.appointment_status != "Completed":
			return
		
		try:
			case_notes = frappe.new_doc("Case Notes")
			case_notes.case = self.case
			case_notes.beneficiary = self.beneficiary
			case_notes.visit_date = self.appointment_date
			case_notes.visit_type = self.appointment_type
			case_notes.social_worker = self.social_worker
			case_notes.visit_location = self.appointment_location or self.location_type
			case_notes.visit_duration = self.get_actual_duration()
			case_notes.visit_outcome = self.appointment_outcome
			
			# Set attendees
			if self.attendees:
				case_notes.attendees_present = self.attendees
			
			# Set observations from appointment notes
			if self.appointment_notes:
				case_notes.observations = self.appointment_notes
			
			# Set action items
			if self.action_items:
				case_notes.actions_taken = self.action_items
			
			# Set referrals
			if self.referrals_made:
				case_notes.referrals_made = self.referrals_made
			
			case_notes.insert()
			
			# Link appointment to case notes
			self.add_comment('Info', f'Case notes created: {case_notes.name}')
			
			return case_notes.name
			
		except Exception as e:
			frappe.log_error(f"Error creating case notes from appointment: {str(e)}")
			return None
	
	def get_actual_duration(self):
		"""Calculate actual appointment duration in minutes"""
		if not self.actual_start_time or not self.actual_end_time:
			return self.duration_minutes
		
		try:
			duration_hours = time_diff_in_hours(self.actual_end_time, self.actual_start_time)
			return int(duration_hours * 60)
		except:
			return self.duration_minutes
	
	def reschedule_appointment(self, new_date, new_time, reason=None):
		"""Reschedule this appointment"""
		# Create new appointment
		new_appointment = frappe.copy_doc(self)
		new_appointment.appointment_date = new_date
		new_appointment.appointment_time = new_time
		new_appointment.appointment_status = "Scheduled"
		new_appointment.rescheduled_to = None
		new_appointment.actual_start_time = None
		new_appointment.actual_end_time = None
		new_appointment.appointment_outcome = None
		new_appointment.attendance_status = None
		
		new_appointment.insert()
		
		# Update current appointment
		self.appointment_status = "Rescheduled"
		self.attendance_status = "Rescheduled"
		self.rescheduled_to = new_appointment.name
		if reason:
			if self.appointment_notes:
				self.appointment_notes += f"\n\nRescheduled: {reason}"
			else:
				self.appointment_notes = f"Rescheduled: {reason}"
		
		self.save()
		
		# Link appointments
		self.add_comment('Info', f'Rescheduled to: {new_appointment.name}')
		new_appointment.add_comment('Info', f'Rescheduled from: {self.name}')
		
		return new_appointment.name
	
	def get_appointment_summary(self):
		"""Get summary information for dashboard display"""
		summary = {
			'status': self.appointment_status,
			'days_until': None,
			'is_overdue': False,
			'duration_actual': None,
			'efficiency': None
		}
		
		# Calculate days until appointment
		if self.appointment_date:
			from frappe.utils import date_diff
			days_diff = date_diff(self.appointment_date, today())
			summary['days_until'] = days_diff
			
			# Check if overdue (past appointment that's not completed)
			if days_diff < 0 and self.appointment_status not in ["Completed", "Cancelled", "No Show"]:
				summary['is_overdue'] = True
		
		# Calculate actual duration and efficiency
		if self.appointment_status == "Completed":
			actual_duration = self.get_actual_duration()
			summary['duration_actual'] = actual_duration
			
			if self.duration_minutes and actual_duration:
				summary['efficiency'] = (self.duration_minutes / actual_duration) * 100
		
		return summary
	
	def get_preparation_checklist(self):
		"""Get preparation checklist for appointment"""
		checklist = []
		
		if self.documents_needed:
			checklist.append({
				'item': 'Prepare required documents',
				'details': self.documents_needed,
				'category': 'Documentation'
			})
		
		if self.interpreter_required:
			checklist.append({
				'item': 'Arrange interpreter',
				'details': f'Language: {self.interpreter_language}',
				'category': 'Accessibility'
			})
		
		if self.transportation_needed:
			checklist.append({
				'item': 'Arrange transportation',
				'details': 'Transportation assistance required',
				'category': 'Logistics'
			})
		
		if self.accessibility_requirements:
			checklist.append({
				'item': 'Ensure accessibility',
				'details': self.accessibility_requirements,
				'category': 'Accessibility'
			})
		
		if self.pre_appointment_tasks:
			checklist.append({
				'item': 'Complete pre-appointment tasks',
				'details': self.pre_appointment_tasks,
				'category': 'Preparation'
			})
		
		if not self.reminder_sent:
			checklist.append({
				'item': 'Send appointment reminder',
				'details': 'Remind client of upcoming appointment',
				'category': 'Communication'
			})
		
		return checklist
