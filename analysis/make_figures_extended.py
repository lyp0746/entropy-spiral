# -*- coding: utf-8 -*-
"""make_figures_extended.py — 扩展章节（第 11—14 章、附录 F/G）的矢量插图。

产物（assets/svg/）：
  fig-scenario-panel.svg        三情景的风险分解与时间窗口对照
  fig-time-hierarchy.svg        社会子系统的运行时间层级（对数尺度）
  fig-time-mismatch.svg         市场时间与政治时间的错位（甘特图）
  fig-multiscale-crisis.svg     五重危机的时间叠加
  fig-controllability.svg       可控性 C = T_policy / T_threat
  fig-controllability-space.svg 可控性空间：耦合 × 协调错配
  fig-coordination.svg          协调概率随可用时间与参与者数量的变化
  fig-i-redefine.svg            I 的三次失败尝试与真实身份
  fig-era-controllability.svg   十九至二十一世纪可控性的历史转变
  fig-policy-matrix.svg         六类冲击 × 政策选项的有效性矩阵

用法：python analysis/make_figures_extended.py
（本脚本为纯确定性绘图，不依赖外部数据文件。）
"""
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "assets", "svg")
SANS = "'Microsoft YaHei','SimHei',Arial,sans-serif"
SERIF = "'Times New Roman','Songti SC',serif"
BLUE, GREEN, GOLD, RED, GREY = "#3a6ea5", "#009E73", "#b8862f", "#c94f4f", "#666"
PURPLE = "#6a4c93"

os.makedirs(SVG, exist_ok=True)


def head(w, h, title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{SANS}">\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n')


def save(name, o):
    p = os.path.join(SVG, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("".join(o) + "</svg>\n")
    print("wrote assets/svg/" + name)


def cap(o, x, y, t, sub=None):
    o.append(f'<text x="{x}" y="{y}" font-size="21" font-weight="700" fill="#1a1a1a" '
             f'text-anchor="middle">{t}</text>')
    if sub:
        o.append(f'<text x="{x}" y="{y+24}" font-size="13.5" fill="#666" '
                 f'text-anchor="middle">{sub}</text>')


# ---------------------------------------------------------------------------
# 1. 三情景风险分解面板
# ---------------------------------------------------------------------------
def fig_scenario_panel():
    W, H = 1060, 620
    o = [head(W, H)]
    cap(o, W // 2, 44, "三个情景的适应能力分解与风险结果",
        "AdaptiveCapacity = ¼(Reserves + Substitutability + Diversification + Θ) × (1 − κ/5)")

    scenarios = [
        ("台湾芯片中断\n60 天", 0.7, 0.08, dict(res=0.10, sub=0.15, div=0.30, th=0.90, kap=3.5), 0.46, "±0.10", BLUE),
        ("东南亚债务\n72 小时", 0.6, 0.035, dict(res=0.20, sub=0.60, div=0.80, th=0.40, kap=3.5), 0.28, "±0.25", GOLD),
        ("全球债务\n同步", 0.6, 1.00, dict(res=0.05, sub=0.00, div=0.00, th=0.50, kap=5.0), 0.55, "±0.60", RED),
    ]
    labels = [("缓冲", BLUE), ("替代", GREEN), ("多元", GOLD), ("Θ 韧性", PURPLE), ("κ 惩罚", RED)]

    x0, cw, gap = 60, 300, 30
    bx, bw = 92, 30
    top, height = 160, 250

    for si, (name, haz, exp, f, risk, ci, col) in enumerate(scenarios):
        X = x0 + si * (cw + gap)
        o.append(f'<rect x="{X}" y="90" width="{cw}" height="{H-150}" rx="10" '
                 f'fill="{col}" opacity="0.045"/>')
        o.append(f'<rect x="{X}" y="90" width="{cw}" height="4" rx="2" fill="{col}"/>')
        o.append(f'<text x="{X+cw/2}" y="126" font-size="16" font-weight="700" fill="#222" '
                 f'text-anchor="middle">{name.splitlines()[0]}</text>')
        o.append(f'<text x="{X+cw/2}" y="147" font-size="13" fill="#777" '
                 f'text-anchor="middle">{name.splitlines()[1]}</text>')
        # 五个因素条形
        keys = ["res", "sub", "div", "th", "kap"]
        maxes = [1, 1, 1, 1, 5]
        for j, (k, mx) in enumerate(zip(keys, maxes)):
            yy = top + j * 46
            v = f[k] / mx
            o.append(f'<text x="{bx-10}" y="{yy+16}" font-size="13" fill="#555" '
                     f'text-anchor="end">{labels[j][0]}</text>')
            bxr = X + 92
            o.append(f'<rect x="{bxr}" y="{yy}" width="{200}" height="20" rx="4" fill="#eef1f6"/>')
            o.append(f'<rect x="{bxr}" y="{yy}" width="{v*200:.1f}" height="20" rx="4" '
                     f'fill="{labels[j][1]}" opacity="0.85"/>')
            val = f"{f[k]:.2f}" if k != "kap" else f"{f[k]:.1f}/5"
            o.append(f'<text x="{bxr+208}" y="{yy+15}" font-size="12.5" fill="#333">{val}</text>')
        # 风险结果
        o.append(f'<line x1="{X+20}" y1="430" x2="{X+cw-20}" y2="430" stroke="#ddd"/>')
        o.append(f'<text x="{X+24}" y="466" font-size="13" fill="#666">Risk(S)</text>')
        o.append(f'<text x="{X+cw-24}" y="472" font-size="34" font-weight="800" fill="{col}" '
                 f'text-anchor="end">{risk:.2f}</text>')
        o.append(f'<text x="{X+cw-24}" y="492" font-size="12" fill="#888" '
                 f'text-anchor="end">{ci}</text>')
        o.append(f'<text x="{X+24}" y="500" font-size="12" fill="#888">Hazard {haz:.1%}　'
                 f'Exposure {exp:.1%}</text>')
        tier = ["框架精确，可指导政策", "框架有用，可排序选项", "框架失效，需政治判断"][si]
        o.append(f'<text x="{X+cw/2}" y="536" font-size="13.5" font-weight="600" fill="{col}" '
                 f'text-anchor="middle">{tier}</text>')
    save("fig-scenario-panel.svg", o)


# ---------------------------------------------------------------------------
# 2. 子系统时间层级（对数）
# ---------------------------------------------------------------------------
def fig_time_hierarchy():
    W, H = 1060, 560
    o = [head(W, H)]
    cap(o, W // 2, 44, "社会子系统的运行时间层级",
        "横轴为对数尺度：从小时到数十年，各子系统的“最小决策／反馈时间”相差六个数量级")

    bands = [
        ("金融市场反应", 0.1, 1, RED),
        ("央行流动性操作", 2, 6, "#d97a3d"),
        ("政治协调（内阁／央行）", 24, 240, GOLD),
        ("国际谈判（G20／IMF）", 72, 672, GREEN),
        ("社会反馈（就业／舆论）", 168, 720, BLUE),
        ("财政政策执行", 720, 2160, PURPLE),
        ("社会心理恢复", 720, 4320, "#8a6fbf"),
        ("生态系统恢复", 43800, 438000, "#5b7f6a"),
    ]
    x0, x1 = 250, 990
    lo, hi = math.log10(0.08), math.log10(600000)

    def X(h):
        return x0 + (math.log10(h) - lo) / (hi - lo) * (x1 - x0)

    # 网格
    for h, lab in [(0.1, "6 min"), (1, "1 h"), (24, "1 d"), (168, "1 w"),
                   (720, "1 m"), (8760, "1 y"), (87600, "10 y")]:
        o.append(f'<line x1="{X(h):.1f}" y1="96" x2="{X(h):.1f}" y2="470" '
                 f'stroke="#ececec"/>')
        o.append(f'<text x="{X(h):.1f}" y="490" font-size="12" fill="#999" '
                 f'text-anchor="middle">{lab}</text>')
    o.append(f'<line x1="{x0}" y1="470" x2="{x1}" y2="470" stroke="#333" stroke-width="1.2"/>')

    for i, (name, a, b, col) in enumerate(bands):
        yy = 110 + i * 45
        o.append(f'<text x="{x0-14}" y="{yy+16}" font-size="13.5" fill="#333" '
                 f'text-anchor="end">{name}</text>')
        o.append(f'<rect x="{X(a):.1f}" y="{yy}" width="{X(b)-X(a):.1f}" height="22" rx="4" '
                 f'fill="{col}" opacity="0.8"/>')
    # 快慢分界
    xd = X(24)
    o.append(f'<line x1="{xd:.1f}" y1="96" x2="{xd:.1f}" y2="470" stroke="{RED}" '
             f'stroke-width="1.6" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{xd+6:.1f}" y="112" font-size="12.5" fill="{RED}">'
             f'“临界日”——市场已在数小时内定价</text>')
    o.append(f'<text x="{x0}" y="530" font-size="12" fill="#999">'
             f'注：区间为典型量级（示意，质量 C）。真正的脆弱性来自“快系统”与“慢系统”之间的错位，'
             f'而非任一系统的绝对速度。</text>')
    save("fig-time-hierarchy.svg", o)


# ---------------------------------------------------------------------------
# 3. 时间错位甘特图
# ---------------------------------------------------------------------------
def fig_time_mismatch():
    W, H = 1060, 520
    o = [head(W, H)]
    cap(o, W // 2, 44, "市场时间与政治时间的错位",
        "评级、定价与流动性枯竭发生在数小时内；可用的政治协调却在数日到数周之后")

    x0, x1 = 250, 990
    lo, hi = math.log10(0.5), math.log10(24 * 60)

    def X(h):
        return x0 + (math.log10(max(h, 0.5)) - lo) / (hi - lo) * (x1 - x0)

    rows = [
        ("评级下调", 0.5, 1, RED, "S&amp;P 单一决策"),
        ("市场定价完成", 2, 6, "#d97a3d", "利差跳升、赎回潮"),
        ("央行初步反应", 12, 24, GOLD, "口头干预／互换询价"),
        ("IMF 审议程序", 96, 168, GREEN, "执行董事会批准"),
        ("议会立法（财政规则暂停）", 672, 2160, PURPLE, "民主程序不可压缩"),
    ]
    # 黄金窗口
    o.append(f'<rect x="{X(0.5):.1f}" y="96" width="{X(48)-X(0.5):.1f}" height="368" '
             f'fill="{GREEN}" opacity="0.10"/>')
    o.append(f'<text x="{X(12):.1f}" y="112" font-size="12.5" fill="{GREEN}">'
             f'黄金窗口（24—48 小时）</text>')
    for h, lab in [(1, "1 h"), (6, "6 h"), (24, "1 d"), (168, "1 w"), (720, "1 m")]:
        o.append(f'<line x1="{X(h):.1f}" y1="96" x2="{X(h):.1f}" y2="470" stroke="#ececec"/>')
        o.append(f'<text x="{X(h):.1f}" y="490" font-size="12" fill="#999" '
                 f'text-anchor="middle">{lab}</text>')
    o.append(f'<line x1="{x0}" y1="470" x2="{x1}" y2="470" stroke="#333" stroke-width="1.2"/>')

    for i, (name, a, b, col, note) in enumerate(rows):
        yy = 120 + i * 66
        o.append(f'<text x="{x0-14}" y="{yy+18}" font-size="13.5" fill="#333" '
                 f'text-anchor="end">{name}</text>')
        o.append(f'<rect x="{X(a):.1f}" y="{yy}" width="{max(X(b)-X(a),4):.1f}" height="26" '
                 f'rx="5" fill="{col}" opacity="0.82"/>')
        o.append(f'<text x="{X(b)+10:.1f}" y="{yy+18}" font-size="12" fill="#777">{note}</text>')
    o.append(f'<text x="{x0}" y="508" font-size="12" fill="#999">'
             f'注：错位区间（约 24—168 小时）内，市场按最坏情况定价，而政治协调尚未完成——'
             f'这正是“事后补救”取代“事前预防”的机制。</text>')
    save("fig-time-mismatch.svg", o)


# ---------------------------------------------------------------------------
# 4. 五重危机的时间叠加
# ---------------------------------------------------------------------------
def fig_multiscale_crisis():
    W, H = 1060, 520
    o = [head(W, H)]
    cap(o, W // 2, 44, "五重危机的时间叠加与单一响应能力",
        "五条曲线各自的时间尺度不同，却要求同一组决策者在同一时刻做出取舍")

    x0, x1, y0, y1 = 110, 990, 110, 430
    days = list(range(0, 91))

    def X(d):
        return x0 + d / 90 * (x1 - x0)

    def Y(v):
        return y1 - v * (y1 - y0)

    curves = [
        ("金融流动性", RED, lambda d: math.exp(-((d - 3) / 6) ** 2)),
        ("企业债务违约", "#d97a3d", lambda d: math.exp(-((d - 14) / 12) ** 2)),
        ("失业上升", GOLD, lambda d: math.exp(-((d - 35) / 22) ** 2)),
        ("社会抗议", BLUE, lambda d: math.exp(-((d - 55) / 26) ** 2)),
        ("财政赤字压力", PURPLE, lambda d: math.exp(-((d - 75) / 30) ** 2)),
    ]
    for g in [0.25, 0.5, 0.75, 1.0]:
        o.append(f'<line x1="{x0}" y1="{Y(g):.1f}" x2="{x1}" y2="{Y(g):.1f}" stroke="#eee"/>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')
    for d in [0, 15, 30, 45, 60, 75, 90]:
        o.append(f'<text x="{X(d):.1f}" y="{y1+20}" font-size="12" fill="#999" '
                 f'text-anchor="middle">{d} 天</text>')
    for name, col, fn in curves:
        pts = [(X(d), Y(fn(d))) for d in days]
        o.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
                 f'" fill="none" stroke="{col}" stroke-width="2.6"/>')
    # 图例
    lx, ly = 130, 452
    for i, (name, col, _) in enumerate(curves):
        bxp = lx + (i % 3) * 300
        byp = ly + (i // 3) * 26
        o.append(f'<rect x="{bxp}" y="{byp-11}" width="20" height="5" rx="2" fill="{col}"/>')
        o.append(f'<text x="{bxp+28}" y="{byp-6}" font-size="13" fill="#444">{name}</text>')
    # 响应能力单线
    o.append(f'<line x1="{X(0):.1f}" y1="{Y(0.62):.1f}" x2="{X(90):.1f}" y2="{Y(0.62):.1f}" '
             f'stroke="{GREY}" stroke-width="2" stroke-dasharray="7 5"/>')
    o.append(f'<text x="{X(46):.1f}" y="{Y(0.62)-8:.1f}" font-size="12.5" fill="{GREY}" '
             f'text-anchor="middle">单一“执行能力”上限（同一组决策者）</text>')
    save("fig-multiscale-crisis.svg", o)


# ---------------------------------------------------------------------------
# 5. 可控性 C = T_policy / T_threat
# ---------------------------------------------------------------------------
def fig_controllability():
    W, H = 1060, 540
    o = [head(W, H)]
    cap(o, W // 2, 44, "可控性 C = T_policy / T_threat",
        "当政策执行时间超过威胁进展时间，C &lt; 1，系统进入“结构性不可控”区间")

    x0, x1, y0, y1 = 130, 990, 120, 430
    lo, hi = math.log10(0.05), math.log10(6)

    def X(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)

    for v, lab in [(0.05, "0.05"), (0.1, "0.1"), (0.5, "0.5"), (1, "1 临界"), (3, "3"), (6, "6")]:
        o.append(f'<line x1="{X(v):.1f}" y1="{y0}" x2="{X(v):.1f}" y2="{y1}" '
                 f'stroke="#eee"/>')
        o.append(f'<text x="{X(v):.1f}" y="{y1+20}" font-size="12" fill="#999" '
                 f'text-anchor="middle">{lab}</text>')
    # 不可控区
    o.append(f'<rect x="{x0}" y="{y0}" width="{X(1)-x0:.1f}" height="{y1-y0}" '
             f'fill="{RED}" opacity="0.07"/>')
    o.append(f'<line x1="{X(1):.1f}" y1="{y0}" x2="{X(1):.1f}" y2="{y1}" stroke="{RED}" '
             f'stroke-width="1.6" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{X(0.22):.1f}" y="{y0+24}" font-size="13" fill="{RED}" '
             f'text-anchor="middle">不可控区（C &lt; 1）</text>')
    o.append(f'<text x="{X(2.4):.1f}" y="{y0+24}" font-size="13" fill="{GREEN}" '
             f'text-anchor="middle">可控区（C &gt; 1）</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')

    items = [
        ("台湾芯片", 0.5, BLUE, "T_policy 30 天 / T_threat 60 天"),
        ("东南亚债务", 0.14, GOLD, "T_policy 7 天 / T_threat 50 小时"),
        ("全球债务", 0.04, RED, "T_policy 30 天 / T_threat 24 小时"),
    ]
    for i, (name, c, col, note) in enumerate(items):
        cx = X(c)
        yy = 200 + i * 82
        o.append(f'<circle cx="{cx:.1f}" cy="{yy}" r="11" fill="{col}"/>')
        o.append(f'<circle cx="{cx:.1f}" cy="{yy}" r="18" fill="none" stroke="{col}" '
                 f'opacity="0.4"/>')
        o.append(f'<text x="{cx:.1f}" y="{yy-26}" font-size="14.5" font-weight="700" '
                 f'fill="#222" text-anchor="middle">{name}</text>')
        o.append(f'<text x="{cx:.1f}" y="{yy+40}" font-size="12" fill="#666" '
                 f'text-anchor="middle">C = {c:g}</text>')
        o.append(f'<text x="{cx:.1f}" y="{yy+57}" font-size="11.5" fill="#999" '
                 f'text-anchor="middle">{note}</text>')
    o.append(f'<text x="{x0}" y="516" font-size="12" fill="#999">'
             f'注：C 为量级示意（质量 C）。它的价值不在精确值，而在提示“哪一类系统天然不可控”。</text>')
    save("fig-controllability.svg", o)


# ---------------------------------------------------------------------------
# 6. 可控性空间：耦合 × 协调错配
# ---------------------------------------------------------------------------
def fig_controllability_space():
    W, H = 1060, 600
    o = [head(W, H)]
    cap(o, W // 2, 44, "可控性空间：耦合度 × 协调错配",
        "越向右上，系统越接近“结构性不可控”；三个情景沿对角线依次失守")

    x0, x1, y0, y1 = 130, 960, 110, 500

    def X(k):
        return x0 + k / 5 * (x1 - x0)

    def Y(m):
        return y1 - m * (y1 - y0)

    # 背景梯度
    o.append(f'<defs><linearGradient id="ctrl" x1="0" y1="1" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="#009E73" stop-opacity="0.10"/>'
             f'<stop offset="55%" stop-color="#b8862f" stop-opacity="0.14"/>'
             f'<stop offset="100%" stop-color="#c94f4f" stop-opacity="0.22"/>'
             f'</linearGradient></defs>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="url(#ctrl)"/>')
    for k in range(0, 6):
        o.append(f'<line x1="{X(k):.1f}" y1="{y0}" x2="{X(k):.1f}" y2="{y1}" stroke="#fff" '
                 f'opacity="0.8"/>')
        o.append(f'<text x="{X(k):.1f}" y="{y1+20}" font-size="12" fill="#999" '
                 f'text-anchor="middle">{k}</text>')
    for m in [0, 0.25, 0.5, 0.75, 1.0]:
        o.append(f'<line x1="{x0}" y1="{Y(m):.1f}" x2="{x1}" y2="{Y(m):.1f}" stroke="#fff" '
                 f'opacity="0.8"/>')
        o.append(f'<text x="{x0-12}" y="{Y(m)+4:.1f}" font-size="12" fill="#999" '
                 f'text-anchor="end">{m:g}</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')
    o.append(f'<text x="{(x0+x1)/2:.0f}" y="{y1+44}" font-size="13.5" fill="#444" '
             f'text-anchor="middle">耦合度 κ（0—5）</text>')
    o.append(f'<text x="60" y="{(y0+y1)/2:.0f}" font-size="13.5" fill="#444" '
             f'transform="rotate(-90 60 {(y0+y1)/2:.0f})" text-anchor="middle">'
             f'协调错配 M = T_min / T_available</text>')

    pts = [("台湾芯片", 3.5, 0.35, BLUE), ("东南亚债务", 3.5, 0.60, GOLD),
           ("全球债务", 5.0, 0.95, RED)]
    for name, k, m, col in pts:
        cx, cy = X(k), Y(m)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="{col}"/>')
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="20" fill="none" stroke="{col}" '
                 f'opacity="0.4"/>')
        o.append(f'<text x="{cx-26:.1f}" y="{cy+5:.1f}" font-size="13.5" font-weight="600" '
                 f'fill="#222" text-anchor="end">{name}</text>')
    o.append(f'<path d="M{X(3.5):.1f},{Y(0.35):.1f} L{X(3.5):.1f},{Y(0.60):.1f} '
             f'L{X(5.0):.1f},{Y(0.95):.1f}" fill="none" stroke="#888" '
             f'stroke-dasharray="5 4" stroke-width="1.4"/>')
    o.append(f'<text x="{X(4.05):.1f}" y="{Y(0.74):.1f}" font-size="12.5" fill="#666" text-anchor="end">'
             f'失守方向：耦合上升 + 协调时间不足</text>')
    o.append(f'<text x="{x1-12}" y="{y1-16}" font-size="12.5" fill="{RED}" '
             f'text-anchor="end">结构性不可控区</text>')
    save("fig-controllability-space.svg", o)


# ---------------------------------------------------------------------------
# 7. 协调概率
# ---------------------------------------------------------------------------
def fig_coordination():
    W, H = 1060, 540
    o = [head(W, H)]
    cap(o, W // 2, 44, "协调概率随可用时间与参与者数量的变化",
        "P(协调 | T, N)：参与者越多、可用时间越短，达成一致的概率越接近零（示意模型）")

    x0, x1, y0, y1 = 130, 980, 110, 450

    def X(t):
        return x0 + t / 30 * (x1 - x0)

    def Y(p):
        return y1 - p * (y1 - y0)

    for g in [0.25, 0.5, 0.75, 1.0]:
        o.append(f'<line x1="{x0}" y1="{Y(g):.1f}" x2="{x1}" y2="{Y(g):.1f}" stroke="#eee"/>')
        o.append(f'<text x="{x0-12}" y="{Y(g)+4:.1f}" font-size="12" fill="#999" '
                 f'text-anchor="end">{g:.2f}</text>')
    for t in [0, 5, 10, 15, 20, 25, 30]:
        o.append(f'<text x="{X(t):.1f}" y="{y1+20}" font-size="12" fill="#999" '
                 f'text-anchor="middle">{t}</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#333" stroke-width="1.2"/>')
    o.append(f'<text x="{(x0+x1)/2:.0f}" y="{y1+44}" font-size="13.5" fill="#444" '
             f'text-anchor="middle">可用时间 T（天）</text>')
    o.append(f'<text x="60" y="{(y0+y1)/2:.0f}" font-size="13.5" fill="#444" '
             f'transform="rotate(-90 60 {(y0+y1)/2:.0f})" text-anchor="middle">'
             f'达成协调的概率 P</text>')

    curves = [("N = 2（双边互换）", 2, GREEN), ("N = 4", 4, BLUE),
              ("N = 6（G5 + IMF）", 6, GOLD), ("N = 10+（含议会）", 10, RED)]
    for name, N, col in curves:
        pts = []
        for i in range(0, 301):
            t = i / 10
            # 简化模型：协调需要的最小时间随 N 增长，成功概率随时间趋近 1
            Tmin = 0.35 * (N ** 1.35)
            p = 1 / (1 + math.exp(-(t - Tmin) / (0.35 * N)))
            pts.append((X(t), Y(p)))
        o.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
                 f'" fill="none" stroke="{col}" stroke-width="2.6"/>')
    lx = 150
    for i, (name, N, col) in enumerate(curves):
        o.append(f'<rect x="{lx+i*210}" y="470" width="20" height="5" rx="2" fill="{col}"/>')
        o.append(f'<text x="{lx+i*210+28}" y="476" font-size="12.5" fill="#444">{name}</text>')
    # 24 小时窗口
    o.append(f'<line x1="{X(1):.1f}" y1="{y0}" x2="{X(1):.1f}" y2="{y1}" stroke="{RED}" '
             f'stroke-width="1.5" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{X(1)+6:.1f}" y="{y0+20}" font-size="12.5" fill="{RED}">'
             f'危机窗口 ≈ 1 天</text>')
    o.append(f'<text x="{x0}" y="520" font-size="12" fill="#999">'
             f'注：曲线为示意模型（质量 C），仅用于说明“参与者增加 + 时间压缩”的双重压力。</text>')
    save("fig-coordination.svg", o)


# ---------------------------------------------------------------------------
# 8. I 的三次失败尝试
# ---------------------------------------------------------------------------
def fig_i_redefine():
    W, H = 1060, 560
    o = [head(W, H)]
    cap(o, W // 2, 44, "I 的三次操作化尝试与它的真实身份",
        "复杂度、信息处理、政治意愿都无法量化 I；它实际测度的是“政治制度下达成协调的最小时间”")

    boxes = [
        ("尝试一", "I = 组织复杂度", "层级数、机构数、协调节点数", "复杂组织反而更慢；简单组织也可能脆弱", BLUE),
        ("尝试二", "I = 信息处理能力", "带宽、算力、数据存量", "2008 年信息充足，协调仍然失败", GOLD),
        ("尝试三", "I = 政治意愿", "承诺指数、信用评级、政治稳定", "有意愿仍需时间，程序不可压缩", GREEN),
    ]
    bw, bh = 280, 150
    for i, (tag, title, metric, fail, col) in enumerate(boxes):
        X = 60 + i * 330
        o.append(f'<rect x="{X}" y="96" width="{bw}" height="{bh}" rx="10" fill="{col}" '
                 f'opacity="0.06" stroke="{col}" stroke-opacity="0.4"/>')
        o.append(f'<text x="{X+16}" y="124" font-size="12" font-weight="700" fill="{col}" '
                 f'letter-spacing="2">{tag}</text>')
        o.append(f'<text x="{X+16}" y="152" font-size="16" font-weight="700" fill="#1a1a1a">'
                 f'{title}</text>')
        o.append(f'<text x="{X+16}" y="180" font-size="12.5" fill="#555">量度：{metric}</text>')
        o.append(f'<text x="{X+16}" y="206" font-size="12.5" fill="{RED}">'
                 f'失败：{fail[:14]}</text>')
        o.append(f'<text x="{X+16}" y="226" font-size="12.5" fill="{RED}">{fail[14:]}</text>')
        if i < 2:
            o.append(f'<path d="M{X+bw+8},{96+bh/2} l22,0 m-8,-7 l8,7 l-8,7" fill="none" '
                     f'stroke="#bbb" stroke-width="2"/>')
    # 底部真实身份
    o.append(f'<path d="M530,262 L530,296" stroke="#888" stroke-width="2" '
             f'marker-end=""/>')
    o.append(f'<path d="M522,288 l8,10 l8,-10" fill="#888"/>')
    o.append(f'<rect x="200" y="300" width="660" height="150" rx="12" fill="{PURPLE}" '
             f'opacity="0.08" stroke="{PURPLE}" stroke-opacity="0.5"/>')
    o.append(f'<text x="530" y="336" font-size="15" font-weight="700" fill="{PURPLE}" '
             f'text-anchor="middle">I 的真实身份</text>')
    o.append(f'<text x="530" y="374" font-size="20" font-weight="800" fill="#1a1a1a" '
             f'text-anchor="middle">在给定政治制度下，达成必要协调的最小时间</text>')
    o.append(f'<text x="530" y="410" font-size="13.5" fill="#555" text-anchor="middle">'
             f'I = T_political(制度结构, 参与者数, 利益冲突强度)　——　政治变量，不是组织变量</text>')
    o.append(f'<text x="530" y="438" font-size="12.5" fill="#888" text-anchor="middle">'
             f'它的“不可测”不是数据缺失，而是制度时间与市场时间的矛盾本身</text>')
    save("fig-i-redefine.svg", o)


# ---------------------------------------------------------------------------
# 9. 历史时代可控性
# ---------------------------------------------------------------------------
def fig_era_controllability():
    W, H = 1060, 520
    o = [head(W, H)]
    cap(o, W // 2, 44, "十九至二十一世纪：威胁周期与应对时间的交叉",
        "威胁周期不断缩短（实线下降），应对时间却因协调阶数增加而延长（虚线上升），约在二十世纪末交叉")

    x0, x1, y0, y1 = 130, 980, 110, 430
    eras = ["19 世纪", "20 世纪中期", "20 世纪末", "21 世纪"]
    xs = [x0 + i * (x1 - x0) / 3 for i in range(4)]

    def X(i):
        return xs[i]

    def Y(v):
        return y1 - v * (y1 - y0)

    # 威胁周期（对数感受，逐渐缩短）
    threat = [0.62, 0.48, 0.30, 0.14]
    response = [0.22, 0.34, 0.50, 0.72]
    for g in [0.25, 0.5, 0.75]:
        o.append(f'<line x1="{x0-20}" y1="{Y(g):.1f}" x2="{x1}" y2="{Y(g):.1f}" stroke="#eee"/>')
    # 交叉点
    xcross = x0 + (x1 - x0) * 0.62
    o.append(f'<rect x="{x0-20}" y="{y0}" width="{xcross-(x0-20):.1f}" height="{y1-y0}" '
             f'fill="{GREEN}" opacity="0.05"/>')
    o.append(f'<rect x="{xcross:.1f}" y="{y0}" width="{x1-xcross:.1f}" height="{y1-y0}" '
             f'fill="{RED}" opacity="0.06"/>')
    o.append(f'<line x1="{xcross:.1f}" y1="{y0}" x2="{xcross:.1f}" y2="{y1}" stroke="{RED}" '
             f'stroke-width="1.5" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{xcross-8:.1f}" y="{y0+22}" font-size="12.5" fill="{GREEN}" '
             f'text-anchor="end">可控</text>')
    o.append(f'<text x="{xcross+8:.1f}" y="{y0+22}" font-size="12.5" fill="{RED}">不可控</text>')

    o.append('<path d="M' + " L".join(f"{X(i):.1f},{Y(threat[i]):.1f}" for i in range(4)) +
             f'" fill="none" stroke="{RED}" stroke-width="3" marker-end=""/>')
    o.append('<path d="M' + " L".join(f"{X(i):.1f},{Y(response[i]):.1f}" for i in range(4)) +
             f'" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    for i in range(4):
        o.append(f'<circle cx="{X(i):.1f}" cy="{Y(threat[i]):.1f}" r="6" fill="{RED}"/>')
        o.append(f'<circle cx="{X(i):.1f}" cy="{Y(response[i]):.1f}" r="6" fill="{BLUE}"/>')
    o.append(f'<text x="{X(0)+10:.1f}" y="{Y(threat[0])-14:.1f}" font-size="13" fill="{RED}">'
             f'威胁周期</text>')
    o.append(f'<text x="{X(3)-6:.1f}" y="{Y(response[3])-14:.1f}" font-size="13" fill="{BLUE}" '
             f'text-anchor="end">应对时间</text>')
    for i, e in enumerate(eras):
        o.append(f'<text x="{X(i):.1f}" y="{y1+24}" font-size="12.5" fill="#555" '
                 f'text-anchor="middle">{e}</text>')
    o.append(f'<text x="{x0-20}" y="496" font-size="12" fill="#999">'
             f'注：纵轴为“相对时间尺度”示意（质量 C）；交叉点的含义是“应对能力的增长慢于威胁节奏的加快”。</text>')
    save("fig-era-controllability.svg", o)


# ---------------------------------------------------------------------------
# 10. 政策矩阵热图
# ---------------------------------------------------------------------------
def fig_policy_matrix():
    W, H = 1060, 620
    o = [head(W, H)]
    cap(o, W // 2, 44, "冲击类型 × 政策选项：有效性矩阵",
        "深绿 = 首选；浅绿 = 次选；灰 = 无效；红 = 可能有害（示意，质量 C）")

    rows = ["产品冲击\n（芯片、石油）", "区域农业危机\n（出口禁令）", "金融冲击\n（融资枯竭）",
            "供应链断裂\n（物流中断）", "垄断滥用\n（趁机涨价）", "系统债务危机\n（全球同步）"]
    cols = ["战略库存", "多元化协议", "央行／IMF 协调", "产能疏散", "反垄断／增产", "价格管制", "资本管制"]
    # 0 无效, 1 次选, 2 首选, -1 有害
    M = [
        [2, 1, 0, 0, 0, -1, 0],
        [1, 2, 0, 0, 0, -1, 0],
        [1, 0, 2, 0, 0, 0, -1],
        [2, 1, 0, 2, 0, 0, 0],
        [2, 1, 0, 0, 2, -1, 0],
        [1, 0, 2, 0, 0, -1, 0],
    ]
    colors = {2: "#1f7a5c", 1: "#8fc7ad", 0: "#eceff3", -1: "#d98a8a"}
    labels = {2: "首选", 1: "次选", 0: "—", -1: "有害"}
    x0, y0, cw, ch = 230, 110, 108, 70
    for j, c in enumerate(cols):
        o.append(f'<text x="{x0+j*cw+cw/2}" y="{y0-12}" font-size="12.5" fill="#333" '
                 f'text-anchor="middle">{c}</text>')
    for i, r in enumerate(rows):
        for k, line in enumerate(r.split("\n")):
            o.append(f'<text x="{x0-14}" y="{y0+i*ch+ch/2-4+k*15}" font-size="12.5" '
                     f'fill="#333" text-anchor="end">{line}</text>')
        for j in range(len(cols)):
            v = M[i][j]
            o.append(f'<rect x="{x0+j*cw}" y="{y0+i*ch}" width="{cw-6}" height="{ch-6}" '
                     f'rx="5" fill="{colors[v]}"/>')
            o.append(f'<text x="{x0+j*cw+(cw-6)/2}" y="{y0+i*ch+ch/2+1}" font-size="12" '
                     f'fill="{"#fff" if v==2 else "#333"}" text-anchor="middle">{labels[v]}</text>')
    # 图例
    lx = 240
    for v in [2, 1, 0, -1]:
        o.append(f'<rect x="{lx}" y="560" width="26" height="16" rx="3" fill="{colors[v]}"/>')
        o.append(f'<text x="{lx+34}" y="573" font-size="12.5" fill="#444">{labels[v]}</text>')
        lx += 120
    o.append(f'<text x="{x0}" y="600" font-size="12" fill="#999">'
             f'注：有效性为方向性判断（质量 C）；现实中政策组合需结合国情，单一工具极少足够。</text>')
    save("fig-policy-matrix.svg", o)


# ---------------------------------------------------------------------------
# 11. 跨域的"变化尺度 vs 适应尺度"（第 15 章）
# ---------------------------------------------------------------------------
def fig_domain_mismatch():
    W, H = 1060, 600
    o = [head(W, H)]
    cap(o, W // 2, 44, "四个领域的“变化尺度”与“适应尺度”错位",
        "医疗、气候、心理、教育看似无关，却共享同一结构：应对所需时间远长于变化发生时间")

    # (领域, 变化尺度(天), 适应尺度(天), 标签变化, 标签适应)
    domains = [
        ("传染病", 3, 30, "疫情倍增（3 天）", "床位与物资扩充（约 30 天）"),
        ("气候", 4 * 365, 50 * 365, "政治激励周期（4 年）", "政策效果显现（约 50 年）"),
        ("精神健康", 1, 180, "社交媒体再创伤（约 1 天）", "治疗显著见效（约 6 个月）"),
        ("教育", 730, 1460, "技术知识陈旧（约 2 年）", "学位取得（约 4 年）"),
    ]
    x0, x1 = 250, 980
    lo, hi = math.log10(0.6), math.log10(40000)

    def X(d):
        return x0 + (math.log10(d) - lo) / (hi - lo) * (x1 - x0)

    for d, lab in [(1, "1 天"), (30, "1 月"), (365, "1 年"), (3650, "10 年"), (36500, "100 年")]:
        o.append(f'<line x1="{X(d):.1f}" y1="96" x2="{X(d):.1f}" y2="510" stroke="#ececec"/>')
        o.append(f'<text x="{X(d):.1f}" y="530" font-size="12" fill="#999" '
                 f'text-anchor="middle">{lab}</text>')
    o.append(f'<line x1="{x0}" y1="510" x2="{x1}" y2="510" stroke="#333" stroke-width="1.2"/>')

    for i, (name, tt, tr, lt, lr) in enumerate(domains):
        yy = 120 + i * 92
        o.append(f'<text x="{x0-16}" y="{yy+24}" font-size="15" font-weight="700" fill="#222" '
                 f'text-anchor="end">{name}</text>')
        # 变化尺度（红）
        o.append(f'<rect x="{X(0.6):.1f}" y="{yy}" width="{X(tt)-X(0.6):.1f}" height="24" rx="4" '
                 f'fill="{RED}" opacity="0.85"/>')
        o.append(f'<text x="{X(tt)+10:.1f}" y="{yy+17}" font-size="12" fill="{RED}">{lt}</text>')
        # 适应尺度（蓝）
        o.append(f'<rect x="{X(0.6):.1f}" y="{yy+30}" width="{X(tr)-X(0.6):.1f}" height="24" rx="4" '
                 f'fill="{BLUE}" opacity="0.85"/>')
        if X(tr) > 880:
            o.append(f'<text x="{X(tr)-10:.1f}" y="{yy+47}" font-size="12" fill="#ffffff" '
                     f'text-anchor="end">{lr}</text>')
        else:
            o.append(f'<text x="{X(tr)+10:.1f}" y="{yy+47}" font-size="12" fill="{BLUE}">{lr}</text>')
        # 连接缺口
        o.append(f'<line x1="{X(tt):.1f}" y1="{yy+24}" x2="{X(tr):.1f}" y2="{yy+30}" '
                 f'stroke="#999" stroke-width="1.2" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{x0}" y="566" font-size="12" fill="#999">'
             f'注：横轴为对数尺度（天）。四者的共同点是“适应尺度”远长于“变化尺度”；'
             f'这不是管理能力不足，而是时间结构的错配。</text>')
    save("fig-domain-mismatch.svg", o)


# ---------------------------------------------------------------------------
# 12. 制度类型 × 时间尺度（第 15 章）
# ---------------------------------------------------------------------------
def fig_institution_timescales():
    W, H = 1060, 520
    o = [head(W, H)]
    cap(o, W // 2, 44, "制度类型 × 时间尺度：优越性是相对的",
        "同一制度在不同时间尺度上优劣相反；不存在能同时优化所有尺度的制度")

    rows = ["专制中央集权", "民主自由制", "混合型"]
    cols = ["分钟级", "小时级", "天级", "周级", "年级", "十年级"]
    # 2 强, 1 中, 0 弱, -1 很差
    M = [
        [2, 2, 1, 0, -1, -1],
        [-1, 0, 0, 1, 2, 2],
        [0, 0, 1, 1, 1, 0],
    ]
    colors = {2: "#1f7a5c", 1: "#8fc7ad", 0: "#eceff3", -1: "#d98a8a"}
    labels = {2: "强", 1: "中", 0: "弱", -1: "差"}
    x0, y0, cw, ch = 220, 120, 128, 78
    for j, c in enumerate(cols):
        o.append(f'<text x="{x0+j*cw+cw/2}" y="{y0-12}" font-size="13" fill="#333" '
                 f'text-anchor="middle">{c}</text>')
    for i, r in enumerate(rows):
        o.append(f'<text x="{x0-14}" y="{y0+i*ch+ch/2+4}" font-size="14" fill="#333" '
                 f'text-anchor="end">{r}</text>')
        for j in range(len(cols)):
            v = M[i][j]
            o.append(f'<rect x="{x0+j*cw}" y="{y0+i*ch}" width="{cw-6}" height="{ch-6}" '
                     f'rx="5" fill="{colors[v]}"/>')
            o.append(f'<text x="{x0+j*cw+(cw-6)/2}" y="{y0+i*ch+ch/2+1}" font-size="13" '
                     f'fill="{"#fff" if v == 2 else "#333"}" text-anchor="middle">{labels[v]}</text>')
    o.append(f'<text x="{x0}" y="{y0+3*ch+40}" font-size="12" fill="#999">'
             f'注：为方向性判断（质量 C）。它同时解释了为什么“制度孰优”的争论在时间尺度不明确时永远无解。</text>')
    save("fig-institution-timescales.svg", o)


if __name__ == "__main__":
    fig_scenario_panel()
    fig_time_hierarchy()
    fig_time_mismatch()
    fig_multiscale_crisis()
    fig_controllability()
    fig_controllability_space()
    fig_coordination()
    fig_i_redefine()
    fig_era_controllability()
    fig_policy_matrix()
    fig_domain_mismatch()
    fig_institution_timescales()
    print("v6 figures done.")
