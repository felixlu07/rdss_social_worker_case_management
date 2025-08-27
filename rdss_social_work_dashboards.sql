-- RDSS Social Work Dashboard Creation Script
-- Creates comprehensive dashboards for different audiences
-- Combines Number Cards and Dashboard Charts for complete visualization

-- =====================================================
-- DASHBOARD CREATION
-- =====================================================

INSERT INTO `tabDashboard` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `dashboard_name`, `is_default`, `is_standard`, `module`, `chart_options`, 
    `_user_tags`, `_comments`, `_assign`, `_liked_by`
) VALUES 

-- 1. Executive Overview Dashboard (For Funders & Leadership)
('RDSS Executive Overview', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 
    'RDSS Executive Overview', 0, 1, 'RDSS Social Work', '{}', NULL, NULL, NULL, NULL),

-- 2. Case Management Dashboard (For Social Workers)  
('RDSS Case Management', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
    'RDSS Case Management', 0, 1, 'RDSS Social Work', '{}', NULL, NULL, NULL, NULL),

-- 3. Service Impact Dashboard (For Impact Reporting)
('RDSS Service Impact', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
    'RDSS Service Impact', 0, 1, 'RDSS Social Work', '{}', NULL, NULL, NULL, NULL),

-- 4. Operations Dashboard (For Day-to-day Operations)
('RDSS Operations', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
    'RDSS Operations', 1, 1, 'RDSS Social Work', '{}', NULL, NULL, NULL, NULL);

-- =====================================================
-- DASHBOARD CHART LINKS (Charts to Dashboards)
-- =====================================================

INSERT INTO `tabDashboard Chart Links` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `chart`, `width`, `parent`, `parentfield`, `parenttype`
) VALUES 

-- === RDSS EXECUTIVE OVERVIEW DASHBOARD ===
-- Key trend charts for high-level view
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 
    'RDSS Total Beneficiaries', 'Full', 'RDSS Executive Overview', 'charts', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 
    'RDSS Case Flow Trends', 'Full', 'RDSS Executive Overview', 'charts', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 
    'RDSS Beneficiaries by Disorder', 'Half', 'RDSS Executive Overview', 'charts', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 
    'RDSS Case Status Distribution', 'Half', 'RDSS Executive Overview', 'charts', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 
    'RDSS Geographic Coverage', 'Half', 'RDSS Executive Overview', 'charts', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 
    'RDSS Age Demographics', 'Half', 'RDSS Executive Overview', 'charts', 'Dashboard'),

-- === RDSS CASE MANAGEMENT DASHBOARD ===
-- Operational charts for social workers
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 
    'RDSS Cases by Priority', 'Half', 'RDSS Case Management', 'charts', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 
    'RDSS Workload Distribution', 'Half', 'RDSS Case Management', 'charts', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 
    'RDSS Service Plan Progress', 'Full', 'RDSS Case Management', 'charts', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 
    'RDSS Referral Status', 'Half', 'RDSS Case Management', 'charts', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 
    'RDSS Case Status Distribution', 'Half', 'RDSS Case Management', 'charts', 'Dashboard'),

-- === RDSS SERVICE IMPACT DASHBOARD ===
-- Service delivery and outcomes
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 
    'RDSS Monthly Appointments', 'Full', 'RDSS Service Impact', 'charts', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 
    'RDSS Appointment Outcomes', 'Half', 'RDSS Service Impact', 'charts', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 
    'RDSS Beneficiaries by Disorder', 'Half', 'RDSS Service Impact', 'charts', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 
    'RDSS Total Beneficiaries', 'Full', 'RDSS Service Impact', 'charts', 'Dashboard'),

-- === RDSS OPERATIONS DASHBOARD ===
-- Daily operational monitoring
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 
    'RDSS Monthly Appointments', 'Full', 'RDSS Operations', 'charts', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 
    'RDSS Appointment Outcomes', 'Half', 'RDSS Operations', 'charts', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 
    'RDSS Referral Status', 'Half', 'RDSS Operations', 'charts', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 
    'RDSS Workload Distribution', 'Full', 'RDSS Operations', 'charts', 'Dashboard');

-- =====================================================
-- ADDITIONAL NUMBER CARD LINKS FOR NEW DASHBOARDS
-- =====================================================

INSERT INTO `tabNumber Card Link` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `card`, `parent`, `parentfield`, `parenttype`
) VALUES 

-- === EXECUTIVE OVERVIEW DASHBOARD NUMBER CARDS ===
-- High-level impact metrics for leadership
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Total Active Beneficiaries', 'RDSS Executive Overview', 'cards', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'New Beneficiaries (This Month)', 'RDSS Executive Overview', 'cards', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Total Beneficiary Interactions (This Year)', 'RDSS Executive Overview', 'cards', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Cases with Positive Outcomes (This Quarter)', 'RDSS Executive Overview', 'cards', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Critical Severity Cases', 'RDSS Executive Overview', 'cards', 'Dashboard'),
(LOWER(CONCAT('exec', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'Active Cases', 'RDSS Executive Overview', 'cards', 'Dashboard'),

-- === CASE MANAGEMENT DASHBOARD NUMBER CARDS ===
-- Operational metrics for social workers
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Active Cases', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'High Priority Cases', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Cases Opened (This Month)', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Cases Closed Successfully (This Month)', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Overdue Case Reviews', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'Average Case Duration (Days)', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'Active Service Plans', 'RDSS Case Management', 'cards', 'Dashboard'),
(LOWER(CONCAT('case', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'Service Plans Due for Review', 'RDSS Case Management', 'cards', 'Dashboard'),

-- === SERVICE IMPACT DASHBOARD NUMBER CARDS ===
-- Service delivery and impact metrics
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Total Beneficiary Interactions (This Year)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'Completed Appointments (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'Home Visits (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Successful Referrals (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Initial Assessments (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'Financial Assessments (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'Emergency Interventions (This Month)', 'RDSS Service Impact', 'cards', 'Dashboard'),
(LOWER(CONCAT('impact', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'Cases with Positive Outcomes (This Quarter)', 'RDSS Service Impact', 'cards', 'Dashboard'),

-- === OPERATIONS DASHBOARD NUMBER CARDS ===
-- Day-to-day operational monitoring
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'Appointments This Month', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'Completed Appointments (This Month)', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'No-Show Appointments (This Month)', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 4, 'Referrals Made (This Month)', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 5, 'Pending Referrals', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 6, 'High Priority Cases', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'Service Plans Due for Review', 'RDSS Operations', 'cards', 'Dashboard'),
(LOWER(CONCAT('ops', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'Cases per Social Worker (Average)', 'RDSS Operations', 'cards', 'Dashboard');

-- =====================================================
-- UPDATE EXISTING RDSS DASHBOARD
-- =====================================================

-- Add additional cards to the existing RDSS dashboard to make it a comprehensive overview
INSERT INTO `tabNumber Card Link` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `card`, `parent`, `parentfield`, `parenttype`
) VALUES 

-- Enhance existing RDSS dashboard
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 7, 'Full Care Support Cases', 'RDSS', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 8, 'Medical Referrals (This Month)', 'RDSS', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 9, 'High Financial Risk Cases', 'RDSS', 'cards', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 10, 'Emergency Interventions (This Month)', 'RDSS', 'cards', 'Dashboard');

-- Add charts to existing RDSS dashboard
INSERT INTO `tabDashboard Links` (
    `name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, 
    `chart`, `width`, `parent`, `parentfield`, `parenttype`
) VALUES 

(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 1, 'RDSS Total Beneficiaries', 'Full', 'RDSS', 'charts', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 2, 'RDSS Case Status Distribution', 'Half', 'RDSS', 'charts', 'Dashboard'),
(LOWER(CONCAT('rdss', RAND()*1000000)), NOW(), NOW(), 'Administrator', 'Administrator', 0, 3, 'RDSS Appointment Outcomes', 'Half', 'RDSS', 'charts', 'Dashboard');

-- =====================================================
-- DASHBOARD COMPLETION MESSAGE
-- =====================================================
-- Run this script to create a comprehensive dashboard system for RDSS Social Work
-- Four strategic dashboards created:
-- 1. RDSS Executive Overview - For funders and leadership
-- 2. RDSS Case Management - For social workers  
-- 3. RDSS Service Impact - For impact reporting
-- 4. RDSS Operations - For daily operations (set as default)
-- 5. Enhanced existing RDSS dashboard
