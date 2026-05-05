import streamlit as st
from collections import Counter
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
# BUILD DEMAND (ACTIVE REMAINING SYSTEM)
# -----------------------------
def build_remaining(cuts, yield_mult):
    remaining = Counter()
    for c in cuts:
        remaining[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return remaining

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
# SCORE LAYOUT BASED ON CURRENT REMAINING DEMAND
# -----------------------------
def score_layout(layout, remaining):

    usefulness = 0

    for w in layout:
        if remaining[w] > 0:
            usefulness += 1

    fill = sum(layout)
    waste = MAT_WIDTH - fill

    return usefulness, fill, -waste

# -----------------------------
# PICK BEST LAYOUT (DYNAMIC)
# -----------------------------
def pick_best_layout(layouts, remaining):

    best = None
    best_score = (-1, -1, -999)

    for l in layouts:
        score = score_layout(l, remaining)

        if score > best_score:
            best_score = score
            best = l

    return best

# -----------------------------
# APPLY PRODUCTION → REDUCE DEMAND (KEY FIX)
# -----------------------------
def apply_layout(layout, remaining, yield_mult):

    for w in layout:
        if remaining[w] > 0:
            remaining[w] -= yield_mult

            if remaining[w] < 0:
                remaining[w] = 0

# -----------------------------
# CHECK IF DONE
# -----------------------------
def is_done(remaining):
    return all(v <= 0 for v in remaining.values())

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts, yield_mult):

    remaining = build_remaining(cuts, yield_mult)

    widths = list(remaining.keys())
    all_layouts = generate_layouts(widths)

    history = []

    max_iters = 10000
    i = 0

    while i < max_iters:

        if is_done(remaining):
            break

        best = pick_best_layout(all_layouts, remaining)

        if not best:
            break

        apply_layout(best, remaining, yield_mult)

        history.append(best)

        i += 1

    # -----------------------------
    # GROUP RESULTS
    # -----------------------------
    grouped = Counter(history)

    layouts = []

    for layout, runs in grouped.items():
        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Runs (Mats)": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Total Output per Run": Counter(layout)
        })

    summary = []

    for w, val in remaining.items():
        summary.append({
            "Width": w,
            "Remaining (Final)": val
        })

    return layouts, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v7 – DEMAND DRIVEN ENGINE (134\")")

st.caption("System now removes completed demand and re-optimizes automatically")

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
    st.subheader("PRODUCTION LAYOUTS (v7)")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("REMAINING DEMAND (FINAL STATE)")
    st.dataframe(st.session_state.summary, use_container_width=True)
