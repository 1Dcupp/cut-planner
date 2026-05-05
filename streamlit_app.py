import streamlit as st
from collections import Counter
import itertools

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134
YIELD = 1  # keep production clean per run

# -----------------------------
# STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "layouts" not in st.session_state:
    st.session_state.layouts = []

# -----------------------------
# BUILD DEMAND
# -----------------------------
def build_demand(cuts):
    demand = Counter()
    for c in cuts:
        demand[float(c["Width"])] += int(c["Qty"])
    return demand

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
# SIMULATE HOW MANY RUNS EACH LAYOUT CONTRIBUTES
# -----------------------------
def simulate_schedule(demand, layouts):

    remaining = demand.copy()
    schedule = Counter()

    def done():
        return all(v <= 0 for v in remaining.values())

    while not done():

        best_layout = None
        best_score = -1

        # choose layout that hits most remaining demand
        for layout in layouts:
            score = 0
            for w in layout:
                if remaining[w] > 0:
                    score += 1

            if score > best_score:
                best_score = score
                best_layout = layout

        if not best_layout:
            break

        # APPLY ONCE (THIS IS KEY)
        for w in best_layout:
            if remaining[w] > 0:
                remaining[w] -= YIELD
                if remaining[w] < 0:
                    remaining[w] = 0

        schedule[best_layout] += 1

    return schedule, remaining

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v8 – SHOP FLOOR MODE (FINAL)")

col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    if width > 0 and qty > 0:
        st.session_state.cuts.append({"Width": width, "Qty": qty})
        st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

run = st.button("Generate Production Schedule")
clear = st.button("Clear All")

if clear:
    st.session_state.cuts = []
    st.rerun()

# -----------------------------
# EXECUTION
# -----------------------------
if run:

    demand = build_demand(st.session_state.cuts)
    widths = list(demand.keys())
    layouts = generate_layouts(widths)

    schedule, remaining = simulate_schedule(demand, layouts)

    # -----------------------------
    # FORMAT OUTPUT (IMPORTANT FIX)
    # -----------------------------
    output = []

    for layout, runs in schedule.items():
        output.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Run Count (Mats)": runs,
            "Pieces per Run": len(layout),
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2)
        })

    st.subheader("SHOP FLOOR SCHEDULE (WHAT YOU ACTUALLY RUN)")
    st.dataframe(output, use_container_width=True)

    st.subheader("REMAINING (SHOULD BE ZERO OR OVERLIMIT)")
    st.dataframe(dict(remaining), use_container_width=True)
