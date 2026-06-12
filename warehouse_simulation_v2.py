"""
RETAIL WAREHOUSE DIGITAL TWIN - Discrete Event Simulation
=========================================================
Simulates one day of operations in a retail distribution center:

    Order arrives -> waits for a PICKER -> waits for a PACKING station -> ships

Every order's timestamps are logged to a CSV, which feeds the
Azure pipeline (Blob -> ADF -> Azure SQL -> Power BI).

HOW TO RUN:   python3 warehouse_simulation.py
OUTPUT:       warehouse_events.csv  (all scenarios combined)

Author: Vyshnavi | MS Engineering Management, UNT
"""

import simpy      # discrete-event simulation library (handles queues/waiting)
import random     # generates realistic randomness (arrival times, pick times)
import pandas as pd

# ---------------------------------------------------------------
# 1. SCENARIOS - the "what-if" experiments
#    Each scenario is one version of the warehouse.
#    Change these numbers to create your own experiments!
# ---------------------------------------------------------------
SCENARIOS = [
    # name,                pickers, packers, orders_per_hour
    ("Baseline",                4,       2,      40),
    ("Add One Picker",          5,       2,      40),
    ("Holiday Demand +30pct",   4,       2,      52),
    ("Holiday + Extra Staff",   6,       3,      52),
]

SHIFT_HOURS = 10            # warehouse operates a 10-hour shift
AVG_PICK_MINUTES = 5        # average time to pick one order
AVG_PACK_MINUTES = 3        # average time to pack one order
RANDOM_SEED = 42            # makes results repeatable (same every run)

# ---- SUPPLY CHAIN SERVICE LEVELS (SLA) ----
# Each order promises to ship within a time window based on priority.
SLA_MINUTES = {
    "Express":  45,         # express orders must ship within 45 min
    "Standard": 90,         # standard orders within 90 min
}
PRIORITY_MIX = ["Express"] * 3 + ["Standard"] * 7   # 30% express, 70% standard
REGIONS = ["DFW", "Houston", "Austin", "San Antonio", "Oklahoma"]

# ---------------------------------------------------------------
# 2. THE LIFE OF ONE ORDER
#    This function describes what ONE order goes through.
#    'env' is the simulation clock. 'yield' means "wait here".
# ---------------------------------------------------------------
def order_lifecycle(env, order_id, pickers, packers, log, scenario_name):
    arrival_time = env.now                      # clock time when order arrives

    # ---- ORDER ATTRIBUTES (like fields on a real retail order) ----
    priority = random.choice(PRIORITY_MIX)      # Express or Standard
    region = random.choice(REGIONS)             # shipping destination
    sla = SLA_MINUTES[priority]                 # promised ship window

    # ---- STAGE 1: PICKING ----
    with pickers.request() as req:              # get in line for a picker
        yield req                               # wait until a picker is free
        pick_start = env.now
        # actual pick time varies around the average (real life is messy)
        pick_duration = random.expovariate(1.0 / AVG_PICK_MINUTES)
        yield env.timeout(pick_duration)        # picking happens
        pick_end = env.now

    # ---- STAGE 2: PACKING ----
    with packers.request() as req:              # get in line for a pack station
        yield req
        pack_start = env.now
        pack_duration = random.expovariate(1.0 / AVG_PACK_MINUTES)
        yield env.timeout(pack_duration)
        ship_time = env.now                     # order ships when packing ends

    # ---- LOG EVERYTHING (one row per order) ----
    cycle = ship_time - arrival_time
    log.append({
        "scenario":            scenario_name,
        "order_id":            order_id,
        "priority":            priority,
        "region":              region,
        "arrival_min":         round(arrival_time, 2),
        "pick_start_min":      round(pick_start, 2),
        "pick_end_min":        round(pick_end, 2),
        "pack_start_min":      round(pack_start, 2),
        "ship_min":            round(ship_time, 2),
        "wait_for_picker_min": round(pick_start - arrival_time, 2),
        "wait_for_packer_min": round(pack_start - pick_end, 2),
        "total_cycle_min":     round(cycle, 2),
        "sla_min":             sla,
        "on_time":             1 if cycle <= sla else 0,   # 1 = met SLA (OTIF)
        "minutes_late":        round(max(0, cycle - sla), 2),
    })

# ---------------------------------------------------------------
# 3. ORDER GENERATOR - creates new orders all day long
# ---------------------------------------------------------------
def order_generator(env, pickers, packers, log, scenario_name, orders_per_hour):
    order_id = 0
    avg_gap_minutes = 60.0 / orders_per_hour    # avg minutes between orders
    while True:
        # wait a random gap, then a new order arrives
        yield env.timeout(random.expovariate(1.0 / avg_gap_minutes))
        order_id += 1
        env.process(order_lifecycle(env, order_id, pickers, packers,
                                    log, scenario_name))

# ---------------------------------------------------------------
# 4. RUN EVERY SCENARIO AND SAVE RESULTS
# ---------------------------------------------------------------
def run_all():
    all_rows = []
    for name, num_pickers, num_packers, orders_per_hour in SCENARIOS:
        random.seed(RANDOM_SEED)                # fair comparison across scenarios
        env = simpy.Environment()               # fresh warehouse, clock at 0
        pickers = simpy.Resource(env, capacity=num_pickers)
        packers = simpy.Resource(env, capacity=num_packers)
        log = []
        env.process(order_generator(env, pickers, packers, log,
                                    name, orders_per_hour))
        env.run(until=SHIFT_HOURS * 60)         # simulate the full shift

        all_rows.extend(log)

        # quick console summary so you see results instantly
        df = pd.DataFrame(log)
        otif = df["on_time"].mean() * 100
        print(f"\n--- {name} ---")
        print(f"  Orders shipped:        {len(df)}")
        print(f"  OTIF (on-time %):      {otif:.1f}%")
        print(f"  Avg cycle time:        {df['total_cycle_min'].mean():.1f} min")
        print(f"  Avg wait for picker:   {df['wait_for_picker_min'].mean():.1f} min")
        print(f"  Worst order took:      {df['total_cycle_min'].max():.1f} min")

    pd.DataFrame(all_rows).to_csv("warehouse_events.csv", index=False)
    print(f"\nSaved {len(all_rows)} order records to warehouse_events.csv")

if __name__ == "__main__":
    run_all()
