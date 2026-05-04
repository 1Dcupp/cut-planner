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

if "plan" not in st.session_state:
    st.session_state.plan = []

# -----------------------------
# OPTIMIZER ENGINE (FACTORY MODE)
# -----------------------------
def generate_layouts(cuts):
    items = []

    # expand quantity into list
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

            key = tuple(sorted(combo))

            layout_counts[key] += 1

            layout_data[key] = {
                "Blade Setup": " + ".join([f"{w}\"" for w in key]),
                "Pieces": len(key),
                "Total Width": total,
                "Waste": round(MAT_WIDTH - total, 2)
            }

    results = []

    for key, data in layout_data.items():
        results.append({
            **data,
            "Runs (Mats Needed)": layout_counts[key]
        })

    results.sort(key=lambda x: (x["Waste"], -x["Total Width"]))

    return results[:20]

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner Optimizer (134\" Factory Mode)")

st.info(f"Total Cuts in List: {len(st.session_state.cuts)}")

# -----------------------------
# INPUT
# -----------------------------
col1, col2, col3, col4 = st.columns([2,2,2,1])

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

with col3:
    gram = st.number_input("Gram Weight", step=1)

with col4:
    if st.button("Add Cut"):

        if width > 0 and qty > 0:
            st.session_state.cuts.append({
                "Width": width,
                "Qty": qty,
                "Gram": gram
            })

            st.success(f"Added cut: {width}\" x {qty}")

            st.rerun()
        else:
            st.error("Enter valid width and quantity")

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts List")

if st.session_state.cuts:
    st.dataframe(st.session_state.cuts, use_container_width=True)
else:
    st.caption("No cuts added yet")

# -----------------------------
# ACTION BUTTONS
# -----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Factory Plan")

with colB:
    clear = st.button("Clear All")

with colC:
    print_btn = st.button("Print")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.plan = generate_layouts(st.session_state.cuts)
    st.success("Factory plan generated")

# -----------------------------
# CLEAR ALL
# -----------------------------
if clear:
    st.session_state.cuts = []
    st.session_state.plan = []
    st.success("All cuts and layouts cleared")
    st.rerun()

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.plan:
    st.subheader("Factory Layouts")

    st.dataframe(st.session_state.plan, use_container_width=True)

# -----------------------------
# PRINT PLACEHOLDER
# -----------------------------
if print_btn:
    st.info("Print export will be added in next upgrade")
