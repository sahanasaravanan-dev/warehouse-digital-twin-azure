# Project Charter — Warehouse Digital Twin & Control Tower

**Project name:** Retail Warehouse Digital Twin on Azure
**Project manager / Engineer:** Sahana Saravanan
**Date:** June 2026 | **Duration:** 4-day sprint
**Sponsor (simulated):** Director of Distribution Operations, regional retail company

## Business problem
Distribution center leadership cannot test staffing and demand decisions (e.g., "should we add a picker for the holiday peak?") on the live operation. Decisions are made on intuition, risking SLA breaches and overtime cost.

## Project objective
Build a discrete-event simulation ("digital twin") of DC order fulfillment, run staffing/demand what-if scenarios, and deliver the results through an Azure data pipeline into a Power BI control tower that reports supply chain KPIs (OTIF, cycle time, SLA breaches).

## Scope
**In scope:** order pick/pack flow simulation (Python/SimPy); 4 scenarios; Azure Blob → ADF → Azure SQL pipeline; Power BI semantic model with DAX measures; 2-page report; PM documentation.
**Out of scope:** real WMS/ERP integration; inventory and replenishment modeling; automated scheduled refresh; cost modeling.

## Success criteria
1. Simulation generates ≥1,500 order records across ≥4 scenarios
2. Pipeline loads to Azure SQL with row-count and KPI reconciliation vs. source
3. Dashboard reports OTIF, cycle time, and stage wait times by scenario, region, priority
4. At least one actionable capacity insight identified and documented

## Stakeholders
| Role | Interest |
|---|---|
| DC Operations Director (simulated) | Staffing decisions, SLA performance |
| Supply Chain Analysts | KPI definitions, scenario requests |
| IT / Data Engineering | Pipeline reliability, schema governance |

## Milestones
| Day | Deliverable |
|---|---|
| 1 | Simulation built; scenario dataset generated (1,646 orders) |
| 2 | Azure pipeline (Blob → ADF → SQL) deployed and verified |
| 3 | Power BI semantic model + 2-page control tower report |
| 4 | Documentation, lessons learned, repository published |

## Key risks (see RAID log)
Schema/type mismatches on load; single-developer schedule risk; synthetic-data validity assumptions.
