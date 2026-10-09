# -*- coding: utf-8 -*-
"""
make_cover.py — 生成满版 A4 封面（现代学术风格）。

输出：assets/svg/cover.svg  （viewBox 1000×1414，与 A4 同比例，可满版出血）

用法：python analysis/make_cover.py
"""
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "svg", "cover.svg")

W, H = 1000, 1414
FONT_SANS = "'Microsoft YaHei','Heiti SC','SimHei',Arial,sans-serif"
FONT_SERIF = "'Songti SC','SimSun','Times New Roman',serif"


def helix_path(cx, y_bottom, y_top, r_bottom, r_top, turns, n=420, front_only=None):
    """返回螺旋折线点列表；front_only 为 None 表示整条，True/False 只取前半/后半。"""
    pts = []
    total_angle = turns * 2 * math.pi
    for i in range(n + 1):
        t = i / n
        ang = total_angle * t
        r = r_bottom + (r_top - r_bottom) * t
        x = cx + r * math.cos(ang)
        y = y_bottom + (y_top - y_bottom) * t
        front = math.cos(ang) > 0          # 朝观察者的一半
        if front_only is None or front == front_only:
            pts.append((x, y, math.cos(ang)))
    return pts


def polyline(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)


def main():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" font-family="{FONT_SANS}">']
    # 背景
    o.append("""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0%" stop-color="#070b16"/>
    <stop offset="52%" stop-color="#0e1630"/>
    <stop offset="100%" stop-color="#1a1230"/>
  </linearGradient>
  <radialGradient id="glow" cx="66%" cy="32%" r="62%">
    <stop offset="0%" stop-color="#3f66b0" stop-opacity="0.42"/>
    <stop offset="55%" stop-color="#1c2a52" stop-opacity="0.12"/>
    <stop offset="100%" stop-color="#070b16" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glow2" cx="22%" cy="86%" r="55%">
    <stop offset="0%" stop-color="#b8862f" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="#070b16" stop-opacity="0"/>
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

    # 细点阵（数据感，右下淡出）
    o.append('<g fill="#9db8e0" opacity="0.10">')
    for gy in range(120, 1320, 44):
        for gx in range(60, 960, 44):
            # 越靠右下越亮
            k = (gx / W) * 0.5 + (gy / H) * 0.5
            if k > 0.45:
                o.append(f'<circle cx="{gx}" cy="{gy}" r="1.4"/>')
    o.append("</g>")

    # 螺旋（三轴上升）——整条平滑曲线 + 光晕 + 高光
    cx, yb, yt = 706, 1075, 470
    full = helix_path(cx, yb, yt, 176, 26, 4.6, front_only=None)
    d = polyline(full)
    o.append(f'<path d="{d}" fill="none" stroke="#b8862f" stroke-width="16" '
             f'stroke-linecap="round" stroke-linejoin="round" opacity="0.10"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#e8c36a" stroke-width="9" '
             f'stroke-linecap="round" stroke-linejoin="round" opacity="0.16"/>')
    o.append(f'<path d="{d}" fill="none" stroke="url(#gold)" stroke-width="5.4" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#fff6dc" stroke-width="1.4" '
             f'stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>')
    # 截面椭圆
    o.append('<g fill="none" stroke="#c94f4f" stroke-width="1.5" opacity="0.45">')
    for (cxx, cyy, rx, rot) in [(cx - 40, 980, 120, -16), (cx + 6, 800, 92, -16),
                                (cx + 22, 640, 62, -16)]:
        o.append(f'<ellipse cx="{cxx}" cy="{cyy}" rx="{rx}" ry="{rx*0.32:.0f}" '
                 f'transform="rotate({rot} {cxx} {cyy})"/>')
    o.append("</g>")
    # 节点
    for (nx, ny) in [(cx - 150, 990), (cx + 120, 860), (cx - 70, 700), (cx + 46, 545)]:
        o.append(f'<circle cx="{nx}" cy="{ny}" r="6" fill="#f0d894" opacity="0.95"/>')
        o.append(f'<circle cx="{nx}" cy="{ny}" r="14" fill="none" stroke="#e8c36a" '
                 f'stroke-width="1.2" opacity="0.5"/>')

    # 边框
    o.append(f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" '
             f'stroke="#e8c36a" stroke-width="1.2" opacity="0.28"/>')

    # 标题区
    o.append('<text x="82" y="210" font-size="15" letter-spacing="6" fill="#c8a24a" '
             'font-weight="600">ACADEMIC MONOGRAPH</text>')
    o.append(f'<text x="82" y="330" font-size="60" font-weight="800" fill="#f6f2e8" '
             f'letter-spacing="2">社会系统熵增螺旋</text>')
    o.append(f'<text x="82" y="408" font-size="60" font-weight="800" fill="#f6f2e8" '
             f'letter-spacing="8">与脆弱性诊断</text>')
    o.append('<rect x="82" y="446" width="300" height="2.6" fill="url(#rule)"/>')
    o.append(f'<text x="82" y="492" font-size="24" fill="#b9c6dd" letter-spacing="1">'
             f'从周期论破产到局部可描述性框架</text>')
    o.append('<text x="82" y="524" font-size="13.5" letter-spacing="2.6" fill="#7f8db0">'
             'FROM THE FAILURE OF CYCLES TO LOCAL DESCRIPTABILITY</text>')

    # 三轴芯片
    chips = [("Θ", "租佃份额"), ("I", "组织复杂度"), ("κ", "地缘耦合")]
    cxx = 82
    for sym, lab in chips:
        o.append(f'<rect x="{cxx}" y="560" width="{118 if lab.startswith("租") else 128}" '
                 f'height="38" rx="19" fill="#ffffff" opacity="0.06"/>')
        o.append(f'<text x="{cxx+18}" y="586" font-size="18" fill="#e8c36a" '
                 f'font-weight="700">{sym}</text>')
        o.append(f'<text x="{cxx+42}" y="586" font-size="15" fill="#c3cee2">{lab}</text>')
        cxx += 142

    # 页脚
    o.append(f'<rect x="82" y="1250" width="836" height="1" fill="#ffffff" opacity="0.14"/>')
    o.append(f'<text x="82" y="1310" font-size="30" font-weight="700" fill="#eef3fb" '
             f'letter-spacing="4">李毅芃　著</text>')
    o.append('<text x="82" y="1345" font-size="13.5" letter-spacing="3.4" fill="#7f8db0">'
             'LI YIPENG　·　2026</text>')
    o.append(f'<text x="{W-82}" y="1310" font-size="13.5" text-anchor="end" fill="#7f8db0" '
             f'letter-spacing="1.5">熵增螺旋 · 脆弱性 · 局部可描述性</text>')
    o.append(f'<text x="{W-82}" y="1345" font-size="13.5" text-anchor="end" fill="#5f6f92" '
             f'letter-spacing="1">ENTROPY SPIRAL · VULNERABILITY · LOCAL DESCRIPTABILITY</text>')

    o.append("</svg>\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
