# -*- coding: utf-8 -*-
"""
v_framework_real.py — 用真实 World Bank 数据重塑第7章 V 框架。

真实分量（质量 A）：
  Θ 代理 = 收入 Gini + 私人信贷/GDP + 政府债务/GDP 的合成（越高=租佃越重）
  κ 代理 = 贸易开放度（贸易/GDP，商品耦合）
  I 代理 = 政府最终消费支出/GDP（国家规模的粗略代理；β≈0，影响很小）
定性分量（质量 C，需 V-Dem 补齐）：
  ι = 政治一致性（本书定性赋值）
缺失值用可得系统的中位数填补，并逐条记录。

输出：analysis/results/v_framework_real.json, assets/charts/v_real.png
"""
import json
import os
import urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
OUT = os.path.join(BOOK, "analysis", "results")
FIGS = os.path.join(BOOK, "assets", "charts")

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
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#595959"}


def panel(ax, l):
    ax.text(-0.16, 1.05, l, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="bottom", ha="left")


COUNTRIES = {"US": "美国", "CN": "中国", "RU": "俄罗斯", "IN": "印度",
             "JP": "日本", "GB": "英国", "EUU": "欧盟"}
INDS = {"gini": "SI.POV.GINI", "trade": "NE.TRD.GNFS.ZS",
        "credit": "FS.AST.PRVT.GD.ZS", "debt": "GC.DOD.TOTL.GD.ZS",
        "govexp": "NE.CON.GOV.ZS"}
# ι 为定性输入（无 WB 序列），须由 V-Dem 补齐
IOTA = {"美国": 0.60, "中国": 0.70, "俄罗斯": 0.45, "印度": 0.55,
        "日本": 0.80, "英国": 0.68, "欧盟": 0.65}


def latest(c, ind):
    u = (f"https://api.worldbank.org/v2/country/{c}/indicator/{ind}"
         f"?format=json&per_page=100&date=2015:2024")
    try:
        d = json.load(urllib.request.urlopen(u, timeout=20))
        rows = [(r["date"], r["value"]) for r in d[1] if r["value"] is not None]
        rows.sort()
        return float(rows[-1][1]) if rows else None
    except Exception:
        return None


raw = {}
print("fetching ...")
for c, name in COUNTRIES.items():
    raw[name] = {k: latest(c, i) for k, i in INDS.items()}
    print(f"  {name}: {raw[name]}")

# 缺失值：用可得系统中位数填补
imputed = {}
for k in INDS:
    vals = [raw[n][k] for n in COUNTRIES.values() if raw[n][k] is not None]
    med = float(np.median(vals)) if vals else 0.0
    imputed[k] = med


def minmax(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo + 1e-12) for x in xs]


names = list(COUNTRIES.values())
gini = [raw[n]["gini"] if raw[n]["gini"] is not None else imputed["gini"] for n in names]
credit = [raw[n]["credit"] if raw[n]["credit"] is not None else imputed["credit"] for n in names]
debt = [raw[n]["debt"] if raw[n]["debt"] is not None else imputed["debt"] for n in names]
trade = [raw[n]["trade"] if raw[n]["trade"] is not None else imputed["trade"] for n in names]
govexp = [raw[n]["govexp"] if raw[n]["govexp"] is not None else imputed["govexp"] for n in names]

Theta = np.mean([minmax(gini), minmax(credit), minmax(debt)], axis=0)
Kappa = np.array(minmax(trade))
Ix = np.array(minmax(govexp))
Iota = np.array([IOTA[n] for n in names])

W = {"alpha": 0.30, "beta": 0.05, "gamma": 0.45, "lam": 0.20}
V = W["alpha"] * Theta + W["beta"] * Ix + W["gamma"] * Kappa + W["lam"] * Theta * Kappa
V_iota = V * (1 + 0.5 * (1 - Iota))

R = {"weights": W, "systems": names,
     "raw": {n: raw[n] for n in names}, "imputed": imputed,
     "Theta": {n: round(float(t), 3) for n, t in zip(names, Theta)},
     "Kappa": {n: round(float(k), 3) for n, k in zip(names, Kappa)},
     "I": {n: round(float(i), 3) for n, i in zip(names, Ix)},
     "iota": {n: IOTA[n] for n in names},
     "V": {n: round(float(v), 3) for n, v in zip(names, V)},
     "V_iota": {n: round(float(v), 3) for n, v in zip(names, V_iota)},
     "rank_V": [names[i] for i in np.argsort(-V)],
     "rank_V_iota": [names[i] for i in np.argsort(-V_iota)],
     "note": "Θ/κ/I 为 World Bank 真实数据（质量 A/B）；ι 为定性输入（质量 C，待 V-Dem 补齐）"}

# ---------------- 图 ----------------
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), layout="constrained")
order = np.argsort(-V_iota)
nm = [names[i] for i in order]
ax = axes[0]
x = np.arange(len(nm))
ax.bar(x - 0.2, [V[names.index(n)] for n in nm], width=0.4, color=OI["blue"], label="V")
ax.bar(x + 0.2, [V_iota[names.index(n)] for n in nm], width=0.4,
       color=OI["vermillion"], label="V（含 ι）")
ax.set_xticks(x); ax.set_xticklabels(nm, rotation=30, ha="right", fontsize=5.4)
ax.set_ylabel("脆弱性 V（真实数据）"); ax.set_title("七系统 V 排序"); ax.legend(fontsize=5.0)
panel(ax, "a")

ax = axes[1]
ax.scatter(Theta, Kappa, s=16, color=OI["purple"], lw=0)
for n, t, k in zip(names, Theta, Kappa):
    ax.text(t + 0.01, k, n, fontsize=5.0)
ax.set_xlabel("Θ（真实合成）"); ax.set_ylabel("κ（贸易/GDP，真实）")
ax.set_title("Θ–κ 相图（2020 年代）"); panel(ax, "b")

ax = axes[2]
ax.barh(np.arange(len(nm)), [V_iota[names.index(n)] for n in nm], color=OI["green"])
ax.set_yticks(np.arange(len(nm))); ax.set_yticklabels(nm, fontsize=5.6)
ax.invert_yaxis(); ax.set_xlabel("V（含 ι 调节）")
ax.set_title("真实数据下的脆弱性排序"); panel(ax, "c")
fig.savefig(os.path.join(FIGS, "v_real.png"))
plt.close(fig)

with open(os.path.join(OUT, "v_framework_real.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("\n=== 真实数据 V 框架 ===")
for n in R["rank_V_iota"]:
    print(f"  {n}: Θ={R['Theta'][n]:.2f} κ={R['Kappa'][n]:.2f} ι={R['iota'][n]:.2f} "
          f"V={R['V'][n]:.3f} V_ι={R['V_iota'][n]:.3f}")
print("排序:", R["rank_V_iota"])
