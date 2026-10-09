# -*- coding: utf-8 -*-
"""
make_figures.py — 生成方案 C 新增的矢量插图（SVG）。

产物（assets/svg/）：
  fig-cycle.svg        中国帝制政体存续时长的分布（Seshat，图 2.2）
  fig-bifurcation.svg  精英二分机制（图 4.2）
  fig-capture.svg      评价权 Φ 的俘获路径（图 4.3）

用法：python analysis/make_figures.py
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "assets", "svg")

SANS = "'Microsoft YaHei','SimHei',sans-serif"
BLUE, GREEN, RED, GOLD, GREY = "#3a6ea5", "#009E73", "#c94f4f", "#b8862f", "#666"


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{SANS}">\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ 图 2.2
def fig_cycle():
    d = json.load(open(os.path.join(HERE, "data", "seshat_cn_summary.json"), encoding="utf-8"))
    s = d["series"]
    W, H = 1000, 600
    x0, x1, y0, y1 = 150, 960, 70, 500
    yr_min, yr_max, du_max = -300, 1950, 300

    def X(yr):
        return x0 + (yr - yr_min) / (yr_max - yr_min) * (x1 - x0)

    def Y(du):
        return y1 - du / du_max * (y1 - y0)

    mean, sd = d["mean_duration"], d["sd_duration"]
    out = [head(W, H)]
    # ±1 SD 带 + 均值线
    out.append(f'<rect x="{x0}" y="{Y(mean+sd):.1f}" width="{x1-x0}" '
               f'height="{Y(mean-sd)-Y(mean+sd):.1f}" fill="#f0f4f9"/>')
    out.append(f'<line x1="{x0}" y1="{Y(mean):.1f}" x2="{x1}" y2="{Y(mean):.1f}" '
               f'stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="7 5"/>')
    out.append(f'<text x="{x0+8}" y="{Y(mean)-7:.1f}" font-size="16" fill="{BLUE}">'
               f'均值 {mean:.0f} 年</text>')
    out.append(f'<text x="{x1-8}" y="{Y(mean+sd)-7:.1f}" font-size="14" fill="#8a9bb0" '
               f'text-anchor="end">+1 SD（{mean+sd:.0f} 年）</text>')
    out.append(f'<text x="{x1-8}" y="{Y(mean-sd)+20:.1f}" font-size="14" fill="#8a9bb0" '
               f'text-anchor="end">−1 SD（{mean-sd:.0f} 年）</text>')
    # 坐标轴
    out.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    out.append(f'<line x1="{x0}" y1="{y0-10}" x2="{x0}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    for yr in range(-200, 1901, 200):
        out.append(f'<line x1="{X(yr):.1f}" y1="{y1}" x2="{X(yr):.1f}" y2="{y1+5}" stroke="#333"/>')
        out.append(f'<text x="{X(yr):.1f}" y="{y1+24}" font-size="14" fill="#555" '
                   f'text-anchor="middle">{yr if yr>=0 else -yr}{"公元" if yr>=0 else "前"}</text>')
    for du in (0, 100, 200, 300):
        out.append(f'<line x1="{x0-5}" y1="{Y(du):.1f}" x2="{x0}" y2="{Y(du):.1f}" stroke="#333"/>')
        out.append(f'<text x="{x0-10}" y="{Y(du)+5:.1f}" font-size="14" fill="#555" '
                   f'text-anchor="end">{du}</text>')
    out.append(f'<text x="24" y="285" font-size="16" fill="#333" '
               f'transform="rotate(-90 24 285)" text-anchor="middle">存续时长（年）</text>')
    out.append(f'<text x="{(x0+x1)/2:.0f}" y="{H-18}" font-size="16" fill="#333" '
               f'text-anchor="middle">政体起始年</text>')
    # 趋势线（斜率 −0.5 年/百年，近乎水平）
    sx = sum(p["start"] for p in s); sy = sum(p["duration"] for p in s); n = len(s)
    mx, my = sx / n, sy / n
    slope = sum((p["start"] - mx) * (p["duration"] - my) for p in s) / sum(
        (p["start"] - mx) ** 2 for p in s)
    b = my - slope * mx
    xa, xb = -200, 1850
    out.append(f'<line x1="{X(xa):.1f}" y1="{Y(slope*xa+b):.1f}" x2="{X(xb):.1f}" '
               f'y2="{Y(slope*xb+b):.1f}" stroke="{GOLD}" stroke-width="2" opacity="0.85"/>')
    # 数据点（个别标签错位避让）
    OFF = {"唐（后期）": (10, 26)}
    for p in s:
        x, y = X(p["start"]), Y(p["duration"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{RED}" '
                   f'stroke="#fff" stroke-width="1.2"/>')
        ox, oy = OFF.get(p["label"], (0, 0))
        out.append(f'<text x="{x+ox:.1f}" y="{y-10+oy:.1f}" font-size="14" fill="#333" '
                   f'text-anchor="middle">{esc(p["label"])}</text>')
    # 注释
    out.append(f'<text x="{x0+18}" y="{y0+16}" font-size="19" font-weight="700" fill="#1a1a1a">'
               f'帝制政体时长并无稳定“周期”</text>')
    out.append(f'<text x="{x0+18}" y="{y0+42}" font-size="15.5" fill="#444">'
               f'n = {n}，均值 {mean:.0f} 年，标准差 {sd:.0f} 年，变异系数 CV = {d["cv"]:.2f}</text>')
    out.append(f'<text x="{x0+18}" y="{y0+65}" font-size="15.5" fill="#444">'
               f'时长对起始年回归斜率 ≈ −0.5 年／百年（Spearman ρ = −0.14，不显著）</text>')
    out.append(f'<text x="{x0+18}" y="{y0+88}" font-size="15.5" fill="{GOLD}">'
               f'“周期加速”叙事未被数据支持；高方差本身即周期论的反证</text>')
    out.append("</svg>\n")
    open(os.path.join(SVG, "fig-cycle.svg"), "w", encoding="utf-8").write("".join(out))
    print("wrote assets/svg/fig-cycle.svg")


# ------------------------------------------------------------------ 图 4.2
def fig_bifurcation():
    W, H = 1000, 640
    o = [head(W, H)]
    o.append(f'<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             f'text-anchor="middle">精英二分：同一精英池的两条配置路径</text>')
    # 精英池
    o.append(f'<rect x="360" y="70" width="280" height="62" rx="10" fill="#eef3fb" stroke="#7fa0cc"/>')
    o.append(f'<text x="500" y="108" font-size="19" font-weight="700" fill="#1b3a63" '
             f'text-anchor="middle">精英池（受技术与制度约束）</text>')
    # 分流决策
    o.append('<line x1="500" y1="132" x2="500" y2="176" stroke="#333" stroke-width="2.4" marker-end="url(#ar)"/>')
    o.append(f'<rect x="330" y="176" width="340" height="52" rx="8" fill="#fbf7ee" stroke="#c9a06a"/>')
    o.append(f'<text x="500" y="198" font-size="16.5" fill="#6b3d12" text-anchor="middle">'
             f'相对收益比较：位置租 r ／ 生产回报 π</text>')
    o.append(f'<text x="500" y="218" font-size="14.5" fill="#8a6520" text-anchor="middle">'
             f'Θ↑（租佃份额上升）⇒ r/π ↑ ⇒ 分流右移</text>')
    # 两条支路
    o.append('<path d="M500,228 L500,252 L235,252 L235,286" stroke="#333" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
    o.append('<path d="M500,228 L500,252 L765,252 L765,286" stroke="#333" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
    # 左：生产性
    o.append(f'<rect x="80" y="286" width="310" height="150" rx="10" fill="#f3f9f5" stroke="{GREEN}"/>')
    o.append(f'<text x="235" y="316" font-size="18" font-weight="700" fill="#24502b" '
             f'text-anchor="middle">生产性精英</text>')
    for i, t in enumerate(["创新、组织生产、承担风险", "评价权来自可复现的产出", "产出扩大 ⇒ 税基扩大"]):
        o.append(f'<text x="235" y="{344+i*26}" font-size="15.5" fill="#3a4a60" '
                 f'text-anchor="middle">{t}</text>')
    o.append(f'<text x="235" y="424" font-size="16" font-weight="700" fill="{GREEN}" '
             f'text-anchor="middle">系统韧性 ↑</text>')
    # 右：寄生性
    o.append(f'<rect x="610" y="286" width="310" height="150" rx="10" fill="#fdf2f0" stroke="{RED}"/>')
    o.append(f'<text x="765" y="316" font-size="18" font-weight="700" fill="#7a2626" '
             f'text-anchor="middle">寄生性精英（租金型）</text>')
    for i, t in enumerate(["争夺位置租、俘获评价权 Φ", "评价权由自我授权/流量决定", "再分配挤压 ⇒ 生产被挤出"]):
        o.append(f'<text x="765" y="{344+i*26}" font-size="15.5" fill="#5a3a3a" '
                 f'text-anchor="middle">{t}</text>')
    o.append(f'<text x="765" y="424" font-size="16" font-weight="700" fill="{RED}" '
             f'text-anchor="middle">系统脆弱性 ↑</text>')
    # 汇聚到“压力释放失效”
    o.append('<path d="M235,436 L235,486 L500,486 L500,510" stroke="#333" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
    o.append('<path d="M765,436 L765,486 L500,486" stroke="#333" stroke-width="2.2" fill="none"/>')
    o.append(f'<rect x="330" y="510" width="340" height="52" rx="8" fill="#fff6ee" stroke="#D55E00"/>')
    o.append(f'<text x="500" y="542" font-size="16.5" font-weight="700" fill="#A83A00" '
             f'text-anchor="middle">压力释放失效 ⇒ 积累张力 ⇒ 阈值重置</text>')
    # 超稳定回环（走右上空白，避开右侧方框）
    o.append('<path d="M920,405 C 985,405 985,105 648,105" stroke="#b8862f" stroke-width="2.2" '
             'fill="none" stroke-dasharray="8 6" marker-end="url(#au)"/>')
    o.append(f'<text x="806" y="88" font-size="14.5" fill="#8a6520" text-anchor="middle">'
             f'重置只清状态，不改结构</text>')
    # markers
    o.insert(1, '<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker>'
                '<marker id="au" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#b8862f"/></marker></defs>')
    o.append("</svg>\n")
    open(os.path.join(SVG, "fig-bifurcation.svg"), "w", encoding="utf-8").write("".join(o))
    print("wrote assets/svg/fig-bifurcation.svg")


# ------------------------------------------------------------------ 图 4.3
def fig_capture():
    W, H = 1000, 660
    o = [head(W, H)]
    o.append(f'<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             f'text-anchor="middle">评价权 Φ 的俘获路径：五场域的共同结构</text>')
    # 中央环：Φ↑ → q↓
    o.append(f'<rect x="360" y="90" width="280" height="60" rx="10" fill="#eef3fb" stroke="#7fa0cc"/>')
    o.append(f'<text x="500" y="118" font-size="17" font-weight="700" fill="#1b3a63" '
             f'text-anchor="middle">评价权被俘获：Φ ↑</text>')
    o.append(f'<text x="500" y="140" font-size="14.5" fill="#3a4a60" text-anchor="middle">'
             f'选拔质量 q = q₀(1 − Φ) ↓ ⇒ 精英逆向选择</text>')
    o.append('<line x1="500" y1="150" x2="500" y2="196" stroke="#333" stroke-width="2.4" marker-end="url(#ar2)"/>')
    o.append(f'<rect x="330" y="196" width="340" height="56" rx="8" fill="#fdf2f0" stroke="{RED}"/>')
    o.append(f'<text x="500" y="222" font-size="16.5" font-weight="700" fill="#7a2626" '
             f'text-anchor="middle">中层传导失效：信息与制度不再纠错</text>')
    o.append(f'<text x="500" y="242" font-size="14.5" fill="#5a3a3a" text-anchor="middle">'
             f'压力无法被常规释放 ⇒ 第 2 章“高频分量”被放大</text>')
    # 旁路
    o.append('<path d="M330,224 C 200,224 200,560 500,586 C 800,560 800,224 670,224" '
             'stroke="' + GREEN + '" stroke-width="2.4" fill="none" stroke-dasharray="9 6" marker-end="url(#ag2)"/>')
    o.append(f'<text x="500" y="612" font-size="16" font-weight="700" fill="#24502b" '
             f'text-anchor="middle">旁路：恢复评价权的独立外部可检验性 ⇒ q 回升</text>')
    # 五个场域卡片
    domains = [
        ("学术", "同行评议\n期刊等级", "指标化、资助捆绑", "预注册／独立复现"),
        ("金融", "评级、基准利率", "评级付费、太大而不倒", "公共信用／反周期资本"),
        ("平台", "搜索排序、推荐", "流量租金、自我优待", "互操作／算法审计"),
        ("AI", "基准、算力与数据", "算力垄断、数据圈地", "公共算力／模型审计"),
        ("宗教", "正统解释权", "教产与政治庇护", "世俗化／多元解释"),
    ]
    cw, gap, x_start, ytop = 168, 18, 40, 286
    for i, (name, carrier, capture, bypass) in enumerate(domains):
        x = x_start + i * (cw + gap)
        o.append(f'<rect x="{x}" y="{ytop}" width="{cw}" height="230" rx="10" fill="#fafafa" stroke="#ccc"/>')
        o.append(f'<rect x="{x}" y="{ytop}" width="{cw}" height="38" rx="10" fill="#eef3fb" stroke="none"/>')
        o.append(f'<text x="{x+cw/2}" y="{ytop+26}" font-size="18" font-weight="700" '
                 f'fill="#1b3a63" text-anchor="middle">{name}</text>')
        o.append(f'<text x="{x+12}" y="{ytop+64}" font-size="12.5" fill="#888">评价权载体</text>')
        for j, line in enumerate(carrier.split("\n")):
            o.append(f'<text x="{x+12}" y="{ytop+86+j*19}" font-size="14" fill="#333">{line}</text>')
        o.append(f'<text x="{x+12}" y="{ytop+140}" font-size="12.5" fill="#a04848">俘获方式</text>')
        for j, line in enumerate(capture.split("／")):
            o.append(f'<text x="{x+12}" y="{ytop+162+j*19}" font-size="13.5" fill="#5a3a3a">{line}</text>')
        o.append(f'<text x="{x+12}" y="{ytop+214}" font-size="12.5" fill="#2f7a4f">旁路</text>')
        o.append(f'<text x="{x+12}" y="{ytop+236}" font-size="13" fill="#24502b">{bypass}</text>')
        # 连到中央
        o.append(f'<line x1="{x+cw/2}" y1="{ytop}" x2="{x+cw/2}" y2="{ytop-18}" stroke="#bbb" stroke-width="1.4"/>')
    o.insert(1, '<defs><marker id="ar2" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker>'
                '<marker id="ag2" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#009E73"/></marker></defs>')
    o.append("</svg>\n")
    open(os.path.join(SVG, "fig-capture.svg"), "w", encoding="utf-8").write("".join(o))
    print("wrote assets/svg/fig-capture.svg")


# ------------------------------------------------------------------ 图 8.2
def fig_debt_cases():
    """债务永续化的分国对照：r−g 与政治一致性 ι，气泡=政府债务/GDP。"""
    cases = [
        # 名称, r−g（%）, ι, 债务/GDP（%）, 颜色
        ("日本", -0.5, 0.80, 250, GREEN),
        ("美国", 0.5, 0.60, 122, RED),
        ("欧元区", 0.3, 0.65, 90, BLUE),
        ("中国", 0.8, 0.70, 120, GOLD),
        ("英国", 0.6, 0.68, 100, "#8a5fa8"),
    ]
    W, H = 1000, 620
    x0, x1, y0, y1 = 130, 940, 90, 520
    xmin, xmax, ymin, ymax = -1.0, 1.5, 0.50, 0.90

    def X(v):
        return x0 + (v - xmin) / (xmax - xmin) * (x1 - x0)

    def Y(v):
        return y1 - (v - ymin) / (ymax - ymin) * (y1 - y0)

    o = [head(W, H)]
    o.append(f'<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             f'text-anchor="middle">债务永续化的分国对照：利息—增长差与政治一致性</text>')
    o.append(f'<text x="500" y="66" font-size="14.5" fill="#666" text-anchor="middle">'
             f'气泡面积 ∝ 政府债务/GDP；右上 = 高利息差 + 低一致性，脆弱性最高</text>')
    # 象限底色
    o.append(f'<rect x="{X(0):.1f}" y="{Y(ymax):.1f}" width="{X(xmax)-X(0):.1f}" '
             f'height="{Y(0.7)-Y(ymax):.1f}" fill="#fdf6f4"/>')
    o.append(f'<rect x="{X(0):.1f}" y="{Y(0.7):.1f}" width="{X(xmax)-X(0):.1f}" '
             f'height="{Y(ymin)-Y(0.7):.1f}" fill="#fdf0ee"/>')
    o.append(f'<line x1="{X(0):.1f}" y1="{y0}" x2="{X(0):.1f}" y2="{y1}" stroke="#999" '
             f'stroke-dasharray="6 5"/>')
    o.append(f'<line x1="{x0}" y1="{Y(0.7):.1f}" x2="{x1}" y2="{Y(0.7):.1f}" stroke="#999" '
             f'stroke-dasharray="6 5"/>')
    # 坐标轴
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    o.append(f'<line x1="{x0}" y1="{y0-10}" x2="{x0}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    for v in (-1.0, -0.5, 0.0, 0.5, 1.0, 1.5):
        o.append(f'<text x="{X(v):.1f}" y="{y1+24}" font-size="14" fill="#555" '
                 f'text-anchor="middle">{v:+.1f}</text>')
    for v in (0.5, 0.6, 0.7, 0.8, 0.9):
        o.append(f'<text x="{x0-10}" y="{Y(v)+5:.1f}" font-size="14" fill="#555" '
                 f'text-anchor="end">{v:.1f}</text>')
    o.append(f'<text x="{(x0+x1)/2:.0f}" y="{H-18}" font-size="16" fill="#333" '
             f'text-anchor="middle">利息—增长差 r − g（百分点）</text>')
    o.append(f'<text x="30" y="{(y0+y1)/2:.0f}" font-size="16" fill="#333" '
             f'transform="rotate(-90 30 {(y0+y1)/2:.0f})" text-anchor="middle">政治一致性 ι</text>')
    # 象限注
    o.append(f'<text x="{X(0.05):.1f}" y="{Y(0.885):.1f}" font-size="14" fill="#2f7a4f">'
             f'r&lt;g：债务被增长/低利率吸收</text>')
    o.append(f'<text x="{X(0.05):.1f}" y="{Y(0.525):.1f}" font-size="14" fill="#a04848">'
             f'r&gt;g 且一致性低：脆弱性上升</text>')
    # 气泡
    for name, rg, iota, debt, col in cases:
        x, y = X(rg), Y(iota)
        r = 9 + debt / 250 * 26
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" '
                 f'fill-opacity="0.30" stroke="{col}" stroke-width="2"/>')
        o.append(f'<text x="{x:.1f}" y="{y+5:.1f}" font-size="14.5" font-weight="700" '
                 f'fill="#1a1a1a" text-anchor="middle">{name}</text>')
        o.append(f'<text x="{x:.1f}" y="{y+r+18:.1f}" font-size="12.5" fill="#666" '
                 f'text-anchor="middle">债务 {debt}%</text>')
    o.append(f'<text x="{x1}" y="{y1-16}" font-size="12.5" fill="#888" text-anchor="end">'
             f'指示性数据（质量 C），仅示结构，数值不可引用</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-debt-cases.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-debt-cases.svg")


# ------------------------------------------------------------------ 图 B.1
def fig_diagnostic_template():
    """五步诊断模板（附录 B.6）。"""
    W, H = 1000, 560
    o = [head(W, H)]
    o.append(f'<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             f'text-anchor="middle">脆弱性诊断五步模板</text>')
    o.append(f'<text x="500" y="66" font-size="14.5" fill="#666" text-anchor="middle">'
             f'每一步都必须能被独立检验；不可检验的步退回重做</text>')
    steps = [
        ("1. 界定系统与边界", "地理范围·承载流量\n替代路径", BLUE),
        ("2. 四维赋值并标等级", "Θ I κ ι\n逐项标 A/B/C", GOLD),
        ("3. 计算 V 与敏感性", "式(7.1)(7.2)\n扰动 γ、β", RED),
        ("4. 情景与监测信号", "3—5 个 if–then\n指标组合阈值", GREEN),
        ("5. 登记与复检", "时间戳条目\n到期核对", "#8a5fa8"),
    ]
    bw, gap, x0, y0 = 168, 22, 30, 140
    for i, (title, sub, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        o.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="150" rx="10" '
                 f'fill="#fafafa" stroke="{col}" stroke-width="1.8"/>')
        o.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="40" rx="10" fill="{col}" opacity="0.14"/>')
        o.append(f'<text x="{x+bw/2}" y="{y0+27}" font-size="15.5" font-weight="700" '
                 f'fill="{col}" text-anchor="middle">{title}</text>')
        for j, line in enumerate(sub.split("\n")):
            o.append(f'<text x="{x+bw/2}" y="{y0+72+j*24}" font-size="14" fill="#333" '
                     f'text-anchor="middle">{line}</text>')
        if i < len(steps) - 1:
            xa = x + bw
            o.append(f'<line x1="{xa+3}" y1="{y0+75}" x2="{xa+gap-3}" y2="{y0+75}" '
                     f'stroke="#333" stroke-width="2.2" marker-end="url(#dt)"/>')
    # 预登记强调
    o.append(f'<rect x="{x0+3*(bw+gap)}" y="{y0+170}" width="{bw}" height="44" rx="8" '
             f'fill="#fff6ee" stroke="#D55E00"/>')
    o.append(f'<text x="{x0+3*(bw+gap)+bw/2}" y="{y0+198}" font-size="13.5" font-weight="700" '
             f'fill="#A83A00" text-anchor="middle">阈值必须在看信号前登记</text>')
    # 反馈回路
    o.append('<path d="M950,360 C 985,360 985,480 500,480 C 15,480 15,360 50,360" '
             'stroke="#b8862f" stroke-width="2.2" fill="none" stroke-dasharray="8 6" '
             'marker-end="url(#dt2)"/>')
    o.append(f'<text x="500" y="505" font-size="14.5" fill="#8a6520" text-anchor="middle">'
             f'系统性偏离全部情景 ⇒ 修改框架（不是修改预测）</text>')
    o.append('<defs><marker id="dt" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker>'
             '<marker id="dt2" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#b8862f"/></marker></defs>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-diagnostic-template.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-diagnostic-template.svg")


# ------------------------------------------------------------------ 图 7.2
def fig_acceleration_matrix():
    """加速 × 脆弱性的诊断叉积（第 7.9 节）。"""
    W, H = 1000, 660
    o = [head(W, H)]
    o.append('<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">加速的形式与脆弱性的诊断叉积</text>')
    o.append('<text x="500" y="66" font-size="14.5" fill="#666" text-anchor="middle">'
             '行 = V 的趋势，列 = κ 的结构变化；单元格为典型形态。这是诊断参考，不是因果矩阵。</text>')
    cols = ["κ 上升（耦合加深）", "κ 不变（结构锁定）", "κ 下降（去耦合）"]
    rows = ["V 上升", "V 平稳", "V 下降"]
    cells = [
        [("典型红皇后", "AI 算力竞赛、军备竞赛", RED),
         ("度量反演", "投入加速但依赖不减（民国）", "#c98a4f"),
         ("脱钩阵痛期", "快速去耦合的转型成本", "#b8862f")],
        [("稳态耦合", "贸易稳定期，风险被制度吸收", BLUE),
         ("锁定均衡", "气候适应（分化路径）", "#6b8fbf"),
         ("有序收缩", "主动去耦合，缓冲充足", GREEN)],
        [("结构性矛盾", "少见：需 ι 大幅改善抵销 κ", "#9a5fb0"),
         ("自我修复", "衰退后的去杠杆与重置", GREEN),
         ("孤立失效", "封闭系统失去外部缓冲", "#7a8a9a")],
    ]
    x0, y0 = 190, 130
    cw, ch = 250, 156
    # 列头
    for j, c in enumerate(cols):
        o.append(f'<text x="{x0+j*cw+cw/2}" y="{y0-16}" font-size="15" font-weight="700" '
                 f'fill="#333" text-anchor="middle">{c}</text>')
    # 行头 + 单元格
    for i, r in enumerate(rows):
        yy = y0 + i * ch
        o.append(f'<text x="{x0-18}" y="{yy+ch/2}" font-size="16" font-weight="700" '
                 f'fill="#333" text-anchor="end">{r}</text>')
        for j in range(3):
            title, sub, col = cells[i][j]
            xx = x0 + j * cw
            o.append(f'<rect x="{xx+6}" y="{yy+6}" width="{cw-12}" height="{ch-12}" '
                     f'rx="10" fill="{col}" opacity="0.10"/>')
            o.append(f'<rect x="{xx+6}" y="{yy+6}" width="{cw-12}" height="{ch-12}" '
                     f'rx="10" fill="none" stroke="{col}" stroke-width="1.4" opacity="0.75"/>')
            o.append(f'<text x="{xx+cw/2}" y="{yy+58}" font-size="16.5" font-weight="700" '
                     f'fill="{col}" text-anchor="middle">{title}</text>')
            o.append(f'<text x="{xx+cw/2}" y="{yy+86}" font-size="13" fill="#444" '
                     f'text-anchor="middle">{sub}</text>')
    # 强调 AI 单元
    o.append(f'<rect x="{x0+6}" y="{y0+6}" width="{cw-12}" height="{ch-12}" rx="10" '
             f'fill="none" stroke="{RED}" stroke-width="3"/>')
    o.append(f'<text x="{x0+cw-18}" y="{y0+34}" font-size="12.5" font-weight="700" '
             f'fill="{RED}" text-anchor="end">红皇后成立</text>')
    o.append(f'<text x="{x0+cw+18}" y="{y0+34}" font-size="12.5" font-weight="700" '
             f'fill="#c98a4f" text-anchor="start">度量反演</text>')
    o.append(f'<text x="{x0}" y="{y0+3*ch+34}" font-size="13" fill="#777">'
             f'注：κ 上升不必然推高 V；当 ι 能快速调整或去耦合有序时，V 可平稳甚至下降。</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-acceleration-matrix.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-acceleration-matrix.svg")


# ------------------------------------------------------------------ 现代重绘：图 2.1 三层网络
def fig_layers_modern():
    W, H = 1000, 640
    o = [head(W, H)]
    o.append('<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">三层思维网络</text>')
    o.append('<text x="500" y="66" font-size="14" fill="#666" text-anchor="middle">'
             '底层地缘—人口 · 中层制度—信息 · 上层政治实体；实线为约束，虚线为反馈</text>')
    bands = [
        ("上层 · 政治实体与两种主义", "吸取—重置循环 · 压力 ψ = αG", "#3a6ea5", "#eef3fb", 96),
        ("中层 · 制度、文化与信息", "评价权 Φ · 选拔质量 q = q₀(1−Φ) · 技术棘轮", "#24502b", "#f3f9f5", 258),
        ("底层 · 地缘与人口分布", "地缘 Γ · 人口 n(x,t) · 承载力 K", "#6b3d12", "#fbf4ee", 420),
    ]
    for title, sub, col, bg, y in bands:
        o.append(f'<rect x="70" y="{y}" width="860" height="120" rx="14" fill="{bg}" '
                 f'stroke="{col}" stroke-width="1.5" opacity="0.95"/>')
        o.append(f'<circle cx="104" cy="{y+60}" r="12" fill="{col}" opacity="0.85"/>')
        o.append(f'<text x="130" y="{y+52}" font-size="20" font-weight="700" fill="{col}">{title}</text>')
        o.append(f'<text x="130" y="{y+82}" font-size="15" fill="#445">{sub}</text>')
        # 节点
        for k in range(5):
            nx = 620 + k * 58
            o.append(f'<circle cx="{nx}" cy="{y+60}" r="5" fill="{col}" opacity="0.5"/>')
    # 自下而上约束
    for (x, y1, y2) in [(430, 420, 378), (430, 258, 216)]:
        o.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#333" '
                 f'stroke-width="2.4" marker-end="url(#lm1)"/>')
    o.append('<text x="444" y="402" font-size="14" fill="#333">约束</text>')
    o.append('<text x="444" y="240" font-size="14" fill="#333">约束</text>')
    # 自上而下反馈
    for (x, y1, y2) in [(680, 216, 258), (680, 378, 420)]:
        o.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{GOLD}" '
                 f'stroke-width="2.2" stroke-dasharray="8 6" marker-end="url(#lm2)"/>')
    o.append('<text x="694" y="242" font-size="14" fill="#8a6520">重置改写底层</text>')
    o.append('<defs><marker id="lm1" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker>'
             '<marker id="lm2" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#b8862f"/></marker></defs>')
    o.append(f'<rect x="70" y="556" width="860" height="52" rx="10" fill="#fff8e8" stroke="#e0c58a"/>')
    o.append('<text x="90" y="588" font-size="15.5" fill="#6b3d12">关键设定：重置清除的是状态'
             '（α、G、ψ），不是边界（s、I、Φ）；因此同一个漩涡得以反复出现。</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-layers.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-layers.svg (modern)")


# ------------------------------------------------------------------ 现代重绘：图 3.1 螺旋
def fig_spiral_modern():
    import math
    W, H = 1000, 640
    o = [head(W, H)]
    # 坐标轴
    o.append('<g stroke="#aaa" stroke-width="1.4">')
    o.append('<line x1="140" y1="540" x2="140" y2="80"/>')
    o.append('<line x1="140" y1="540" x2="760" y2="540"/>')
    o.append('<line x1="140" y1="540" x2="70" y2="590"/>')
    o.append('</g>')
    o.append('<text x="120" y="74" font-size="15" fill="#666">时间 / κ ↑</text>')
    o.append('<text x="768" y="546" font-size="15" fill="#666">Θ ↑</text>')
    o.append('<text x="40" y="606" font-size="15" fill="#666">I（深度）</text>')
    # 螺旋
    pts = []
    cx, cy, R = 430, 330, 190
    n = 260
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * 3.3 * t
        r = R * (1 - 0.55 * t)
        x = cx + r * math.cos(ang)
        y = 540 - 460 * t + r * 0.18 * math.sin(ang)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="12" opacity="0.12" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="3.4" stroke-linecap="round"/>')
    # 截面椭圆
    for cyy, rx in [(470, 120), (330, 92), (200, 60)]:
        o.append(f'<ellipse cx="{cx}" cy="{cyy}" rx="{rx}" ry="{rx*0.3:.0f}" fill="none" '
                 f'stroke="{RED}" stroke-width="1.5" opacity="0.5"/>')
    o.append(f'<text x="{cx+140}" y="478" font-size="14.5" fill="#8a3030">截面振荡：局部看像“周期”</text>')
    o.append(f'<text x="{cx+120}" y="208" font-size="14.5" fill="#8a6520">轴向漂移：回不到原点</text>')
    # 右侧说明
    notes = [("周期", "回到原点，"), ("", "同一水平往复"),
             ("螺旋", "每圈都在更高处，"), ("", "永不回到原点")]
    o.append('<rect x="780" y="120" width="190" height="200" rx="12" fill="#fafafa" stroke="#ddd"/>')
    o.append('<text x="800" y="156" font-size="17" font-weight="700" fill="#333">为什么不是周期</text>')
    o.append('<text x="800" y="192" font-size="14.5" fill="#c94f4f">周期 = 回到原点</text>')
    o.append('<text x="800" y="218" font-size="14.5" fill="#333">同一水平往复</text>')
    o.append('<text x="800" y="256" font-size="14.5" fill="#b8862f">螺旋 = 回不到原点</text>')
    o.append('<text x="800" y="282" font-size="14.5" fill="#333">每圈都在更高处</text>')
    o.append('<text x="800" y="308" font-size="13" fill="#888">“后继周期更短”多为投影失真</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-spiral.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-spiral.svg (modern)")


# ------------------------------------------------------------------ 新增：图 6.2 κ 三通道
def fig_kappa_channels():
    W, H = 1000, 560
    o = [head(W, H)]
    o.append('<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">κ 的三条耦合通道</text>')
    o.append('<text x="500" y="66" font-size="14" fill="#666" text-anchor="middle">'
             '商品 · 金融 · 信息：通道不同，可逆性与传导速度不同</text>')
    lanes = [
        ("商品耦合", "贸易/GDP · 供应链", BLUE, [0.10, 0.22, 0.35, 0.52, 0.66, 0.74, 0.80], "慢、难逆"),
        ("金融耦合", "跨境头寸 · 资本流", RED, [0.20, 0.42, 0.60, 0.72, 0.66, 0.70, 0.78], "快、可逆"),
        ("信息耦合", "算力 · 数据 · 协议", GREEN, [0.05, 0.10, 0.20, 0.34, 0.55, 0.74, 0.92], "最快、最集中"),
    ]
    x0, x1 = 250, 760
    for i, (name, sub, col, vals, tag) in enumerate(lanes):
        y = 150 + i * 130
        o.append(f'<text x="80" y="{y-6}" font-size="17" font-weight="700" fill="{col}">{name}</text>')
        o.append(f'<text x="80" y="{y+18}" font-size="13" fill="#777">{sub}</text>')
        o.append(f'<line x1="{x0}" y1="{y+70}" x2="{x1}" y2="{y+70}" stroke="#eee"/>')
        pts = [(x0 + (x1 - x0) * k / (len(vals) - 1), y + 70 - v * 70) for k, v in enumerate(vals)]
        d = "M" + " L".join(f"{x:.1f},{yy:.1f}" for x, yy in pts)
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3"/>')
        for x, yy in pts:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="4" fill="{col}"/>')
        o.append(f'<rect x="{x1+16}" y="{y+40}" width="96" height="34" rx="17" fill="{col}" opacity="0.12"/>')
        o.append(f'<text x="{x1+64}" y="{y+62}" font-size="14" fill="{col}" font-weight="700" '
                 f'text-anchor="middle">{tag}</text>')
    o.append(f'<text x="{x0}" y="510" font-size="13" fill="#999">时间 →（示意图，非实测刻度）</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-kappa-channels.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-kappa-channels.svg")


# ------------------------------------------------------------------ 新增：图 3.2 反馈速度与纠错的不对称
def fig_feedback():
    W, H = 1000, 580
    o = [head(W, H)]
    o.append('<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">传播快、纠错慢：五类反馈通道</text>')
    o.append('<text x="500" y="66" font-size="14" fill="#666" text-anchor="middle">'
             '横轴为信号速度（对数示意），纵轴为纠错轮次（定性）</text>')
    x0, x1, y0, y1 = 140, 760, 100, 470

    def X(t):
        return x0 + t * (x1 - x0)

    def Y(v):
        return y1 - v * (y1 - y0)

    # 失配区（高速 + 低纠错）
    o.append(f'<rect x="{X(0.50):.0f}" y="{Y(0.40):.0f}" width="{x1-X(0.50):.0f}" '
             f'height="{y1-Y(0.40):.0f}" fill="#c94f4f" opacity="0.07"/>')
    o.append(f'<rect x="{X(0.50):.0f}" y="{Y(0.40):.0f}" width="{x1-X(0.50):.0f}" '
             f'height="{y1-Y(0.40):.0f}" fill="none" stroke="#c94f4f" '
             f'stroke-width="1.2" stroke-dasharray="6 5"/>')
    o.append(f'<text x="{X(0.99):.0f}" y="{Y(0.05):.0f}" font-size="13" fill="#c94f4f" '
             f'text-anchor="end">失配区：冲击已到、纠正未完成</text>')

    # 坐标轴
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.4"/>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x0}" y2="{y0}" stroke="#333" stroke-width="1.4"/>')
    o.append(f'<text x="{(x0+x1)/2:.0f}" y="{y1+42}" font-size="14" fill="#555" '
             f'text-anchor="middle">信号速度 →（快）</text>')
    o.append(f'<text x="{x0-14}" y="{(y0+y1)/2:.0f}" font-size="14" fill="#555" '
             f'transform="rotate(-90 {x0-14} {(y0+y1)/2:.0f})" text-anchor="middle">纠错轮次 →（多）</text>')

    pts = [
        ("政治", 0.08, 0.20, GOLD,  "选票·立法"),
        ("商品", 0.30, 0.25, BLUE,  "运价·库存"),
        ("技术", 0.55, 0.55, GREY,  "CVE·补丁"),
        ("金融", 0.78, 0.45, RED,   "利率·利差"),
        ("信息", 0.97, 0.85, GREEN, "数据·转发"),
    ]
    for name, t, v, col, sub in pts:
        cx, cy = X(t), Y(v)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{col}" opacity="0.9"/>')
        o.append(f'<text x="{cx:.1f}" y="{cy-18:.1f}" font-size="16" font-weight="700" '
                 f'fill="{col}" text-anchor="middle">{name}</text>')
        o.append(f'<text x="{cx:.1f}" y="{cy+26:.1f}" font-size="12" fill="#888" '
                 f'text-anchor="middle">{sub}</text>')

    o.append(f'<text x="{x0}" y="{y1+70}" font-size="13" fill="#555">'
             '传播速度由最快通道决定；纠错速度由最慢通道决定。二者之差即系统在失稳区暴露的时长。</text>')
    o.append(f'<text x="{x0}" y="{y1+92}" font-size="12" fill="#999">'
             '示意性（质量 C），非实测刻度；点位表示通道间的相对位置。</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-feedback.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-feedback.svg")


# ------------------------------------------------------------------ 新增：图 7.3 V 的构成
def fig_v_composition():
    W, H = 1000, 520
    o = [head(W, H)]
    o.append('<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">脆弱性 V 的构成与权重</text>')
    o.append('<text x="500" y="66" font-size="14" fill="#666" text-anchor="middle">'
             'V = α·Θ + β·I + γ·κ + λ·(Θ×κ)；权重 γ &gt; α &gt; λ &gt; β ≈ 0</text>')
    blocks = [("γ·κ", 0.45, RED, "耦合（主导）"), ("α·Θ", 0.30, BLUE, "租佃"),
              ("λ·Θκ", 0.20, GOLD, "交互"), ("β·I", 0.05, "#9db8e0", "复杂度（≈0）")]
    x = 80
    for lab, wgt, col, desc in blocks:
        wpx = 800 * wgt
        o.append(f'<rect x="{x:.1f}" y="170" width="{wpx:.1f}" height="90" rx="10" fill="{col}" '
                 f'opacity="0.85"/>')
        if wpx > 90:
            o.append(f'<text x="{x+wpx/2:.1f}" y="210" font-size="20" font-weight="700" '
                     f'fill="#fff" text-anchor="middle">{lab}</text>')
            o.append(f'<text x="{x+wpx/2:.1f}" y="236" font-size="13.5" fill="#fff" '
                     f'text-anchor="middle" opacity="0.9">{desc}</text>')
        else:
            o.append(f'<text x="{x+wpx/2:.1f}" y="150" font-size="14" fill="{col}" '
                     f'text-anchor="middle">{lab}</text>')
        o.append(f'<text x="{x+wpx/2:.1f}" y="285" font-size="13" fill="#888" '
                 f'text-anchor="middle">{wgt:.2f}</text>')
        x += wpx
    # 箭头到 V，再到 V_ι
    o.append(f'<line x1="480" y1="300" x2="480" y2="352" stroke="#333" stroke-width="2.4" marker-end="url(#vc)"/>')
    o.append(f'<circle cx="480" cy="392" r="40" fill="#1a1a1a"/>')
    o.append('<text x="480" y="400" font-size="22" font-weight="700" fill="#fff" text-anchor="middle">V</text>')
    o.append(f'<line x1="524" y1="392" x2="600" y2="392" stroke="#333" stroke-width="2.4" marker-end="url(#vc)"/>')
    o.append('<text x="562" y="380" font-size="13" fill="#666">×[1+0.5(1−ι)]</text>')
    o.append(f'<circle cx="650" cy="392" r="46" fill="none" stroke="{RED}" stroke-width="3"/>')
    o.append(f'<text x="650" y="400" font-size="20" font-weight="700" fill="{RED}" text-anchor="middle">V<tspan font-size="13">ι</tspan></text>')
    o.append('<text x="720" y="386" font-size="14" fill="#555">ι 越低，放大越强</text>')
    o.append('<text x="720" y="410" font-size="13" fill="#999">ι=1 → ×1.0；ι=0 → ×1.5</text>')
    o.append('<defs><marker id="vc" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-v-composition.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-v-composition.svg")


if __name__ == "__main__":
    fig_cycle()
    fig_bifurcation()
    fig_capture()
    fig_debt_cases()
    fig_diagnostic_template()
    fig_acceleration_matrix()
    fig_layers_modern()
    fig_spiral_modern()
    fig_kappa_channels()
    fig_feedback()
    fig_v_composition()
