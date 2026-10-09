# -*- coding: utf-8 -*-
"""
Θ（垄断/租佃份额）代理敏感性分析
构建《压力、熵增与社会螺旋》第二部分核心章（Θ 的六重代理系统）。

输出：
  analysis/results/theta_sensitivity.json
  assets/charts/theta_matrix.png

方法：
  1. 逐代理趋势（Spearman ρ、Theil–Sen 斜率、Mann–Kendall p）
  2. 现代合成指数 + 留一（leave-one-out）单调性
  3. 代理间相关矩阵（重叠年份线性插值）
  4. 2015 年转折点专项（美国财富/收入份额）
数据来源：世界银行 Gini（真实）；其余为公开来源的指示性序列，在图注中标明。
"""
import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "analysis", "results")
FIGS = os.path.join(BASE, "assets", "charts")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "purple": "#CC79A7", "sky": "#56B4E9",
      "grey": "#595959", "black": "#000000"}
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False, "font.size": 6.8, "axes.labelsize": 6.8,
    "axes.titlesize": 7.2, "xtick.labelsize": 6.2, "ytick.labelsize": 6.2,
    "legend.fontsize": 5.6, "axes.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 400, "savefig.dpi": 400, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03, "legend.frameon": False,
})


def panel(ax, letter):
    ax.text(-0.16, 1.05, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="bottom", ha="left")


# ---------------------------------------------------------- 真实数据：世界银行 Gini
def wb_gini(country_code):
    f = os.path.join(DATA, "API_SI.POV.GINI_DS2_en_csv_v2_457854.csv")
    df = pd.read_csv(f, skiprows=4)
    row = df[df["Country Code"] == country_code]
    if row.empty:
        return {}
    s = row.iloc[0, 5:].dropna()
    return {int(k): float(v) for k, v in s.items()}


# ---------------------------------------------------------- 代理序列
proxies = {}

# P1 盐铁专卖（历史，文献估计带的中值）
proxies["P1 盐铁专卖占比（中国，历史）"] = {
    -200: 0.40, -100: 0.42, 0: 0.45, 100: 0.45, 200: 0.45, 300: 0.45,
    500: 0.45, 600: 0.45, 700: 0.45, 800: 0.45, 900: 0.45, 1000: 0.45,
    1085: 0.11, 1328: 0.46, 1407: 0.12, 1577: 0.12, 1685: 0.085,
    1776: 0.085, 1840: 0.10, 1911: 0.10,
    "_note": "文献估计带中值；短期非单调，长时段重心不降",
}

# P2 收入不平等（真实：世界银行美国 Gini）
proxies["P2 收入不平等（美国 Gini，真实）"] = {**wb_gini("USA"),
                                             "_note": "World Bank SI.POV.GINI"}

# P2b 财富集中（美国前 1% 财富份额，Saez–Zucman / WID 近似）
proxies["P2b 财富集中（美国前1%份额）"] = {
    1980: 0.228, 1990: 0.279, 2000: 0.334, 2010: 0.348, 2015: 0.375,
    2020: 0.354, 2022: 0.349, "_note": "Saez–Zucman / WID 近似"}

# P3 金融利润份额（美国，近似）
proxies["P3 金融利润份额"] = {
    1980: 0.14, 1990: 0.18, 2000: 0.23, 2010: 0.27, 2020: 0.25,
    "_note": "BEA/行业统计近似"}

# P4 AI/科技垄断集中度
proxies["P4 AI/科技集中度"] = {
    2010: 0.05, 2015: 0.12, 2020: 0.32, 2024: 0.41, "_note": "公开数据近似"}

# P5 企业集中度（S&P 500 前十权重）
proxies["P5 企业集中度（S&P500前十）"] = {
    1980: 0.20, 1990: 0.21, 2000: 0.25, 2010: 0.30, 2020: 0.36, 2024: 0.375,
    "_note": "公开数据近似"}

# P6 债务/GDP（全球）
proxies["P6 债务/GDP（全球）"] = {
    1980: 1.50, 1990: 1.75, 2000: 2.00, 2010: 2.55, 2020: 3.20, 2024: 3.30,
    "_note": "IMF Global Debt Monitor 近似"}

# P7 价格—成本加成（补充）
proxies["P7 价格—成本加成（美国）"] = {
    1980: 1.18, 1990: 1.25, 2000: 1.40, 2010: 1.55, 2014: 1.61,
    "_note": "De Loecker–Eeckhout 型估计"}


def series(d):
    yrs = np.array(sorted(k for k in d if isinstance(k, int)), dtype=float)
    vals = np.array([d[int(y)] for y in yrs], dtype=float)
    return yrs, vals


# ---------------------------------------------------------- 1. 逐代理趋势
R = {"proxy_trends": {}}
for name, d in proxies.items():
    yrs, vals = series(d)
    if len(yrs) < 4:
        continue
    rho, p = stats.spearmanr(yrs, vals)
    slope = stats.theilslopes(vals, yrs)[0]
    tau, mk_p = stats.kendalltau(yrs, vals)
    R["proxy_trends"][name] = {
        "n": int(len(yrs)), "spearman_rho": float(rho), "p": float(p),
        "theil_sen_per_century": float(slope * 100), "mk_p": float(mk_p),
        "first_year": int(yrs[0]), "last_year": int(yrs[-1]),
        "first_val": float(vals[0]), "last_val": float(vals[-1]),
        "note": d.get("_note", ""),
    }

# ---------------------------------------------------------- 2. 现代合成 + 留一
modern_names = ["P2 收入不平等（美国 Gini，真实）", "P2b 财富集中（美国前1%份额）",
                "P3 金融利润份额", "P4 AI/科技集中度",
                "P5 企业集中度（S&P500前十）", "P6 债务/GDP（全球）"]


def z_series(name, grid):
    yrs, vals = series(proxies[name])
    z = (vals - vals.mean()) / (vals.std() + 1e-12)
    return np.interp(grid, yrs, z)


def composite_metrics(names, grid):
    Z = np.array([z_series(n, grid) for n in names])
    comp = Z.mean(axis=0)
    rho, p = stats.spearmanr(grid, comp)
    inc = np.mean(np.diff(comp) > 0)
    return {"rho": float(rho), "p": float(p), "pct_increasing": float(inc),
            "composite": comp.tolist(), "grid": grid.tolist()}


grid_short = np.arange(2010, 2025)      # 全六代理
grid_long = np.arange(1980, 2021)       # 五个长期代理
R["composite_short_2010_2024"] = composite_metrics(modern_names, grid_short)
R["composite_long_1980_2020"] = composite_metrics(
    [n for n in modern_names if n != "P4 AI/科技集中度"], grid_long)

# 留一：每次剔除一个代理，看合成是否仍单调上升
loo = {}
for i, name in enumerate(modern_names):
    sub = [n for j, n in enumerate(modern_names) if j != i]
    m = composite_metrics(sub, grid_short)
    loo[name] = {"rho": m["rho"], "pct_increasing": m["pct_increasing"]}
R["leave_one_out_short"] = loo

loo_long = {}
long_names = [n for n in modern_names if n != "P4 AI/科技集中度"]
for i, name in enumerate(long_names):
    sub = [n for j, n in enumerate(long_names) if j != i]
    m = composite_metrics(sub, grid_long)
    loo_long[name] = {"rho": m["rho"], "pct_increasing": m["pct_increasing"]}
R["leave_one_out_long"] = loo_long

# 仅用单一代理
single = {}
for name in modern_names:
    yrs, vals = series(proxies[name])
    rho, p = stats.spearmanr(yrs, vals)
    single[name] = {"rho": float(rho), "p": float(p)}
R["single_proxy"] = single

# ---------------------------------------------------------- 3. 相关矩阵
overlap_years = np.arange(1980, 2021)
mat_names = [n for n in long_names]
M = np.array([z_series(n, overlap_years) for n in mat_names])
C = np.corrcoef(M)
R["corr_matrix"] = {"names": mat_names, "years": "1980-2020",
                    "matrix": C.tolist()}

# ---------------------------------------------------------- 4. 2015 转折点
def breakpoint_analysis(vals, breaks):
    out = {}
    for b in breaks:
        pre = [v for y, v in vals if y < b]
        post = [v for y, v in vals if y >= b]
        if len(pre) >= 3 and len(post) >= 3:
            sp = stats.theilslopes(pre)[0]
            sq = stats.theilslopes(post)[0]
            out[str(b)] = {"slope_pre": float(sp), "slope_post": float(sq)}
    return out


g = wb_gini("USA")
R["breakpoint_us_gini"] = breakpoint_analysis(g.items(), [2000, 2010, 2015])
R["breakpoint_us_top1"] = breakpoint_analysis(
    [(k, v) for k, v in proxies["P2b 财富集中（美国前1%份额）"].items()
     if isinstance(k, int)], [2000, 2010, 2015])

# ---------------------------------------------------------- 图
fig = plt.figure(figsize=(7.2, 5.0), layout="constrained")
gs = gridspec.GridSpec(2, 3, figure=fig)

# (a) 代理轨迹（归一化）
ax = fig.add_subplot(gs[0, 0])
for name in modern_names:
    yrs, vals = series(proxies[name])
    z = (vals - vals.min()) / (vals.max() - vals.min() + 1e-12)
    ax.plot(yrs, z, "o-", ms=2.4, lw=1.0, label=name[:6])
ax.set_xlabel("年份"); ax.set_ylabel("归一化水平")
ax.set_title("六重代理（归一化）"); ax.legend(fontsize=4.6, loc="upper left")
panel(ax, "a")

# (b) 合成 + 留一
ax = fig.add_subplot(gs[0, 1])
for name in modern_names:
    sub = [n for n in modern_names if n != name]
    m = composite_metrics(sub, grid_short)
    ax.plot(m["grid"], m["composite"], lw=0.8, alpha=0.6)
ax.plot(R["composite_short_2010_2024"]["grid"],
        R["composite_short_2010_2024"]["composite"], color=OI["vermillion"], lw=1.8,
        label="全六代理")
ax.set_xlabel("年份"); ax.set_ylabel("合成 z 分数")
ax.set_title("留一：剔除任一代理"); ax.legend(fontsize=5.2)
panel(ax, "b")

# (c) 相关矩阵
ax = fig.add_subplot(gs[0, 2])
im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(mat_names)))
ax.set_yticks(range(len(mat_names)))
ax.set_xticklabels([n[:4] for n in mat_names], rotation=40, ha="right", fontsize=4.8)
ax.set_yticklabels([n[:4] for n in mat_names], fontsize=4.8)
for i in range(len(mat_names)):
    for j in range(len(mat_names)):
        ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", fontsize=4.2)
ax.set_title("代理相关矩阵（1980–2020）")
panel(ax, "c")

# (d) 单代理 vs 留一 rho
ax = fig.add_subplot(gs[1, 0])
names = modern_names
s_rho = [R["single_proxy"][n]["rho"] for n in names]
l_rho = [loo[n]["rho"] for n in names]
y = np.arange(len(names))
ax.barh(y - 0.2, s_rho, height=0.4, color=OI["blue"], label="仅用该代理")
ax.barh(y + 0.2, l_rho, height=0.4, color=OI["orange"], label="剔除该代理后的合成")
ax.set_yticks(y); ax.set_yticklabels([n[:6] for n in names], fontsize=5.0)
ax.axvline(0, color=OI["grey"], lw=0.6)
ax.set_xlabel("Spearman ρ（对年份）"); ax.set_title("敏感性矩阵"); ax.legend(fontsize=5.0)
panel(ax, "d")

# (e) 美国 Gini 与 top1% 财富
ax = fig.add_subplot(gs[1, 1])
yg = np.array(sorted(g)); vg = np.array([g[k] for k in yg])
ax.plot(yg, vg, color=OI["blue"], lw=1.3, label="美国 Gini（收入）")
yt = np.array(sorted(k for k in proxies["P2b 财富集中（美国前1%份额）"] if isinstance(k, int)))
vt = np.array([proxies["P2b 财富集中（美国前1%份额）"][k] for k in yt]) * 100
ax.plot(yt, vt, "s-", color=OI["vermillion"], lw=1.3, ms=3, label="美国前1%财富份额")
ax.axvline(2015, color=OI["grey"], ls=":", lw=0.9)
ax.text(2015, ax.get_ylim()[0] + 2, "2015", fontsize=5.2, color=OI["grey"])
ax.set_xlabel("年份"); ax.set_ylabel("%")
ax.set_title("2015 年转折?"); ax.legend(fontsize=5.0)
panel(ax, "e")

# (f) 趋势斜率
ax = fig.add_subplot(gs[1, 2])
sl = [R["proxy_trends"][n]["theil_sen_per_century"] for n in modern_names]
ax.barh(np.arange(len(modern_names)), sl, color=OI["green"])
ax.set_yticks(np.arange(len(modern_names)))
ax.set_yticklabels([n[:6] for n in modern_names], fontsize=5.0)
ax.axvline(0, color=OI["grey"], lw=0.6)
ax.set_xlabel("Theil–Sen 斜率／百年")
ax.set_title("趋势幅度差异大")
panel(ax, "f")

fig.savefig(os.path.join(FIGS, "theta_matrix.png"))
plt.close(fig)

with open(os.path.join(OUT, "theta_sensitivity.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("=== 逐代理趋势 ===")
for k, v in R["proxy_trends"].items():
    print(f"  {k}: n={v['n']} rho={v['spearman_rho']:+.2f} p={v['p']:.3f} "
          f"slope/century={v['theil_sen_per_century']:+.2f}")
print("=== 合成 ===")
print("  short(2010-24):", {k: round(R["composite_short_2010_2024"][k], 3)
      for k in ["rho", "p", "pct_increasing"]})
print("  long(1980-2020):", {k: round(R["composite_long_1980_2020"][k], 3)
      for k in ["rho", "p", "pct_increasing"]})
print("=== 留一（long）rho 范围 ===",
      round(min(v["rho"] for v in loo_long.values()), 3), "-",
      round(max(v["rho"] for v in loo_long.values()), 3))
print("=== 相关矩阵（下三角）===")
for i, n in enumerate(mat_names):
    print("  ", n[:8], [round(C[i, j], 2) for j in range(i)])
print("=== 2015 断点 ===")
print("  US Gini:", R["breakpoint_us_gini"])
print("  US top1:", R["breakpoint_us_top1"])
