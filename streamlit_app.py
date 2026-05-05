import streamlit as st
from collections import Counter, defaultdict
import itertools

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
# BUILD DEMAND
# -----------------------------
def build_needed(cuts, yield_mult):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return needed

# -----------------------------
# GENERATE POSSIBLE COMBOS (KEY FIX)
# -----------------------------
def generate_combos(widths, max_width):
    combos = []

    # allow repeated use, small controlled depth
    for r in range(1, 6):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= max_width:
                combos.append(tuple(sorted(combo, reverse=True)))

    # remove duplicates
    return list(set(combos))

# -----------------------------
# PICK BEST FIT COMBO
# -----------------------------
def best_fit_combo(widths, remaining):
    best = None
    best_fill = 0

    combos = generate_combos(widths, MAT_WIDTH)

    for c in combos:
        total = sum(c)
        if total <= remaining and total > best_fill:
            best = c
            best_fill = total

    return best

# -----------------------------
# BUILD ONE MAT (REAL OPTIMIZER)
# -----------------------------
def build_mat(needed, produced):

    widths = list(needed.keys())
    mat = []
    remaining = MAT_WIDTH

    while True:

        combo = best_fit_combo(widths, remaining)

        if not combo:
            break

        mat.extend(combo)
        remaining -= sum(combo)

    return mat

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts, yield_mult):

    needed = build_needed(cuts, yield_mult)
    produced = Counter()

    layout_groups = defaultdict(int)
    layouts = []

    while True:

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

        # production tracking
        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layout_groups[key] += 1

    # build output table
    for layout, runs in layout_groups.items():
        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Runs (Mats)": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Total Pieces": sum(layout) * runs
        })

    summary = []

    for w in needed:
        summary.append({
            "Width": w,
            "Needed (Adj)": needed[w],
            "Produced": produced[w],
            "Remaining": max(0, needed[w] - produced[w]),
            "Overrun": max(0, produced[w] - needed[w])
        })

    return layouts, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER – FINAL MIXED LAYOUT ENGINE (134\")")

st.caption("Now supports X1 / X2 / X3 + true mixed-size layouts")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_mult = st.selectbox("Yield Mode", [1, 2, 3])

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

if clear:
    st.session_state.cuts = []
    st.session_state.layouts = []
    st.session_state.summary = []
    st.rerun()

if run:
    st.session_state.layouts, st.session_state.summary = solve(st.session_state.cuts, yield_mult)

if st.session_state.layouts:
    st.subheader("OPTIMIZED MIXED LAYOUTS")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("PRODUCTION SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
