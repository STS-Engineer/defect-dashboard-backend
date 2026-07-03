-- Add optional second Final Control inspector fields to defects table.
BEGIN;

ALTER TABLE defects ADD COLUMN mat_cf_2 TEXT;
ALTER TABLE defects ADD COLUMN prenom_nom_cf_2 TEXT;

COMMIT;

