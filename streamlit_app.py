import streamlit as st
import qrcode
from io import BytesIO

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
# QR FUNCTION
# -----------------------------
def make_qr(url):
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf)
    return buf

# -----------------------------
# SIMPLE LAYOUT ENGINE (REAL)
# -----------------------------
def generate_layouts(cuts):
    layouts = []

    for c in cuts:
        width = c["Width"]
        qty = c["Qty"]

        if width <= 0:
            continue

        per_mat = MAT_WIDTH // width
        mats_needed = (qty // per_mat) if per_mat > 0 else 0
        remainder = qty % per_mat if per_mat > 0 else qty

        layouts.append({
            "Blade Setup": f"{width}\" cut",
            "Qty Needed": qty,
            "Per Mat Output": int(per_mat),
            "Mats Needed": int(mats_needed + (1 if remainder > 0 else 0)),
            "Waste Per Mat": round(MAT_WIDTH - (per_mat * width), 2) if per_mat > 0 else MAT_WIDTH
        })

    return layouts

# -----------------------------
# UI HEADER
# -----------------------------
st.title("Cut Planner Dashboard")

# -----------------------------
# INPUT ROW (COMPACT)
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
# ACTION BUTTONS
# -----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Layout")

with colB:
    print_btn = st.button("Print")

with colC:
    qr_btn = st.button("Show QR")

# -----------------------------
# GENERATE LAYOUT
# -----------------------------
if generate:
    st.session_state.layouts = generate_layouts(st.session_state.cuts)
    st.success("Layouts generated using 134\" mat width")

# -----------------------------
# OUTPUT LAYOUTS
# -----------------------------
if st.session_state.layouts:
    st.subheader("Blade Setups")
    st.dataframe(st.session_state.layouts, use_container_width=True)

# -----------------------------
# PRINT (EXPORT PLACEHOLDER)
# -----------------------------
if print_btn:
    st.info("Print feature placeholder — next step will be PDF export")

# -----------------------------
# QR CODE
# -----------------------------
if qr_btn:
    st.subheader("Share App")
    qr = make_qr(APP_URL)
    st.image(qr, width=200)
    st.caption(APP_URL)
