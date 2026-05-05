import streamlit as st
from collections import Counter
import itertools

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134
YIELD = 1

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

    for r in range(1, 7):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# SCORE LAYOUT (v9 = efficiency + reuse bias)
# -----------------------------
def score_layout(layout, demand):

    coverage = 0
    total_fit = sum(layout)
    waste = MAT_WIDTH - total_fit

    # how much demand it hits
    for w in layout:
        if demand[w] > 0:
            coverage += 1

    # BIG CHANGE:
    # reward reuse potential (fewer unique widths = better consolidation)
    uniqueness_penalty = len(set(layout)) * 0.5

    score = (coverage * 10) + (total_fit / MAT_WIDTH * 5) - uniqueness_penalty - (waste * 0.1)

    return score

# -----------------------------
# PICK BEST CONSOLIDATED LAYOUT
# -----------------------------
def pick_best_layout(layouts, demand):

    best = None
    best_score = -999999

    for l in layouts:
        s = score_layout(l, demand)
        if s > best_score:
            best_score = s
            best = l

    return best

# -----------------------------
# APPLY RUN (REDUCE DEMAND)
# -----------------------------
def apply(layout, demand):

    for w in layout:
        if demand[w] > 0:
            demand[w] -= YIELD
            if demand[w] < 0:
                demand[w] = 0

# -----------------------------
# CHECK DONE
# -----------------------------
def done(demand):
    return all(v <= 0 for v in demand.values())

# -----------------------------
# SOLVER (v9)
# -----------------------------
def solve(cuts):

    demand = build_demand(cuts)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    schedule = Counter()

    max_iter = 10000
    i = 0

    while not done(demand) and i < max_iter:

        best = pick_best_layout(layouts, demand)

        if not best:
            break

        apply(best, demand)
        schedule[best] += 1

        i += 1

    return schedule, demand

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v9 – FACTORY CONSOLIDATION ENGINE")

col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    st.session_state.cuts.append({"Width": width, "Qty": qty})
    st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Optimized Production Schedule")
clear = st.button("Clear All")

if clear:
    st.session_state.cuts = []
    st.rerun()

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    schedule, remaining = solve(st.session_state.cuts)

    st.subheader("CONSOLIDATED SHOP FLOOR SCHEDULE")

    for layout, runs in schedule.items():
        st.markdown(f"""
### Layout
**{ " + ".join([f'{w}\"' for w in layout]) }**

- RUN THIS: **{runs} times**
- Pieces per run: {len(layout)}
- Total mat width used: {sum(layout)}
- Waste: {MAT_WIDTH - sum(layout)}
""")

    st.subheader("REMAINING DEMAND")
    st.dataframe(dict(remaining))
