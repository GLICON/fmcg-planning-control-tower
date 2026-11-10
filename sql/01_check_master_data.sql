-- Data-quality check: find materials that have sales orders (VBAP) or goods movements (MSEG)
-- but no material master record (MARA). In a clean SAP system this returns 0 rows.
SELECT DISTINCT m.MATNR, 'Has orders/movements but no material master' AS issue
FROM (SELECT MATNR FROM dbo.VBAP UNION SELECT MATNR FROM dbo.MSEG) AS m
WHERE NOT EXISTS (SELECT 1 FROM dbo.MARA a WHERE a.MATNR = m.MATNR);