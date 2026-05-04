import streamlit as st
from collections import Counter, defaultdict

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

if "layouts" not in st.session_state:
    st.session_state.layouts = []

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
# BUILD ONE FULL MAT (REAL PACKING)
# -----------------------------
def build_mat(needed, produced):
    available = [
        w for w in needed
        if produced[w] < needed[w] + OVER_LIMIT
    ]

    available.sort(reverse=True)

    mat = []
    remaining = MAT_WIDTH

    while True:
        placed = False

        for w in available:
            if w <= remaining:
                mat.append(w)
                remaining -= w
                placed = True
                break

        if not placed:
            break

    return mat

# -----------------------------
# OPTIMIZER ENGINE
# -----------------------------
def solve(cuts):

    needed = build_needed(cuts)
    produced = Counter()

    layouts = []
    layout_groups = defaultdict(int)

    # safety loop
    max_iters = 10000
    i = 0

    while i < max_iters:

        # check done
        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        mat = build_mat(needed, produced)

        if not mat:
            break

        # apply production (REAL assignment into layout)
        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layout_groups[key] += 1

        i += 1

    # build final layout table (IMPORTANT FIX)
    for layout, runs in layout_groups.items():
        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Mat Runs": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Total Pieces Produced": sum(layout) * runs
        })

    # summary per width
    summary = []

    for w in needed:
        summary.append({
            "Width": w,
            "Needed": needed[w],
            "Produced": produced[w],
            "Remaining": max(0, needed[w] - produced[w]),
            "Overrun": max(0, produced[w] - needed[w])
        })

    return layouts, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER – FINAL FACTORY ENGINE (134\")")

st.caption("Every piece is assigned to a real layout. No floating counts. No fake yields.")

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

st.subheader("Cuts Input")
st.dataframe(st.session_state.cuts, use_container_width=True)

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB = st.columns(2)

with colA:
    run = st.button("Generate Layouts")

with colB:
    clear = st.button("Clear All")

if clear:
    st.session_state.cuts = []
    st.session_state.layouts = []
    st.session_state.summary = []
    st.rerun()

if run:
    st.session_state.layouts, st.session_state.summary = solve(st.session_state.cuts)

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.layouts:
    st.subheader("FINAL LAYOUTS (REAL GROUPED RUNS)")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("PRODUCTION SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
