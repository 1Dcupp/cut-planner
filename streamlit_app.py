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
# GENERATE ALL COMBINATIONS (REAL KEY FIX)
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    # controlled depth search (fast but powerful)
    for r in range(1, 7):
        for combo in itertools.combinations_with_replacement(widths, r):
            total = sum(combo)
            if total <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# SCORE LAYOUTS
# -----------------------------
def score_layout(layout):
    fill = sum(layout)
    waste = MAT_WIDTH - fill
    efficiency = fill / MAT_WIDTH
    return efficiency, -waste  # higher is better

# -----------------------------
# PICK BEST LAYOUT
# -----------------------------
def pick_best_layout(widths):
    candidates = generate_layouts(widths)

    best = None
    best_score = (-1, -999)

    for layout in candidates:
        eff, waste_score = score_layout(layout)
        score = (eff, waste_score)

        if score > best_score:
            best_score = score
            best = layout

    return best

# -----------------------------
# BUILD MAT
# -----------------------------
def build_mat(needed, produced):

    usable = [
        w for w in needed
        if produced[w] < needed[w] + OVER_LIMIT
    ]

    if not usable:
        return []

    layout = pick_best_layout(usable)

    return list(layout) if layout else []

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts, yield_mult):

    needed = build_needed(cuts, yield_mult)
    produced = Counter()

    layout_groups = defaultdict(int)

    max_iters = 10000
    i = 0

    while i < max_iters:

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

        # APPLY PRODUCTION AFTER LAYOUT IS BUILT (CORRECT)
        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layout_groups[key] += 1

        i += 1

    # build output
    layouts = []

    for layout, runs in layout_groups.items():
        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Runs (Mats)": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Total Pieces Produced": sum(layout) * runs
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
st.title("CUT PLANNER – v3 FACTORY OPTIMIZER (134\")")

st.caption("True optimizer: generates + scores layouts before selecting best mix")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    yield_mult = st.selectbox("Yield Mode (X1 / X2 / X3)", [1, 2, 3])

if st.button("Add Cut"):
    if width > 0 and qty > 0:
        st.session_state.cuts.append({"Width": width, "Qty": qty})
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
    st.session_state.layouts, st.session_state.summary = solve(
        st.session_state.cuts,
        yield_mult
    )

if st.session_state.layouts:
    st.subheader("OPTIMIZED LAYOUTS (v3)")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("PRODUCTION SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
