-- One-time script: mark historical imported defects
BEGIN;

-- Set imported/legacy 'equipe' shift values to 'Non assigné' and mark status HISTORIQUE
UPDATE defects
SET equipe = 'Non assigné'
WHERE equipe IS NULL
   OR equipe IN ('Matin', 'Après-midi', 'Nuit')
   OR TRIM(equipe) = '';

UPDATE defects
SET status = 'HISTORIQUE'
WHERE monday_group IS NOT NULL
  AND status IS NULL;

COMMIT;

-- Review results before applying in production.