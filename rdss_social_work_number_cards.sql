-- RDSS Social Work Number Cards SQL Insert Statements
-- Created for Rare Disorder Society of Singapore
-- Purpose: Showcase social work impact and metrics for funders

INSERT INTO `tabNumber Card` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `is_standard`, `module`, `label`, `type`, `function`, `document_type`, 
    `is_public`, `show_percentage_stats`, `stats_time_interval`, `filters_json`, 
    `color`, `report_name`, `method`, `aggregate_function_based_on`, 
    `parent_document_type`, `report_field`, `report_function`, 
    `filters_config`, `dynamic_filters_json`, `_user_tags`, `_comments`, 
    `_assign`, `_liked_by`
) VALUES 

-- ===== BENEFICIARY IMPACT METRICS =====
('Total Active Beneficiaries', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Total Active Beneficiaries', 'Document Type', 'Count', 'Beneficiary', 
    1, 1, 'Monthly', '[[\"Beneficiary\",\"current_status\",\"=\",\"Active\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('New Beneficiaries (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'New Beneficiaries (This Month)', 'Document Type', 'Count', 'Beneficiary', 
    1, 1, 'Monthly', '[[\"Beneficiary\",\"registration_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Rare Disorder Cases by Severity - Critical', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Critical Severity Cases', 'Document Type', 'Count', 'Beneficiary', 
    1, 1, 'Monthly', '[[\"Beneficiary\",\"severity_level\",\"=\",\"Critical\",false],[\"Beneficiary\",\"current_status\",\"=\",\"Active\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Beneficiaries Requiring Full Care Support', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Full Care Support Cases', 'Document Type', 'Count', 'Beneficiary', 
    1, 1, 'Monthly', '[[\"Beneficiary\",\"care_level\",\"=\",\"Full Care\",false],[\"Beneficiary\",\"current_status\",\"=\",\"Active\",false]]', 
    '#ff7f0e', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== CASE MANAGEMENT METRICS =====
('Active Cases', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Active Cases', 'Document Type', 'Count', 'Case', 
    1, 1, 'Daily', '[[\"Case\",\"case_status\",\"=\",\"Active\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Cases Opened (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Cases Opened (This Month)', 'Document Type', 'Count', 'Case', 
    1, 1, 'Monthly', '[[\"Case\",\"case_opened_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Cases Closed Successfully (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Cases Closed Successfully (This Month)', 'Document Type', 'Count', 'Case', 
    1, 1, 'Monthly', '[[\"Case\",\"case_status\",\"=\",\"Closed\",false],[\"Case\",\"actual_closure_date\",\"Timespan\",\"this month\",false],[\"Case\",\"closure_reason\",\"in\",[\"Goals Achieved\",\"Services Completed\"],false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('High Priority Cases', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'High Priority Cases', 'Document Type', 'Count', 'Case', 
    1, 1, 'Daily', '[[\"Case\",\"priority_level\",\"=\",\"High\",false],[\"Case\",\"case_status\",\"=\",\"Active\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Average Case Duration (Days)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Average Case Duration (Days)', 'Document Type', 'Average', 'Case', 
    1, 0, 'Monthly', '[[\"Case\",\"case_status\",\"=\",\"Closed\",false]]', 
    '#17becf', NULL, NULL, 'case_duration_days', NULL, NULL, 'Average', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== APPOINTMENT & SERVICE DELIVERY METRICS =====
('Appointments This Month', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Appointments This Month', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Monthly', '[[\"Appointment\",\"appointment_date\",\"Timespan\",\"this month\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Completed Appointments (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Completed Appointments (This Month)', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Monthly', '[[\"Appointment\",\"appointment_outcome\",\"=\",\"Completed as Planned\",false],[\"Appointment\",\"appointment_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('No-Show Rate (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'No-Show Appointments (This Month)', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Monthly', '[[\"Appointment\",\"appointment_outcome\",\"=\",\"No Show\",false],[\"Appointment\",\"appointment_date\",\"Timespan\",\"this month\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Home Visits (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Home Visits (This Month)', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Monthly', '[[\"Appointment\",\"location_type\",\"=\",\"Home Visit\",false],[\"Appointment\",\"appointment_date\",\"Timespan\",\"this month\",false]]', 
    '#ff7f0e', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== REFERRAL & COLLABORATION METRICS =====
('Referrals Made (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Referrals Made (This Month)', 'Document Type', 'Count', 'Referral', 
    1, 1, 'Monthly', '[[\"Referral\",\"referral_date\",\"Timespan\",\"this month\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Successful Referrals (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Successful Referrals (This Month)', 'Document Type', 'Count', 'Referral', 
    1, 1, 'Monthly', '[[\"Referral\",\"referral_outcome\",\"=\",\"Service Connected\",false],[\"Referral\",\"outcome_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Medical Referrals (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Medical Referrals (This Month)', 'Document Type', 'Count', 'Referral', 
    1, 1, 'Monthly', '[[\"Referral\",\"service_category\",\"=\",\"Medical\",false],[\"Referral\",\"referral_date\",\"Timespan\",\"this month\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Pending Referrals', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Pending Referrals', 'Document Type', 'Count', 'Referral', 
    1, 1, 'Daily', '[[\"Referral\",\"status\",\"=\",\"Pending\",false]]', 
    '#ff7f0e', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== ASSESSMENT & INTERVENTION METRICS =====
('Initial Assessments (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Initial Assessments (This Month)', 'Document Type', 'Count', 'Initial Assessment', 
    1, 1, 'Monthly', '[[\"Initial Assessment\",\"assessment_date\",\"Timespan\",\"this month\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Financial Assessments (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Financial Assessments (This Month)', 'Document Type', 'Count', 'Financial Assessment', 
    1, 1, 'Monthly', '[[\"Financial Assessment\",\"assessment_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('High Financial Risk Beneficiaries', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'High Financial Risk Cases', 'Document Type', 'Count', 'Financial Assessment', 
    1, 1, 'Monthly', '[[\"Financial Assessment\",\"financial_stability_rating\",\"=\",\"High Risk\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Follow-Up Assessments (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Follow-Up Assessments (This Month)', 'Document Type', 'Count', 'Follow Up Assessment', 
    1, 1, 'Monthly', '[[\"Follow Up Assessment\",\"assessment_date\",\"Timespan\",\"this month\",false]]', 
    '#ff7f0e', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== SERVICE PLANNING METRICS =====
('Active Service Plans', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Active Service Plans', 'Document Type', 'Count', 'Service Plan', 
    1, 1, 'Daily', '[[\"Service Plan\",\"plan_status\",\"=\",\"Active\",false]]', 
    '#1f77b4', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Service Plans Created (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Service Plans Created (This Month)', 'Document Type', 'Count', 'Service Plan', 
    1, 1, 'Monthly', '[[\"Service Plan\",\"plan_date\",\"Timespan\",\"this month\",false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Service Plans Due for Review', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Service Plans Due for Review', 'Document Type', 'Count', 'Service Plan', 
    1, 1, 'Daily', '[[\"Service Plan\",\"review_date\",\"<=\",\"today()\",false],[\"Service Plan\",\"plan_status\",\"=\",\"Active\",false]]', 
    '#ff7f0e', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== IMPACT & OUTCOME METRICS =====
('Total Beneficiary Interactions (This Year)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Total Interactions (This Year)', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Yearly', '[[\"Appointment\",\"appointment_date\",\"Timespan\",\"this year\",false],[\"Appointment\",\"appointment_outcome\",\"in\",[\"Completed as Planned\",\"Partially Completed\"],false]]', 
    '#17becf', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Emergency Interventions (This Month)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Emergency Interventions (This Month)', 'Document Type', 'Count', 'Appointment', 
    1, 1, 'Monthly', '[[\"Appointment\",\"appointment_outcome\",\"=\",\"Emergency Intervention\",false],[\"Appointment\",\"appointment_date\",\"Timespan\",\"this month\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Cases with Positive Outcomes (This Quarter)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Positive Outcome Cases (This Quarter)', 'Document Type', 'Count', 'Case', 
    1, 1, 'Quarterly', '[[\"Case\",\"actual_closure_date\",\"Timespan\",\"this quarter\",false],[\"Case\",\"closure_reason\",\"in\",[\"Goals Achieved\",\"Services Completed\",\"Improvement Achieved\"],false]]', 
    '#2ca02c', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

-- ===== WORKLOAD & CAPACITY METRICS =====
('Cases per Social Worker (Average)', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Average Caseload per Worker', 'Custom', 'Count', NULL, 
    1, 0, 'Monthly', 'null', 
    '#9467bd', NULL, 'rdss_social_work.utils.get_average_caseload', NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL),

('Overdue Case Reviews', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    1, 'RDSS Social Work', 'Overdue Case Reviews', 'Document Type', 'Count', 'Case', 
    1, 1, 'Daily', '[[\"Case\",\"next_review_date\",\"<\",\"today()\",false],[\"Case\",\"case_status\",\"=\",\"Active\",false]]', 
    '#d62728', NULL, NULL, NULL, NULL, NULL, 'Sum', NULL, '[]', NULL, NULL, NULL, NULL);

-- Create the corresponding Number Card Links for RDSS Social Work Dashboard
INSERT INTO `tabNumber Card Link` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `card`, `parent`, `parentfield`, `parenttype`
) VALUES 

-- Link cards to "RDSS Social Work" dashboard
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Total Active Beneficiaries', 'RDSS Social Work', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'New Beneficiaries (This Month)', 'RDSS Social Work', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Active Cases', 'RDSS Social Work', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Cases Opened (This Month)', 'RDSS Social Work', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Completed Appointments (This Month)', 'RDSS Social Work', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'Successful Referrals (This Month)', 'RDSS Social Work', 'cards', 'Dashboard'),

-- Link cards to "Case Management" dashboard
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Active Cases', 'Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'High Priority Cases', 'Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Cases Closed Successfully (This Month)', 'Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Average Case Duration (Days)', 'Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Overdue Case Reviews', 'Case Management', 'cards', 'Dashboard'),

-- Link cards to "Service Delivery" dashboard  
(LOWER(CONCAT('serv', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Appointments This Month', 'Service Delivery', 'cards', 'Dashboard'),
(LOWER(CONCAT('serv', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'Completed Appointments (This Month)', 'Service Delivery', 'cards', 'Dashboard'),
(LOWER(CONCAT('serv', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Home Visits (This Month)', 'Service Delivery', 'cards', 'Dashboard'),
(LOWER(CONCAT('serv', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'No-Show Appointments (This Month)', 'Service Delivery', 'cards', 'Dashboard'),

-- Link cards to "Impact Metrics" dashboard for funders
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Total Beneficiary Interactions (This Year)', 'Impact Metrics', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'Cases with Positive Outcomes (This Quarter)', 'Impact Metrics', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Critical Severity Cases', 'Impact Metrics', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Emergency Interventions (This Month)', 'Impact Metrics', 'cards', 'Dashboard');
