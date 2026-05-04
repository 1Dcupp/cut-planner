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
# BUILD DEMAND
# -----------------------------
def build_demand(cuts):
    demand = []
    for c in cuts:
        demand += [c["Width"]] * int(c["Qty"])
    return demand

# -----------------------------
# PICK BEST SINGLE MAT LAYOUT
# (greedy fit)
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
# FACTORY SOLVER
# -----------------------------
def solve(cuts, layers):
    remaining = build_demand(cuts)
    plan = []

    while remaining:
        layout = build_layout(remaining)

        if not layout:
            break

        # remove used items
        for w in layout:
            remaining.remove(w)

        plan.append({
            "Blade Setup": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Layers per Mat": layers,
            "Effective Output": len(layout) * layers
        })

    return plan

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – FACTORY MODE (134\")")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2,2,2,2])

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    gram = st.number_input("Gram Weight", step=1)

with col4:
    layers = st.selectbox("Layers per Mat", [1, 2, 3])

if st.button("Add Cut"):
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
# GENERATE
# -----------------------------
if st.button("Generate Factory Plan"):
    st.session_state.plan = solve(st.session_state.cuts, layers)
    st.success("Factory plan generated")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.plan:
    st.subheader("Factory Production Plan")

    st.dataframe(st.session_state.plan, use_container_width=True)

    total_mats = len(st.session_state.plan)
    total_output = sum(p["Effective Output"] for p in st.session_state.plan)

    st.subheader("Summary")
    st.write(f"Total Mats Needed: {total_mats}")
    st.write(f"Total Output Produced: {total_output}")
