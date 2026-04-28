# Cut Planner Web App (Streamlit)
# Version 3 - Full Job Solver (Minimize Total Mats)

import streamlit as st
from itertools import combinations_with_replacement

MAX_WIDTH = 134
MAX_LANES = 8
MAX_OVERRUN = 6

st.set_page_config(page_title="Cut Planner", layout="wide")

st.title("Complete Filter Media - Cut Planner (V3 Solver)")

st.header("Inputs")

num_items = st.number_input("How many cut sizes?", min_value=1, max_value=25, value=5)

cuts = []
qtys = []

for i in range(num_items):
    col1, col2 = st.columns(2)
    with col1:
        w = st.number_input(f"Cut Width {i+1}", min_value=1.0, max_value=134.0, step=0.5, key=f"w{i}")
    with col2:
        q = st.number_input(f"Qty Needed {i+1}", min_value=0, step=1, key=f"q{i}")
    cuts.append(w)
    qtys.append(q)

st.divider()

output_multiplier = st.selectbox("Output per mat (manual)", ["2x", "3x"])
mult = 2 if output_multiplier == "2x" else 3

def evaluate_layout(layout):
    total = sum(layout)
    if total > MAX_WIDTH or len(layout) > MAX_LANES:
        return None
    return {
        "layout": layout,
        "total": total,
        "fill": total / MAX_WIDTH,
        "waste": MAX_WIDTH - total
    }

def generate_layouts(cuts):
    valid = []
    for r in range(1, MAX_LANES + 1):
        for combo in combinations_with_replacement(cuts, r):
            res = evaluate_layout(combo)
            if res:
                valid.append(res)
    valid.sort(key=lambda x: (-x["fill"], x["waste"]))
    return valid[:20]

def solve_job(layouts, cuts, qtys):
    remaining = qtys[:]
    plan = []

    while any(r > 0 for r in remaining):

        best = None
        best_score = -1

        for layout in layouts:

            produced = []
            total_gain = 0

            for i, c in enumerate(cuts):
                if c in layout:
                    gain = layout.count(c) * mult
                else:
                    gain = 0

                usable = min(gain, max(remaining[i], 0))
                total_gain += usable
                produced.append(gain)

            if total_gain == 0:
                continue

            if total_gain > best_score:
                best_score = total_gain
                best = (layout, produced)

        if best is None:
            break

        layout, produced = best

        new_remaining = []
        for i in range(len(remaining)):
            rem = remaining[i] - produced[i]
            if rem < -MAX_OVERRUN:
                rem = -MAX_OVERRUN
            new_remaining.append(rem)

        remaining = new_remaining

        plan.append({
            "layout": layout,
            "produced": produced,
            "remaining": remaining[:]
        })

    return plan

if st.button("Run Full Optimization"):

    layouts = generate_layouts(cuts)
    plan = solve_job(layouts, cuts, qtys)

    st.subheader(f"Total Mats Needed: {len(plan)}")

    for i, p in enumerate(plan):
        st.write(f"Layout Run {i+1}")
        st.write("Cuts:", p["layout"])
        st.write("Produced:", p["produced"])
        st.write("Remaining:", p["remaining"])
        st.write("---")
