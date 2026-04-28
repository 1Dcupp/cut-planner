import streamlit as st
from itertools import combinations_with_replacement

MAX_WIDTH = 134
MAX_LANES = 8
MAX_OVERRUN = 6

st.set_page_config(page_title="DJ's Cut Planner", layout="wide")

st.title("DJ's Cut Planner")
st.caption("Excel Style Layout Planner")

st.header("Inputs")

num_items = st.number_input("How many cut sizes?", min_value=1, max_value=25, value=3)

cuts = []
qtys = []

for i in range(int(num_items)):
    col1, col2 = st.columns(2)

    with col1:
        w = st.text_input(f"Cut Width {i+1}", key=f"w{i}")

    with col2:
        q = st.text_input(f"Qty {i+1}", key=f"q{i}")

    try:
        w_val = float(w) if w.strip() != "" else None
    except:
        w_val = None

    try:
        q_val = int(q) if q.strip() != "" else None
    except:
        q_val = None

    cuts.append(w_val)
    qtys.append(q_val)

clean = [(c, q) for c, q in zip(cuts, qtys) if c is not None and q is not None]

if len(clean) == 0:
    st.warning("Enter at least one width and quantity.")
    st.stop()

cuts, qtys = zip(*clean)

cuts = list(cuts)
qtys = list(qtys)

output_multiplier = st.selectbox("Output per mat", ["2x", "3x"])
mult = 2 if output_multiplier == "2x" else 3

def evaluate(layout):
    total = sum(float(x) for x in layout)
    if total > MAX_WIDTH or len(layout) > MAX_LANES:
        return None
    return {
        "layout": layout,
        "total": total,
        "fill": (total / MAX_WIDTH) * 100,
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
            "fill": (sum(float(x) for x in layout) / MAX_WIDTH) * 100
        })

        if all(r <= 0 for r in remaining):
            break

    return plan

if st.button("Run Optimization"):
    layouts = generate(cuts)

    if not layouts:
        st.error("No valid layouts found under 134 width.")
        st.stop()

    plan = solve(layouts, cuts, qtys)

    st.subheader(f"Total Mats Needed: {len(plan)}")

    for i, p in enumerate(plan):
        fill = p["fill"]
        color = "🟢" if fill >= 95 else "🟡" if fill >= 85 else "🔴"

        st.markdown(f"""
### {color} Layout {i+1}

**Cuts:** {p['layout']}  
**Fill %:** {fill:.1f}%  
**Produced:** {p['produced']}  
**Remaining:** {p['remaining']}  
**Output:** {output_multiplier}  
---
""")

st.caption("DJ's Cut Planner")
