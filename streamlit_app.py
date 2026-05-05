import streamlit as st
from collections import Counter
import itertools

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
        d[float(c["Width"])] += int(c["Qty"])
    return d

# -----------------------------
# GENERATE LAYOUTS
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 6):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# SCORE (GLOBAL IMPACT)
# -----------------------------
def score(layout, demand):
    coverage = sum(1 for w in layout if demand[w] > 0)
    fill = sum(layout)
    waste = MAT_WIDTH - fill

    # prefer fewer unique setups + higher coverage
    return (coverage * 20) + (fill / MAT_WIDTH * 10) - (len(set(layout)) * 2) - waste

# -----------------------------
# HOW MANY RUNS DOES LAYOUT NEED
# -----------------------------
def required_runs(layout, demand):
    # how many times we need to run this layout to satisfy its weakest link
    runs = float("inf")

    for w in layout:
        if demand[w] > 0:
            runs = min(runs, demand[w])

    return max(0, int(runs if runs != float("inf") else 0))

# -----------------------------
# APPLY LAYOUT
# -----------------------------
def apply(layout, runs, demand):
    for w in layout:
        demand[w] -= runs
        if demand[w] < 0:
            demand[w] = 0

# -----------------------------
# SOLVER (LOCKED LAYOUT SYSTEM)
# -----------------------------
def solve(cuts):

    demand = build_demand(cuts)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    # STEP 1: rank all layouts ONCE
    ranked = sorted(layouts, key=lambda l: score(l, demand), reverse=True)

    # STEP 2: LOCK TOP 3 ONLY
    locked_layouts = ranked[:3]

    schedule = {}

    # STEP 3: allocate demand ONLY across locked layouts
    for layout in locked_layouts:

        runs = required_runs(layout, demand)

        if runs > 0:
            apply(layout, runs, demand)
            schedule[layout] = runs

    return schedule, demand

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v14 — LOCKED LAYOUT ENGINE")

col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    st.session_state.cuts.append({"Width": width, "Qty": qty})
    st.rerun()

if st.button("Clear All"):
    st.session_state.cuts = []
    st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Production Plan")

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    schedule, remaining = solve(st.session_state.cuts)

    st.subheader("LOCKED PRODUCTION PLAN (FINAL STRUCTURE)")

    total_runs = 0

    for layout, runs in schedule.items():
        total_runs += runs

        st.markdown(f"""
### Layout
**{" + ".join([f'{w}\"' for w in layout])}**

- RUN COUNT: **{runs}**
- Pieces per run: {len(layout)}
""")

    st.success(f"TOTAL MATS REQUIRED: {total_runs}")

    st.subheader("REMAINING DEMAND (should be near 0)")
    st.dataframe(dict(remaining))
