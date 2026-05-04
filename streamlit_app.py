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

if "summary" not in st.session_state:
    st.session_state.summary = []

# -----------------------------
# DEMAND BUILD
# -----------------------------
def build_needed(cuts):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"])
    return needed

# -----------------------------
# TRUE BEST-FIT PACKING
# -----------------------------
def pack_mat(needed, produced):

    available = [
        w for w in needed
        if produced[w] < needed[w] + OVER_LIMIT
    ]

    # largest-first ordering
    available.sort(reverse=True)

    mat = []
    remaining = MAT_WIDTH

    # CRITICAL FIX: keep scanning until NOTHING fits
    while True:
        best_fit = None

        for w in available:
            if w <= remaining:
                best_fit = w
                break

        if best_fit is None:
            break

        mat.append(best_fit)
        remaining -= best_fit

    return mat

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts):

    needed = build_needed(cuts)
    produced = Counter()

    layout_count = Counter()
    output = []

    while True:

        # stop when all requirements met (within overrun limit)
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

        # count production correctly (NO fake multipliers)
        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layout_count[key] += 1

        output.append({
            "Blade Layout": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Runs (Mats)": layout_count[key],
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
st.title("CUT PLANNER – FINAL FACTORY OPTIMIZER (134\")")

st.caption("True production-grade bin packing system — stable, grouped, real output")

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

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB = st.columns(2)

with colA:
    run = st.button("Generate Layouts")

with colB:
    clear = st.button("Clear All")

if run:
    st.session_state.plan, st.session_state.summary = solve(st.session_state.cuts)

if clear:
    st.session_state.cuts = []
    st.session_state.plan = []
    st.session_state.summary = []
    st.rerun()

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.plan:
    st.subheader("Blade Layouts (Optimized Runs)")
    st.dataframe(st.session_state.plan, use_container_width=True)

if st.session_state.summary:
    st.subheader("Production Summary")
    st.dataframe(st.session_state.summary, use_container_width=True)
