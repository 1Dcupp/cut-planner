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

if "locked_layouts" not in st.session_state:
    st.session_state.locked_layouts = []

# -----------------------------
# BUILD DEMAND (NO CONFUSION VERSION)
# -----------------------------
def build_needed(cuts, yield_mult):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"]) * yield_mult
    return needed

# -----------------------------
# GENERATE ALL POSSIBLE LAYOUTS
# -----------------------------
def generate_layouts(widths):
    layouts = set()

    for r in range(1, 7):
        for combo in itertools.combinations_with_replacement(widths, r):
            total = sum(combo)
            if total <= MAT_WIDTH:
                layouts.add(tuple(sorted(combo, reverse=True)))

    return list(layouts)

# -----------------------------
# SCORE LAYOUTS
# -----------------------------
def score(layout):
    fill = sum(layout)
    waste = MAT_WIDTH - fill
    efficiency = fill / MAT_WIDTH
    return efficiency, -waste

# -----------------------------
# LOCK TOP LAYOUTS (KEY CHANGE)
# -----------------------------
def lock_best_layouts(widths):

    all_layouts = generate_layouts(widths)

    scored = []

    for l in all_layouts:
        eff, waste = score(l)
        scored.append((eff, waste, l))

    # sort best first
    scored.sort(reverse=True)

    # take TOP 3 ONLY
    top = [x[2] for x in scored[:3]]

    return top

# -----------------------------
# PICK BEST FROM LOCKED SET ONLY
# -----------------------------
def pick_from_locked(locked, needed, produced):

    best = None
    best_score = (-1, -999)

    for layout in locked:
        score_val = sum(layout) / MAT_WIDTH

        if score_val > best_score[0]:
            best_score = (score_val, 0)
            best = layout

    return best

# -----------------------------
# BUILD MAT
# -----------------------------
def build_mat(locked, needed, produced):

    usable = [
        w for w in needed
        if produced[w] < needed[w] + OVER_LIMIT
    ]

    if not usable:
        return []

    layout = pick_from_locked(locked, needed, produced)

    return list(layout) if layout else []

# -----------------------------
# SOLVER (LOCKED SYSTEM)
# -----------------------------
def solve(cuts, yield_mult):

    needed = build_needed(cuts, yield_mult)
    produced = Counter()

    widths = list(needed.keys())

    # LOCK layouts ONCE
    locked = lock_best_layouts(widths)
    st.session_state.locked_layouts = locked

    layout_groups = defaultdict(int)

    i = 0
    max_iters = 10000

    while i < max_iters:

        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        mat = build_mat(locked, needed, produced)

        if not mat:
            break

        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layout_groups[key] += 1

        i += 1

    layouts = []

    for layout, runs in layout_groups.items():
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
st.title("CUT PLANNER v4 – LOCKED FACTORY SYSTEM (134\")")

st.caption("Now uses locked top layouts (NO layout explosion)")

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
    st.session_state.locked_layouts = []
    st.rerun()

if run:
    st.session_state.layouts, st.session_state.summary = solve(
        st.session_state.cuts,
        yield_mult
    )

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.locked_layouts:
    st.subheader("LOCKED MASTER LAYOUTS (TOP 3)")
    for l in st.session_state.locked_layouts:
        st.write(" + ".join([f'{x}"' for x in l]))

if st.session_state.layouts:
    st.subheader("PRODUCTION RUNS")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if st.session_state.summary:
    st.subheader("SUMMARY")
    st.dataframe(st.session_state.summary, use_container_width=True)
