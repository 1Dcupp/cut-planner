import streamlit as st
from collections import Counter

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
# BUILD FLAT ORDER LIST
# -----------------------------
def build_demand(cuts):
    demand = []
    for c in cuts:
        demand += [c["Width"]] * int(c["Qty"])
    return sorted(demand, reverse=True)

# -----------------------------
# FIND BEST LAYOUT FOR REMAINING PIECES
# -----------------------------
def find_best_layout(remaining):
    best = None
    best_score = 0

    # try building a mat greedily
    for i in range(len(remaining)):
        total = 0
        layout = []

        for j in range(i, len(remaining)):
            if total + remaining[j] <= MAT_WIDTH:
                total += remaining[j]
                layout.append(remaining[j])

        if layout:
            score = total  # higher fill = better

            if score > best_score:
                best_score = score
                best = layout

    return best

# -----------------------------
# MAIN SOLVER
# -----------------------------
def solve(cuts):
    remaining = build_demand(cuts)
    result = []

    while remaining:
        layout = find_best_layout(remaining)

        if not layout:
            break

        # remove used items
        for w in layout:
            remaining.remove(w)

        result.append({
            "Blade Setup": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Mat Width Used": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2)
        })

    return result

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – Production Optimizer (134\")")

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
    if st.button("Add"):
        st.session_state.cuts.append({
            "Width": width,
            "Qty": qty,
            "Gram": gram
        })
        st.rerun()

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

# -----------------------------
# RUN OPTIMIZER
# -----------------------------
if st.button("Generate Production Plan"):
    st.session_state.plan = solve(st.session_state.cuts)
    st.success("Production plan generated")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.plan:
    st.subheader("Production Layouts (Real Mats)")

    st.dataframe(st.session_state.plan, use_container_width=True)

    st.subheader("Summary")
    st.write(f"Total Mats Needed: {len(st.session_state.plan)}")
