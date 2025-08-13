# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt, add_months


class FinancialAssessment(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set assessment date if not provided
		if not self.assessment_date:
			self.assessment_date = today()
		
		# Set assessed by if not provided
		if not self.assessed_by:
			self.assessed_by = frappe.session.user
		
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
		
		# Calculate debt-to-income ratio
		self.calculate_debt_to_income_ratio()
		
		# Auto-calculate next assessment date
		if self.follow_up_timeline and not self.next_assessment_date:
			self.next_assessment_date = self.calculate_next_assessment_date()
		
		# Auto-determine financial stability rating if not set
		if not self.financial_stability_rating:
			self.financial_stability_rating = self.calculate_financial_stability()
	
	def validate(self):
		"""Validate financial assessment data"""
		# Validate assessment date
		if self.assessment_date and getdate(self.assessment_date) > getdate(today()):
			frappe.throw("Assessment date cannot be in the future")
		
		# Validate income amounts
		if self.monthly_net_income and self.monthly_gross_income:
			if flt(self.monthly_net_income) > flt(self.monthly_gross_income):
				frappe.throw("Net income cannot be greater than gross income")
		
		# Validate household size
		if self.household_size <= 0:
			frappe.throw("Household size must be greater than 0")
		
		if self.dependents_count and self.dependents_count >= self.household_size:
			frappe.throw("Number of dependents cannot be equal to or greater than household size")
		
		# Validate debt information
		if self.monthly_debt_payments and self.total_debt_amount:
			if flt(self.monthly_debt_payments) * 12 > flt(self.total_debt_amount):
				frappe.msgprint(
					"Monthly debt payments seem high relative to total debt amount",
					title="Debt Payment Validation",
					indicator="yellow"
				)
		
		# Validate expense totals
		self.validate_expense_totals()
		
		# Check for financial crisis indicators
		self.check_crisis_indicators()
	
	def on_submit(self):
		"""Actions to perform when financial assessment is submitted"""
		# Update beneficiary with financial information
		if self.beneficiary:
			self.update_beneficiary_financial_info()
		
		# Update case with financial assessment information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Financial Assessment completed: {self.financial_stability_rating}')
		
		# Create financial assistance referrals if needed
		if self.assistance_needs or self.financial_stability_rating in ["Crisis", "Unstable"]:
			self.create_assistance_referrals()
		
		# Schedule follow-up assessment
		if self.next_assessment_date:
			self.schedule_follow_up_assessment()
		
		# Send notifications
		self.send_financial_assessment_notification()
	
	def calculate_debt_to_income_ratio(self):
		"""Calculate debt-to-income ratio"""
		if self.monthly_debt_payments and self.monthly_gross_income:
			ratio = (flt(self.monthly_debt_payments) / flt(self.monthly_gross_income)) * 100
			self.debt_to_income_ratio = ratio
		else:
			self.debt_to_income_ratio = 0
	
	def calculate_next_assessment_date(self):
		"""Calculate next assessment date based on follow-up timeline"""
		if not self.follow_up_timeline or not self.assessment_date:
			return None
		
		base_date = getdate(self.assessment_date)
		
		if self.follow_up_timeline == "1 month":
			return add_months(base_date, 1)
		elif self.follow_up_timeline == "3 months":
			return add_months(base_date, 3)
		elif self.follow_up_timeline == "6 months":
			return add_months(base_date, 6)
		elif self.follow_up_timeline == "1 year":
			return add_months(base_date, 12)
		
		return None
	
	def calculate_financial_stability(self):
		"""Calculate financial stability rating based on various factors"""
		score = 0
		
		# Income stability
		if self.employment_status in ["Full-time Employed", "Self-Employed"]:
			score += 2
		elif self.employment_status in ["Part-time Employed"]:
			score += 1
		elif self.employment_status in ["Unemployed"]:
			score -= 2
		
		# Employment stability
		if self.employment_stability in ["Very Stable", "Stable"]:
			score += 2
		elif self.employment_stability in ["Somewhat Unstable"]:
			score -= 1
		elif self.employment_stability in ["Unstable"]:
			score -= 2
		
		# Debt-to-income ratio
		if self.debt_to_income_ratio:
			if self.debt_to_income_ratio < 20:
				score += 2
			elif self.debt_to_income_ratio < 40:
				score += 1
			elif self.debt_to_income_ratio > 60:
				score -= 2
		
		# Savings and assets
		if self.savings_amount and flt(self.savings_amount) > 0:
			score += 1
		
		# Insurance coverage
		if self.health_insurance:
			score += 1
		
		# Financial management skills
		if self.budgeting_skills in ["Excellent", "Good"]:
			score += 1
		elif self.budgeting_skills in ["Poor", "None"]:
			score -= 1
		
		# Determine rating based on score
		if score >= 6:
			return "Very Stable"
		elif score >= 3:
			return "Stable"
		elif score >= 0:
			return "At Risk"
		elif score >= -3:
			return "Unstable"
		else:
			return "Crisis"
	
	def validate_expense_totals(self):
		"""Validate that expenses don't exceed income significantly"""
		total_expenses = (
			flt(self.monthly_housing_cost) +
			flt(self.monthly_utilities) +
			flt(self.monthly_food_expenses) +
			flt(self.monthly_transportation) +
			flt(self.monthly_medical_expenses) +
			flt(self.monthly_other_expenses) +
			flt(self.monthly_debt_payments)
		)
		
		if total_expenses > 0 and self.monthly_net_income:
			expense_ratio = (total_expenses / flt(self.monthly_net_income)) * 100
			
			if expense_ratio > 100:
				frappe.msgprint(
					f"Total expenses ({expense_ratio:.1f}% of income) exceed net income. This indicates financial stress.",
					title="High Expense Ratio",
					indicator="red"
				)
			elif expense_ratio > 80:
				frappe.msgprint(
					f"Total expenses ({expense_ratio:.1f}% of income) are high relative to income.",
					title="High Expense Ratio",
					indicator="orange"
				)
	
	def check_crisis_indicators(self):
		"""Check for financial crisis indicators"""
		crisis_indicators = []
		
		# No income
		if not self.monthly_gross_income or flt(self.monthly_gross_income) <= 0:
			crisis_indicators.append("No reported income")
		
		# Unemployment
		if self.employment_status == "Unemployed":
			crisis_indicators.append("Unemployed")
		
		# High debt-to-income ratio
		if self.debt_to_income_ratio and self.debt_to_income_ratio > 60:
			crisis_indicators.append(f"High debt-to-income ratio ({self.debt_to_income_ratio:.1f}%)")
		
		# No health insurance
		if not self.health_insurance:
			crisis_indicators.append("No health insurance")
		
		# No banking access
		if self.banking_access in ["No Access", "Unbanked"]:
			crisis_indicators.append("Limited banking access")
		
		# No savings
		if not self.savings_amount or flt(self.savings_amount) <= 0:
			crisis_indicators.append("No savings")
		
		if crisis_indicators:
			self.financial_risk_factors = "; ".join(crisis_indicators)
			
			if len(crisis_indicators) >= 3:
				self.financial_stability_rating = "Crisis"
				self.financial_stress_level = "Severe"
	
	def update_beneficiary_financial_info(self):
		"""Update beneficiary with financial information"""
		try:
			beneficiary_doc = frappe.get_doc("Beneficiary", self.beneficiary)
			
			# Update financial status
			beneficiary_doc.financial_status = self.financial_stability_rating
			
			# Update income information
			if self.monthly_gross_income:
				beneficiary_doc.monthly_income = self.monthly_gross_income
			
			# Update employment status
			if self.employment_status:
				beneficiary_doc.employment_status = self.employment_status
			
			beneficiary_doc.save()
			
		except Exception as e:
			frappe.log_error(f"Error updating beneficiary financial info: {str(e)}")
	
	def create_assistance_referrals(self):
		"""Create referrals for financial assistance programs"""
		if not self.assistance_needs and self.financial_stability_rating not in ["Crisis", "Unstable"]:
			return
		
		try:
			# Create referral for financial assistance
			referral_doc = frappe.new_doc("Referral")
			referral_doc.case = self.case
			referral_doc.beneficiary = self.beneficiary
			referral_doc.referral_date = self.assessment_date
			referral_doc.referred_by = self.assessed_by
			referral_doc.referral_type = "Financial Assistance"
			referral_doc.service_category = "Social Services"
			referral_doc.priority = "High" if self.financial_stability_rating == "Crisis" else "Medium"
			referral_doc.referral_reason = f"Financial Assessment indicates need for assistance. Status: {self.financial_stability_rating}"
			
			if self.assistance_needs:
				referral_doc.referral_reason += f"\n\nSpecific needs: {self.assistance_needs}"
			
			referral_doc.referred_to_organization = "Financial Assistance Program"
			referral_doc.status = "Pending"
			referral_doc.insert()
			
			# Link referral to this assessment
			self.add_comment('Info', f'Financial assistance referral created: {referral_doc.name}')
			
		except Exception as e:
			frappe.log_error(f"Error creating assistance referral: {str(e)}")
	
	def schedule_follow_up_assessment(self):
		"""Schedule follow-up financial assessment"""
		if not self.next_assessment_date:
			return
		
		try:
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Financial Assessment follow-up due for {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
			todo_doc.reference_type = "Financial Assessment"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.assessed_by
			todo_doc.owner = self.assessed_by
			todo_doc.date = self.next_assessment_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error scheduling follow-up assessment: {str(e)}")
	
	def send_financial_assessment_notification(self):
		"""Send notification about completed financial assessment"""
		if not self.case:
			return
		
		case_doc = frappe.get_doc("Case", self.case)
		recipients = [self.assessed_by]
		
		# Add case team to recipients
		if case_doc.case_manager and case_doc.case_manager != self.assessed_by:
			recipients.append(case_doc.case_manager)
		
		if case_doc.assigned_social_worker and case_doc.assigned_social_worker not in recipients:
			recipients.append(case_doc.assigned_social_worker)
		
		if case_doc.supervisor:
			recipients.append(case_doc.supervisor)
		
		# Determine urgency
		urgency = "Normal"
		if self.financial_stability_rating in ["Crisis", "Unstable"]:
			urgency = "High"
		
		subject = f"Financial Assessment Completed: {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}"
		
		message = f"""
		<p>Financial Assessment <strong>{self.name}</strong> has been completed.</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name')}</p>
		<p><strong>Financial Stability:</strong> {self.financial_stability_rating}</p>
		<p><strong>Monthly Income:</strong> ${self.monthly_gross_income or 0:,.2f}</p>
		<p><strong>Debt-to-Income Ratio:</strong> {self.debt_to_income_ratio or 0:.1f}%</p>
		"""
		
		if self.immediate_financial_needs:
			message += f"<p><strong>Immediate Needs:</strong> {self.immediate_financial_needs}</p>"
		
		if self.priority_actions:
			message += f"<p><strong>Priority Actions:</strong> {self.priority_actions}</p>"
		
		if self.next_assessment_date:
			message += f"<p><strong>Next Assessment Due:</strong> {self.next_assessment_date}</p>"
		
		if urgency == "High":
			message += "<p><strong style='color: red;'>This financial assessment indicates crisis or instability requiring immediate attention.</strong></p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending financial assessment notification: {str(e)}")
	
	def get_financial_summary(self):
		"""Get financial summary for dashboard display"""
		total_expenses = (
			flt(self.monthly_housing_cost) +
			flt(self.monthly_utilities) +
			flt(self.monthly_food_expenses) +
			flt(self.monthly_transportation) +
			flt(self.monthly_medical_expenses) +
			flt(self.monthly_other_expenses) +
			flt(self.monthly_debt_payments)
		)
		
		net_income = flt(self.monthly_net_income)
		disposable_income = net_income - total_expenses
		
		return {
			"monthly_income": net_income,
			"monthly_expenses": total_expenses,
			"disposable_income": disposable_income,
			"debt_ratio": self.debt_to_income_ratio or 0,
			"stability_rating": self.financial_stability_rating,
			"poverty_status": self.poverty_level_status,
			"assistance_programs": len(self.current_assistance_programs.split('\n')) if self.current_assistance_programs else 0
		}
	
	def get_budget_breakdown(self):
		"""Get budget breakdown by category"""
		total_income = flt(self.monthly_net_income)
		
		if total_income <= 0:
			return {}
		
		breakdown = {
			"Housing": {
				"amount": flt(self.monthly_housing_cost),
				"percentage": (flt(self.monthly_housing_cost) / total_income) * 100
			},
			"Utilities": {
				"amount": flt(self.monthly_utilities),
				"percentage": (flt(self.monthly_utilities) / total_income) * 100
			},
			"Food": {
				"amount": flt(self.monthly_food_expenses),
				"percentage": (flt(self.monthly_food_expenses) / total_income) * 100
			},
			"Transportation": {
				"amount": flt(self.monthly_transportation),
				"percentage": (flt(self.monthly_transportation) / total_income) * 100
			},
			"Medical": {
				"amount": flt(self.monthly_medical_expenses),
				"percentage": (flt(self.monthly_medical_expenses) / total_income) * 100
			},
			"Debt Payments": {
				"amount": flt(self.monthly_debt_payments),
				"percentage": (flt(self.monthly_debt_payments) / total_income) * 100
			},
			"Other": {
				"amount": flt(self.monthly_other_expenses),
				"percentage": (flt(self.monthly_other_expenses) / total_income) * 100
			}
		}
		
		return breakdown
	
	def get_assistance_eligibility(self):
		"""Determine eligibility for various assistance programs"""
		eligibility = {
			"food_assistance": False,
			"housing_assistance": False,
			"utility_assistance": False,
			"medical_assistance": False,
			"emergency_assistance": False
		}
		
		# Basic eligibility based on income and stability
		if self.poverty_level_status in ["Below Poverty Line", "Deep Poverty"]:
			eligibility["food_assistance"] = True
			eligibility["housing_assistance"] = True
			eligibility["utility_assistance"] = True
			eligibility["medical_assistance"] = True
		
		if self.financial_stability_rating == "Crisis":
			eligibility["emergency_assistance"] = True
		
		# Housing assistance based on housing costs
		if self.monthly_housing_cost and self.monthly_net_income:
			housing_ratio = (flt(self.monthly_housing_cost) / flt(self.monthly_net_income)) * 100
			if housing_ratio > 50:  # Spending more than 50% on housing
				eligibility["housing_assistance"] = True
		
		# Medical assistance if no insurance
		if not self.health_insurance:
			eligibility["medical_assistance"] = True
		
		return eligibility
	
	def calculate_poverty_guidelines(self):
		"""Calculate poverty guidelines based on household size (simplified)"""
		# Simplified poverty guidelines (actual guidelines vary by location and year)
		base_amount = 12000  # Base amount for 1 person
		additional_per_person = 4500
		
		poverty_line = base_amount + (additional_per_person * (self.household_size - 1))
		annual_income = flt(self.monthly_gross_income) * 12
		
		if annual_income <= poverty_line * 0.5:
			return "Deep Poverty"
		elif annual_income <= poverty_line:
			return "Below Poverty Line"
		elif annual_income <= poverty_line * 1.25:
			return "Near Poverty Line"
		else:
			return "Above Poverty Line"
