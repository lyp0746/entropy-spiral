# -*- coding: utf-8 -*-
"""make_figures_domains.py — 附录 D 的矢量插图（粮食/能源跨域检验）。

产物：
  assets/svg/fig-food-trend.svg       粮食系统 V 的年度轨迹（2012—2024）
  assets/svg/fig-food-components.svg  八国 V 的三分量（加权）堆叠
"""
import csv
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "assets", "svg")
SANS = "'Microsoft YaHei','SimHei',sans-serif"
BLUE, GREEN, GOLD, RED, GREY = "#3a6ea5", "#009E73", "#b8862f", "#c94f4f", "#666"
W_T, W_I, W_K = 0.40, 0.35, 0.25


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{SANS}">\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n')


def load_food():
    rows = list(csv.DictReader(open(os.path.join(HERE, "analysis", "results", "food_v_panel.csv"),
                                    encoding="utf-8")))
    for r in rows:
        r["Year"] = int(r["Year"])
        for k in ("Theta_n", "I_n", "Kappa_n", "V_food"):
            r[k] = float(r[k]) if r[k] not in ("", "nan") else None
    return rows


def fig_trend(rows):
    years = list(range(2012, 2025))
    yv = {}
    for y in years:
        vals = [r["V_food"] for r in rows if r["Year"] == y and r["V_food"] is not None]
        if vals:
            yv[y] = sum(vals) / len(vals)
    W, H = 1000, 520
    o = [head(W, H)]
    o.append('<text x="500" y="42" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">粮食系统脆弱性 V 的年度轨迹</text>')
    o.append('<text x="500" y="66" font-size="14" fill="#666" text-anchor="middle">'
             '八国等权平均（FAOSTAT；V = 0.40Θ + 0.35I + 0.25κ，域特异权重）</text>')
    x0, x1, y0, y1 = 120, 940, 110, 440
    lo, hi = 0.25, 0.42

    def X(y):
        return x0 + (y - years[0]) / (years[-1] - years[0]) * (x1 - x0)

    def Y(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)

    for g in [0.25, 0.30, 0.35, 0.40]:
        o.append(f'<line x1="{x0}" y1="{Y(g):.0f}" x2="{x1}" y2="{Y(g):.0f}" stroke="#eee"/>')
        o.append(f'<text x="{x0-8}" y="{Y(g)+4:.0f}" font-size="12" fill="#999" text-anchor="end">{g:.2f}</text>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    pts = [(X(y), Y(v)) for y, v in yv.items()]
    o.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
             f'" fill="none" stroke="{GREEN}" stroke-width="3"/>')
    for (a, b), y in zip(pts, yv):
        o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4.5" fill="{GREEN}"/>')
        if y in (2012, 2021, 2024):
            o.append(f'<text x="{a:.1f}" y="{b-12:.1f}" font-size="12" fill="#333" '
                     f'text-anchor="middle">{yv[y]:.3f}</text>')
    o.append(f'<text x="{X(2021):.0f}" y="{Y(0.405)-28:.0f}" font-size="13" fill="{RED}" '
             f'text-anchor="middle">2021 峰值</text>')
    for y in years:
        o.append(f'<text x="{X(y):.1f}" y="{y1+20:.0f}" font-size="12" fill="#555" '
                 f'text-anchor="middle">{y}</text>')
    o.append(f'<text x="{x0}" y="{y1+52}" font-size="12" fill="#999">'
             '2010—2011 因滚动窗口不足未计入。示意性结果（质量 C），排序不作为结论。</text>')
    o.append("</svg>\n")
    open(os.path.join(SVG, "fig-food-trend.svg"), "w", encoding="utf-8").write("".join(o))
    print("wrote assets/svg/fig-food-trend.svg")


def fig_components(rows):
    comp = {}
    for r in rows:
        if r["Year"] < 2012 or r["V_food"] is None:
            continue
        c = comp.setdefault(r["Country"], {"t": [], "i": [], "k": []})
        c["t"].append(r["Theta_n"]); c["i"].append(r["I_n"]); c["k"].append(r["Kappa_n"])
    data = []
    for cn, v in comp.items():
        t = W_T * sum(v["t"]) / len(v["t"])
        i = W_I * sum(v["i"]) / len(v["i"])
        k = W_K * sum(v["k"]) / len(v["k"])
        data.append((cn, t, i, k, t + i + k))
    data.sort(key=lambda x: -x[4])

    W, H = 1000, 560
    o = [head(W, H)]
    o.append('<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">粮食系统 V 的分量构成（八国）</text>')
    o.append('<text x="500" y="64" font-size="14" fill="#666" text-anchor="middle">'
             '色块为加权分量：蓝=0.40Θ（产量集中）· 绿=0.35I（波动）· 金=0.25κ（进口依赖）</text>')
    x0, bw, gap = 150, 62, 52
    y1, scale = 470, 470
    for g in [0.2, 0.4, 0.6]:
        yy = y1 - g * scale
        o.append(f'<line x1="{x0-10}" y1="{yy:.0f}" x2="940" y2="{yy:.0f}" stroke="#eee"/>')
        o.append(f'<text x="{x0-18}" y="{yy+4:.0f}" font-size="12" fill="#999" text-anchor="end">{g:.1f}</text>')
    for idx, (cn, t, i, k, tot) in enumerate(data):
        x = x0 + idx * (bw + gap)
        yt = y1 - t * scale
        yi = yt - i * scale
        o.append(f'<rect x="{x}" y="{yt:.1f}" width="{bw}" height="{t*scale:.1f}" fill="{BLUE}"/>')
        o.append(f'<rect x="{x}" y="{yi:.1f}" width="{bw}" height="{i*scale:.1f}" fill="{GREEN}"/>')
        o.append(f'<rect x="{x}" y="{y1-k*scale:.1f}" width="{bw}" height="{k*scale:.1f}" fill="{GOLD}"/>')
        o.append(f'<text x="{x+bw/2:.0f}" y="{y1-tot*scale-8:.0f}" font-size="13" fill="#222" '
                 f'text-anchor="middle" font-weight="700">{tot:.3f}</text>')
        o.append(f'<text x="{x+bw/2:.0f}" y="{y1+20:.0f}" font-size="12" fill="#555" '
                 f'text-anchor="middle">{cn}</text>')
    o.append(f'<text x="{x0}" y="520" font-size="12" fill="#999">'
             '注：Θ 为作物 HHI，将“稻米单一化”的出口国排名抬高；排序仅为探索性（质量 C）。</text>')
    o.append("</svg>\n")
    open(os.path.join(SVG, "fig-food-components.svg"), "w", encoding="utf-8").write("".join(o))
    print("wrote assets/svg/fig-food-components.svg")


if __name__ == "__main__":
    rows = load_food()
    fig_trend(rows)
    fig_components(rows)
