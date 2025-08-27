"""
Seed data script for Document Attachment documents in RDSS Social Work Case Management System

This script creates sample document attachment data for demonstration purposes.

Usage:
    bench execute rdss_social_work.seed_document_attachment
"""

import frappe
from frappe.utils import today, add_days
import random

def execute():
    """Main function to seed document attachment data"""
    print("Starting RDSS Social Work document attachment data seeding...")
    
    # Get existing beneficiaries and cases
    beneficiaries = frappe.get_all("Beneficiary", fields=["name"])
    cases = frappe.get_all("Case", fields=["name", "beneficiary"])
    
    if not beneficiaries or not cases:
        print("No beneficiaries or cases found. Please run seed_data.py first.")
        return
    
    # Create sample document attachments
    create_sample_document_attachments(beneficiaries, cases)
    
    print("Document attachment data seeding completed successfully!")

def create_sample_document_attachments(beneficiaries, cases):
    """Create sample document attachments for beneficiaries and cases"""
    document_types = [
        "Medical Record", "Assessment Report", "Service Plan", "Consent Form", 
        "Identification Document", "Insurance Document", "Financial Document", 
        "Legal Document", "Correspondence", "Photo", "Video", "Audio Recording"
    ]
    
    document_categories = [
        "Personal Information", "Medical Information", "Financial Information", 
        "Legal Information", "Service Documentation", "Communication", 
        "Multimedia", "Administrative"
    ]
    
    access_levels = ["Public", "Internal", "Confidential", "Highly Confidential"]
    confidentiality_levels = ["Low", "Medium", "High"]
    document_statuses = ["Draft", "Under Review", "Approved", "Archived"]
    
    # Get social workers
    social_workers = ["social_worker@example.com", "supervisor@example.com"]
    
    # Create 2-3 document attachments per case
    for i, case in enumerate(cases[:3]):  # Create document attachments for first 3 cases
        num_documents = random.randint(2, 3)
        
        for j in range(num_documents):
            document_attachment = frappe.new_doc("Document Attachment")
            
            # Document information
            document_attachment.beneficiary = case["beneficiary"]
            document_attachment.case = case["name"]
            document_attachment.document_title = f"{random.choice(document_types)} for {case['beneficiary']} - {j+1}"
            document_attachment.document_type = document_types[j] if j < len(document_types) else random.choice(document_types)
            document_attachment.document_category = random.choice(document_categories)
            document_attachment.upload_date = add_days(today(), -random.randint(1, 30))
            document_attachment.uploaded_by = random.choice(social_workers)
            
            # File details (simulated)
            document_attachment.attached_file = f"/files/{document_attachment.document_title.replace(' ', '_').lower()}.pdf"
            document_attachment.file_name = f"{document_attachment.document_title.replace(' ', '_').lower()}.pdf"
            document_attachment.file_size = random.randint(100, 5000)  # KB
            document_attachment.file_type = "application/pdf"
            document_attachment.file_url = f"/files/{document_attachment.file_name}"
            document_attachment.storage_location = "Local Server"
            
            # Document metadata
            document_attachment.document_date = document_attachment.upload_date
            document_attachment.document_source = "Internal" if random.choice([True, False]) else "External Provider"
            document_attachment.document_author = random.choice(social_workers)
            document_attachment.document_version = "1.0"
            document_attachment.language = "English"
            document_attachment.page_count = random.randint(1, 20)
            
            # Access control
            document_attachment.access_level = random.choice(access_levels)
            document_attachment.confidentiality_level = random.choice(confidentiality_levels)
            document_attachment.sharing_permissions = "Restricted" if "Confidential" in document_attachment.access_level else "Standard"
            document_attachment.expiry_date = add_days(today(), 365) if random.choice([True, False]) else ""
            document_attachment.retention_period = "5 Years" if random.choice([True, False]) else "Permanent"
            document_attachment.disposal_method = "Physical Destruction" if "Confidential" in document_attachment.access_level else "Secure Deletion"
            
            # Content
            document_attachment.document_description = f"This document contains {document_attachment.document_type.lower()} information for {case['beneficiary']}"
            document_attachment.keywords = f"{case['beneficiary']}, {document_attachment.document_type}, {document_attachment.document_category}"
            document_attachment.summary = f"Summary of {document_attachment.document_type} for case {case['name']}"
            
            # Workflow
            document_attachment.document_status = random.choice(document_statuses)
            document_attachment.review_required = "No" if random.choice([True, False]) else "Yes"
            document_attachment.review_date = add_days(today(), 30) if document_attachment.review_required == "Yes" else ""
            document_attachment.approved_by = random.choice(social_workers) if document_attachment.review_required == "Yes" else ""
            document_attachment.approval_date = add_days(today(), -5) if document_attachment.review_required == "Yes" else ""
            document_attachment.next_review_date = add_days(today(), 180) if document_attachment.review_required == "Yes" else ""
            
            # Compliance
            document_attachment.compliance_requirements = "Standard data protection requirements"
            document_attachment.audit_trail = "Document created and uploaded by authorized user"
            document_attachment.legal_hold = "No" if random.choice([True, False]) else "Yes"
            document_attachment.gdpr_classification = "Personal Data" if random.choice([True, False]) else "Sensitive Personal Data"
            document_attachment.retention_justification = "Required for case management and legal compliance"
            
            # Technical
            document_attachment.file_hash = f"{random.randint(1000000000, 9999999999):x}"
            document_attachment.encryption_status = "Encrypted at Rest" if "Confidential" in document_attachment.access_level else "Not Encrypted"
            document_attachment.backup_status = "Backed Up"
            document_attachment.virus_scan_status = "Clean"
            document_attachment.last_accessed = add_days(today(), -random.randint(1, 10))
            document_attachment.access_count = random.randint(1, 20)
            
            try:
                document_attachment.insert()
                print(f"Created Document Attachment: {document_attachment.name} for Case: {case['name']}")
            except Exception as e:
                print(f"Error creating document attachment for case {case['name']}: {str(e)}")
