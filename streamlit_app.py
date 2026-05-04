import streamlit as st
from itertools import combinations
from collections import defaultdict, Counter

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134

# -----------------------------
# SESSION STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "plan" not in st.session_state:
    st.session_state.plan = []

# -----------------------------
# BUILD DEMAND
# -----------------------------
def build_demand(cuts):
    demand = []
    for c in cuts:
        demand += [c["Width"]] * int(c["Qty"])
    return demand

# -----------------------------
# FIND BEST LAYOUT (GREEDY)
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
# FACTORY SOLVER (WITH TRACKING)
# -----------------------------
def solve(cuts):
    remaining = build_demand(cuts)
    original_counts = Counter(remaining)

    plan = []
    used_counts = Counter()

    while remaining:
        layout = build_layout(remaining)

        if not layout:
            break

        # apply layout once (one mat run)
        for w in layout:
            remaining.remove(w)
            used_counts[w] += 1

        plan.append({
            "Blade Setup": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2)
        })

    # -----------------------------
    # PRODUCTION SUMMARY TABLE
    # -----------------------------
    summary = []

    for c in st.session_state.cuts:
        w = c["Width"]
        needed = int(c["Qty"])
        produced = used_counts[w]
        remaining_qty = max(0, needed - produced)
        overrun = max(0, produced - needed)

        summary.append({
            "Width": w,
            "Qty Needed": needed,
            "Qty Produced": produced,
            "Remaining": remaining_qty,
            "Overrun": overrun
        })

    return plan, summary

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – Production Tracker (134\")")

st.info(f"Total Cuts in List: {len(st.session_state.cuts)}")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2,2,2,1])

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
st.dataframe(st.session_state.cuts, use_container_width=True)

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Production Plan")

with colB:
    clear = st.button("Clear All")

with colC:
    print_btn = st.button("Print")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.plan, st.session_state.summary = solve(st.session_state.cuts)
    st.success("Production plan generated")

# -----------------------------
# CLEAR
# -----------------------------
if clear:
    st.session_state.cuts = []
    st.session_state.plan = []
    st.session_state.summary = []
    st.success("Reset complete")
    st.rerun()

# -----------------------------
# OUTPUT: LAYOUTS
# -----------------------------
if st.session_state.plan:
    st.subheader("Factory Layouts")

    st.dataframe(st.session_state.plan, use_container_width=True)

# -----------------------------
# OUTPUT: PRODUCTION SUMMARY
# -----------------------------
if "summary" in st.session_state and st.session_state.summary:
    st.subheader("Production Tracking")

    st.dataframe(st.session_state.summary, use_container_width=True)

    total_mats = len(st.session_state.plan)

    st.write(f"Total Mats Used: {total_mats}")

# -----------------------------
# PRINT
# -----------------------------
if print_btn:
    st.info("Print export coming next upgrade")
