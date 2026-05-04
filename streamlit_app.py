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
    yield_map = {}

    for c in cuts:
        demand += [c["Width"]] * int(c["Qty"])
        yield_map[c["Width"]] = c["Yield"]

    return demand, yield_map

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
# SOLVER (FIXED FACTORY LOGIC)
# -----------------------------
def solve(cuts):

    demand, yield_map = build_demand(cuts)
    remaining = demand.copy()

    layout_counts = Counter()
    layout_map = {}

    while remaining:
        layout = build_layout(remaining)

        if not layout:
            break

        key = tuple(sorted(layout))
        layout_counts[key] += 1

        layout_map[key] = {
            "Blade Setup": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Mat Fill": sum(key),
            "Waste": round(MAT_WIDTH - sum(key), 2),
            "Runs (Mats)": layout_counts[key]
        }

        for w in layout:
            remaining.remove(w)

    # -----------------------------
    # FINAL OUTPUT FIX (NO DUPLICATES)
    # -----------------------------
    final = []

    total_output = Counter()

    for key, data in layout_map.items():

        runs = data["Runs (Mats)"]

        # production output per width
        for w in key:
            total_output[w] += runs * yield_map.get(w, 1)

        final.append(data)

    # -----------------------------
    # SUMMARY TABLE
    # -----------------------------
    summary = []

    for c in cuts:
        w = c["Width"]
        needed = int(c["Qty"])
        produced = total_output[w]
        yield_per_mat = c["Yield"]

        summary.append({
            "Width": w,
            "Qty Needed": needed,
            "Yield/Mat": yield_per_mat,
            "Qty Produced": produced,
            "Remaining": max(0, needed - produced),
            "Overrun": max(0, produced - needed)
        })

    return final, summary

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – TRUE Factory Mode (134\")")

st.info(f"Total Cuts: {len(st.session_state.cuts)}")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2,2,2,2])

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_per_mat = st.number_input("Yield per Mat", step=1, value=1)

with col4:
    if st.button("Add Cut"):
        if width > 0 and qty > 0:
            st.session_state.cuts.append({
                "Width": width,
                "Qty": qty,
                "Yield": yield_per_mat
            })
            st.success(f"Added {width}\" x {qty} (Yield {yield_per_mat})")
            st.rerun()

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

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
# OUTPUT LAYOUTS
# -----------------------------
if st.session_state.plan:
    st.subheader("Layouts (Grouped Runs)")

    st.dataframe(st.session_state.plan, use_container_width=True)

# -----------------------------
# OUTPUT SUMMARY
# -----------------------------
if "summary" in st.session_state:
    st.subheader("Production Summary")

    st.dataframe(st.session_state.summary, use_container_width=True)
