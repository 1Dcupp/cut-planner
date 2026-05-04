import streamlit as st
from itertools import combinations

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
# OPTIMIZER ENGINE (STABLE V1)
# -----------------------------
def generate_layouts(cuts):
    items = []

    # expand quantities into list
    for c in cuts:
        for _ in range(int(c["Qty"])):
            items.append(c["Width"])

    if not items:
        return []

    layouts = []

    # combinations up to 4 blades per mat
    for r in range(1, min(5, len(items) + 1)):
        for combo in combinations(items, r):

            total = sum(combo)

            if total > MAT_WIDTH:
                continue

            waste = MAT_WIDTH - total

            layouts.append({
                "Blade Setup": " + ".join([f"{w}\"" for w in combo]),
                "Pieces": len(combo),
                "Total Width": total,
                "Waste": round(waste, 2)
            })

    # best first (least waste, best fill)
    layouts.sort(key=lambda x: (x["Waste"], -x["Total Width"]))

    return layouts[:20]

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner Optimizer (134\" System)")

# -----------------------------
# INPUT AREA
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
    if st.button("Add"):
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
    generate = st.button("Generate Layouts")

with colB:
    print_btn = st.button("Print")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.layouts = generate_layouts(st.session_state.cuts)
    st.success("Optimized layouts generated")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.layouts:
    st.subheader("Best Blade Layouts")

    st.dataframe(st.session_state.layouts, use_container_width=True)

# -----------------------------
# PRINT PLACEHOLDER
# -----------------------------
if print_btn:
    st.info("Print export will be added after optimizer is finalized")
