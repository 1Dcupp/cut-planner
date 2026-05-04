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

if "summary" not in st.session_state:
    st.session_state.summary = []

# -----------------------------
# BUILD DEMAND MAP
# -----------------------------
def build_needed(cuts):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"])
    return needed

# -----------------------------
# BUILD ONE MAT LAYOUT (IMPORTANT FIX)
# -----------------------------
def build_layout(needed, produced):
    """
    Greedy pack but does NOT remove items prematurely.
    Only uses availability + remaining mat space.
    """

    candidates = []

    for w in needed:
        # enforce +6 cap per width
        if produced[w] < needed[w] + OVER_LIMIT:
            candidates.append(w)

    # largest-first packing (standard cutting logic)
    candidates.sort(reverse=True)

    layout = []
    total = 0

    for w in candidates:
        if total + w <= MAT_WIDTH:
            layout.append(w)
            total += w

    return layout

# -----------------------------
# MAIN SOLVER
# -----------------------------
def solve(cuts):

    needed = build_needed(cuts)
    produced = Counter()

    plan = []
    layout_count = Counter()

    max_iters = 10000
    i = 0

    while i < max_iters:

        # check if done
        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        layout = build_layout(needed, produced)

        if not layout:
            break

        # apply production (REAL WORLD LOGIC)
        for w in layout:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(layout))
        layout_count[key] += 1

        plan.append({
            "Blade Setup": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Runs (Mats)": layout_count[key],
            "Mat Fill": sum(key),
            "Waste": round(MAT_WIDTH - sum(key), 2)
        })

        i += 1

    # -----------------------------
    # SUMMARY TABLE
    # -----------------------------
    summary = []

    for w in needed:
        summary.append({
            "Width": w,
            "Needed": needed[w],
            "Produced": produced[w],
            "Remaining": max(0, needed[w] - produced[w]),
            "Overrun": max(0, produced[w] - needed[w])
        })

    return plan, summary

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – Stable Production System (134\")")

st.info("No yield system. +6 max overrun per width. True mat packing.")

# -----------------------------
# INPUT
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    if width > 0 and qty > 0:
        st.session_state.cuts.append({
            "Width": width,
            "Qty": qty
        })
        st.rerun()

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts List")
st.dataframe(st.session_state.cuts, use_container_width=True)

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB = st.columns(2)

with colA:
    generate = st.button("Generate Layouts")

with colB:
    clear = st.button("Clear All")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.plan, st.session_state.summary = solve(st.session_state.cuts)
    st.success("Layouts generated")

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
    st.subheader("Blade Layouts")

    st.dataframe(st.session_state.plan, use_container_width=True)

# -----------------------------
# OUTPUT: SUMMARY
# -----------------------------
if st.session_state.summary:
    st.subheader("Production Summary")

    st.dataframe(st.session_state.summary, use_container_width=True)
