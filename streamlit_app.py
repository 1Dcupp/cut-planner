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
# DEMAND BUILDER
# -----------------------------
def build_needed(cuts, yield_mult):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return needed

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
# SCORE LAYOUT AGAINST CURRENT DEMAND
# -----------------------------
def score_layout(layout, needed, produced):

    # how useful is this layout RIGHT NOW?
    usefulness = 0

    for w in layout:
        if produced[w] < needed[w]:
            usefulness += 1

    fill = sum(layout)
    waste = MAT_WIDTH - fill

    return usefulness, fill, -waste

# -----------------------------
# PICK BEST LAYOUT (DYNAMIC)
# -----------------------------
def pick_best_layout(layouts, needed, produced):

    best = None
    best_score = (-1, -1, -999)

    for l in layouts:
        score = score_layout(l, needed, produced)

        # prioritize usefulness first, then efficiency
        if score > best_score:
            best_score = score
            best = l

    return best

# -----------------------------
# RUN ONE MAT
# -----------------------------
def run_mat(layout, needed, produced):

    for w in layout:
        if produced[w] < needed[w] + OVER_LIMIT:
            produced[w] += 1

    return layout

# -----------------------------
# SOLVER (FULL ADAPTIVE LOOP)
# -----------------------------
def solve(cuts, yield_mult):

    needed = build_needed(cuts, yield_mult)
    produced = Counter()

    widths = list(needed.keys())
    all_layouts = generate_layouts(widths)

    layout_history = []

    max_iters = 10000
    i = 0

    while i < max_iters:

        # check if done
        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        # pick BEST layout based on CURRENT state
        best = pick_best_layout(all_layouts, needed, produced)

        if not best:
            break

        # run ONE mat
        run_mat(best, needed, produced)

        layout_history.append(best)

        i += 1

    # -----------------------------
    # GROUP RESULTS
    # -----------------------------
    grouped = Counter(layout_history)

    layouts = []

    for layout, runs in grouped.items():
        layouts.append({
            "Blade Layout": " + ".join([f'{w}"' for w in layout]),
            "Pieces per Mat": len(layout),
            "Runs (Mats)": runs,
            "Mat Fill": sum(layout),
            "Waste": round(MAT_WIDTH - sum(layout), 2),
            "Total Produced": sum(layout) * runs
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

    return layouts, summary

# -----------------------------
# UI
# -----------------------------
st.title("CUT PLANNER v5 – ADAPTIVE FACTORY ENGINE (134\")")

st.caption("Switches layouts dynamically based on remaining demand")

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
    st.subheader("PRODUCTION LAYOUTS (ADAPTIVE)")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
