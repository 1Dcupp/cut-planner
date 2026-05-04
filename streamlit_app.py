import streamlit as st
from io import BytesIO

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")
MAT_WIDTH = 134

APP_URL = "https://your-app-url.streamlit.app"

# -----------------------------
# SESSION STATE
# -----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "layouts" not in st.session_state:
    st.session_state.layouts = []

# -----------------------------
# SAFE QR (no crash dependency risk)
# -----------------------------
def make_qr_placeholder():
    return "QR feature requires qrcode library"

# -----------------------------
# SIMPLE LAYOUT ENGINE (STABLE)
# -----------------------------
def generate_layouts(cuts):
    layouts = []

    for c in cuts:
        width = c["Width"]
        qty = c["Qty"]

        if width <= 0:
            continue

        per_mat = int(MAT_WIDTH // width)
        if per_mat < 1:
            per_mat = 1

        mats_needed = (qty + per_mat - 1) // per_mat
        waste = MAT_WIDTH - (per_mat * width)

        layouts.append({
            "Blade Setup": f"{width}\" cut x{per_mat}",
            "Qty Needed": qty,
            "Per Mat Output": per_mat,
            "Mats Needed": mats_needed,
            "Waste Per Mat": round(waste, 2)
        })

    return layouts

# -----------------------------
# HEADER
# -----------------------------
st.title("Cut Planner")

# -----------------------------
# INPUT AREA (compact)
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
    generate = st.button("Generate Layout")

with colB:
    print_btn = st.button("Print")

with colC:
    qr_btn = st.button("Show QR")

# -----------------------------
# GENERATE
# -----------------------------
if generate:
    st.session_state.layouts = generate_layouts(st.session_state.cuts)
    st.success("Layouts generated")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.layouts:
    st.subheader("Blade Setups")
    st.dataframe(st.session_state.layouts, use_container_width=True)

# -----------------------------
# PRINT (placeholder)
# -----------------------------
if print_btn:
    st.info("Print feature will export PDF next step")

# -----------------------------
# QR (SAFE VERSION)
# -----------------------------
if qr_btn:
    st.subheader("Share App")
    st.warning("QR code not enabled yet (to keep app stable)")
    st.write(APP_URL)
