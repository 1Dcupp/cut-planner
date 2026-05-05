import streamlit as st
from collections import Counter
import itertools
import math

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")
MAT_WIDTH = 134

# -----------------------------
# STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

# -----------------------------
# BUILD DEMAND
# -----------------------------
def build_demand(cuts):
    d = Counter()
    for c in cuts:
        d[float(c["width"])] += int(c["qty"])
    return d

# -----------------------------
# GENERATE LAYOUTS (PHASE 2)
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 6):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# OUTPUT PER RUN
# -----------------------------
def production_per_run(layout):
    return Counter(layout)

# -----------------------------
# SCORE LAYOUTS (global efficiency)
# -----------------------------
def score(layout, demand):
    coverage = sum(1 for w in layout if demand[w] > 0)
    fill = sum(layout)
    waste = MAT_WIDTH - fill

    return (coverage * 20) + fill - waste - len(set(layout))

# -----------------------------
# RUN CALCULATION (PHASE 3 ONLY)
# -----------------------------
def calculate_runs(layouts, demand):

    schedule = {}
    remaining = demand.copy()

    # sort layouts once (NO RE-LOOPING)
    ranked = sorted(layouts, key=lambda l: score(l, remaining), reverse=True)

    # only use top layouts (stability fix)
    locked = ranked[:3]

    for layout in locked:

        prod = production_per_run(layout)

        # compute max runs needed for this layout
        runs_needed = 0

        for w in layout:
            if prod[w] > 0:
                runs_needed = max(runs_needed, math.ceil(remaining[w] / prod[w]))

        runs_needed = max(0, runs_needed)

        if runs_needed > 0:
            for w in layout:
                remaining[w] -= prod[w] * runs_needed
                if remaining[w] < 0:
                    remaining[w] = 0

            schedule[layout] = runs_needed

    return schedule, remaining

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v2 — STREAMLIT PRODUCTION ENGINE")

col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    st.session_state.cuts.append({"width": width, "qty": qty})
    st.rerun()

if st.button("Clear All"):
    st.session_state.cuts = []
    st.rerun()

st.subheader("Cuts Input")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Production Plan")

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    demand = build_demand(st.session_state.cuts)
    widths = list(demand.keys())

    layouts = generate_layouts(widths)

    schedule, remaining = calculate_runs(layouts, demand)

    st.subheader("FINAL PRODUCTION PLAN")

    total_runs = 0

    for layout, runs in schedule.items():
        total_runs += runs

        st.markdown(f"""
### Layout
**{" + ".join([f'{w}\"' for w in layout])}**

- RUNS: **{runs}**
- Pieces per run: {dict(Counter(layout))}
""")

    st.success(f"TOTAL MATS REQUIRED: {total_runs}")

    st.subheader("REMAINING DEMAND")
    st.dataframe(dict(remaining))
