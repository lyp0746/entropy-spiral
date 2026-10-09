# -*- coding: utf-8 -*-
"""
v_timeseries.py — 全球/美国锚定的脆弱性 V 的年度时间序列（2000—2024，真实数据）。

用第 7 章的式(7.1)(7.2)，把已有的真实序列组装为一个可追踪的 V(t)：
    Θ 代理 = 收入 Gini + 私人信贷/GDP + 政府债务/GDP 的合成（归一化）
    κ 代理 = 世界贸易/GDP（商品耦合）
    I 代理 = 美国政府最终消费支出/GDP（国家规模的粗略代理）
    ι 代理 = WGI 美国政治稳定（越高越一致）
各序列在 2000—2024 窗口内做 min–max 归一化。

输出：
    analysis/results/v_timeseries.json
    assets/svg/fig-v-timeseries.svg

用法：python analysis/v_timeseries.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "analysis", "results")
SVG = os.path.join(HERE, "assets", "svg")
os.makedirs(OUT, exist_ok=True)

BLUE, GREEN, RED, GOLD = "#3a6ea5", "#009E73", "#c94f4f", "#b8862f"

W = {"alpha": 0.30, "beta": 0.05, "gamma": 0.45, "lam": 0.20}
BETA_IOTA = 0.5
Y0, Y1 = 2000, 2024


def load_csv(name):
    d = {}
    with open(os.path.join(DATA, name), encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                d[int(float(row["year"]))] = float(row["value"])
            except (KeyError, ValueError):
                continue
    return d


def interp(d, years):
    """线性插值并对端点外推（ffill/bffill）。"""
    ks = sorted(d)
    out = {}
    for y in years:
        if y in d:
            out[y] = d[y]
            continue
        lo = max((k for k in ks if k < y), default=None)
        hi = min((k for k in ks if k > y), default=None)
        if lo is not None and hi is not None:
            out[y] = d[lo] + (d[hi] - d[lo]) * (y - lo) / (hi - lo)
        elif lo is not None:
            out[y] = d[lo]
        elif hi is not None:
            out[y] = d[hi]
    return out


def norm(d):
    vs = [v for v in d.values() if v is not None]
    lo, hi = min(vs), max(vs)
    return {k: (v - lo) / (hi - lo) if hi > lo else 0.0 for k, v in d.items()}


def main():
    years = list(range(Y0, Y1 + 1))
    inj = json.load(open(os.path.join(DATA, "injected.json"), encoding="utf-8"))
    pol = {int(k.split("_")[-1]): v for k, v in inj.items() if k.startswith("us_polstab_")}

    gini = norm(interp(load_csv("usa_gini.csv"), years))
    credit = norm(interp(load_csv("usa_private_credit_gdp.csv"), years))
    debt = norm(interp(load_csv("usa_gov_debt_gdp.csv"), years))
    trade = norm(interp(load_csv("world_trade_gdp.csv"), years))
    govexp = norm(interp(load_csv("us_govexpense_gdp.csv"), years))
    iota = norm(interp(pol, years))

    rows = []
    for y in years:
        Theta = (gini[y] + credit[y] + debt[y]) / 3.0
        I = govexp[y]
        kappa = trade[y]
        V = W["alpha"] * Theta + W["beta"] * I + W["gamma"] * kappa + W["lam"] * Theta * kappa
        Vi = V * (1 + BETA_IOTA * (1 - iota[y]))
        rows.append({"year": y, "Theta": round(Theta, 3), "I": round(I, 3),
                     "kappa": round(kappa, 3), "iota": round(iota[y], 3),
                     "V": round(V, 3), "V_iota": round(Vi, 3)})

    R = {"weights": W, "beta_iota": BETA_IOTA, "years": [Y0, Y1],
         "note": "真实序列（A/B 级）经 2000—2024 min–max 归一化后代入式(7.1)(7.2)；"
                 "κ 为世界贸易/GDP，Θ 为美国三项代理合成，I 为政府支出/GDP，ι 为美国政治稳定。",
         "rows": rows}
    with open(os.path.join(OUT, "v_timeseries.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)

    for y in (2000, 2008, 2015, 2020, 2022, 2024):
        r = next(x for x in rows if x["year"] == y)
        print(f"  {y}: Θ={r['Theta']:.2f} I={r['I']:.2f} κ={r['kappa']:.2f} "
              f"ι={r['iota']:.2f}  V={r['V']:.2f} V_ι={r['V_iota']:.2f}")
    draw_svg(rows)
    return R


def draw_svg(rows):
    Wd, Ht = 1000, 650
    x0, x1, y0, y1 = 110, 940, 90, 500
    vmax = max(r["V_iota"] for r in rows) * 1.15

    def X(y):
        return x0 + (y - Y0) / (Y1 - Y0) * (x1 - x0)

    def Yv(v):
        return y1 - v / vmax * (y1 - y0)

    def path(key):
        pts = [(X(r["year"]), Yv(r[key])) for r in rows]
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Ht}" '
         f'width="{Wd}" height="{Ht}" font-family="\'Microsoft YaHei\',\'SimHei\',sans-serif">',
         f'<rect width="{Wd}" height="{Ht}" fill="#ffffff"/>']
    o.append('<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">脆弱性 V 的年度轨迹（2000—2024，真实序列）</text>')
    o.append('<text x="500" y="66" font-size="14.5" fill="#666" text-anchor="middle">'
             'κ（世界贸易/GDP）主导长期上升；Θ 与 ι 决定短期波动与放大</text>')
    # 轴与网格
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    o.append(f'<line x1="{x0}" y1="{y0-10}" x2="{x0}" y2="{y1}" stroke="#333" stroke-width="1.3"/>')
    for y in range(2000, 2025, 4):
        o.append(f'<line x1="{X(y):.1f}" y1="{y1}" x2="{X(y):.1f}" y2="{y1+5}" stroke="#333"/>')
        o.append(f'<text x="{X(y):.1f}" y="{y1+24}" font-size="13.5" fill="#555" '
                 f'text-anchor="middle">{y}</text>')
    for v in [0, 0.25, 0.5, 0.75, 1.0, 1.25]:
        if v <= vmax:
            o.append(f'<line x1="{x0}" y1="{Yv(v):.1f}" x2="{x1}" y2="{Yv(v):.1f}" '
                     f'stroke="#eee"/>')
            o.append(f'<text x="{x0-10}" y="{Yv(v)+5:.1f}" font-size="13" fill="#888" '
                     f'text-anchor="end">{v:.2f}</text>')
    # 事件标记
    for yr, lab in [(2008, "金融危机"), (2020, "疫情"), (2022, "俄乌/加息")]:
        o.append(f'<line x1="{X(yr):.1f}" y1="{y0}" x2="{X(yr):.1f}" y2="{y1}" '
                 f'stroke="#ddd" stroke-dasharray="4 4"/>')
        o.append(f'<text x="{X(yr):.1f}" y="{y0-6}" font-size="12.5" fill="#999" '
                 f'text-anchor="middle">{lab}</text>')
    # 分量细线
    o.append(f'<path d="{path("kappa")}" fill="none" stroke="{GOLD}" stroke-width="1.6" '
             f'stroke-dasharray="7 5"/>')
    o.append(f'<path d="{path("Theta")}" fill="none" stroke="{GREEN}" stroke-width="1.6" '
             f'stroke-dasharray="3 4"/>')
    o.append(f'<path d="{path("iota")}" fill="none" stroke="#9db8e0" stroke-width="1.6" '
             f'stroke-dasharray="3 4"/>')
    # 主线
    o.append(f'<path d="{path("V_iota")}" fill="none" stroke="{RED}" stroke-width="3"/>')
    o.append(f'<path d="{path("V")}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    # 端点标注
    last = rows[-1]
    o.append(f'<text x="{X(Y1)+4:.1f}" y="{Yv(last["V_iota"])+5:.1f}" font-size="14" '
             f'font-weight="700" fill="{RED}">V_ι</text>')
    o.append(f'<text x="{X(Y1)+4:.1f}" y="{Yv(last["V"])+5:.1f}" font-size="14" '
             f'font-weight="700" fill="{BLUE}">V</text>')
    # 图例
    lg = [(BLUE, "V", ""), (RED, "V_ι", ""), (GOLD, "κ（贸易/GDP）", "dash"),
          (GREEN, "Θ（合成）", "dot"), ("#9db8e0", "ι（稳定）", "dot")]
    lx = 120
    for col, lab, style in lg:
        dash = "7 5" if style == "dash" else ("3 4" if style == "dot" else "none")
        o.append(f'<line x1="{lx}" y1="{y1+42}" x2="{lx+24}" y2="{y1+42}" stroke="{col}" '
                 f'stroke-width="3" stroke-dasharray="{dash}"/>')
        o.append(f'<text x="{lx+30}" y="{y1+47}" font-size="13.5" fill="#333">{lab}</text>')
        lx += 150
    o.append(f'<text x="{x0}" y="{y1+82}" font-size="12.5" fill="#888">'
             f'真实序列（A/B 级）在 2000—2024 窗口归一化；仅用于轨迹与结构，不作水平引用</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-v-timeseries.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-v-timeseries.svg")


if __name__ == "__main__":
    main()
