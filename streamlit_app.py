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
# BUILD DEMAND (APPLY YIELD)
# -----------------------------
def build_demand(cuts, yield_mult):
    d = Counter()
    for c in cuts:
        d[float(c["Width"])] += int(c["Qty"]) * yield_mult
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
# PRODUCTION PER RUN (CRITICAL FIX)
# -----------------------------
def production_per_run(layout, yield_mult):
    prod = Counter()
    for w in layout:
        prod[w] += yield_mult
    return prod

# -----------------------------
# SCORE LAYOUT (efficiency bias)
# -----------------------------
def score(layout, demand):
    fill = sum(layout)
    waste = MAT_WIDTH - fill

    coverage = sum(1 for w in layout if demand[w] > 0)

    return (coverage * 10) + (len(layout) * 2) - (waste * 0.1)

# -----------------------------
# SOLVER (FIXED LOGIC)
# -----------------------------
def solve(cuts, yield_mult):

    demand = build_demand(cuts, yield_mult)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    schedule = Counter()

    while any(v > 0 for v in demand.values()):

        best_layout = max(layouts, key=lambda l: score(l, demand))

        prod = production_per_run(best_layout, yield_mult)

        # determine max runs we can do safely
        runs = float("inf")

        for w in prod:
            if prod[w] > 0:
                runs = min(runs, (demand[w] // prod[w]) if prod[w] > 0 else 0)

        # force at least 1 run
        runs = max(1, int(runs))

        # apply production properly
        for w in prod:
            demand[w] -= prod[w] * runs
            if demand[w] < 0:
                demand[w] = 0

        schedule[best_layout] += runs

    return schedule, demand

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v13 — TRUE PRODUCTION ENGINE")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_mult = st.selectbox("Yield Mode", [1, 2, 3])

if st.button("Add Cut"):
    st.session_state.cuts.append({"Width": width, "Qty": qty})
    st.rerun()

if st.button("Clear All"):
    st.session_state.cuts = []
    st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Final Plan")

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    schedule, remaining = solve(st.session_state.cuts, yield_mult)

    st.subheader("FINAL PRODUCTION PLAN")

    total_mats = 0

    for layout, runs in schedule.items():
        total_mats += runs

        st.markdown(f"""
### Layout
**{" + ".join([f'{w}\"' for w in layout])}**

- RUN COUNT: **{runs}**
- Pieces per run: {len(layout)}
- Total output per run: {Counter({w: yield_mult for w in layout})}
""")

    st.success(f"TOTAL MATS REQUIRED: {total_mats}")

    st.subheader("REMAINING (should be ~0)")
    st.dataframe(dict(remaining))
