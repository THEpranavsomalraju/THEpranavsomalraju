"""Draws pranav-net-4.svg: PRANAV spelled in network nodes, with a slow wave of activation moving through it."""
GLYPHS = {
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
}
WORD = "PRANAV"
W, H, S = 760, 190, 15          # card size, grid spacing
COLS, ROWS = 5 * len(WORD) + 2 * (len(WORD) - 1), 7
ox, oy = (W - (COLS - 1) * S) / 2, (H - (ROWS - 1) * S) / 2
WAVE, DUR = 2.2, 5.0            # seconds for the wave to cross, seconds per cycle

lit, letter_of = set(), {}
for li, ch in enumerate(WORD):
    for r, row in enumerate(GLYPHS[ch]):
        for c, bit in enumerate(row):
            if bit == "1":
                gc = li * 7 + c
                lit.add((gc, r))
                letter_of[(gc, r)] = li
pos = lambda c, r: (ox + c * S, oy + r * S)

# faint background grid covering the whole card
bg = []
c0, c1 = -int(ox // S), int((W - ox) // S)
r0, r1 = -int(oy // S), int((H - oy) // S)
for c in range(c0, c1 + 1):
    for r in range(r0, r1 + 1):
        x, y = pos(c, r)
        if 10 < x < W - 10 and 10 < y < H - 10 and (c, r) not in lit:
            bg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.1"/>')

# edges: neighbors inside a letter, and a few links from each letter to the next (like layers)
edges = []
for (c, r) in lit:
    for dc, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
        n = (c + dc, r + dr)
        if dc and dr and ((c + dc, r) in lit or (c, r + dr) in lit):
            continue                       # a straight edge already covers this step
        if n in lit and letter_of[n] == letter_of[(c, r)]:
            (x1, y1), (x2, y2) = pos(c, r), pos(*n)
            edges.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
links = []
DENSE = set(range(len(WORD) - 1))  # every pair of letters: link the outer node of every row, so the whole name looks even
for li in DENSE:
    pts_a = [p for p in lit if letter_of[p] == li]
    pts_b = [p for p in lit if letter_of[p] == li + 1]
    right = [max((p for p in pts_a if p[1] == r), key=lambda p: p[0]) for r in range(ROWS) if any(p[1] == r for p in pts_a)]
    left = [min((p for p in pts_b if p[1] == r), key=lambda p: p[0]) for r in range(ROWS) if any(p[1] == r for p in pts_b)]
    for a in right:
        for b in sorted(left, key=lambda q: abs(q[1] - a[1]))[:3]:
            (x1, y1), (x2, y2) = pos(*a), pos(*b)
            links.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
for li in range(len(WORD) - 1):
    if li in DENSE:
        continue
    right = [p for p in lit if letter_of[p] == li and p[0] == max(q[0] for q in lit if letter_of[q] == li)]
    left = [p for p in lit if letter_of[p] == li + 1 and p[0] == min(q[0] for q in lit if letter_of[q] == li + 1)]
    for a in right:
        for b in sorted(left, key=lambda q: abs(q[1] - a[1]))[:2]:
            (x1, y1), (x2, y2) = pos(*a), pos(*b)
            links.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

import random
random.seed(3)
last = len(WORD) - 1
# the outermost node of every row, so the start and end nodes get one link per row (7 each)
first_col = [min((p for p in lit if letter_of[p] == 0 and p[1] == r), key=lambda p: p[0]) for r in range(ROWS)]
last_col = [max((p for p in lit if letter_of[p] == last and p[1] == r), key=lambda p: p[0]) for r in range(ROWS)]
IN = (ox - 50, H / 2)
OUT = (ox + (COLS - 1) * S + 50, H / 2)
for p in first_col:
    x, y = pos(*p)
    links.append(f'<line x1="{IN[0]:.1f}" y1="{IN[1]:.1f}" x2="{x:.1f}" y2="{y:.1f}"/>')
for p in last_col:
    x, y = pos(*p)
    links.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{OUT[0]:.1f}" y2="{OUT[1]:.1f}"/>')

def col(li, side):
    pts = [p for p in lit if letter_of[p] == li]
    edge = (min if side == "left" else max)(q[0] for q in pts)
    return [p for p in pts if p[0] == edge]

# every drawn line becomes an edge, so signals only ever travel along lines and through nodes
import heapq
import math
import re
graph = {}
for ln in edges + links:
    x1, y1, x2, y2 = (round(float(v), 1) for v in re.findall(r'"([\d.]+)"', ln))
    graph.setdefault((x1, y1), []).append((x2, y2))
    graph.setdefault((x2, y2), []).append((x1, y1))
START, END = (round(IN[0], 1), round(IN[1], 1)), (round(OUT[0], 1), round(OUT[1], 1))


def route():
    """A shortest path from the start node to the end node under random edge weights: a different route every time."""
    w = {}
    dist, prev, heap = {START: 0.0}, {}, [(0.0, START)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == END:
            break
        if d > dist.get(u, math.inf):
            continue
        for v in graph[u]:
            key = (u, v) if u < v else (v, u)
            w.setdefault(key, math.dist(u, v) * random.uniform(0.6, 2.2))
            nd = d + w[key]
            if nd < dist.get(v, math.inf):
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))
    path, node = [END], END
    while node != START:
        node = prev[node]
        path.append(node)
    return path[::-1]


signals = []
N_SIG, SDUR = 14, 7.0
for k in range(N_SIG):
    pts = route()
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    b = k * SDUR / N_SIG
    signals.append(f'<path id="p{k}" d="{d}" fill="none"/>'
                   f'<circle r="2.4" class="sig"><animateMotion dur="{SDUR}s" begin="{b:.2f}s" repeatCount="indefinite">'
                   f'<mpath href="#p{k}"/></animateMotion>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.04;0.95;1" dur="{SDUR}s" begin="{b:.2f}s" repeatCount="indefinite"/></circle>')

nodes = []
for (c, r) in sorted(lit):
    x, y = pos(c, r)
    t = (x - ox) / ((COLS - 1) * S) * WAVE
    nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6">'
                 f'<animate attributeName="fill" values="#0D1117;#79C0FF;#0D1117;#0D1117" keyTimes="0;0.08;0.3;1" '
                 f'dur="{DUR}s" begin="{t:.2f}s" repeatCount="indefinite"/></circle>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.bg circle {{ fill: #21262D; }}
.links line {{ stroke: #388BFD; stroke-width: 0.7; opacity: 0.4; }}
.edges line {{ stroke: #388BFD; stroke-width: 1.4; opacity: 0.8; }}
.io {{ fill: #0D1117; stroke: #79C0FF; stroke-width: 2.2; }}
.core {{ fill: #79C0FF; }}
.sig {{ fill: #A5D6FF; opacity: 0; }}
.nodes circle {{ fill: #0D1117; stroke: #58A6FF; stroke-width: 1.4; }}
</style>
<rect x="0.5" y="0.5" rx="10" width="{W - 1}" height="{H - 1}" fill="#0D1117" stroke="#30363D"/>
<g class="bg">{"".join(bg)}</g>
<g class="links">{"".join(links)}</g>
<g class="edges">{"".join(edges)}</g>
<g class="nodes">{"".join(nodes)}</g>
{"".join(signals)}
<circle class="io" cx="{IN[0]:.1f}" cy="{IN[1]:.1f}" r="8"/>
<circle class="io" cx="{OUT[0]:.1f}" cy="{OUT[1]:.1f}" r="8"/>
</svg>
'''
open("pranav-net-4.svg", "w").write(svg)
print(len(lit), "letter nodes")
