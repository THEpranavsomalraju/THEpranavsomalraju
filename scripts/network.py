"""Draws network.svg: a small neural network with signals moving through it, in the stats card's colors."""
import random

random.seed(7)
W, H = 760, 190
LAYERS = [4, 6, 8, 8, 6, 3]
xs = [80 + i * (W - 160) / (len(LAYERS) - 1) for i in range(len(LAYERS))]
nodes = [[(x, H / 2 + (j - (n - 1) / 2) * 20) for j in range(n)] for x, n in zip(xs, LAYERS)]

edges = []
for a, b in zip(nodes, nodes[1:]):
    for p in a:
        for q in b:
            edges.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}"/>')

signals = []
for k in range(7):
    path = [random.choice(layer) for layer in nodes]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path)
    begin = k * 0.9
    signals.append(f'<path id="s{k}" d="{d}" class="lit"/>'
                   f'<circle r="2.6" class="sig"><animateMotion dur="4.2s" begin="{begin:.1f}s" repeatCount="indefinite">'
                   f'<mpath href="#s{k}"/></animateMotion>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.9;1" dur="4.2s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>')

dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4"/>' for layer in nodes for x, y in layer)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.edges line {{ stroke: #30363D; stroke-width: 0.6; }}
.lit {{ fill: none; stroke: #1F6FEB; stroke-width: 0.9; opacity: 0.35; }}
.nodes circle {{ fill: #0D1117; stroke: #58A6FF; stroke-width: 1.3; }}
.sig {{ fill: #79C0FF; opacity: 0; }}
</style>
<rect x="0.5" y="0.5" rx="10" width="{W - 1}" height="{H - 1}" fill="#0D1117" stroke="#30363D"/>
<g class="edges">{"".join(edges)}</g>
{"".join(signals)}
<g class="nodes">{dots}</g>
</svg>
'''
open("network.svg", "w").write(svg)
