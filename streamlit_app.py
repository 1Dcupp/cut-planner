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
# DEMAND BUILD (WITH YIELD)
# -----------------------------
def build_demand(cuts, yield_mult):
    d = Counter()
    for c in cuts:
        d[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return d

# -----------------------------
# LAYOUT GENERATION
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 6):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# CAPACITY OF ONE RUN
# -----------------------------
def layout_capacity(layout):
    return len(layout)

# -----------------------------
# SCORE (PREFER BIG + CLEAN LAYOUTS)
# -----------------------------
def score(layout, demand):
    fill = sum(layout)
    waste = MAT_WIDTH - fill

    coverage = sum(1 for w in layout if demand[w] > 0)

    return (coverage * 10) + (len(layout) * 2) - (waste * 0.1)

# -----------------------------
# SOLVER (DIRECT ALLOCATION MODEL)
# -----------------------------
def solve(cuts, yield_mult):

    demand = build_demand(cuts, yield_mult)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    schedule = {}

    # copy demand so we can reduce safely
    remaining = dict(demand)

    while any(v > 0 for v in remaining.values()):

        best_layout = max(layouts, key=lambda l: score(l, remaining))

        cap = layout_capacity(best_layout)

        # how many full runs we need for this layout
        possible_runs = float("inf")

        for w in best_layout:
            if remaining[w] > 0:
                possible_runs = min(possible_runs, math.ceil(remaining[w] / 1))

        runs = int(max(1, min(possible_runs, 9999)))

        # apply runs
        for w in best_layout:
            remaining[w] -= runs
            if remaining[w] < 0:
                remaining[w] = 0

        schedule[best_layout] = schedule.get(best_layout, 0) + runs

    return schedule, remaining

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v12 — DIRECT PRODUCTION SOLVER")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_mult = st.selectbox("Yield (X1 / X2 / X3)", [1, 2, 3])

if st.button("Add Cut"):
    st.session_state.cuts.append({"Width": width, "Qty": qty})
    st.rerun()

if st.button("Clear All"):
    st.session_state.cuts = []
    st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Final Production Plan")

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    schedule, remaining = solve(st.session_state.cuts, yield_mult)

    st.subheader("FINAL SHOP FLOOR PLAN (CLEAN ALLOCATION)")

    total_mats = 0

    for layout, runs in schedule.items():
        total_mats += runs

        st.markdown(f"""
### Layout
**{" + ".join([f'{w}\"' for w in layout])}**

- RUN COUNT: **{runs}**
- Pieces per run: {len(layout)}
- Total produced: {runs * len(layout)}
""")

    st.success(f"TOTAL MATS REQUIRED: {total_mats}")

    st.subheader("REMAINING (should be 0 or near 0)")
    st.dataframe(dict(remaining))
