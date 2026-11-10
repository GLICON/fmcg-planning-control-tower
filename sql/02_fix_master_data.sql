-- Fix: the source product list repeats code POP001L12P, so the second product
-- (loaded as 'POP001L12P.1') has no master record. Create it, copying its group and plant
-- from POP001L12P. "WHERE NOT EXISTS" makes the script safe to run more than once.
INSERT INTO dbo.MARA (MATNR, MATKL, SPART)
SELECT 'POP001L12P.1', MATKL, SPART FROM dbo.MARA
WHERE MATNR = 'POP001L12P'
  AND NOT EXISTS (SELECT 1 FROM dbo.MARA WHERE MATNR = 'POP001L12P.1');

INSERT INTO dbo.MARC (MATNR, WERKS)
SELECT 'POP001L12P.1', WERKS FROM dbo.MARC
WHERE MATNR = 'POP001L12P'
  AND NOT EXISTS (SELECT 1 FROM dbo.MARC WHERE MATNR = 'POP001L12P.1');
  