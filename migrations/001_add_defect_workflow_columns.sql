-- Add workflow columns to defects table
BEGIN;

ALTER TABLE defects ADD COLUMN status TEXT;
ALTER TABLE defects ADD COLUMN securisation TEXT;
ALTER TABLE defects ADD COLUMN poste_occurrence TEXT;
ALTER TABLE defects ADD COLUMN poste_detection TEXT;
ALTER TABLE defects ADD COLUMN root_cause_occurrence TEXT;
ALTER TABLE defects ADD COLUMN root_cause_non_detection TEXT;
ALTER TABLE defects ADD COLUMN plan_action_occurrence TEXT;
ALTER TABLE defects ADD COLUMN plan_action_non_detection TEXT;
ALTER TABLE defects ADD COLUMN treatment_date DATE;
ALTER TABLE defects ADD COLUMN treated_by_supervisor BOOLEAN DEFAULT FALSE;
ALTER TABLE defects ADD COLUMN treatment_prod_validation_date TIMESTAMP;
ALTER TABLE defects ADD COLUMN prod_validator_name TEXT;
ALTER TABLE defects ADD COLUMN prod_validation_comment TEXT;
ALTER TABLE defects ADD COLUMN treatment_quality_validation_date TIMESTAMP;
ALTER TABLE defects ADD COLUMN quality_validator_name TEXT;
ALTER TABLE defects ADD COLUMN quality_validation_comment TEXT;

COMMIT;

-- NOTE: Adjust types (TEXT/VARCHAR/TIMESTAMP) to fit your DB if necessary.