# -*- coding: utf-8 -*-
"""
第7章支撑：脆弱性指标 V 的权重敏感性与排序稳定性。

输入为**指示性**（质量 C）的 Θ、I、κ、ι 赋值，用于演示：
  1) 基础 V 与含 ι 调节的 V_ι
  2) 权重扰动（Dirichlet）下排序是否稳定
  3) β（I 权重）=0 / 0.10 / 0.20 时排序是否改变
  4) γ（κ 权重）在 [0.35,0.55] 内排序是否稳定

输出：analysis/results/v_framework.json, assets/charts/v_framework.png
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BOOK, "analysis", "results")
FIGS = os.path.join(BOOK, "assets", "charts")
os.makedirs(OUT, exist_ok=True)

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


# 指示性赋值（质量 C）：Θ 垄断份额；I 组织复杂度；κ 地缘耦合；ι 政治一致性
SYS = {
    "美国":   {"Theta": 0.75, "I": 0.82, "kappa": 0.82, "iota": 0.60},
    "欧盟":   {"Theta": 0.62, "I": 0.88, "kappa": 0.85, "iota": 0.65},
    "英国":   {"Theta": 0.63, "I": 0.72, "kappa": 0.78, "iota": 0.68},
    "中国":   {"Theta": 0.68, "I": 0.71, "kappa": 0.71, "iota": 0.70},
    "俄罗斯": {"Theta": 0.78, "I": 0.60, "kappa": 0.55, "iota": 0.45},
    "日本":   {"Theta": 0.55, "I": 0.65, "kappa": 0.70, "iota": 0.80},
    "印度":   {"Theta": 0.60, "I": 0.55, "kappa": 0.50, "iota": 0.55},
}
W = {"alpha": 0.30, "beta": 0.05, "gamma": 0.45, "lam": 0.20}
BETA_IOTA = 0.5


def V_base(s, w=W):
    return (w["alpha"] * s["Theta"] + w["beta"] * s["I"] + w["gamma"] * s["kappa"]
            + w["lam"] * s["Theta"] * s["kappa"])


def V_iota(s, w=W):
    return V_base(s, w) * (1 + BETA_IOTA * (1 - s["iota"]))


R = {"systems": {}, "weights_base": W, "note": "指示性赋值，质量 C"}

base = {k: V_base(v) for k, v in SYS.items()}
vI = {k: V_iota(v) for k, v in SYS.items()}
R["base"] = base
R["v_iota"] = vI
R["rank_base"] = sorted(base, key=lambda k: -base[k])
R["rank_iota"] = sorted(vI, key=lambda k: -vI[k])

# ---------------- 权重扰动排序稳定性（Dirichlet） ----------------
rng = np.random.default_rng(7)
names = list(SYS.keys())
top1 = {k: 0 for k in names}
top3 = {k: 0 for k in names}
N = 20000
for _ in range(N):
    w = rng.dirichlet([3, 1, 4.5, 2])  # 中心 ≈ (0.30,0.10,0.45,0.20)，偏向 γ
    w = {"alpha": w[0], "beta": w[1], "gamma": w[2], "lam": w[3]}
    v = {k: V_iota(s, w) for k, s in SYS.items()}
    order = sorted(v, key=lambda k: -v[k])
    top1[order[0]] += 1
    for k in order[:3]:
        top3[k] += 1
R["dirichlet_top1_prob"] = {k: top1[k] / N for k in names}
R["dirichlet_top3_prob"] = {k: top3[k] / N for k in names}

# ---------------- β（I 权重）检验 ----------------
beta_test = {}
for b in [0.0, 0.10, 0.20]:
    w = dict(W); w["beta"] = b
    # 保持总和为 1：从 gamma 中扣除
    w["gamma"] = 0.45 + (0.05 - b)
    v = {k: V_iota(s, w) for k, s in SYS.items()}
    beta_test[f"beta={b:.2f}"] = {"weights": w, "rank": sorted(v, key=lambda k: -v[k]),
                                  "V": {k: round(v[k], 3) for k in names}}
R["beta_test"] = beta_test

# ---------------- γ（κ 权重）范围 ----------------
gamma_test = {}
for g in [0.35, 0.45, 0.55]:
    w = dict(W); w["gamma"] = g; w["alpha"] = 1 - g - w["beta"] - w["lam"]
    v = {k: V_iota(s, w) for k, s in SYS.items()}
    gamma_test[f"gamma={g:.2f}"] = sorted(v, key=lambda k: -v[k])
R["gamma_test"] = gamma_test

# ---------------- 图 ----------------
fig = plt.figure(figsize=(7.2, 4.6), layout="constrained")
gs = gridspec.GridSpec(2, 3, figure=fig)

# (a) V_base 与 V_iota
ax = fig.add_subplot(gs[0, 0])
x = np.arange(len(names))
ax.bar(x - 0.2, [base[k] for k in names], width=0.4, color=OI["blue"], label="V 基础")
ax.bar(x + 0.2, [vI[k] for k in names], width=0.4, color=OI["vermillion"],
       label="V（含 ι 调节）")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=5.4)
ax.set_ylabel("脆弱性 V"); ax.set_title("三大系统及对照"); ax.legend(fontsize=5.0)
panel(ax, "a")

# (b) Dirichlet top1 概率
ax = fig.add_subplot(gs[0, 1])
p = [R["dirichlet_top1_prob"][k] for k in names]
ax.barh(np.arange(len(names)), p, color=OI["green"])
ax.set_yticks(np.arange(len(names))); ax.set_yticklabels(names, fontsize=5.4)
ax.set_xlabel("排名第一概率"); ax.set_title("权重扰动的排序稳定性")
panel(ax, "b")

# (c) β 检验
ax = fig.add_subplot(gs[0, 2])
for b, col in zip(["beta=0.00", "beta=0.10", "beta=0.20"],
                  [OI["blue"], OI["orange"], OI["vermillion"]]):
    ax.plot(np.arange(len(names)), [beta_test[b]["V"][k] for k in names],
            "o-", ms=2.4, lw=1.0, color=col, label=b)
ax.set_xticks(np.arange(len(names))); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=5.0)
ax.set_ylabel("V"); ax.set_title("β（I 权重）几乎不动排序"); ax.legend(fontsize=4.8)
panel(ax, "c")

# (d) γ 范围排序稳定性
ax = fig.add_subplot(gs[1, 0])
for g, col in zip(["gamma=0.35", "gamma=0.45", "gamma=0.55"],
                  [OI["blue"], OI["green"], OI["purple"]]):
    order = gamma_test[g]
    ax.plot(range(len(order)), [vI[k] for k in order], "o-", ms=2.4, lw=1.0,
            color=col, label=g)
ax.set_xticks(range(len(order))); ax.set_xticklabels(gamma_test["gamma=0.45"],
        rotation=30, ha="right", fontsize=5.0)
ax.set_ylabel("V"); ax.set_title("γ 在 0.35—0.55 内"); ax.legend(fontsize=4.8)
panel(ax, "d")

# (e) V 的时间动态示意
ax = fig.add_subplot(gs[1, 1])
t = np.linspace(0, 20, 200)
shock = 0.15 * np.exp(-((t - 8) ** 2) / 1.5)
theta = 0.008 * t
kappa = 0.004 * t
ax.plot(t, 0.5 + theta + kappa + shock, color=OI["vermillion"], lw=1.3, label="V(t)")
ax.plot(t, 0.5 + theta + kappa, color=OI["blue"], lw=1.0, ls="--", label="结构项")
ax.plot(t, 0.5 + theta + kappa - 0.1 * np.exp(-((t - 8) ** 2) / 8),
        color=OI["green"], lw=1.0, ls=":", label="含恢复")
ax.set_xlabel("时间（年）"); ax.set_ylabel("V")
ax.set_title("短期冲击 + 长期结构"); ax.legend(fontsize=4.8)
panel(ax, "e")

# (f) V vs FSI 示意
ax = fig.add_subplot(gs[1, 2])
fsi = {"叙利亚": 96, "委内瑞拉": 92, "俄罗斯": 78, "美国": 42,
       "中国": 55, "欧盟": 40, "新加坡": 22}
vmap = {"叙利亚": 0.88, "委内瑞拉": 0.79, "俄罗斯": 0.70, "美国": 0.68,
        "中国": 0.62, "欧盟": 0.64, "新加坡": 0.40}
ax.scatter(list(fsi.values()), [vmap[k] for k in fsi], s=12, color=OI["purple"], lw=0)
for k in fsi:
    ax.text(fsi[k] + 1, vmap[k], k, fontsize=4.8)
ax.set_xlabel("FSI（0—120）"); ax.set_ylabel("V（示意）")
ax.set_title("V 与 FSI 部分重合")
panel(ax, "f")

fig.savefig(os.path.join(FIGS, "v_framework.png"))
plt.close(fig)

with open(os.path.join(OUT, "v_framework.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("V 基础排序:", R["rank_base"])
print("V（含ι）排序:", R["rank_iota"])
print("top1 概率:", {k: round(v, 3) for k, v in R["dirichlet_top1_prob"].items()})
print("β 检验排序:", {k: v["rank"][:3] for k, v in R["beta_test"].items()})
print("γ 检验排序:", {k: v[:3] for k, v in R["gamma_test"].items()})
