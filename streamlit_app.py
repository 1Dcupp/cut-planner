import streamlit as st
from itertools import combinations
from collections import defaultdict

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

if "layouts" not in st.session_state:
    st.session_state.layouts = []

# -----------------------------
# OPTIMIZER ENGINE (CLEAN + GROUPED)
# -----------------------------
def generate_layouts(cuts):
    items = []

    # expand quantities into individual pieces
    for c in cuts:
        for _ in range(int(c["Qty"])):
            items.append(c["Width"])

    if not items:
        return []

    layout_counts = defaultdict(int)
    layout_data = {}

    # generate combinations (up to 4 blades per mat)
    for r in range(1, min(5, len(items) + 1)):
        for combo in combinations(items, r):

            total = sum(combo)

            if total > MAT_WIDTH:
                continue

            # normalize so duplicates group together
            key = tuple(sorted(combo))

            layout_counts[key] += 1

            layout_data[key] = {
                "Blade Setup": " + ".join([f"{w}\"" for w in key]),
                "Total Width": total,
                "Waste": round(MAT_WIDTH - total, 2),
                "Pieces": len(key)
            }

    # build final output
    results = []

    for key, data in layout_data.items():
        results.append({
            **data,
            "Runs (Mats Needed)": layout_counts[key]
        })

    # sort best first
    results.sort(key=lambda x: (x["Waste"], -x["Total Width"]))

    return results[:20]

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner Optimizer (134\" Production System)")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    gram = st.number_input("Gram Weight", step=1)

with col4:
    st.write("")
    if st.button("Add Cut"):
        if width > 0 and qty > 0:
            st.session_state.cuts.append({
                "Width": width,
                "Qty": qty,
                "Gram": gram
            })
        st.rerun()

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts List")

if st.session_state.cuts:
    st.dataframe(st.session_state.cuts, use_container_width=True)
else:
    st.caption("No cuts added yet")

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB = st.columns(2)

with colA:
    generate = st.button("Generate Optimized Layouts")

with colB:
    print_btn = st.button("Print")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.layouts = generate_layouts(st.session_state.cuts)
    st.success("Layouts generated (optimized + grouped)")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.layouts:
    st.subheader("Best Blade Layouts (Ranked)")

    st.dataframe(st.session_state.layouts, use_container_width=True)

# -----------------------------
# PRINT PLACEHOLDER
# -----------------------------
if print_btn:
    st.info("Next step: PDF export for shop-floor printing (coming next upgrade)")
