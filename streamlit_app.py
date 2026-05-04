import streamlit as st

st.set_page_config(layout="wide")

# ----------------------------
# SESSION STATE
# ----------------------------
if "cuts" not in st.session_state:
    st.session_state.cuts = []

if "layouts" not in st.session_state:
    st.session_state.layouts = []

# ----------------------------
# HEADER (compact)
# ----------------------------
st.title("Cut Planner Dashboard")

# ----------------------------
# INPUT ROW (compact, no scrolling)
# ----------------------------
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

# ----------------------------
# CURRENT INPUT TABLE
# ----------------------------
st.subheader("Cuts List")

if st.session_state.cuts:
    st.dataframe(st.session_state.cuts, use_container_width=True)
else:
    st.caption("No cuts added yet")

# ----------------------------
# ACTION ROW (compact buttons)
# ----------------------------
colA, colB, colC = st.columns(3)

with colA:
    generate = st.button("Generate Layout")

with colB:
    print_btn = st.button("Print")

with colC:
    qr_btn = st.button("QR Code")

# ----------------------------
# OUTPUT AREA
# ----------------------------
st.divider()

# ----------------------------
# PLACEHOLDER LOGIC (safe so app won't crash)
# ----------------------------
if generate:
    st.session_state.layouts = [
        {"Layout": "Demo Layout 1", "Mat Usage": "124 in", "Waste": "4 in"},
        {"Layout": "Demo Layout 2", "Mat Usage": "118 in", "Waste": "10 in"}
    ]

    st.success("Layout generated")

if st.session_state.layouts:
    st.subheader("Generated Layouts")
    st.dataframe(st.session_state.layouts, use_container_width=True)

if print_btn:
    st.info("Print feature placeholder (we will connect PDF export next)")

if qr_btn:
    st.info("QR feature placeholder (next step we add real QR code)")
