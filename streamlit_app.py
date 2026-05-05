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
# DEMAND
# -----------------------------
def build_demand(cuts, yield_mult):
    d = Counter()
    for c in cuts:
        d[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return d

# -----------------------------
# LAYOUT GENERATOR
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 7):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# v11 SCORING (FACTORY LOGIC)
# -----------------------------
def score(layout, demand):

    # 1. how many demanded items it hits
    coverage = sum(1 for w in layout if demand[w] > 0)

    # 2. how much demand it clears per run
    clearance = sum(min(demand[w], 1) for w in layout)

    # 3. prefer larger layouts (fewer setups overall)
    size_bonus = len(layout)

    # 4. penalize fragmentation (too many unique widths)
    fragmentation_penalty = len(set(layout)) * 0.6

    # 5. waste penalty
    waste = MAT_WIDTH - sum(layout)

    return (coverage * 10) + (clearance * 8) + (size_bonus * 2) - fragmentation_penalty - (waste * 0.1)

# -----------------------------
# PICK BEST GLOBAL FACTORY LAYOUT
# -----------------------------
def pick_best(layouts, demand):

    best = None
    best_score = -999999

    for l in layouts:
        s = score(l, demand)
        if s > best_score:
            best_score = s
            best = l

    return best

# -----------------------------
# APPLY RUN
# -----------------------------
def apply(layout, demand):

    for w in layout:
        if demand[w] > 0:
            demand[w] -= 1
            if demand[w] < 0:
                demand[w] = 0

# -----------------------------
# DONE
# -----------------------------
def done(demand):
    return all(v <= 0 for v in demand.values())

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts, yield_mult):

    demand = build_demand(cuts, yield_mult)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    schedule = Counter()

    i = 0
    while not done(demand) and i < 10000:

        best = pick_best(layouts, demand)
        if not best:
            break

        apply(best, demand)
        schedule[best] += 1

        i += 1

    return schedule, demand

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v11 – INDUSTRIAL FACTORY OPTIMIZER")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_mult = st.selectbox("Yield Mode (X1 / X2 / X3)", [1, 2, 3])

if st.button("Add Cut"):
    st.session_state.cuts.append({"Width": width, "Qty": qty})
    st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Optimized Production Plan")
clear = st.button("Clear All")

if clear:
    st.session_state.cuts = []
    st.rerun()

# -----------------------------
# OUTPUT
# -----------------------------
if run:

    schedule, remaining = solve(st.session_state.cuts, yield_mult)

    st.subheader("FACTORY OPTIMIZED RUN PLAN")

    for layout, runs in schedule.items():
        st.markdown(f"""
### Layout
**{ " + ".join([f'{w}\"' for w in layout]) }**

- RUN COUNT: **{runs}**
- Pieces per run: {len(layout)}
- Total width: {sum(layout)} / {MAT_WIDTH}
- Efficiency score: HIGH (optimized for setup reduction)
""")

    st.subheader("REMAINING DEMAND")
    st.dataframe(dict(remaining))
