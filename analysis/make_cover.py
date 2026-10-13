# -*- coding: utf-8 -*-
"""make_cover.py — 生成《错位的时间》满版封面 SVG（A4 比例 1000×1414）。

输出：assets/svg/cover.svg
封面须满版：配合 assets/css/book.css 中 .cover-page 的 210mm×297mm 与
@page :first { margin: 0 }，让底色铺满整页。

系列统一版式：与《遗忘的边界》《区分的演化》共用同一暗色渐变、顶部金线与
标题/副标题/作者/英文行的位置和字号；仅中心的线描母题因书而异。
母题：转速与相位各不相同的若干“时钟环”，一条未对齐的临界半径，以及一条
贯穿的螺旋（熵增轴线）——错位是结构性的，不是暂时失调。
"""
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "svg", "cover.svg")


def build():
    W, H = 1000, 1414
    ink = "#e8e6df"
    dim = "#9aa0a6"
    layers = []

    # 错位时钟环：刻度密度（转速）与相位各不相同
    cx, cy = 500, 560
    rings = [(96, 12, 0, "#3a6ea5"),
             (156, 10, 24, "#b8862f"),
             (224, 8, 52, "#009E73"),
             (300, 6, 12, "#3a6ea5")]
    for r, ticks, phase, col in rings:
        layers.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                      f'stroke="{col}" stroke-width="1.2" opacity="0.30"/>')
        for t in range(ticks):
            a = math.radians(phase + t * 360.0 / ticks)
            x0 = cx + (r - 8) * math.cos(a)
            y0 = cy + (r - 8) * math.sin(a)
            x1 = cx + (r + 8) * math.cos(a)
            y1 = cy + (r + 8) * math.sin(a)
            major = (t == 0)
            layers.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                          f'stroke="{col}" stroke-width="{2.2 if major else 1.2}" '
                          f'opacity="{0.75 if major else 0.42}"/>')
    # 环心
    layers.append(f'<circle cx="{cx}" cy="{cy}" r="18" fill="none" '
                  f'stroke="#e8c36a" stroke-width="1.2" opacity="0.70"/>')
    layers.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#e8c36a" opacity="0.80"/>')

    # 未对齐的临界半径：本应对齐，实际错开
    xe = cx + 300 * math.cos(math.radians(-64))
    ye = cy + 300 * math.sin(math.radians(-64))
    layers.append(f'<line x1="{cx}" y1="{cy}" x2="{xe:.1f}" y2="{ye:.1f}" stroke="#c94f4f" '
                  f'stroke-width="1.5" stroke-dasharray="7,6" opacity="0.60"/>')

    # 熵增螺旋：自环心向外贯穿
    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        ang = -math.radians(64) + t * 3.2 * 2 * math.pi
        rr = 300 * (1 - t) + 18 * t
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang) - 220 * t
        pts.append(f"{x:.1f},{y:.1f}")
    layers.append('<polyline points="' + " ".join(pts) + '" fill="none" stroke="#b8862f" '
                  'stroke-width="2.2" opacity="0.60" stroke-linejoin="round"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#0e1117"/><stop offset="0.55" stop-color="#151a23"/>
<stop offset="1" stop-color="#0b0e14"/>
</linearGradient>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<rect x="0" y="0" width="{W}" height="8" fill="#b8862f" opacity="0.85"/>
{chr(10).join(layers)}
<style>
text{{font-family:'Microsoft YaHei','SimHei',Arial,sans-serif;}}
.ttl{{font-size:108px;font-weight:700;letter-spacing:12px;fill:{ink};}}
.sub{{font-size:29px;fill:{dim};letter-spacing:2px;}}
.eng{{font-size:21px;fill:{dim};letter-spacing:1px;}}
.au{{font-size:30px;fill:{ink};letter-spacing:2px;}}
.rule{{stroke:{dim};stroke-width:1;opacity:0.6;}}
</style>
<text x="80" y="176" class="eng">DESYNCHRONIZED TIME</text>
<text x="80" y="300" class="ttl">错位的时间</text>
<line x1="84" y1="344" x2="660" y2="344" class="rule"/>
<text x="84" y="396" class="sub">为什么我们总是来不及：</text>
<text x="84" y="440" class="sub">社会系统的时间错配与可控性边界</text>
<text x="80" y="1180" class="au">李毅芃　著</text>
<text x="80" y="1232" class="eng">Temporal Mismatch and the Boundary of Controllability</text>
<text x="80" y="1274" class="eng">学术专著 · 2026</text>
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
