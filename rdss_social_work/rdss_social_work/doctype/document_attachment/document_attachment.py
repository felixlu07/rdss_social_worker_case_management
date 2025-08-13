# Copyright (c) 2025, RDSS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, get_files_path, get_file_size
import os
import hashlib


class DocumentAttachment(Document):
	def before_save(self):
		"""Set default values and auto-populate fields before saving"""
		# Set upload date if not provided
		if not self.upload_date:
			self.upload_date = today()
		
		# Set uploaded by if not provided
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
		
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
		
		# Set default document status
		if not self.document_status:
			self.document_status = "Draft"
		
		# Set default access level based on document type
		if not self.access_level:
			self.access_level = self.determine_default_access_level()
		
		# Extract file information if file is attached
		if self.attached_file:
			self.extract_file_information()
		
		# Set default retention period based on document type
		if not self.retention_period:
			self.retention_period = self.determine_retention_period()
		
		# Update audit trail
		self.update_audit_trail("Document modified")
	
	def validate(self):
		"""Validate document attachment data"""
		# Validate upload date
		if self.upload_date and getdate(self.upload_date) > getdate(today()):
			frappe.throw("Upload date cannot be in the future")
		
		# Validate document date
		if self.document_date and getdate(self.document_date) > getdate(today()):
			frappe.throw("Document date cannot be in the future")
		
		# Validate expiry date
		if self.expiry_date and self.document_date:
			if getdate(self.expiry_date) <= getdate(self.document_date):
				frappe.throw("Expiry date must be after document date")
		
		# Validate review dates
		if self.review_date and getdate(self.review_date) < getdate(today()):
			frappe.msgprint(
				"Review date is in the past",
				title="Review Date Warning",
				indicator="yellow"
			)
		
		# Validate file attachment
		if not self.attached_file:
			frappe.throw("File attachment is required")
		
		# Check file size limits
		self.validate_file_size()
		
		# Validate access control
		self.validate_access_control()
		
		# Check compliance requirements
		self.check_compliance_requirements()
	
	def on_submit(self):
		"""Actions to perform when document is submitted"""
		# Update document status to approved if not set
		if self.document_status == "Draft":
			self.document_status = "Approved"
		
		# Set approval information
		if not self.approved_by:
			self.approved_by = frappe.session.user
			self.approval_date = today()
		
		# Update case with document information
		if self.case:
			case_doc = frappe.get_doc("Case", self.case)
			case_doc.add_comment('Info', f'Document attached: {self.document_title}')
		
		# Create review reminder if required
		if self.review_required and self.next_review_date:
			self.create_review_reminder()
		
		# Update audit trail
		self.update_audit_trail("Document submitted and approved")
		
		# Send notifications
		self.send_document_notification()
	
	def on_cancel(self):
		"""Actions to perform when document is cancelled"""
		self.document_status = "Superseded"
		self.update_audit_trail("Document cancelled")
	
	def determine_default_access_level(self):
		"""Determine default access level based on document type"""
		high_confidentiality_types = [
			"Medical Record", "Financial Document", "Legal Document", 
			"Assessment Report", "Identification Document"
		]
		
		if self.document_type in high_confidentiality_types:
			return "Confidential"
		elif self.document_type in ["Service Plan", "Correspondence"]:
			return "Restricted"
		else:
			return "Internal"
	
	def determine_retention_period(self):
		"""Determine retention period based on document type"""
		retention_mapping = {
			"Medical Record": "7 Years",
			"Assessment Report": "7 Years",
			"Service Plan": "5 Years",
			"Financial Document": "7 Years",
			"Legal Document": "Permanent",
			"Consent Form": "7 Years",
			"Identification Document": "Until Case Closure",
			"Correspondence": "3 Years",
			"Photo": "5 Years",
			"Video": "5 Years",
			"Audio Recording": "5 Years"
		}
		
		return retention_mapping.get(self.document_type, "5 Years")
	
	def extract_file_information(self):
		"""Extract file information from attached file"""
		if not self.attached_file:
			return
		
		try:
			# Get file details from Frappe's file system
			file_doc = frappe.get_doc("File", {"file_url": self.attached_file})
			
			self.file_name = file_doc.file_name
			self.file_url = file_doc.file_url
			self.file_size = self.format_file_size(file_doc.file_size) if file_doc.file_size else None
			
			# Extract file type from extension
			if self.file_name:
				self.file_type = os.path.splitext(self.file_name)[1].lower().replace('.', '')
			
			# Calculate file hash for integrity
			self.calculate_file_hash()
			
		except Exception as e:
			frappe.log_error(f"Error extracting file information: {str(e)}")
	
	def format_file_size(self, size_bytes):
		"""Format file size in human readable format"""
		if not size_bytes:
			return None
		
		for unit in ['B', 'KB', 'MB', 'GB']:
			if size_bytes < 1024.0:
				return f"{size_bytes:.1f} {unit}"
			size_bytes /= 1024.0
		return f"{size_bytes:.1f} TB"
	
	def calculate_file_hash(self):
		"""Calculate SHA-256 hash of the file for integrity checking"""
		if not self.attached_file:
			return
		
		try:
			file_path = get_files_path(self.attached_file.replace('/files/', ''))
			
			if os.path.exists(file_path):
				with open(file_path, 'rb') as f:
					file_hash = hashlib.sha256(f.read()).hexdigest()
					self.file_hash = file_hash
		except Exception as e:
			frappe.log_error(f"Error calculating file hash: {str(e)}")
	
	def validate_file_size(self):
		"""Validate file size against limits"""
		if not self.attached_file:
			return
		
		try:
			file_doc = frappe.get_doc("File", {"file_url": self.attached_file})
			file_size_mb = file_doc.file_size / (1024 * 1024) if file_doc.file_size else 0
			
			# Set size limits based on file type
			size_limits = {
				'pdf': 50,  # 50MB
				'doc': 25,  # 25MB
				'docx': 25,
				'jpg': 10,  # 10MB
				'jpeg': 10,
				'png': 10,
				'mp4': 100,  # 100MB
				'avi': 100,
				'mp3': 50,  # 50MB
				'wav': 50
			}
			
			limit = size_limits.get(self.file_type, 25)  # Default 25MB
			
			if file_size_mb > limit:
				frappe.throw(f"File size ({file_size_mb:.1f}MB) exceeds limit of {limit}MB for {self.file_type} files")
				
		except Exception as e:
			frappe.log_error(f"Error validating file size: {str(e)}")
	
	def validate_access_control(self):
		"""Validate access control settings"""
		# Check if highly confidential documents have proper restrictions
		if self.access_level in ["Confidential", "Highly Confidential"]:
			if not self.sharing_permissions:
				frappe.msgprint(
					"Sharing permissions should be specified for confidential documents",
					title="Access Control Recommendation",
					indicator="orange"
				)
		
		# Check GDPR classification for personal data
		if self.document_category in ["Personal Information", "Medical Information"]:
			if not self.gdpr_classification:
				self.gdpr_classification = "Personal Data"
			
			if self.document_category == "Medical Information":
				self.gdpr_classification = "Sensitive Personal Data"
	
	def check_compliance_requirements(self):
		"""Check compliance requirements based on document type"""
		compliance_requirements = []
		
		# Medical records compliance
		if self.document_type == "Medical Record":
			compliance_requirements.append("HIPAA compliance required")
			compliance_requirements.append("Medical records retention policy applies")
		
		# Financial documents compliance
		if self.document_type == "Financial Document":
			compliance_requirements.append("Financial records retention policy applies")
			compliance_requirements.append("Audit trail required")
		
		# Legal documents compliance
		if self.document_type == "Legal Document":
			compliance_requirements.append("Legal hold procedures may apply")
			compliance_requirements.append("Permanent retention may be required")
		
		# Consent forms compliance
		if self.document_type == "Consent Form":
			compliance_requirements.append("Consent management policy applies")
			compliance_requirements.append("Data subject rights apply")
		
		if compliance_requirements:
			self.compliance_requirements = "; ".join(compliance_requirements)
	
	def update_audit_trail(self, action):
		"""Update audit trail with action"""
		timestamp = frappe.utils.now()
		user = frappe.session.user
		entry = f"{timestamp} - {user}: {action}"
		
		if self.audit_trail:
			self.audit_trail += f"\n{entry}"
		else:
			self.audit_trail = entry
	
	def create_review_reminder(self):
		"""Create reminder for document review"""
		if not self.next_review_date:
			return
		
		try:
			todo_doc = frappe.new_doc("ToDo")
			todo_doc.description = f"Document Review Due: {self.document_title}"
			todo_doc.reference_type = "Document Attachment"
			todo_doc.reference_name = self.name
			todo_doc.assigned_by = self.uploaded_by
			todo_doc.owner = self.uploaded_by
			todo_doc.date = self.next_review_date
			todo_doc.priority = "Medium"
			todo_doc.status = "Open"
			todo_doc.insert()
			
		except Exception as e:
			frappe.log_error(f"Error creating review reminder: {str(e)}")
	
	def send_document_notification(self):
		"""Send notification about document submission"""
		if not self.case:
			return
		
		case_doc = frappe.get_doc("Case", self.case)
		recipients = [self.uploaded_by]
		
		# Add case team to recipients
		if case_doc.case_manager and case_doc.case_manager != self.uploaded_by:
			recipients.append(case_doc.case_manager)
		
		if case_doc.assigned_social_worker and case_doc.assigned_social_worker not in recipients:
			recipients.append(case_doc.assigned_social_worker)
		
		subject = f"Document Uploaded: {self.document_title}"
		
		message = f"""
		<p>Document <strong>{self.name}</strong> has been uploaded and approved.</p>
		<p><strong>Document Title:</strong> {self.document_title}</p>
		<p><strong>Document Type:</strong> {self.document_type}</p>
		<p><strong>Beneficiary:</strong> {frappe.db.get_value('Beneficiary', self.beneficiary, 'beneficiary_name') if self.beneficiary else 'N/A'}</p>
		<p><strong>Access Level:</strong> {self.access_level}</p>
		"""
		
		if self.document_description:
			message += f"<p><strong>Description:</strong> {frappe.utils.strip_html(self.document_description)[:200]}...</p>"
		
		if self.expiry_date:
			message += f"<p><strong>Expiry Date:</strong> {self.expiry_date}</p>"
		
		if self.next_review_date:
			message += f"<p><strong>Next Review:</strong> {self.next_review_date}</p>"
		
		try:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Error sending document notification: {str(e)}")
	
	def track_access(self, user=None):
		"""Track document access"""
		if not user:
			user = frappe.session.user
		
		# Update access tracking
		self.last_accessed = frappe.utils.now()
		self.access_count = (self.access_count or 0) + 1
		
		# Log access in audit trail
		self.update_audit_trail(f"Document accessed by {user}")
		
		# Save without triggering validation
		self.db_set('last_accessed', self.last_accessed)
		self.db_set('access_count', self.access_count)
		self.db_set('audit_trail', self.audit_trail)
	
	def get_document_summary(self):
		"""Get document summary for dashboard display"""
		return {
			"title": self.document_title,
			"type": self.document_type,
			"category": self.document_category,
			"status": self.document_status,
			"access_level": self.access_level,
			"file_size": self.file_size,
			"file_type": self.file_type,
			"upload_date": self.upload_date,
			"uploaded_by": frappe.db.get_value('User', self.uploaded_by, 'full_name') if self.uploaded_by else None,
			"access_count": self.access_count or 0,
			"expires": self.expiry_date,
			"review_due": self.next_review_date
		}
	
	def check_expiry_status(self):
		"""Check if document is expired or expiring soon"""
		if not self.expiry_date:
			return {"status": "no_expiry", "days_until_expiry": None}
		
		from frappe.utils import date_diff
		days_until_expiry = date_diff(self.expiry_date, today())
		
		if days_until_expiry < 0:
			return {"status": "expired", "days_until_expiry": days_until_expiry}
		elif days_until_expiry <= 30:
			return {"status": "expiring_soon", "days_until_expiry": days_until_expiry}
		else:
			return {"status": "valid", "days_until_expiry": days_until_expiry}
	
	def get_retention_status(self):
		"""Get document retention status"""
		if self.legal_hold:
			return {"status": "legal_hold", "action": "Cannot be disposed due to legal hold"}
		
		if not self.retention_period or self.retention_period == "Permanent":
			return {"status": "permanent", "action": "Permanent retention"}
		
		# Calculate retention end date (simplified)
		from frappe.utils import add_years, add_months
		
		retention_years = {
			"1 Year": 1,
			"3 Years": 3,
			"5 Years": 5,
			"7 Years": 7,
			"10 Years": 10
		}
		
		if self.retention_period in retention_years:
			years = retention_years[self.retention_period]
			retention_end = add_years(self.upload_date, years)
			
			from frappe.utils import date_diff
			days_until_disposal = date_diff(retention_end, today())
			
			if days_until_disposal <= 0:
				return {"status": "disposal_due", "action": f"Eligible for disposal via {self.disposal_method or 'secure deletion'}"}
			elif days_until_disposal <= 90:
				return {"status": "disposal_approaching", "action": f"Disposal due in {days_until_disposal} days"}
			else:
				return {"status": "retained", "action": f"Retain for {days_until_disposal} more days"}
		
		return {"status": "unknown", "action": "Retention period not specified"}
	
	def create_version(self, new_file, version_notes=None):
		"""Create a new version of this document"""
		# Create new document version
		new_doc = frappe.copy_doc(self)
		new_doc.attached_file = new_file
		new_doc.document_version = self.get_next_version_number()
		new_doc.upload_date = today()
		new_doc.uploaded_by = frappe.session.user
		new_doc.document_status = "Draft"
		new_doc.approved_by = None
		new_doc.approval_date = None
		
		if version_notes:
			new_doc.document_notes = f"Version {new_doc.document_version}: {version_notes}\n\n{self.document_notes or ''}"
		
		new_doc.insert()
		
		# Update current document status
		self.document_status = "Superseded"
		self.update_audit_trail(f"Superseded by version {new_doc.document_version}")
		self.save()
		
		# Link documents
		self.add_comment('Info', f'Superseded by new version: {new_doc.name}')
		new_doc.add_comment('Info', f'New version of document: {self.name}')
		
		return new_doc.name
	
	def get_next_version_number(self):
		"""Get next version number for this document"""
		if not self.document_version:
			return "1.0"
		
		try:
			current_version = float(self.document_version)
			return str(current_version + 0.1)
		except:
			return "1.0"
