# -*- coding: utf-8 -*-
"""
第6章支撑：地缘耦合 κ 的三个维度与合成指数（指示性构造，质量 C）。

注意：本机无网络，无法拉取 WTO/BIS/ITU 原始序列。以下数值为**指示性构造**，
仅用于说明方向与量级，不得作为实测数据引用。正式出版前须替换为：
  商品耦合：World Bank NE.TRD.GNFS.ZS / UN Comtrade
  金融耦合：BIS 跨境头寸 / IMF CPIS
  信息耦合：ITU 互联网普及率 / 平台集中度统计
输出：analysis/results/kappa.json, assets/charts/kappa.png
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BOOK, "analysis", "results")
FIGS = os.path.join(BOOK, "assets", "charts")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#595959", "black": "#000000"}
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False, "font.size": 6.8, "axes.labelsize": 6.8,
    "axes.titlesize": 7.2, "xtick.labelsize": 6.2, "ytick.labelsize": 6.2,
    "legend.fontsize": 5.4, "axes.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 400, "savefig.dpi": 400, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03, "legend.frameon": False,
})


def panel(ax, letter):
    ax.text(-0.16, 1.05, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="bottom", ha="left")


YEARS = np.array([1980, 1990, 2000, 2010, 2020, 2026])
DIMS = {
    "商品耦合": {
        "贸易开放度": [0.23, 0.26, 0.28, 0.30, 0.31, 0.315],
        "供应链集中度": [0.42, 0.60, 0.68, 0.85, 0.87, 0.89],
    },
    "金融耦合": {
        "跨境投资/GDP": [0.07, 0.12, 0.17, 0.25, 0.28, 0.30],
        "央行资产关联": [0.21, 0.38, 0.54, 0.78, 0.82, 0.84],
    },
    "信息耦合": {
        "互联网普及": [0.00, 0.01, 0.05, 0.30, 0.60, 0.66],
        "平台数据集中": [0.08, 0.18, 0.35, 0.72, 0.92, 0.95],
    },
}

R = {"years": YEARS.tolist(), "dims": {}, "note": "指示性构造，质量 C"}

# 合成 κ：各维度内指标等权归一后平均
dim_scores = {}
for dname, sub in DIMS.items():
    arrs = []
    for k, v in sub.items():
        v = np.array(v, float)
        arrs.append((v - v.min()) / (v.max() - v.min() + 1e-12))
    dim_scores[dname] = np.mean(arrs, axis=0)
    R["dims"][dname] = {"series": sub, "score": dim_scores[dname].tolist()}
kappa = np.mean(np.array(list(dim_scores.values())), axis=0)
R["kappa"] = kappa.tolist()
R["kappa_rho"] = float(stats.spearmanr(YEARS, kappa)[0])
# 增量（是否仍在加速）
d1 = np.diff(kappa)
R["increments"] = d1.tolist()
R["still_accelerating"] = bool(d1[-1] >= d1[-2])

# ------------------------------------------------------------- 图
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.3), layout="constrained")

ax = axes[0]
for (dname, s), col in zip(dim_scores.items(),
                           [OI["blue"], OI["green"], OI["purple"]]):
    ax.plot(YEARS, s, "o-", ms=2.6, lw=1.1, color=col, label=dname)
ax.set_xlabel("年份"); ax.set_ylabel("耦合度（归一）")
ax.set_title("三个维度的耦合"); ax.legend(loc="upper left")
panel(ax, "a")

ax = axes[1]
ax.plot(YEARS, kappa, "o-", color=OI["vermillion"], lw=1.6, ms=3.2)
ax.fill_between(YEARS, 0, kappa, color=OI["vermillion"], alpha=0.10, lw=0)
ax.set_ylim(0, 1); ax.set_xlabel("年份"); ax.set_ylabel("合成耦合指数 κ")
ax.set_title(f"κ 单调上升（ρ={R['kappa_rho']:.2f}）")
panel(ax, "b")

# Θ-I-κ 象限示意
ax = axes[2]
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.axhline(0.5, color=OI["grey"], lw=0.6, ls=":")
ax.axvline(0.5, color=OI["grey"], lw=0.6, ls=":")
pts = {"美国": (0.75, 0.82), "中国": (0.68, 0.71), "欧盟": (0.62, 0.88)}
for name, (x, y) in pts.items():
    ax.plot(x, y, "o", color=OI["vermillion"], ms=4)
    ax.text(x + 0.02, y, name, fontsize=5.6)
ax.set_xlabel("Θ（垄断份额）"); ax.set_ylabel("I / κ（复杂度与耦合）")
ax.set_title("当代系统集中于右上")
panel(ax, "c")

fig.savefig(os.path.join(FIGS, "kappa.png"))
plt.close(fig)

with open(os.path.join(OUT, "kappa.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("合成 κ:", [round(x, 3) for x in kappa])
print("κ 对年份 Spearman ρ:", round(R["kappa_rho"], 3))
print("增量:", [round(x, 3) for x in d1], "仍在加速:", R["still_accelerating"])
