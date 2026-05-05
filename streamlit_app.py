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
        needed[float(c["Width"])] += int(c["Qty"])
    return needed, yield_mult

# -----------------------------
# GENERATE ALL LAYOUTS
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 7):
        for combo in itertools.combinations_with_replacement(widths, r):
            if sum(combo) <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# SCORE LAYOUTS (pure efficiency)
# -----------------------------
def score_layout(layout):
    fill = sum(layout)
    waste = MAT_WIDTH - fill
    efficiency = fill / MAT_WIDTH
    return efficiency, -waste

# -----------------------------
# PICK BEST LAYOUT (based on efficiency)
# -----------------------------
def pick_best_layout(layouts):
    best = None
    best_score = (-1, -999)

    for l in layouts:
        score = score_layout(l)

        if score > best_score:
            best_score = score
            best = l

    return best

# -----------------------------
# APPLY PRODUCTION CORRECTLY
# -----------------------------
def apply_production(layout, needed, produced, yield_mult):

    # IMPORTANT FIX:
    # each WIDTH gets multiplied individually

    for w in layout:
        produced[w] += yield_mult

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts, yield_mult):

    needed, yield_mult = build_needed(cuts, yield_mult)
    produced = Counter()

    widths = list(needed.keys())
    all_layouts = generate_layouts(widths)

    layout_history = []

    max_iters = 10000
    i = 0

    while i < max_iters:

        # check completion
        done = True
        for w in needed:
            if produced[w] < needed[w] * yield_mult:
                done = False
                break

        if done:
            break

        # pick best layout globally
        best = pick_best_layout(all_layouts)

        if not best:
            break

        # run ONE mat
        apply_production(best, needed, produced, yield_mult)

        layout_history.append(best)

        i += 1

    # -----------------------------
    # GROUP LAYOUTS
    # -----------------------------
    grouped = Counter(layout_history)

    layouts = []

    for layout, runs in grouped.items():
        per_layout_production = Counter()

        for w in layout:
            per_layout_production[w] += 1

        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Runs (Mats)": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),

            # FIXED TRUE OUTPUT
            "Total Production (Corrected)": {
                str(w): per_layout_production[w] * runs * yield_mult
                for w in per_layout_production
            }
        })

    # -----------------------------
    # SUMMARY (TRUE ACCURATE)
    # -----------------------------
    summary = []

    for w in needed:
        summary.append({
            "Width": w,
            "Needed": needed[w] * yield_mult,
            "Produced": produced[w],
            "Remaining": max(0, (needed[w] * yield_mult) - produced[w]),
            "Overrun": max(0, produced[w] - (needed[w] * yield_mult))
        })

    return layouts, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v6 – PRODUCTION-CORRECT ENGINE (134\")")

st.caption("Fixes per-width yield math (real factory logic)")

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

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.layouts:
    st.subheader("PRODUCTION LAYOUTS (v6 CORRECTED)")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("TRUE PRODUCTION SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
