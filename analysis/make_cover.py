# -*- coding: utf-8 -*-
"""make_cover.py — 生成满版 A4 封面（v6，现代学术风格）。

设计母题：**错位的时间**——由多圈“时钟环”构成，各环转速、刻度与相位彼此不同步，
金线螺旋自上而下贯穿，象征“熵增螺旋”与“制度时间／市场时间的永久错配”。
另以一枚红色虚线半径标出“临界日”：理论上应当对齐、实际却错开的时刻。

输出：assets/svg/cover.svg  （viewBox 1000×1414，与 A4 同比例，可满版出血）

用法：python analysis/make_cover.py
"""
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "svg", "cover.svg")

W, H = 1000, 1414
FONT_SANS = "'Microsoft YaHei','Heiti SC','SimHei',Arial,sans-serif"

TITLE_1 = "错位的时间"
TITLE_2 = ""
SUB_CN = "为什么我们总是来不及：社会系统的时间错配与可控性边界"
SUB_EN = "WHY WE ARE ALWAYS TOO LATE · TIME MISMATCH AND THE BOUNDARY OF CONTROLLABILITY"

CX, CY = 706, 872          # 时钟环中心
RINGS = [
    # 半径, 刻度数, 相位(度), 颜色, 高亮起点, 高亮跨度
    (78, 12, 0, "#e8c36a", 20, 96),
    (126, 10, 26, "#7fa8dd", 150, 70),
    (180, 8, 58, "#c94f4f", 255, 44),
    (240, 6, 12, "#e8c36a", 90, 120),
    (304, 5, 40, "#7fa8dd", 300, 60),
]


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc(cx, cy, r, d0, d1):
    x0, y0 = pol(cx, cy, r, d0)
    x1, y1 = pol(cx, cy, r, d1)
    large = 1 if (d1 - d0) % 360 > 180 else 0
    return f"M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}"


def main():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" font-family="{FONT_SANS}">']
    o.append("""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.34" y2="1">
    <stop offset="0%" stop-color="#05080f"/>
    <stop offset="50%" stop-color="#0d1730"/>
    <stop offset="100%" stop-color="#1b1233"/>
  </linearGradient>
  <radialGradient id="glow" cx="70%" cy="60%" r="62%">
    <stop offset="0%" stop-color="#3f66b0" stop-opacity="0.40"/>
    <stop offset="55%" stop-color="#1c2a52" stop-opacity="0.12"/>
    <stop offset="100%" stop-color="#05080f" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glow2" cx="20%" cy="20%" r="55%">
    <stop offset="0%" stop-color="#b8862f" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="#05080f" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="gold" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0%" stop-color="#8a6520"/>
    <stop offset="38%" stop-color="#e8c36a"/>
    <stop offset="72%" stop-color="#c8a24a"/>
    <stop offset="100%" stop-color="#f0d894"/>
  </linearGradient>
  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#e8c36a"/>
    <stop offset="100%" stop-color="#e8c36a" stop-opacity="0"/>
  </linearGradient>
</defs>""")
    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow2)"/>')

    # 细点阵（数据感）
    o.append('<g fill="#9db8e0" opacity="0.09">')
    for gy in range(96, 1340, 46):
        for gx in range(56, 962, 46):
            k = (gx / W) * 0.45 + (gy / H) * 0.55
            if k > 0.35:
                o.append(f'<circle cx="{gx}" cy="{gy}" r="1.3"/>')
    o.append("</g>")

    # ---- 错位时钟环 ----
    o.append(f'<circle cx="{CX}" cy="{CY}" r="336" fill="#0a1226" opacity="0.55"/>')
    for r, ticks, phase, col, hs, hspan in RINGS:
        # 环底
        o.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{col}" '
                 f'stroke-width="1.1" opacity="0.32"/>')
        # 刻度
        for t in range(ticks):
            deg = phase + t * 360.0 / ticks
            x0, y0 = pol(CX, CY, r - 7, deg)
            x1, y1 = pol(CX, CY, r + 7, deg)
            major = (t == 0)
            o.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                     f'stroke="{col}" stroke-width="{2.4 if major else 1.4}" '
                     f'opacity="{0.85 if major else 0.5}"/>')
        # 高亮弧（该子系统“应该对齐”的相位窗）
        o.append(f'<path d="{arc(CX, CY, r, phase+hs, phase+hs+hspan)}" fill="none" '
                 f'stroke="{col}" stroke-width="5" stroke-linecap="round" opacity="0.9"/>')
    # 中心
    o.append(f'<circle cx="{CX}" cy="{CY}" r="34" fill="#0d1730" stroke="#e8c36a" '
             f'stroke-width="1.4"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="7" fill="#f0d894"/>')

    # ---- 临界日虚线半径（本应对齐，实际错开） ----
    xe, ye = pol(CX, CY, 336, -66)
    o.append(f'<line x1="{CX}" y1="{CY}" x2="{xe:.1f}" y2="{ye:.1f}" stroke="#e05a5a" '
             f'stroke-width="1.8" stroke-dasharray="7 6"/>')
    o.append(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="5" fill="#e05a5a"/>')

    # ---- 熵增螺旋：自中心向上贯穿 ----
    pts = []
    n = 460
    for i in range(n + 1):
        t = i / n
        ang = -math.radians(66) + t * 3.7 * 2 * math.pi
        r = 300 * (1 - t) + 34 * t
        x = CX + r * math.cos(ang)
        y = CY + r * math.sin(ang) - 300 * t
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="#b8862f" stroke-width="15" '
             f'stroke-linecap="round" opacity="0.10"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#e8c36a" stroke-width="8.5" '
             f'stroke-linecap="round" opacity="0.16"/>')
    o.append(f'<path d="{d}" fill="none" stroke="url(#gold)" stroke-width="4.4" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    for (nx, ny) in pts[::92]:
        o.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="4.6" fill="#f0d894" opacity="0.95"/>')
        o.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="11" fill="none" stroke="#e8c36a" '
                 f'stroke-width="1.1" opacity="0.45"/>')

    # 边框
    o.append(f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" '
             f'stroke="#e8c36a" stroke-width="1.2" opacity="0.26"/>')

    # ---- 标题区 ----
    o.append('<text x="82" y="182" font-size="14.5" letter-spacing="6.5" fill="#c8a24a" '
             'font-weight="600">ACADEMIC MONOGRAPH</text>')
    o.append(f'<text x="78" y="336" font-size="108" font-weight="800" fill="#f6f2e8" '
             f'letter-spacing="6">错位的时间</text>')
    o.append('<rect x="82" y="378" width="330" height="2.6" fill="url(#rule)"/>')
    o.append(f'<text x="82" y="430" font-size="23" fill="#b9c6dd" letter-spacing="0.5">'
             f'为什么我们总是来不及：</text>')
    o.append(f'<text x="82" y="466" font-size="23" fill="#b9c6dd" letter-spacing="0.5">'
             f'社会系统的时间错配与可控性边界</text>')
    o.append('<text x="82" y="504" font-size="12.5" letter-spacing="2.2" fill="#7f8db0">'
             'WHY WE ARE ALWAYS TOO LATE · TIME MISMATCH AND THE BOUNDARY OF CONTROLLABILITY</text>')

    # 四轴芯片（含新增的 τ）
    chips = [("Θ", "租佃份额"), ("I", "组织复杂度"), ("κ", "地缘耦合"), ("τ", "时间错配")]
    cxx = 82
    for sym, lab in chips:
        wid = 30 + 15 * len(lab)
        o.append(f'<rect x="{cxx}" y="548" width="{wid}" height="38" rx="19" '
                 f'fill="#ffffff" opacity="0.06"/>')
        o.append(f'<text x="{cxx+16}" y="574" font-size="18" fill="#e8c36a" '
                 f'font-weight="700">{sym}</text>')
        o.append(f'<text x="{cxx+38}" y="574" font-size="14.5" fill="#c3cee2">{lab}</text>')
        cxx += wid + 12

    # ---- 页脚 ----
    o.append(f'<rect x="82" y="1246" width="836" height="1" fill="#ffffff" opacity="0.14"/>')
    o.append('<text x="82" y="1308" font-size="30" font-weight="700" fill="#eef3fb" '
             'letter-spacing="4">李毅芃　著</text>')
    o.append('<text x="82" y="1343" font-size="13.5" letter-spacing="3.4" fill="#7f8db0">'
             'LI YIPENG　·　2026</text>')
    o.append(f'<text x="{W-82}" y="1308" font-size="13.5" text-anchor="end" fill="#7f8db0" '
             f'letter-spacing="1.5">时间错配 · 可控性 · 局部可描述性</text>')
    o.append(f'<text x="{W-82}" y="1343" font-size="13.5" text-anchor="end" fill="#5f6f92" '
             f'letter-spacing="1">TIME MISMATCH · CONTROLLABILITY · LOCAL DESCRIPTABILITY</text>')

    o.append("</svg>\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
