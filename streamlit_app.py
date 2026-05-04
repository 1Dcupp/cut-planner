import streamlit as st
from itertools import combinations
from io import BytesIO
import qrcode

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

MAT_WIDTH = 134
APP_URL = "https://cut-planner-ztz5lflxkp2i3hseturgac.streamlit.app"

# -----------------------------
# SESSION STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "layouts" not in st.session_state:
    st.session_state.layouts = []

# -----------------------------
# QR
# -----------------------------
def make_qr(url):
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf)
    return buf

# -----------------------------
# REAL OPTIMIZER (CORE ENGINE)
# -----------------------------
def generate_layouts(cuts):
    widths = []

    # expand into usable list
    for c in cuts:
        for _ in range(int(c["Qty"])):
            widths.append(c["Width"])

    if not widths:
        return []

    layouts = []

    # try combinations of up to 4 blades (keeps it fast + realistic)
    for r in range(1, min(5, len(widths) + 1)):
        for combo in combinations(widths, r):

            total = sum(combo)

            if total > MAT_WIDTH:
                continue

            waste = MAT_WIDTH - total

            layouts.append({
                "Blade Setup": " + ".join([f"{w}\"" for w in combo]),
                "Total Width": total,
                "Waste": round(waste, 2),
                "Pieces": len(combo)
            })

    # rank best (least waste, most usage)
    layouts.sort(key=lambda x: (x["Waste"], -x["Total Width"]))

    return layouts[:20]  # top 20 best layouts

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner – Optimizer Mode (134\")")

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
    if st.button("Add"):
        st.session_state.cuts.append({
            "Width": width,
            "Qty": qty,
            "Gram": gram
        })
        st.rerun()

# -----------------------------
# CUT LIST
# -----------------------------
st.subheader("Cuts")

if st.session_state.cuts:
    st.dataframe(st.session_state.cuts, use_container_width=True)
else:
    st.caption("No cuts added")

# -----------------------------
# ACTIONS
# -----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Best Layouts")

with colB:
    print_btn = st.button("Print")

with colC:
    qr_btn = st.button("QR Code")

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
    st.subheader("Best Blade Layouts (Ranked)")

    st.dataframe(st.session_state.layouts, use_container_width=True)

# -----------------------------
# PRINT PLACEHOLDER
# -----------------------------
if print_btn:
    st.info("Next step: PDF print sheet export (ready
