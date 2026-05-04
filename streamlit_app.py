import streamlit as st
from collections import Counter

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134
OVER_LIMIT = 6  # max allowed overrun per width

# -----------------------------
# SESSION STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "plan" not in st.session_state:
    st.session_state.plan = []

# -----------------------------
# BUILD DEMAND LIST
# -----------------------------
def build_demand(cuts):
    demand = []
    for c in cuts:
        demand += [c["Width"]] * int(c["Qty"])
    return demand

# -----------------------------
# GREEDY LAYOUT BUILDER
# -----------------------------
def build_layout(remaining):
    remaining = sorted(remaining, reverse=True)

    layout = []
    total = 0

    for w in remaining:
        if total + w <= MAT_WIDTH:
            layout.append(w)
            total += w

    return layout

# -----------------------------
# FACTORY SOLVER (WITH +6 OVER LIMIT)
# -----------------------------
def solve(cuts):

    demand = build_demand(cuts)
    remaining = demand.copy()

    needed = Counter()
    produced = Counter()

    for c in cuts:
        needed[c["Width"]] = int(c["Qty"])

    plan = []
    layout_runs = Counter()

    while remaining:

        layout = build_layout(remaining)

        if not layout:
            break

        # filter layout by overrun rule
        safe_layout = []

        for w in layout:
            if produced[w] < needed[w] + OVER_LIMIT:
                safe_layout.append(w)
                produced[w] += 1

        # if nothing valid, stop
        if not safe_layout:
            break

        # remove used items from remaining
        for w in safe_layout:
            if w in remaining:
                remaining.remove(w)

        key = tuple(sorted(safe_layout))
        layout_runs[key] += 1

        plan.append({
            "Blade Setup": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Mat Fill": sum(key),
            "Waste": round(MAT_WIDTH - sum(key), 2),
            "Runs (Mats)": layout_runs[key]
        })

    # -----------------------------
    # PRODUCTION SUMMARY
    # -----------------------------
    summary = []

    for c in cuts:
        w = c["Width"]
        need = int(c["Qty"])
        prod = produced[w]

        summary.append({
            "Width": w,
            "Qty Needed": need,
            "Qty Produced": prod,
            "Remaining": max(0, need - prod),
            "Overrun": max(0, prod - need)
        })

    return plan, summary

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – Factory Optimizer (134\")")

st.info(f"Total Cuts Loaded: {len(st.session_state.cuts)}")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    gram = st.number_input("Gram Weight", step=1)

with col4:
    if st.button("Add Cut"):

        if width > 0 and qty > 0:
            st.session_state.cuts.append({
                "Width": width,
                "Qty": qty,
                "Gram": gram
            })
            st.success(f"Added {width}\" x {qty}")
            st.rerun()
        else:
            st.error("Invalid input")

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts List")

if st.session_state.cuts:
    st.dataframe(st.session_state.cuts, use_container_width=True)
else:
    st.caption("No cuts added yet")

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Factory Plan")

with colB:
    clear = st.button("Clear All")

with colC:
    st.button("Print")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.plan, st.session_state.summary = solve(st.session_state.cuts)
    st.success("Factory plan generated")

# -----------------------------
# CLEAR
# -----------------------------
if clear:
    st.session_state.cuts = []
    st.session_state.plan = []
    st.session_state.summary = []
    st.rerun()

# -----------------------------
# OUTPUT: LAYOUTS
# -----------------------------
if st.session_state.plan:
    st.subheader("Factory Layouts")

    st.dataframe(st.session_state.plan, use_container_width=True)

# -----------------------------
# OUTPUT: SUMMARY
# -----------------------------
if "summary" in st.session_state:
    st.subheader("Production Summary")

    st.dataframe(st.session_state.summary, use_container_width=True)
