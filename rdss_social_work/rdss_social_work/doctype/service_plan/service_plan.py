# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, date_diff, add_months


class ServicePlan(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set plan date if not provided
		if not self.plan_date:
			self.plan_date = today()
		
		# Set primary social worker if not provided
		if not self.primary_social_worker:
			self.primary_social_worker = frappe.session.user
		
		# Set plan developed by if not provided
		if not self.plan_developed_by:
			self.plan_developed_by = frappe.session.user
		
		# Auto-populate beneficiary from case
		if self.case and not self.beneficiary:
			case_doc = frappe.get_doc("Case", self.case)
			self.beneficiary = case_doc.beneficiary
			
			# Also populate team members from case
			if not self.supervisor and case_doc.supervisor:
				self.supervisor = case_doc.supervisor
		
		# Set default status for new plans
		if not self.plan_status:
			self.plan_status = "Draft"
		
		# Auto-calculate review date based on review schedule
		if self.review_schedule and self.effective_date and not self.review_date:
			self.review_date = self.calculate_next_review_date()
		
		# Set effective date to plan date if not specified
		if not self.effective_date and self.plan_status == "Active":
			self.effective_date = self.plan_date
	
	def on_submit(self):
		"""Create tasks when service plan is activated"""
		self.create_service_plan_tasks()
	
	def create_service_plan_tasks(self):
		"""Auto-create tasks for service plan reviews and goal tracking"""
		# Create review task
		if self.review_date:
			frappe.get_doc({
				"doctype": "ToDo",
				"description": f"Service Plan Review due for {self.beneficiary}",
				"reference_type": "Service Plan",
				"reference_name": self.name,
				"assigned_by": frappe.session.user,
				"owner": self.primary_social_worker,
				"date": self.review_date,
				"priority": "High",
				"status": "Open"
			}).insert()
		
		# Create goal monitoring tasks for each goal with target date
		if hasattr(self, 'goals') and self.goals:
			for goal in self.goals:
				if goal.target_date:
					frappe.get_doc({
						"doctype": "ToDo",
						"description": f"Monitor goal progress: {goal.goal_description} for {self.beneficiary}",
						"reference_type": "Service Plan",
						"reference_name": self.name,
						"assigned_by": frappe.session.user,
						"owner": self.primary_social_worker,
						"date": goal.target_date,
						"priority": "Medium",
						"status": "Open"
					}).insert()
	
	def validate(self):
		"""Validate service plan data"""
		# Ensure case exists and is active
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			if case_doc.case_status in ["Closed", "Transferred"]:
				frappe.throw(f"Cannot create service plan for {case_doc.case_status.lower()} case")
		
		# Validate dates
		if self.effective_date and self.plan_date:
			if getdate(self.effective_date) < getdate(self.plan_date):
				frappe.throw("Effective date cannot be before plan date")
		
		if self.expiry_date and self.effective_date:
			if getdate(self.expiry_date) <= getdate(self.effective_date):
				frappe.throw("Expiry date must be after effective date")
		
		if self.expected_completion_date and self.implementation_start_date:
			if getdate(self.expected_completion_date) <= getdate(self.implementation_start_date):
				frappe.throw("Expected completion date must be after implementation start date")
		
		# Validate approval requirements
		if self.plan_status == "Active":
			if not self.plan_approved_by:
				frappe.throw("Plan must be approved before it can be activated")
			if not self.approval_date:
				self.approval_date = today()
			if not self.beneficiary_consent:
				frappe.msgprint(
					"Beneficiary consent is recommended before activating the plan",
					title="Consent Recommended",
					indicator="orange"
				)
		
		# Validate budget requirements
		if self.estimated_cost and self.estimated_cost > 0:
			if not self.funding_source:
				frappe.throw("Funding source is required when estimated cost is specified")
			if self.estimated_cost > 10000 and not self.budget_approved:
				frappe.msgprint(
					"Budget approval is recommended for high-cost plans",
					title="Budget Approval Recommended",
					indicator="orange"
				)
	
	def on_submit(self):
		"""Actions to perform when service plan is submitted"""
		# Activate the plan
		self.plan_status = "Active"
		if not self.effective_date:
			self.effective_date = today()
		
		# Update case with service plan information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Service Plan activated: {self.plan_title}')
		
		# Send notifications to team members
		self.send_activation_notification()
	
	def on_cancel(self):
		"""Actions to perform when service plan is cancelled"""
		self.plan_status = "Cancelled"
		
		# Notify team members
		self.send_cancellation_notification()
	
	def calculate_next_review_date(self):
		"""Calculate next review date based on review schedule"""
		if not self.effective_date or not self.review_schedule:
			return None
		
		base_date = getdate(self.effective_date)
		
		if self.review_schedule == "Weekly":
			return frappe.utils.add_days(base_date, 7)
		elif self.review_schedule == "Bi-weekly":
			return frappe.utils.add_days(base_date, 14)
		elif self.review_schedule == "Monthly":
			return add_months(base_date, 1)
		elif self.review_schedule == "Quarterly":
			return add_months(base_date, 3)
		elif self.review_schedule == "Bi-annually":
			return add_months(base_date, 6)
		elif self.review_schedule == "Annually":
			return add_months(base_date, 12)
		
		return None
	
	def send_activation_notification(self):
		"""Send notification when service plan is activated"""
		recipients = [self.primary_social_worker]
		
		if self.case_manager and self.case_manager != self.primary_social_worker:
			recipients.append(self.case_manager)
		
		if self.supervisor:
			recipients.append(self.supervisor)
		
		frappe.sendmail(
			recipients=recipients,
			subject=f"Service Plan Activated: {self.plan_title}",
			message=f"""
			<p>Service Plan <strong>{self.name}</strong> has been activated.</p>
			<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
			<p><strong>Effective Date:</strong> {self.effective_date}</p>
			<p><strong>Review Date:</strong> {self.review_date or 'Not scheduled'}</p>
			<p><strong>Primary Goal:</strong> {frappe.utils.strip_html(self.primary_goal)[:200]}...</p>
			<p>Please begin implementation as planned.</p>
			"""
		)
	
	def send_cancellation_notification(self):
		"""Send notification when service plan is cancelled"""
		recipients = [self.primary_social_worker]
		
		if self.case_manager and self.case_manager != self.primary_social_worker:
			recipients.append(self.case_manager)
		
		if self.supervisor:
			recipients.append(self.supervisor)
		
		frappe.sendmail(
			recipients=recipients,
			subject=f"Service Plan Cancelled: {self.plan_title}",
			message=f"""
			<p>Service Plan <strong>{self.name}</strong> has been cancelled.</p>
			<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
			<p>Please review and create a new service plan if needed.</p>
			"""
		)
	
	def create_revision(self):
		"""Create a revised version of this service plan"""
		if self.plan_status not in ["Active", "Under Review"]:
			frappe.throw("Only active or under review plans can be revised")
		
		# Create new revision
		new_plan = frappe.copy_doc(self)
		new_plan.plan_type = "Revised Service Plan"
		new_plan.plan_status = "Draft"
		new_plan.plan_date = today()
		new_plan.effective_date = None
		new_plan.approval_date = None
		new_plan.plan_approved_by = None
		new_plan.beneficiary_consent = 0
		new_plan.consent_date = None
		
		# Update revision history
		revision_note = f"Revised from {self.name} on {today()}"
		if new_plan.revision_history:
			new_plan.revision_history += f"\n{revision_note}"
		else:
			new_plan.revision_history = revision_note
		
		new_plan.insert()
		
		# Update current plan status
		self.plan_status = "Revised"
		self.save()
		
		# Add comments linking the plans
		self.add_comment('Info', f'Plan revised. New version: {new_plan.name}')
		new_plan.add_comment('Info', f'Revision of plan: {self.name}')
		
		return new_plan.name
	
	def get_progress_summary(self):
		"""Get progress summary for this service plan"""
		if self.plan_status != "Active":
			return {"status": "Not Active", "progress": 0}
		
		if not self.implementation_start_date or not self.expected_completion_date:
			return {"status": "Dates Not Set", "progress": 0}
		
		total_days = date_diff(self.expected_completion_date, self.implementation_start_date)
		elapsed_days = date_diff(today(), self.implementation_start_date)
		
		if elapsed_days < 0:
			progress = 0
		elif elapsed_days > total_days:
			progress = 100
		else:
			progress = (elapsed_days / total_days) * 100
		
		return {
			"status": "In Progress",
			"progress": round(progress, 1),
			"days_elapsed": max(0, elapsed_days),
			"total_days": total_days,
			"days_remaining": max(0, total_days - elapsed_days)
		}
	
	def is_review_overdue(self):
		"""Check if plan review is overdue"""
		if not self.review_date or self.plan_status != "Active":
			return False
		
		return getdate(self.review_date) < getdate(today())
	
	def get_related_case_notes(self):
		"""Get case notes related to this service plan"""
		if not self.case:
			return []
		
		# Get case notes from the implementation period
		filters = {'case': self.case}
		
		if self.effective_date:
			filters['visit_date'] = ['>=', self.effective_date]
		
		if self.expiry_date:
			filters['visit_date'] = ['<=', self.expiry_date]
		
		return frappe.get_all('Case Notes',
			filters=filters,
			fields=['name', 'visit_date', 'visit_type', 'visit_outcome', 'social_worker'],
			order_by='visit_date desc'
		)
	
	def get_service_utilization(self):
		"""Calculate service utilization metrics"""
		case_notes = self.get_related_case_notes()
		
		if not case_notes:
			return {"total_visits": 0, "utilization": "No data"}
		
		# Calculate expected vs actual visits based on frequency
		expected_visits = self.calculate_expected_visits()
		actual_visits = len(case_notes)
		
		utilization_rate = (actual_visits / expected_visits * 100) if expected_visits > 0 else 0
		
		return {
			"total_visits": actual_visits,
			"expected_visits": expected_visits,
			"utilization_rate": round(utilization_rate, 1),
			"last_visit": case_notes[0]['visit_date'] if case_notes else None
		}
	
	def calculate_expected_visits(self):
		"""Calculate expected number of visits based on service frequency"""
		if not self.service_frequency or not self.effective_date:
			return 0
		
		end_date = self.expiry_date or today()
		total_days = date_diff(end_date, self.effective_date)
		
		if self.service_frequency == "Daily":
			return total_days
		elif self.service_frequency == "Weekly":
			return total_days // 7
		elif self.service_frequency == "Bi-weekly":
			return total_days // 14
		elif self.service_frequency == "Monthly":
			return total_days // 30
		elif self.service_frequency == "Quarterly":
			return total_days // 90
		
		return 1  # Default for one-time or as-needed services
