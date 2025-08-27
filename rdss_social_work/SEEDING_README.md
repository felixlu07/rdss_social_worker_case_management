# RDSS Social Work Seeding Files Documentation

This directory contains multiple seeding scripts to populate the RDSS Social Work Case Management System with sample data for demonstration and testing purposes.

## Main Seeding Script

- `seed_data.py` - Original seeding script that creates basic data (users, next of kin, beneficiaries, cases, initial assessments)

## Additional Seeding Scripts

Each script below creates sample data for a specific document type:

1. `seed_appointment.py` - Creates sample appointment records
2. `seed_care_team.py` - Creates sample care team records
3. `seed_financial_assessment.py` - Creates sample financial assessment records
4. `seed_service_plan.py` - Creates sample service plan records
5. `seed_referral.py` - Creates sample referral records
6. `seed_case_notes.py` - Creates sample case notes records
7. `seed_follow_up_assessment.py` - Creates sample follow-up assessment records
8. `seed_medical_history.py` - Creates sample medical history records
9. `seed_document_attachment.py` - Creates sample document attachment records
10. `seed_beneficiary_next_of_kin_link.py` - Creates sample beneficiary next of kin link records
11. `seed_initial_assessment_next_of_kin_link.py` - Creates sample initial assessment next of kin link records

## Usage

To run any of these seeding scripts, use the Frappe bench execute command:

```bash
# Run the main seeding script first
bench execute rdss_social_work.seed_data

# Then run any of the additional seeding scripts
bench execute rdss_social_work.seed_appointment
bench execute rdss_social_work.seed_care_team
bench execute rdss_social_work.seed_financial_assessment
bench execute rdss_social_work.seed_service_plan
bench execute rdss_social_work.seed_referral
bench execute rdss_social_work.seed_case_notes
bench execute rdss_social_work.seed_follow_up_assessment
bench execute rdss_social_work.seed_medical_history
bench execute rdss_social_work.seed_document_attachment
bench execute rdss_social_work.seed_beneficiary_next_of_kin_link
bench execute rdss_social_work.seed_initial_assessment_next_of_kin_link
```

## Order of Execution

For best results, run the scripts in this order:

1. `seed_data.py` (main script)
2. `seed_beneficiary_next_of_kin_link.py`
3. `seed_initial_assessment_next_of_kin_link.py`
4. `seed_appointment.py`
5. `seed_care_team.py`
6. `seed_financial_assessment.py`
7. `seed_service_plan.py`
8. `seed_referral.py`
9. `seed_case_notes.py`
10. `seed_follow_up_assessment.py`
11. `seed_medical_history.py`
12. `seed_document_attachment.py`

## Data Deletion

To delete all seeded data, you can use the existing `delete_demo_data.py` script:

```bash
bench execute rdss_social_work.delete_demo_data
```

Alternatively, you can delete data with the prefix "SEED" (though the seeding scripts don't currently use this prefix).

## Notes

- All seeding scripts are designed to be idempotent - running them multiple times will not create duplicate records
- Each script checks for existing records before creating new ones
- The scripts create sample data for the first 3 cases by default
- You can modify the scripts to create more or fewer records as needed
- All scripts follow the same structure and conventions for consistency
