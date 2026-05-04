import streamlit as st
from collections import Counter

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

if "result" not in st.session_state:
    st.session_state.result = []

# -----------------------------
# BUILD DEMAND
# -----------------------------
def build_needed(cuts):
    needed = Counter()
    for c in cuts:
        needed[float(c["Width"])] += int(c["Qty"])
    return needed

# -----------------------------
# BUILD ONE MAT (SIMPLE + CORRECT)
# -----------------------------
def build_mat(needed, produced):
    available = []

    for w in needed:
        if produced[w] < needed[w] + OVER_LIMIT:
            available.append(w)

    available.sort(reverse=True)

    mat = []
    total = 0

    for w in available:
        if total + w <= MAT_WIDTH:
            mat.append(w)
            total += w

    return mat

# -----------------------------
# SOLVER
# -----------------------------
def solve(cuts):

    needed = build_needed(cuts)
    produced = Counter()

    layouts = Counter()
    output = []

    while True:

        # stop if all satisfied (within +6)
        done = True
        for w in needed:
            if produced[w] < needed[w]:
                done = False
                break

        if done:
            break

        mat = build_mat(needed, produced)

        if not mat:
            break

        # apply production (NO MULTIPLIERS, NO YIELD)
        for w in mat:
            if produced[w] < needed[w] + OVER_LIMIT:
                produced[w] += 1

        key = tuple(sorted(mat))
        layouts[key] += 1

        output.append({
            "Blade Layout": " + ".join([f'{w}"' for w in key]),
            "Pieces per Mat": len(key),
            "Runs (Mats)": layouts[key],
            "Mat Fill": sum(key),
            "Waste": round(MAT_WIDTH - sum(key), 2)
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

    return output, summary

# -----------------------------
# UI
# -----------------------------
st.title("Cut Planner (RESET VERSION)")

col1, col2 = st.columns(2)

with col1:
    width = st.number_input("Cut Width", step=0.5)

with col2:
    qty = st.number_input("Qty Needed", step=1)

if st.button("Add Cut"):
    if width > 0 and qty > 0:
        st.session_state.cuts.append({
            "Width": width,
            "Qty": qty
        })
        st.rerun()

st.subheader("Cuts")
st.dataframe(st.session_state.cuts, use_container_width=True)

colA, colB = st.columns(2)

with colA:
    go = st.button("Generate")

with colB:
    clear = st.button("Clear")

if go:
    st.session_state.result = solve(st.session_state.cuts)

if clear:
    st.session_state.cuts = []
    st.session_state.result = []
    st.rerun()

if st.session_state.result:
    st.subheader("Layouts")
    st.dataframe(st.session_state.result[0], use_container_width=True)

    st.subheader("Summary")
    st.dataframe(st.session_state.result[1], use_container_width=True)
