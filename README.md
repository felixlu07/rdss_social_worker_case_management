# RDSS Social Work Case Management System

**A comprehensive, mobile-friendly social work case management system for the Rare Disorder Society of Singapore (RDSS)**

[![Frappe](https://img.shields.io/badge/Frappe-Framework-blue)](https://frappeframework.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Phase%204A%20Complete-green)](PROJECT_TRACKER.md)

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [DocType Relationships](#doctype-relationships)
- [Core Workflows](#core-workflows)
- [Social Worker Daily Workflow](#social-worker-daily-workflow)
- [Mobile-First Features](#mobile-first-features)
- [Current Implementation Status](#current-implementation-status)
- [Missing Features & Gaps](#missing-features--gaps)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)

---   

## 🎯 Overview

The RDSS Social Work system is designed to support social workers in managing beneficiaries with rare disorders through a complete case management lifecycle. The system emphasizes:

- **Mobile-First Design**: Field-ready forms and interfaces for on-the-go documentation
- **Comprehensive Assessment**: Detailed initial and follow-up assessments
- **Care Coordination**: Multi-disciplinary team management and service planning
- **Document Management**: Centralized file storage with compliance tracking
- **Workflow Automation**: Automated notifications, reminders, and task management

---

## 🏗️ System Architecture

### **Core Entity Relationships**

```
┌─────────────────┐
│   Next of Kin   │ ◄─── Master Contact Repository
│   (Master)      │      • Contact Information
└─────────────────┘      • Caregiver Details
         ▲                • Consent Management
         │
    ┌────┴────┬─────────────────┬──────────────────┐
    │         │                 │                  │
┌───▼───┐ ┌──▼──┐ ┌────────────▼───┐ ┌──────────▼─────┐
│Initial│ │Bene-│ │    Case        │ │   Documents    │
│Assess-│ │fici-│ │                │ │   & Files      │
│ment   │ │ary  │ │                │ │                │
└───┬───┘ └──┬──┘ └────────┬───────┘ └────────────────┘
    │        │             │
    └────────┼─────────────┼─────────────────┐
             │             │                 │
    ┌────────▼─┐ ┌─────────▼──┐ ┌───────────▼──┐
    │ Service  │ │ Case Notes │ │ Appointments │
    │ Plans    │ │ & Visits   │ │ & Schedule   │
    └──────────┘ └────────────┘ └──────────────┘
```

### **Data Flow Architecture**

1. **Intake Process**: Beneficiary → Next of Kin → Initial Assessment
2. **Case Management**: Case Creation → Service Planning → Regular Visits
3. **Documentation**: Case Notes → Follow-up Assessments → Document Attachments
4. **Care Coordination**: Care Teams → Referrals → Appointments

---

## 🔗 DocType Relationships

### **Phase 1: Foundation (✅ Complete)**

#### **1. Beneficiary**
- **Purpose**: Master record for service recipients
- **Key Fields**: Personal info, medical summary, care level, contact details
- **Relationships**: 
  - Links to `Next of Kin` via `Beneficiary Next of Kin Link` (child table)
  - Referenced by `Case`, `Initial Assessment`, all service records

#### **2. Next of Kin**
- **Purpose**: Single source of truth for contacts and caregivers
- **Key Fields**: Contact info, caregiver capabilities, consent preferences
- **Relationships**: 
  - Linked from `Beneficiary` and `Initial Assessment`
  - Reusable across multiple beneficiaries

#### **3. Initial Assessment**
- **Purpose**: Comprehensive 4-page intake assessment
- **Key Fields**: 60+ fields covering socio-economic, health, functional abilities
- **Relationships**: 
  - Links to `Beneficiary`
  - Links to `Next of Kin` via `Initial Assessment Next of Kin Link` (child table)
  - Creates `Case` upon submission

#### **4. Case**
- **Purpose**: Central hub for ongoing case management
- **Key Fields**: Case details, team assignments, status tracking
- **Relationships**: 
  - Links to `Beneficiary`
  - Parent to all service activities

### **Phase 2: Core Operations (✅ Complete)**

#### **5. Case Notes**
- **Purpose**: Visit records and interaction documentation
- **Key Fields**: Visit details, observations, actions, outcomes
- **Mobile Features**: ✅ Optimized for field documentation

#### **6. Service Plan**
- **Purpose**: Formal service delivery planning
- **Key Fields**: Goals, services, timelines, budget tracking
- **Workflow**: Draft → Review → Approved → Active

#### **7. Follow-up Assessment**
- **Purpose**: Periodic reassessments and progress tracking
- **Key Fields**: Changes since last assessment, goal progress, recommendations

#### **8. Referral**
- **Purpose**: External service referral management
- **Key Fields**: Referral details, recipient info, outcome tracking

#### **9. Appointment**
- **Purpose**: Scheduling and appointment management
- **Key Fields**: Schedule details, participants, outcomes
- **Features**: Conflict detection, automated reminders

### **Phase 3: Advanced Features (✅ Complete)**

#### **10. Medical History**
- **Purpose**: Comprehensive health record management
- **Key Fields**: Diagnoses, medications, procedures, care requirements

#### **11. Financial Assessment**
- **Purpose**: Detailed financial situation tracking
- **Key Fields**: Income, expenses, assets, assistance programs

#### **12. Care Team**
- **Purpose**: Multi-disciplinary team coordination
- **Key Fields**: Team composition, roles, communication tracking

#### **13. Document Attachment**
- **Purpose**: Centralized file management with compliance
- **Key Fields**: File details, access control, retention policies

---

## 🔄 Core Workflows

### **1. New Beneficiary Intake Workflow**

```
1. Create Beneficiary Record
   ├── Personal Information
   ├── Medical Summary
   └── Care Level Assessment

2. Add Next of Kin Contacts
   ├── Create/Link Next of Kin Records
   ├── Define Relationships
   └── Set Primary Caregiver

3. Conduct Initial Assessment
   ├── 4-Page Comprehensive Assessment
   ├── Link Next of Kin Contacts
   └── Submit Assessment

4. Case Creation (Auto-triggered)
   ├── Assign Case Manager
   ├── Set Priority Level
   └── Create Initial Service Plan
```

### **2. Ongoing Case Management Workflow**

```
1. Regular Visits
   ├── Schedule Appointments
   ├── Conduct Field Visits
   └── Document Case Notes

2. Service Planning
   ├── Assess Needs
   ├── Create Service Plans
   └── Track Progress

3. Follow-up Assessments
   ├── Periodic Reassessments
   ├── Compare with Previous
   └── Update Service Plans

4. Care Coordination
   ├── Manage Care Teams
   ├── External Referrals
   └── Document Management
```

---

## 👩‍💼 Social Worker Daily Workflow

### **Current Implementation Status: 🟢 Phase 4A Complete**

#### **✅ What Works Now:**
1. **Case Management**: View assigned cases, beneficiary details
2. **Documentation**: Create case notes, assessments, service plans
3. **Appointments**: Schedule and manage appointments with calendar view
4. **Mobile Forms**: All forms are mobile-responsive
5. **Dashboard**: Social worker dashboard with today's schedule and tasks
6. **Task Management**: Auto-created tasks from appointments and service plans
7. **Reporting**: Caseload, visit activity, and assessment status reports

#### **✅ Phase 4A Features Implemented:**

### **A. Social Worker Dashboard**
```
✅ Dashboard Page (/desk#social-worker-dashboard)
   ├── Today's Schedule (appointments, planned visits)
   ├── Pending Tasks (overdue assessments, follow-ups)
   ├── Case Alerts (urgent issues, approaching deadlines)
   ├── Quick Stats (active cases, completion rates)
   └── Recent Activity (last visits, notes, updates)
```

### **B. Task Management System**
```
✅ Auto-Task Creation
   ├── Appointment preparation tasks (1 day before)
   ├── Appointment reminders (same day)
   ├── Follow-up tasks (based on schedule)
   ├── Service plan review tasks
   └── Goal monitoring tasks

✅ Task Integration
   ├── Frappe ToDo system integration
   ├── Priority-based task sorting
   └── Mobile-accessible task lists
```

### **B. Schedule Management**
```
✅ Calendar Integration
   ├── Appointment calendar view
   ├── Date/time display with beneficiary context
   ├── Color-coded by status
   ├── Filtering by worker, type, status
   └── Mobile-responsive calendar

✅ Basic Visit Planning
   ├── Appointment scheduling with conflict detection
   ├── Duration-based time slots
   └── Beneficiary context in calendar events
```

### **C. Basic Reporting**
```
✅ Operational Reports
   ├── Caseload Report (by social worker)
   ├── Visit Activity Report (with filters)
   ├── Assessment Status Report (pending/overdue)
   └── Mobile-accessible report views
```

#### **🔴 Future Enhancements (Phase 4B+):**

### **Advanced Features (Deferred)**
```
❌ Offline Capability
   ├── Work without internet
   ├── Sync when connected
   └── Draft saving

❌ Advanced Planning
   ├── Route optimization
   ├── Travel time calculation
   └── GPS integration

❌ External Integrations
   ├── Google Calendar sync
   ├── Voice notes
   └── Advanced analytics
   ├── Emergency Contact
   ├── Photo Capture
   └── Voice Notes
```

---

## 📱 Mobile-First Features

### **✅ Currently Implemented:**
- Responsive form layouts
- Touch-friendly interfaces
- Mobile-optimized field types
- Progress indicators

### **🔴 Missing Mobile Features:**
- **Offline Mode**: Work without internet connection
- **GPS Integration**: Location tracking for visits
- **Camera Integration**: Photo documentation
- **Push Notifications**: Appointment reminders
- **Quick Actions**: Emergency contacts, rapid notes

---

## 📊 Current Implementation Status

| Phase | DocTypes | Status | Mobile Ready | Workflow Complete |
|-------|----------|--------|--------------|-------------------|
| **Phase 1** | 4 DocTypes | ✅ Complete | ✅ Yes | ✅ Yes |
| **Phase 2** | 5 DocTypes | ✅ Complete | ✅ Yes | 🟡 Partial |
| **Phase 3** | 4 DocTypes | ✅ Complete | ✅ Yes | 🟡 Partial |
| **Phase 4A** | 4/4 Features | ✅ Complete | ✅ Yes | ✅ Yes |

### **Detailed Status:**

#### **✅ Fully Implemented (13 DocTypes)**
- Beneficiary, Next of Kin, Initial Assessment, Case
- Case Notes, Service Plan, Follow-up Assessment, Referral, Appointment
- Medical History, Financial Assessment, Care Team, Document Attachment

#### **🔴 Missing Critical Features**
- Social Worker Dashboard
- Task/To-Do Management
- Calendar/Schedule Integration
- Mobile offline capability
- Reporting & Analytics
- Outcome Measurement

---

## 🚨 Missing Features & Gaps Analysis

### **Priority 1: Critical for Daily Operations**

#### **1. Social Worker Dashboard**
```
Need: Central command center for social workers
Components:
├── Today's Schedule (appointments, visits)
├── Pending Tasks (overdue assessments, follow-ups)
├── Case Alerts (urgent issues, deadlines)
├── Quick Stats (caseload, completion rates)
└── Recent Activity (last visits, notes)

Implementation: New DocType + Dashboard Page
```

#### **2. Task Management System**
```
Need: Automated task creation and tracking
Components:
├── ToDo Integration (Frappe built-in)
├── Task Auto-creation (from appointments, assessments)
├── Mobile Task List
├── Task Prioritization
└── Completion Tracking

Implementation: Enhance existing controllers + new Task views
```

#### **3. Schedule Management**
```
Need: Comprehensive scheduling system
Components:
├── Calendar View (daily/weekly/monthly)
├── Visit Templates (recurring schedules)
├── Route Optimization
├── Conflict Detection
└── Emergency Scheduling

Implementation: Calendar integration + scheduling algorithms
```

### **Priority 2: Enhanced Mobile Experience**

#### **4. Offline Capability**
```
Need: Work without internet connection
Components:
├── Local Storage (IndexedDB)
├── Sync Mechanism
├── Conflict Resolution
└── Draft Management

Implementation: PWA features + sync service
```

#### **5. Mobile Field Tools**
```
Need: Field-specific mobile features
Components:
├── GPS Location Tracking
├── Camera Integration
├── Voice Notes
├── Emergency Contacts
└── Quick Actions

Implementation: Mobile app features + device APIs
```

### **Priority 3: Analytics & Reporting**

#### **6. Reporting System (Phase 4)**
```
Need: Comprehensive reporting and analytics
Components:
├── Case Review Reports
├── Outcome Measurement
├── Performance Analytics
├── Compliance Reports
└── Dashboard KPIs

Implementation: 5 additional DocTypes + reporting engine
```

---

## 🛠️ Installation & Setup

### **Prerequisites**
- Frappe Framework v15+
- Python 3.8+
- Node.js 16+
- MariaDB/MySQL

### **Installation Steps**

```bash
# 1. Get the app
cd frappe-bench/apps
git clone [repository-url] rdss_social_work

# 2. Install the app
cd ../
bench install-app rdss_social_work

# 3. Add to site
bench --site [site-name] install-app rdss_social_work

# 4. Run migrations (when ready)
bench --site [site-name] migrate
```

### **Initial Setup**
1. Create Social Worker role users
2. Set up initial beneficiaries and next of kin
3. Configure notification settings
4. Set up mobile access

---

## 💡 Usage Examples

### **Example 1: New Beneficiary Intake**

```python
# 1. Create Next of Kin
next_of_kin = frappe.new_doc("Next of Kin")
next_of_kin.contact_name = "Mary Johnson"
next_of_kin.relationship_to_beneficiary = "Mother"
next_of_kin.mobile_number = "91234567"
next_of_kin.is_primary_caregiver = 1
next_of_kin.insert()

# 2. Create Beneficiary
beneficiary = frappe.new_doc("Beneficiary")
beneficiary.beneficiary_name = "John Johnson"
beneficiary.bc_nric_no = "S1234567A"
beneficiary.primary_diagnosis = "Rare Genetic Disorder"
# Add Next of Kin relationship
beneficiary.append("next_of_kin_relationships", {
    "next_of_kin": next_of_kin.name,
    "relationship_type": "Parent",
    "is_primary_caregiver": 1
})
beneficiary.insert()

# 3. Conduct Initial Assessment
assessment = frappe.new_doc("Initial Assessment")
assessment.client_name = beneficiary.beneficiary_name
assessment.bc_nric_no = beneficiary.bc_nric_no
# Link Next of Kin
assessment.append("next_of_kin_contacts", {
    "next_of_kin": next_of_kin.name,
    "is_primary_contact": 1,
    "contact_priority": "1 - First Contact"
})
assessment.insert()
assessment.submit()  # Creates Case automatically
```

### **Example 2: Field Visit Documentation**

```python
# Create Case Note after visit
case_note = frappe.new_doc("Case Notes")
case_note.case = "CASE-2025-00001"
case_note.visit_date = frappe.utils.today()
case_note.visit_type = "Home Visit"
case_note.attendees = "Beneficiary, Primary Caregiver"
case_note.observations = "Client appears stable, medication compliance good"
case_note.actions_taken = "Reviewed service plan, scheduled follow-up"
case_note.insert()
```

---

## 🎯 Recommended Implementation Roadmap

### **Phase 4A: Critical Workflow Completion (2-3 weeks)**
1. **Social Worker Dashboard** - Central command center
2. **Task Management Integration** - Automated task creation
3. **Basic Calendar View** - Schedule visualization

### **Phase 4B: Mobile Enhancement (2-3 weeks)**
1. **Offline Capability** - PWA implementation
2. **Mobile Field Tools** - Camera, GPS, voice notes
3. **Push Notifications** - Appointment reminders

### **Phase 4C: Analytics & Reporting (3-4 weeks)**
1. **Case Review System** - Formal review process
2. **Outcome Measurement** - Progress tracking
3. **Performance Analytics** - KPI dashboards
4. **Compliance Reporting** - Regulatory reports

---

## 📞 Support & Contributing

- **Project Tracker**: [PROJECT_TRACKER.md](PROJECT_TRACKER.md)
- **Development Environment**: Frappe Framework v15+
- **Repository**: `/home/frappe/frappe-bench/apps/rdss_social_work`

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Last Updated**: January 13, 2025  
**Version**: 0.8.0 (Phase 3 Complete)  
**Next Milestone**: Phase 4A - Workflow Completion