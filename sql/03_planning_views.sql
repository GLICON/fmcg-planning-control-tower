-- View 1: one row per product per day with all four flows side by side.
-- SAP only stores days on which something happened, so the calendar (dim_date)
-- gives every product a row for every day, and missing days become 0.
CREATE OR ALTER VIEW dbo.daily_flows AS
SELECT
    c.calendar_date AS [date],
    a.MATNR         AS product,
    a.SPART         AS product_group,
    a.MATKL         AS sub_group,
    -- demand: sales order quantity (rounded to whole units) and weight (VBAP)
    ROUND(COALESCE((SELECT SUM(KWMENG) FROM dbo.VBAP v WHERE v.MATNR = a.MATNR AND v.ERDAT = c.calendar_date), 0), 0) AS ordered_units,
    COALESCE((SELECT SUM(BRGEW)  FROM dbo.VBAP v WHERE v.MATNR = a.MATNR AND v.ERDAT = c.calendar_date), 0) AS ordered_tonnes,
    -- supply: goods movements by movement type (MSEG.BWART)
    ROUND(COALESCE((SELECT SUM(MENGE) FROM dbo.MSEG s WHERE s.MATNR = a.MATNR AND s.BUDAT_MKPF = c.calendar_date AND s.BWART = '101'), 0), 0) AS produced_units,   -- 101 = receipt from production
    ROUND(COALESCE((SELECT SUM(MENGE) FROM dbo.MSEG s WHERE s.MATNR = a.MATNR AND s.BUDAT_MKPF = c.calendar_date AND s.BWART = '311'), 0), 0) AS issued_units,     -- 311 = transfer out of the factory
    ROUND(COALESCE((SELECT SUM(MENGE) FROM dbo.MSEG s WHERE s.MATNR = a.MATNR AND s.BUDAT_MKPF = c.calendar_date AND s.BWART = '601'), 0), 0) AS delivered_units   -- 601 = delivery to the distributor
FROM dbo.dim_date c
CROSS JOIN dbo.MARA a;
GO

-- View 2: products that were ordered but never made or delivered are inactive (discontinued).
CREATE OR ALTER VIEW dbo.product_status AS
SELECT product, product_group,
       SUM(ordered_units)   AS ordered_units,
       SUM(produced_units)  AS produced_units,
       SUM(delivered_units) AS delivered_units,
       CASE WHEN SUM(produced_units) = 0 AND SUM(delivered_units) <= 1 THEN 'Inactive' ELSE 'Active' END AS status
FROM dbo.daily_flows
GROUP BY product, product_group;
GO