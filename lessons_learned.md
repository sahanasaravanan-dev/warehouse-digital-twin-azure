# Lessons Learned — Warehouse Digital Twin

## What went well
- Reusing proven pipeline patterns (Blob → ADF → SQL) from a previous project cut Day 2 build time significantly.
- Generating data via simulation (instead of a public dataset) made what-if analysis possible — something historical data cannot do.
- Reconciling KPIs between the Python output and SQL after load caught the data quality state immediately (source vs. target validation).

## What was challenging
- **Untyped CSV vs. typed SQL schema.** The load failed on a String→BIT conversion for the `on_time` flag. Root cause: .NET only converts "True"/"False" strings to Boolean, not "1"/"0". Fix: store the flag as INT. Lesson: define load-friendly types up front, or add an explicit staging/typing layer.
- **Power BI edit modes.** Measures created while the semantic model was in Viewing mode were silently lost. Lesson: confirm Editing mode before authoring.
- **Measure formats are global.** A Percentage format applied during one task leaked into wait-time measures (axis displayed 1000%+). Lesson: set format immediately when each measure is created.

## Key analytical insight (Theory of Constraints in practice)
Adding a 5th picker without increasing packing capacity *reduced* OTIF (98.1% → 89.5%): faster picking flooded the 2 packing stations and the bottleneck moved downstream. Balanced capacity (6 pickers + 3 packers) achieved 100% OTIF under +30% holiday demand. Capacity must be added to the constraint, not just the most visible stage.

## What I would do next
- Parameterize the simulation (CLI arguments) so scenarios can be defined without code edits
- Add a date dimension and simulate multiple days for trend analysis
- Schedule the ADF pipeline with a storage event trigger (pattern from my event-driven SFTP project)
- Add a stockout/inventory module to extend KPIs to fill rate and inventory turns
