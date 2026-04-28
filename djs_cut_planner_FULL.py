import streamlit as st
from itertools import combinations_with_replacement

# =======================
# SETTINGS
# =======================
MAX_WIDTH = 134
MAX_LANES = 8
MAX_OVERRUN = 6

st.set_page_config(page_title="DJ's Cut Planner", layout="wide")

st.title("DJ's Cut Planner")
st.caption("Excel-Style Highlighted Layout Optimizer")

# =======================
# INPUTS
# =======================
st.header("Inputs")

num_items = st.number_input("How many cut sizes?", min_value=1, max_value=25, value=3)

cuts = []
qtys = []

for i in range(int(num_items)):
    col1, col2 = st.columns(2)

    with col1:
        w = st.number_input(f"Cut Width {i+1}", min_value=0.0, max_value=134.0, step=0.5, key=f"w{i}")

    with col2:
        q = st.number_input(f"Qty {i+1}", min_value=0, step=1, key=f"q{i}")

    cuts.append(w)
    qtys.append(q)

clean = [(c, q) for c, q in zip(cuts, qtys) if c > 0 and q > 0]

if len(clean) == 0:
    st.warning("Enter at least one valid width and quantity.")
    st.stop()

cuts, qtys = zip(*clean)

# =======================
# SETTINGS
# =======================
st.header("Run Settings")
output_multiplier = st.selectbox("Output per mat", ["2x", "3x"])
mult = 2 if output_multiplier == "2x" else 3

# =======================
# ENGINE
# =======================
def evaluate(layout):
    total = sum(layout)
    if total > MAX_WIDTH or len(layout) > MAX_LANES:
        return None
    return {
        "layout": layout,
        "total": total,
        "fill": total / MAX_WIDTH,
        "waste": MAX_WIDTH - total
    }

def generate(cuts):
    results = []
    for r in range(1, MAX_LANES + 1):
        for combo in combinations_with_replacement(cuts, r):
            res = evaluate(combo)
            if res:
                results.append(res)
    results.sort(key=lambda x: (-x["fill"], x["waste"]))
    return results[:10]

def solve(layouts, cuts, qtys):
    remaining = list(qtys)
    plan = []

    for layout in layouts:
        produced = []

        for i, c in enumerate(cuts):
            produced.append(layout.count(c) * mult if c in layout else 0)

        new_remaining = []
        for i in range(len(remaining)):
            rem = remaining[i] - produced[i]
            if rem < -MAX_OVERRUN:
                rem = -MAX_OVERRUN
            new_remaining.append(rem)

        remaining = new_remaining

        plan.append({
            "layout": layout,
            "produced": produced,
            "remaining": remaining.copy(),
            "fill": (sum(layout) / MAX_WIDTH) * 100
        })

        if all(r <= 0 for r in remaining):
            break

    return plan

# =======================
# RUN
# =======================
if st.button("Run Optimization"):

    layouts = generate(cuts)

    if not layouts:
        st.error("No valid layouts found under 134 width.")
        st.stop()

    plan = solve(layouts, cuts, qtys)

    st.subheader(f"Total Mats Needed: {len(plan)}")

    st.markdown("### 📊 Layout Results")

    for i, p in enumerate(plan):

        fill = p["fill"]

        if fill >= 95:
            color = "🟢"
        elif fill >= 85:
            color = "🟡"
        else:
            color = "🔴"

        st.markdown(f"""
### {color} Layout {i+1}

**Cuts:** {p['layout']}  
**Fill %:** {fill:.1f}%  
**Produced:** {p['produced']}  
**Remaining:** {p['remaining']}  
**Output:** {output_multiplier}  
---
""")

st.caption("DJ's Cut Planner - Excel Style System")