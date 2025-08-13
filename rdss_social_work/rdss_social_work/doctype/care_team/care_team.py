# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class CareTeam(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set formation date if not provided
		if not self.formation_date:
			self.formation_date = today()
		
		# Set team lead if not provided
		if not self.team_lead:
			self.team_lead = frappe.session.user
		
		# Auto-populate case from beneficiary if not provided
		if self.beneficiary and not self.case:
			# Get the most recent active case for this beneficiary
			active_case = frappe.db.get_value(
				"Case",
				{"beneficiary": self.beneficiary, "case_status": ["not in", ["Closed", "Transferred"]]},
				"name",
				order_by="creation desc"
			)
			if active_case:
				self.case = active_case
		
		# Set default team status
		if not self.team_status:
			self.team_status = "Active"
		
		# Auto-populate team members from case if available
		if self.case and not self.primary_social_worker:
			case_doc = frappe.get_doc("Case", self.case)
			self.primary_social_worker = case_doc.assigned_social_worker
			self.case_manager = case_doc.case_manager
			self.supervisor = case_doc.supervisor
		
		# Generate team name if not provided
		if not self.team_name:
			beneficiary_name = frappe.db.get_value("Beneficiary", self.beneficiary, "beneficiary_name")
			self.team_name = f"Care Team - {beneficiary_name}"
	
	def validate(self):
		"""Validate care team data"""
		# Validate formation date
		if self.formation_date and getdate(self.formation_date) > getdate(today()):
			frappe.throw("Formation date cannot be in the future")
		
		# Ensure team lead is part of the core team
		if self.team_lead:
			core_members = [self.primary_social_worker, self.case_manager, self.supervisor]
			if self.team_lead not in core_members:
				frappe.msgprint(
					"Team lead should typically be one of the core team members",
					title="Team Lead Recommendation",
					indicator="yellow"
				)
		
		# Validate team composition
		if not any([self.primary_social_worker, self.case_manager, self.medical_professionals, self.therapy_professionals]):
			frappe.throw("Care team must have at least one core member or professional")
		
		# Check for duplicate team members
		self.check_duplicate_members()
		
		# Validate confidentiality requirements
		if self.medical_professionals or self.healthcare_providers:
			if not self.confidentiality_agreements:
				frappe.msgprint(
					"Confidentiality agreements are recommended when medical professionals are involved",
					title="Confidentiality Recommended",
					indicator="orange"
				)
	
	def on_submit(self):
		"""Actions to perform when care team is submitted"""
		# Update case with care team information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Care Team formed: {self.team_name}')
		
		# Create initial team meeting
		self.create_initial_team_meeting()
		
		# Send team formation notifications
		self.send_team_formation_notification()
		
		# Create team review reminder
		self.create_team_review_reminder()
	
	def on_cancel(self):
		"""Actions to perform when care team is cancelled"""
		self.team_status = "Disbanded"
		
		# Notify team members
		self.send_team_disbandment_notification()
	
	def check_duplicate_members(self):
		"""Check for duplicate team members across different roles"""
		all_members = []
		
		# Collect all user-type members
		if self.team_lead:
			all_members.append(self.team_lead)
		if self.primary_social_worker:
			all_members.append(self.primary_social_worker)
		if self.case_manager:
			all_members.append(self.case_manager)
		if self.supervisor:
			all_members.append(self.supervisor)
		
		# Check for duplicates
		duplicates = []
		seen = set()
		for member in all_members:
			if member in seen:
				duplicates.append(member)
			seen.add(member)
		
		if duplicates:
			frappe.msgprint(
				f"The following users have multiple roles: {', '.join(duplicates)}",
				title="Multiple Roles",
				indicator="yellow"
			)
	
	def create_initial_team_meeting(self):
		"""Create initial team meeting"""
		if not self.meeting_frequency or self.meeting_frequency == "As Needed":
			return
		
		try:
			# Calculate next meeting date based on frequency
			from frappe.utils import add_days, add_months
			
			if self.meeting_frequency == "Weekly":
				meeting_date = add_days(today(), 7)
			elif self.meeting_frequency == "Bi-weekly":
				meeting_date = add_days(today(), 14)
			elif self.meeting_frequency == "Monthly":
				meeting_date = add_months(today(), 1)
			elif self.meeting_frequency == "Quarterly":
				meeting_date = add_months(today(), 3)
			else:
				meeting_date = add_days(today(), 7)  # Default to weekly
			
			# Create ToDo for team meeting
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Care Team Meeting: {self.team_name}"
			todo_doc.reference_type = "Care Team"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.team_lead
			todo_doc.owner = self.team_lead
			todo_doc.date = meeting_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating initial team meeting: {str(e)}")
	
	def create_team_review_reminder(self):
		"""Create reminder for team review"""
		if not self.review_schedule:
			return
		
		try:
			from frappe.utils import add_months
			
			# Calculate review date based on schedule
			if self.review_schedule == "Monthly":
				review_date = add_months(today(), 1)
			elif self.review_schedule == "Quarterly":
				review_date = add_months(today(), 3)
			elif self.review_schedule == "Bi-annually":
				review_date = add_months(today(), 6)
			elif self.review_schedule == "Annually":
				review_date = add_months(today(), 12)
			else:
				review_date = add_months(today(), 3)  # Default to quarterly
			
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Care Team Review Due: {self.team_name}"
			todo_doc.reference_type = "Care Team"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.team_lead
			todo_doc.owner = self.team_lead
			todo_doc.date = review_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating team review reminder: {str(e)}")
	
	def send_team_formation_notification(self):
		"""Send notification about care team formation"""
		recipients = []
		
		# Add core team members
		if self.team_lead:
			recipients.append(self.team_lead)
		if self.primary_social_worker and self.primary_social_worker not in recipients:
			recipients.append(self.primary_social_worker)
		if self.case_manager and self.case_manager not in recipients:
			recipients.append(self.case_manager)
		if self.supervisor and self.supervisor not in recipients:
			recipients.append(self.supervisor)
		
		if not recipients:
			return
		
		subject = f"Care Team Formed: {self.team_name}"
		
		message = f"""
		<p>Care Team <strong>{self.name}</strong> has been formed.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Team Lead:</strong> {frappe.db.get_value('User', self.team_lead, 'full_name')}</p>
		<p><strong>Formation Date:</strong> {self.formation_date}</p>
		"""
		
		if self.meeting_frequency:
			message += f"<p><strong>Meeting Frequency:</strong> {self.meeting_frequency}</p>"
		
		if self.care_goals:
			message += f"<p><strong>Care Goals:</strong> {frappe.utils.strip_html(self.care_goals)[:200]}...</p>"
		
		message += "<p>Please review your roles and responsibilities and prepare for team coordination.</p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending team formation notification: {str(e)}")
	
	def send_team_disbandment_notification(self):
		"""Send notification about care team disbandment"""
		recipients = []
		
		# Add core team members
		if self.team_lead:
			recipients.append(self.team_lead)
		if self.primary_social_worker and self.primary_social_worker not in recipients:
			recipients.append(self.primary_social_worker)
		if self.case_manager and self.case_manager not in recipients:
			recipients.append(self.case_manager)
		if self.supervisor and self.supervisor not in recipients:
			recipients.append(self.supervisor)
		
		if not recipients:
			return
		
		subject = f"Care Team Disbanded: {self.team_name}"
		
		message = f"""
		<p>Care Team <strong>{self.name}</strong> has been disbanded.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p>Please ensure proper transition of care responsibilities.</p>
		"""
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending team disbandment notification: {str(e)}")
	
	def get_team_composition_summary(self):
		"""Get summary of team composition"""
		composition = {
			"core_members": 0,
			"medical_professionals": 0,
			"therapy_professionals": 0,
			"support_staff": 0,
			"external_providers": 0,
			"family_members": 0,
			"total_members": 0
		}
		
		# Count core members
		core_members = [self.primary_social_worker, self.case_manager, self.supervisor]
		composition["core_members"] = len([m for m in core_members if m])
		
		# Count other categories (simplified counting by lines)
		if self.medical_professionals:
			composition["medical_professionals"] = len([line for line in self.medical_professionals.split('\n') if line.strip()])
		
		if self.therapy_professionals:
			composition["therapy_professionals"] = len([line for line in self.therapy_professionals.split('\n') if line.strip()])
		
		if self.support_staff:
			composition["support_staff"] = len([line for line in self.support_staff.split('\n') if line.strip()])
		
		if self.healthcare_providers:
			composition["external_providers"] += len([line for line in self.healthcare_providers.split('\n') if line.strip()])
		
		if self.community_partners:
			composition["external_providers"] += len([line for line in self.community_partners.split('\n') if line.strip()])
		
		if self.family_members:
			composition["family_members"] = len([line for line in self.family_members.split('\n') if line.strip()])
		
		# Calculate total
		composition["total_members"] = sum([
			composition["core_members"],
			composition["medical_professionals"],
			composition["therapy_professionals"],
			composition["support_staff"],
			composition["external_providers"],
			composition["family_members"]
		])
		
		return composition
	
	def get_communication_effectiveness(self):
		"""Assess communication effectiveness"""
		effectiveness = {
			"rating": "Good",  # Default
			"factors": [],
			"recommendations": []
		}
		
		# Assess based on various factors
		if not self.communication_method:
			effectiveness["factors"].append("No primary communication method defined")
			effectiveness["recommendations"].append("Define primary communication method")
		
		if not self.meeting_frequency or self.meeting_frequency == "As Needed":
			effectiveness["factors"].append("No regular meeting schedule")
			effectiveness["recommendations"].append("Establish regular meeting schedule")
		
		if not self.information_sharing_protocol:
			effectiveness["factors"].append("No information sharing protocol")
			effectiveness["recommendations"].append("Develop information sharing protocol")
		
		if not self.confidentiality_agreements and (self.medical_professionals or self.healthcare_providers):
			effectiveness["factors"].append("Missing confidentiality agreements")
			effectiveness["recommendations"].append("Establish confidentiality agreements")
		
		# Determine overall rating
		if len(effectiveness["factors"]) == 0:
			effectiveness["rating"] = "Excellent"
		elif len(effectiveness["factors"]) <= 2:
			effectiveness["rating"] = "Good"
		elif len(effectiveness["factors"]) <= 4:
			effectiveness["rating"] = "Fair"
		else:
			effectiveness["rating"] = "Poor"
		
		return effectiveness
	
	def update_team_performance(self, effectiveness=None, collaboration=None, goal_achievement=None):
		"""Update team performance metrics"""
		if effectiveness:
			self.team_effectiveness = effectiveness
		
		if collaboration:
			self.collaboration_rating = collaboration
		
		if goal_achievement:
			self.goal_achievement = goal_achievement
		
		# Log the performance update
		self.add_comment('Info', f'Team performance updated: Effectiveness: {effectiveness}, Collaboration: {collaboration}, Goals: {goal_achievement}')
		
		self.save()
	
	def create_team_meeting_record(self, meeting_date, attendees, agenda, outcomes):
		"""Create a record of team meeting"""
		meeting_record = f"""
		Date: {meeting_date}
		Attendees: {attendees}
		Agenda: {agenda}
		Outcomes: {outcomes}
		---
		"""
		
		if self.team_meetings:
			self.team_meetings += meeting_record
		else:
			self.team_meetings = meeting_record
		
		self.save()
		
		# Create follow-up tasks if needed
		self.add_comment('Info', f'Team meeting recorded for {meeting_date}')
	
	def get_team_challenges(self):
		"""Identify potential team challenges"""
		challenges = []
		
		composition = self.get_team_composition_summary()
		
		# Check for team size issues
		if composition["total_members"] < 3:
			challenges.append("Small team size may limit expertise coverage")
		elif composition["total_members"] > 15:
			challenges.append("Large team size may complicate coordination")
		
		# Check for missing key roles
		if not self.primary_social_worker:
			challenges.append("No primary social worker assigned")
		
		if not self.case_manager and composition["total_members"] > 5:
			challenges.append("Large team without dedicated case manager")
		
		# Check communication setup
		if not self.communication_method:
			challenges.append("No established communication method")
		
		if not self.meeting_frequency:
			challenges.append("No regular meeting schedule")
		
		# Check for role clarity
		if not self.team_roles:
			challenges.append("Team roles and responsibilities not defined")
		
		return challenges
	
	def generate_team_report(self):
		"""Generate comprehensive team report"""
		composition = self.get_team_composition_summary()
		communication = self.get_communication_effectiveness()
		challenges = self.get_team_challenges()
		
		report = {
			"team_info": {
				"name": self.team_name,
				"status": self.team_status,
				"formation_date": self.formation_date,
				"team_lead": frappe.db.get_value('User', self.team_lead, 'full_name') if self.team_lead else None
			},
			"composition": composition,
			"communication": communication,
			"performance": {
				"effectiveness": self.team_effectiveness,
				"collaboration": self.collaboration_rating,
				"goal_achievement": self.goal_achievement
			},
			"challenges": challenges,
			"beneficiary": frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')
		}
		
		return report
