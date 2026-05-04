from collections import defaultdict
from itertools import combinations

def generate_layouts(cuts):
    items = []

    # expand quantities into list
    for c in cuts:
        for _ in range(int(c["Qty"])):
            items.append(c["Width"])

    if not items:
        return []

    layout_counts = defaultdict(int)
    layout_data = {}

    # generate combinations
    for r in range(1, min(5, len(items) + 1)):
        for combo in combinations(items, r):

            total = sum(combo)

            if total > MAT_WIDTH:
                continue

            # normalize layout (sort so duplicates match)
            key = tuple(sorted(combo))

            layout_counts[key] += 1
            layout_data[key] = {
                "Blade Setup": " + ".join([f"{w}\"" for w in key]),
                "Total Width": total,
                "Waste": round(MAT_WIDTH - total, 2),
                "Pieces": len(key)
            }

    # build final table with usage count
    results = []

    for key, data in layout_data.items():
        results.append({
            **data,
            "Runs (Mats Needed)": layout_counts[key]
        })

    # sort best first (least waste, most efficient)
    results.sort(key=lambda x: (x["Waste"], -x["Total Width"]))

    return results[:20]
