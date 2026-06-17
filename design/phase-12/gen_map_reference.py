"""Generate a faithful schematic reference image of the canonical_1 map from the
engine YAML (so coordinates are guaranteed accurate). Output: a neutral grayscale
SVG (+ PNG if cairosvg is available) to attach to the Claude Design Wave-0 art
exploration. The reference is intentionally style-neutral — it fixes the LAYOUT
only; the exploration restyles it.

Run: uv run python design/phase-12/gen_map_reference.py
"""

from __future__ import annotations

import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAP = os.path.join(ROOT, "engine", "maps", "canonical_1.yaml")
OUT_SVG = os.path.join(HERE, "canonical_1-map-reference.svg")
OUT_PNG = os.path.join(HERE, "canonical_1-map-reference.png")

data = yaml.safe_load(open(MAP, encoding="utf-8"))
rooms = data["rooms"]
edges = data["edges"]
vents = data["vents"]

SCALE = 14
MARGIN = 56
LEGEND_H = 110

xs0 = min(r["position"]["x"] for r in rooms.values())
ys0 = min(r["position"]["y"] for r in rooms.values())
xs1 = max(r["position"]["x"] + r["size"]["width"] for r in rooms.values())
ys1 = max(r["position"]["y"] + r["size"]["height"] for r in rooms.values())


def px(x: float) -> float:
    return MARGIN + (x - xs0) * SCALE


def py(y: float) -> float:
    return MARGIN + (y - ys0) * SCALE


W = int(px(xs1) + MARGIN)
H = int(py(ys1) + MARGIN + LEGEND_H)


def rect(name):
    r = rooms[name]
    p, s = r["position"], r["size"]
    return px(p["x"]), py(p["y"]), s["width"] * SCALE, s["height"] * SCALE


def center(name):
    x, y, w, h = rect(name)
    return x + w / 2, y + h / 2


vent_rooms = {v["room"] for v in vents.values()}
# undirected vent edges (dedup) by the room each vent sits in
vent_edges = set()
for vid, v in vents.items():
    a = v["room"]
    for other in v["connects_to"]:
        b = vents[other]["room"]
        vent_edges.add(tuple(sorted((a, b))))

HUB = data["meeting"]["room"]
# dead-ends = task rooms with exactly one corridor edge
deg = {n: 0 for n in rooms}
for e in edges:
    deg[e["from"]] += 1
    deg[e["to"]] += 1
DEADENDS = {n for n, r in rooms.items() if r["kind"] == "task_room" and deg[n] == 1}

KIND_FILL = {
    "hallway": "#d7dde6",
    "task_room": "#e9eef4",
    "meeting_room": "#e1e8f3",
    "utility": "#edf0f4",
    "room": "#e9eef4",
}
KIND_TAG = {
    "hallway": "hallway",
    "task_room": "task",
    "meeting_room": "meeting",
    "utility": "utility",
    "room": "room",
}
EDGE = "#aab2bd"
VENT = "#1ba3b8"
BORDER = "#566173"
INK = "#1f2733"
SUB = "#6b7480"

el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'font-family="ui-sans-serif, system-ui, -apple-system, sans-serif">',
    f'<rect width="{W}" height="{H}" fill="#f7f8fa"/>',
    f'<text x="{MARGIN}" y="30" font-size="22" font-weight="700" fill="{INK}">'
    f"canonical_1 — AiLibi map (authoritative LAYOUT)</text>",
    f'<text x="{MARGIN}" y="50" font-size="13" fill="{SUB}">Schematic reference for art '
    f"exploration — restyle freely; do NOT move, rename, add, or remove rooms. "
    f"10 rooms · 11 corridors · 6-vent ring.</text>",
]

# corridors (under rooms)
for e in edges:
    ax, ay = center(e["from"])
    bx, by = center(e["to"])
    el.append(
        f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" '
        f'stroke="{EDGE}" stroke-width="3"/>'
    )

# room rects
for name, r in rooms.items():
    x, y, w, h = rect(name)
    extra = ' stroke-width="3.5"' if name == HUB else ' stroke-width="1.8"'
    el.append(
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="6" '
        f'fill="{KIND_FILL.get(r["kind"], "#e9eef4")}" stroke="{BORDER}"{extra}/>'
    )

# vent edges (over rooms, dashed) + markers
for a, b in sorted(vent_edges):
    ax, ay = center(a)
    bx, by = center(b)
    el.append(
        f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" '
        f'stroke="{VENT}" stroke-width="2.2" stroke-dasharray="7 5" opacity="0.75"/>'
    )
for name in vent_rooms:
    x, y, w, h = rect(name)
    mx, my = x + 13, y + h - 13
    el.append(
        f'<path d="M {mx} {my - 6} L {mx + 6} {my} L {mx} {my + 6} L {mx - 6} {my} Z" '
        f'fill="{VENT}" opacity="0.9"/>'
    )

# labels (on top)
for name, r in rooms.items():
    x, y, w, h = rect(name)
    cx, cy = x + w / 2, y + h / 2
    tags = []
    if name == HUB:
        tags.append("hub")
    if name in DEADENDS:
        tags.append("dead-end")
    tagline = " · ".join([KIND_TAG.get(r["kind"], r["kind"])] + tags)
    if w <= 4 * SCALE + 1:  # narrow vertical hall -> rotate
        el.append(
            f'<text x="{cx:.0f}" y="{cy:.0f}" font-size="13" fill="{INK}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'transform="rotate(-90 {cx:.0f} {cy:.0f})">{r["name"]}</text>'
        )
    else:
        el.append(
            f'<text x="{cx:.0f}" y="{cy - 6:.0f}" font-size="15" font-weight="600" '
            f'fill="{INK}" text-anchor="middle">{r["name"]}</text>'
        )
        el.append(
            f'<text x="{cx:.0f}" y="{cy + 12:.0f}" font-size="11" fill="{SUB}" '
            f'text-anchor="middle">{tagline}</text>'
        )

# legend
ly = H - LEGEND_H + 24
lx = MARGIN
el.append(
    f'<line x1="{lx}" y1="{ly}" x2="{lx + 34}" y2="{ly}" stroke="{EDGE}" stroke-width="3"/>'
)
el.append(
    f'<text x="{lx + 44}" y="{ly + 4}" font-size="13" fill="{INK}">corridor (1 tick)</text>'
)
el.append(
    f'<line x1="{lx + 220}" y1="{ly}" x2="{lx + 254}" y2="{ly}" stroke="{VENT}" '
    f'stroke-width="2.2" stroke-dasharray="7 5"/>'
)
el.append(
    f'<path d="M {lx + 275} {ly - 6} L {lx + 281} {ly} L {lx + 275} {ly + 6} L {lx + 269} {ly} Z" fill="{VENT}"/>'
)
el.append(
    f'<text x="{lx + 292}" y="{ly + 4}" font-size="13" fill="{INK}">vent (impostor-only, 6-room ring)</text>'
)
el.append(
    f'<text x="{lx}" y="{ly + 30}" font-size="12" fill="{SUB}">'
    f"Cafeteria = hub (spawn/meeting/emergency) · Reactor &amp; Labs = dead-end kill rooms · "
    f"lights repair @ Admin · reactor repair @ Reactor+Engineering.</text>"
)
el.append("</svg>")

svg = "\n".join(el)
with open(OUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg)
print(
    f"SVG: {OUT_SVG} ({W}x{H})  rooms={len(rooms)} corridors={len(edges)} vent_edges={len(vent_edges)}"
)
print(f"vent_rooms={sorted(vent_rooms)} dead_ends={sorted(DEADENDS)} hub={HUB}")

try:
    import cairosvg  # type: ignore

    cairosvg.svg2png(url=OUT_SVG, write_to=OUT_PNG, output_width=W * 2)
    print(f"PNG: {OUT_PNG}")
except Exception as ex:  # noqa: BLE001
    print(
        f"PNG skipped ({type(ex).__name__}: {ex}) — attach the SVG, or render it in any browser."
    )
