# -*- coding: utf-8 -*-
"""
第5章支撑分析：组织复杂度 I 与政体存续 T 的关系是否非单调（倒 U）？

用 Seshat 编码池 results/pool_coded.csv 中的复杂度代理：
  adm        = 行政层级数
  c_bureau   = 全职官僚（国家能力）
  s_lawcomposite = 法律形式化（成文、法院、法官、律师）
检验 logT ~ X + X^2 + C(NGA)（按 NGA 聚类稳健），并报告拐点与单调性检验。

输出：analysis/results/complexity_analysis.json, assets/charts/complexity.png
"""
import json
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根
POOL = os.path.join(BOOK, "analysis", "results", "pool_coded.csv")
OUT = os.path.join(BOOK, "analysis", "results")
FIGS = os.path.join(BOOK, "assets", "charts")
os.makedirs(OUT, exist_ok=True)

OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "grey": "#595959", "black": "#000000"}
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


df = pd.read_csv(POOL, encoding="utf-8-sig")
df = df[df["arch_period"] == 0].copy()
df["logT"] = np.log(df["T"])

R = {}
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.3), layout="constrained")


def quad_model(var, ax, letter, title, xlab):
    d = df.dropna(subset=[var, "T", "NGA"]).copy()
    d["x"] = d[var]
    d["x2"] = d["x"] ** 2
    m = smf.ols("logT ~ x + x2 + C(NGA)", d).fit(
        cov_type="cluster", cov_kwds={"groups": d["NGA"]})
    b1, b2 = m.params["x"], m.params["x2"]
    p1, p2 = m.pvalues["x"], m.pvalues["x2"]
    # 拐点（若 b2<0 为极大值）
    turn = -b1 / (2 * b2) if b2 != 0 else np.nan
    # 线性（单调）对照
    ml = smf.ols("logT ~ x + C(NGA)", d).fit(
        cov_type="cluster", cov_kwds={"groups": d["NGA"]})
    out = {"n": int(m.nobs), "b1": float(b1), "b2": float(b2),
           "p1": float(p1), "p2": float(p2), "turning_point": float(turn),
           "aic_quad": float(m.aic), "aic_lin": float(ml.aic),
           "shape": "倒U" if b2 < 0 else "正U", "inverted_u": bool(b2 < 0 and p2 < 0.10)}
    R[var] = out
    # 分箱均值 + 拟合
    q = pd.qcut(d["x"].rank(method="first"), min(8, d["x"].nunique()))
    g = d.groupby(q, observed=True).agg(x=("x", "mean"), y=("logT", "mean"),
                                        se=("logT", lambda v: v.std() / np.sqrt(len(v))))
    ax.errorbar(g["x"], g["y"], yerr=g["se"], fmt="o", color=OI["vermillion"],
                capsize=2, ms=3.2, lw=0)
    xs = np.linspace(d["x"].min(), d["x"].max(), 100)
    ax.plot(xs, m.params["Intercept"] + b1 * xs + b2 * xs ** 2, color=OI["black"], lw=1.2)
    if 0 < turn < d["x"].max():
        ax.axvline(turn, color=OI["grey"], ls=":", lw=0.9)
        ax.text(turn, ax.get_ylim()[0] + 0.05, f"拐点≈{turn:.1f}", fontsize=5.0,
                color=OI["grey"])
    ax.set_xlabel(xlab); ax.set_ylabel("log 存续时长")
    ax.set_title(title)
    panel(ax, letter)
    return out


quad_model("adm", axes[0], "a", "行政层级 vs 时长", "行政层级数")
quad_model("s_lawcomposite", axes[1], "b", "法律形式化 vs 时长", "法律形式化程度")
quad_model("c_bureau", axes[2], "c", "全职官僚 vs 时长", "全职官僚（国家能力）")

fig.savefig(os.path.join(FIGS, "complexity.png"))
plt.close(fig)

# 幂次/单调性：adm 与 logT 的秩相关
for v in ["adm", "s_lawcomposite", "c_bureau", "s_main"]:
    d = df.dropna(subset=[v, "logT"])
    rho, p = stats.spearmanr(d[v], d["logT"])
    R.setdefault(v, {})["spearman_T"] = float(rho)
    R[v]["spearman_p"] = float(p)

with open(os.path.join(OUT, "complexity_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)

print("=== 第5章复杂度检验 ===")
for k, v in R.items():
    if "b2" in v:
        print(f"  {k}: n={v['n']} b1={v['b1']:+.3f}(p={v['p1']:.3f}) "
              f"b2={v['b2']:+.3f}(p={v['p2']:.3f}) 拐点={v['turning_point']:.2f} "
              f"形状={v['shape']} 倒U={v['inverted_u']} AIC(quad/lin)={v['aic_quad']:.1f}/{v['aic_lin']:.1f}")
    if "spearman_T" in v:
        print(f"     Spearman(与logT) ρ={v['spearman_T']:+.3f} p={v['spearman_p']:.3f}")
