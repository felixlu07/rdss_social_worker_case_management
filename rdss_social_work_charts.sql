INSERT INTO `tabDashboard Chart` (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `is_standard`, `module`, `chart_name`, `chart_type`, `report_name`, `use_report_chart`, `x_field`, `source`, `document_type`, `parent_document_type`, `based_on`, `value_based_on`, `group_by_type`, `group_by_based_on`, `aggregate_function_based_on`, `number_of_groups`, `is_public`, `heatmap_year`, `timespan`, `from_date`, `to_date`, `time_interval`, `timeseries`, `type`, `filters_json`, `dynamic_filters_json`, `custom_options`, `color`, `last_synced_on`) VALUES

-- 1. Total Beneficiaries Over Time (Timeseries)
('RDSS Total Beneficiaries', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Total Beneficiaries Over Time', 'Group By', NULL, 0, NULL, '', 'Beneficiary', NULL, NULL, NULL, 'Count', 'registration_date', NULL, 0, 1, NULL, 'Last Year', NULL, NULL, 'Monthly', 1, 'Line', '[]', '[]', NULL, '#36B37E', NULL),

-- 2. Case Status Distribution
('RDSS Case Status Distribution', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Case Status Distribution', 'Group By', NULL, 0, NULL, '', 'Case', NULL, NULL, NULL, 'Count', 'case_status', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Donut', '[[\"Case\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#FF5630', NULL),

-- 3. Beneficiaries by Rare Disorder Type
('RDSS Beneficiaries by Disorder', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Beneficiaries by Rare Disorder Type', 'Group By', NULL, 0, NULL, '', 'Beneficiary', NULL, NULL, NULL, 'Count', 'primary_diagnosis', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Bar', '[]', '[]', NULL, '#6554C0', NULL),

-- 4. Monthly Appointments Trend
('RDSS Monthly Appointments', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Monthly Appointments Trend', 'Group By', NULL, 0, NULL, '', 'Appointment', NULL, NULL, NULL, 'Count', 'appointment_date', NULL, 0, 1, NULL, 'Last Year', NULL, NULL, 'Monthly', 1, 'Line', '[[\"Appointment\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#00B8D9', NULL),

-- 5. Appointment Outcomes
('RDSS Appointment Outcomes', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Appointment Outcomes', 'Group By', NULL, 0, NULL, '', 'Appointment', NULL, NULL, NULL, 'Count', 'appointment_outcome', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Pie', '[[\"Appointment\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#FFAB00', NULL),

-- 6. Cases by Priority Level
('RDSS Cases by Priority', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Cases by Priority Level', 'Group By', NULL, 0, NULL, '', 'Case', NULL, NULL, NULL, 'Count', 'priority_level', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Bar', '[[\"Case\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#DE350B', NULL),

-- 7. Beneficiaries by Age Category  
('RDSS Age Demographics', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Beneficiaries by Age Category', 'Group By', NULL, 0, NULL, '', 'Initial Assessment', NULL, NULL, NULL, 'Count', 'age_category', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Donut', '[[\"Initial Assessment\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#8777D9', NULL),

-- 8. Referral Status Tracking
('RDSS Referral Status', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Referral Status Tracking', 'Group By', NULL, 0, NULL, '', 'Referral', NULL, NULL, NULL, 'Count', 'status', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Bar', '[[\"Referral\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#57D9A3', NULL),

-- 9. Cases by Social Worker
('RDSS Workload Distribution', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Cases by Social Worker', 'Group By', NULL, 0, NULL, '', 'Case', NULL, NULL, NULL, 'Count', 'primary_social_worker', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Bar', '[[\"Case\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#FFC400', NULL),

-- 10. Geographic Distribution
('RDSS Geographic Coverage', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Beneficiaries by Postal Code', 'Group By', NULL, 0, NULL, '', 'Beneficiary', NULL, NULL, NULL, 'Count', 'postal_code', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Bar', '[]', '[]', NULL, '#0065FF', NULL),

-- 11. Service Plan Status
('RDSS Service Plan Progress', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Service Plan Status', 'Group By', NULL, 0, NULL, '', 'Service Plan', NULL, NULL, NULL, 'Count', 'plan_status', NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, 0, 'Pie', '[[\"Service Plan\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#36B37E', NULL),

-- 12. Case Flow Trends
('RDSS Case Flow Trends', NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, 0, 'RDSS Social Work', 'Monthly Case Flow', 'Group By', NULL, 0, NULL, '', 'Case', NULL, NULL, NULL, 'Count', 'case_opened_date', NULL, 0, 1, NULL, 'Last Year', NULL, NULL, 'Monthly', 1, 'Line', '[[\"Case\",\"docstatus\",\"=\",\"1\",false]]', '[]', NULL, '#FF8B00', NULL);