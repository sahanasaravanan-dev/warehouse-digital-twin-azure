# Warehouse Digital Twin — Supply Chain Control Tower on Azure

A discrete-event simulation of a retail distribution center, run through an Azure data pipeline into a Power BI control tower — managed as a formal 4-day project with full PM documentation.

**Stack:** Python (SimPy, pandas) · Azure Blob Storage · Azure Data Factory · Azure SQL Database · Power BI (DAX) · Azure DevOps-style PM artifacts

## Why this project
Operations teams can't experiment on a live warehouse. A digital twin answers "what if?" safely: *What happens to on-time shipping if demand spikes 30%? If we add a picker?* This project models the operation, generates order-level event data for 4 staffing/demand scenarios, and turns it into supply chain KPIs leadership can act on.

## Architecture
```
Python SimPy simulation ──► warehouse_events.csv (1,646 orders)
        │
        ▼
Azure Blob Storage (raw container)
        │
        ▼
Azure Data Factory  (pl_load_warehouse_events: Copy activity)
        │
        ▼
Azure SQL Database  (warehouse_orders)
        │
        ▼
Power BI Service    (semantic model + DAX ──► 2-page control tower)
```

## The headline insight (Theory of Constraints)
| Scenario | OTIF % | Avg cycle (min) |
|---|---|---|
| Baseline (4 pickers, 2 packers) | 98.1% | 24.7 |
| **Add One Picker (5 pickers, 2 packers)** | **89.5% ⬇** | **36.9 ⬆** |
| Holiday Demand +30% (no staffing change) | 57.7% | 72.5 |
| Holiday + Balanced Staff (6 pickers, 3 packers) | 100% | 14.7 |

Adding a picker **hurt** on-time performance: faster picking flooded the packing stations and the bottleneck moved downstream. Capacity has to be balanced across the whole flow — adding labor at the wrong stage makes service worse.

## Supply chain KPIs modeled
OTIF (on-time-in-full %), SLA breach count and minutes late (45-min Express / 90-min Standard SLAs), order cycle time, stage-level queue waits (picker vs packer), throughput by scenario/region/priority.

## Repository contents
- `simulation/` — SimPy model (heavily commented), 4 configurable scenarios
- `sql/` — table schema + KPI/verification queries
- `project-management/` — project charter, RAID log, lessons learned
- `screenshots/` — pipeline runs (including a real debugged failure), dashboard pages

## Project management
Run as a 4-day sprint with a one-page charter, RAID log, and lessons learned. Notable issue resolved: ADF TypeConversionFailure loading a CSV "1"/"0" flag into a BIT column — root-caused to .NET Boolean parsing, fixed via schema change, verified by reconciling row counts and KPIs between the Python source and SQL target (all four scenario OTIF values matched to 0.1%).

## Running it
```bash
pip install simpy pandas
python3 simulation/warehouse_simulation_v2.py   # regenerates warehouse_events.csv
```
Then: upload the CSV to a Blob container, create the table from `sql/schema_and_kpi_queries.sql`, point an ADF Copy activity at it, and connect Power BI to the SQL database.



