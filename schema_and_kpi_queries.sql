-- Warehouse Digital Twin: table schema
-- Note: on_time is INT (not BIT) intentionally — ADF cannot convert
-- the CSV string "1"/"0" to BIT (see lessons_learned.md, issue I1).

CREATE TABLE warehouse_orders (
    scenario            VARCHAR(50),
    order_id            INT,
    priority            VARCHAR(20),
    region              VARCHAR(30),
    arrival_min         DECIMAL(10,2),
    pick_start_min      DECIMAL(10,2),
    pick_end_min        DECIMAL(10,2),
    pack_start_min      DECIMAL(10,2),
    ship_min            DECIMAL(10,2),
    wait_for_picker_min DECIMAL(10,2),
    wait_for_packer_min DECIMAL(10,2),
    total_cycle_min     DECIMAL(10,2),
    sla_min             INT,
    on_time             INT,
    minutes_late        DECIMAL(10,2)
);
GO

-- ============ KPI / verification queries ============

-- OTIF and volume by scenario (reconciles with simulation console output)
SELECT scenario,
       COUNT(*) AS orders,
       CAST(AVG(CAST(on_time AS FLOAT)) * 100 AS DECIMAL(5,1)) AS otif_pct,
       CAST(AVG(total_cycle_min) AS DECIMAL(10,1)) AS avg_cycle_min
FROM warehouse_orders
GROUP BY scenario;

-- SLA breaches by region and priority
SELECT region, priority,
       COUNT(*) AS orders,
       SUM(CASE WHEN on_time = 0 THEN 1 ELSE 0 END) AS late_orders,
       CAST(AVG(minutes_late) AS DECIMAL(10,1)) AS avg_minutes_late
FROM warehouse_orders
GROUP BY region, priority
ORDER BY late_orders DESC;

-- Bottleneck view: where do orders wait, by scenario?
SELECT scenario,
       CAST(AVG(wait_for_picker_min) AS DECIMAL(10,1)) AS avg_wait_picker,
       CAST(AVG(wait_for_packer_min) AS DECIMAL(10,1)) AS avg_wait_packer
FROM warehouse_orders
GROUP BY scenario;

-- Worst 10 orders (outlier review — SPC-style)
SELECT TOP 10 scenario, order_id, priority, region, total_cycle_min, minutes_late
FROM warehouse_orders
ORDER BY total_cycle_min DESC;
