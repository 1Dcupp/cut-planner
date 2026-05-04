import streamlit as st
from collections import Counter

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134
OVER_LIMIT = 6

# -----------------------------
# STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "plan" not in st.session_state:
    st.session_state.plan = []

# -----------------------------
# DEMAND
# -----------------------------
def build_needed(cuts):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"])
    return needed

# -----------------------------
# MAT PACKER (UNCHANGED CORE)
# -----------------------------
def pack_mat(needed, produced):

    available = [
        w for w in needed
        if produced[w] < needed[w] + OVER_LIMIT
    ]

    available.sort(reverse=True)

    mat = []
    remaining = MAT_WIDTH

    while True:
        added = False

        for w in available:
            if w <= remaining:
                mat.append(w)
                remaining -= w
                added = True
                break

        if not added:
            break

    return mat

# -----------------------------
# SOLVER (NOW WITH YIELD)
# -----------------------------
def solve(cuts, yield_per_mat):

    needed = build_needed(cuts)
    produced = Counter()

    layout_counts = Counter()
    output = []

    while True:

        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        mat = pack_mat(needed, produced)

        if not mat:
            break

        key = tuple(sorted(mat))
        layout_counts[key] += 1

        # APPLY YIELD MULTIPLIER HERE
        for w in mat:
            produced[w] += yield_per_mat

        output.append({
            "Blade Layout": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Yield per Mat": yield_per_mat,
            "Runs (Mats)": layout_counts[key],
            "Mat Fill": sum(key),
            "Waste": round(MAT_WIDTH - sum(key), 2)
        })

    summary = []

    for w in needed:
        summary.append({
            "Width": w,
            "Needed": needed[w],
            "Produced": produced[w],
            "Remaining": max(0, needed[w] - produced[w]),
            "Overrun": max(0, produced[w] - needed[w])
        })

    return output, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER – YIELD CONTROL VERSION (134\")")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_per_mat = st.selectbox("Yield per Mat", [1, 2, 3])

if st.button("Add Cut"):
    if width > 0 and qty > 0:
        st.session_state.cuts.append({
            "Width": width,
            "Qty": qty
        })
        st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

colA, colB = st.columns(2)

with colA:
    run = st.button("Generate Layouts")

with colB:
    clear = st.button("Clear All")

if run:
    st.session_state.plan, summary = solve(st.session_state.cuts, yield_per_mat)
    st.session_state.summary = summary

if clear:
    st.session_state.cuts = []
    st.session_state.plan = []
    st.session_state.summary = []
    st.rerun()

if st.session_state.plan:
    st.subheader("Layouts")
    st.dataframe(st.session_state.plan, use_container_width=True)

if "summary" in st.session_state:
    st.subheader("Production Summary")
    st.dataframe(st.session_state.summary, use_container_width=True)
