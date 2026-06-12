# RAID Log — Warehouse Digital Twin

## Risks
| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | CSV (untyped) to SQL (typed) load failures | High | Medium | Define explicit table schema; validate with debug runs before full load |
| R2 | 4-day timeline with single developer | High | High | Scope locked at charter; reuse proven pipeline patterns from prior Azure projects |
| R3 | Synthetic data may not reflect real DC variability | Medium | Medium | Use exponential inter-arrival/service distributions (standard queuing assumptions); document assumptions |
| R4 | Azure for Students credit limits | Low | Medium | Basic-tier SQL, single-region resources, manual (not scheduled) pipeline runs |

## Assumptions
| ID | Assumption |
|---|---|
| A1 | Order arrivals follow a Poisson process (exponential gaps) |
| A2 | Pick ≈ 5 min and pack ≈ 3 min average service times |
| A3 | Express = 45-min SLA (30% of volume); Standard = 90-min SLA (70%) |
| A4 | Fixed random seed for reproducible scenario comparison |

## Issues
| ID | Issue | Status | Resolution |
|---|---|---|---|
| I1 | ADF copy failed: TypeConversionFailure — string "1" could not convert to SQL BIT for `on_time`; 0 rows copied | Closed | Altered column to INT (`ALTER TABLE ... ALTER COLUMN on_time INT`); re-ran pipeline; 1,646 rows loaded |
| I2 | Duplicate query created during Power BI Get Data (warehouse_orders (2)) | Closed | Removed duplicate in Power Query before load |
| I3 | Measures created in Viewing mode were not saved | Closed | Switched semantic model to Editing mode; re-created 6 DAX measures |
| I4 | Wait-time measures inherited Percentage format, axis showed 1000%+ | Closed | Reset formats to Decimal in semantic model editor |

## Dependencies
| ID | Dependency |
|---|---|
| D1 | Azure subscription (Azure for Students) |
| D2 | Existing logical SQL server (shared with prior currency pipeline project) |
| D3 | Power BI Service workspace with semantic-model editing enabled |
