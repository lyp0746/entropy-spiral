# -*- coding: utf-8 -*-
"""
tau_sensitivity.py —— τ = T_min / T_available 的不确定性传播（V5.3）。

背景：第 14.8.2 节表 14.6 声称“可测的 I 层越少，τ 的判断精度越低”，
并给出 ±0.10 / ±0.25 / ±0.60 的框架输出区间。审稿意见追问：
这些数字是理论下界、蒙特卡洛结果，还是启发式选择？

本脚本回答这一质疑，做法是**把两个尺度分开**：
  1. τ 本身（时间比，无量纲）：用蒙特卡洛传播 T_min、T_available 与 I₄ 失效。
     输出 τ 的 10/50/90 分位、方向翻转概率、点估计是否被许可。
  2. Risk（0—1 标度）：表 10.4 的 ±0.10/0.25/0.60 属于这一尺度，
     本脚本**不重新推导**它，只在同一情景上并列报告，供读者核对“两种尺度
     是否给出同向的不确定性扩张”。

模型（全部为质量 C 的“stipulated”参数，不是拟合值）：
  T_min      ~ LogNormal(ln M0, σ_m)，σ_m 由 I₂ 可得性决定；
  T_available~ LogNormal(ln A0, σ_a)，σ_a 由情景（冲击窗口清晰度）决定；
  I₄ 失效    ~ Bernoulli(p₄)：一旦发生，协调所依赖的“共同定义”消失，
              T_min 乘以一个大因子 f₄（或等价地，协调概率趋于零）。

输入基线取自第 4 章表 4.2（S1: 30/60；S2: 7/2；S3: 30/1）。
输出：analysis/results/tau_sensitivity.json
      assets/charts/tau_sensitivity.png
"""
import json
import os
import sys

try:  # 避免 Windows 控制台 GBK 编码导致含下标字符的日志崩溃
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "analysis", "results")
FIGS = os.path.join(HERE, "assets", "charts")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

RNG = np.random.default_rng(20261011)
N = 400_000

# 基线（第 4 章表 4.2）
SCENARIOS = {
    "S1 台湾芯片": {"M": 30.0, "A": 60.0, "baseline_tau": 0.5, "cv_a": 0.15},
    "S2 东南亚债务": {"M": 7.0, "A": 2.0, "baseline_tau": 3.5, "cv_a": 0.30},
    "S3 全球债务": {"M": 30.0, "A": 1.0, "baseline_tau": 30.0, "cv_a": 0.50},
}

# I₂ / I₄ 可得性制度（“可测层”逐级减少）
REGIMES = {
    "I₁+I₃ 可测，I₂ 事后校准（CV_m=0.20）": dict(cv_m=0.20, p4=0.00, f4=2.0),
    "I₂ 仅少数同类事件（CV_m=0.45，I₄ 不定）": dict(cv_m=0.45, p4=0.30, f4=6.0),
    "仅 I₁ 可测（CV_m=0.80，I₂/I₄ 缺）": dict(cv_m=0.80, p4=0.70, f4=25.0),
}


def sigma_from_cv(cv):
    """对数正态：CV → 对数标准差。"""
    return float(np.sqrt(np.log(1.0 + cv ** 2)))


def mc(M0, A0, cv_m, cv_a, p4, f4, n=N):
    sm, sa = sigma_from_cv(cv_m), sigma_from_cv(cv_a)
    t_min = M0 * np.exp(RNG.normal(0.0, sm, n))
    # I₄ 失效：协调概率趋于 0，等价于 T_min 被大因子放大
    fail = RNG.random(n) < p4
    t_min = np.where(fail, t_min * f4, t_min)
    t_avail = A0 * np.exp(RNG.normal(0.0, sa, n))
    tau = t_min / t_avail
    return tau, fail


def summarize(tau, fail, baseline_tau):
    p10, p50, p90 = np.percentile(tau, [10, 50, 90])
    base_side = baseline_tau >= 1.0
    side = tau >= 1.0
    flip = float(np.mean(side != base_side))          # 方向翻转概率
    point_ok = bool((p90 / max(p10, 1e-12) < 2.0))    # 10–90 区间跨度 < 2 倍
    return {
        "p10": round(float(p10), 3),
        "p50": round(float(p50), 3),
        "p90": round(float(p90), 3),
        "relative_width_10_90": round(float((p90 - p10) / max(p50, 1e-12)), 3),
        "P_tau_lt_1": round(float(np.mean(tau < 1.0)), 4),
        "direction_flip_prob": round(flip, 4),
        "i4_failure_prob": round(float(np.mean(fail)), 4),
        "point_estimate_licensed": point_ok,
        "direction_robust": bool(flip < 0.05),
    }


def licensed_claim(res):
    """把 MC 结果翻译成“τ 被许可的说法”。"""
    if res["i4_failure_prob"] >= 0.30:
        return "只能给方向；I₄ 失效时不得给点估计"
    if res["direction_robust"] and res["point_estimate_licensed"]:
        return "序数 + 较窄区间"
    if res["direction_robust"]:
        return "只能给序数（方向稳定，幅度不可报）"
    return "方向也不稳定，只能给条件分支"


out = {"note": "Monte Carlo，N=%d；参数为 stipulate（质量 C），非拟合。" % N,
       "model": "tau = T_min/T_available; T_min,I4 failure; lognormal",
       "baseline_source": "第 4 章表 4.2",
       "scenarios": {}, "fixed_S1_by_regime": {}}

# 1) 三个情景 × 匹配的制度（I 层越缺，CV 越大）
regime_for_scenario = {
    "S1 台湾芯片": "I₁+I₃ 可测，I₂ 事后校准（CV_m=0.20）",
    "S2 东南亚债务": "I₂ 仅少数同类事件（CV_m=0.45，I₄ 不定）",
    "S3 全球债务": "仅 I₁ 可测（CV_m=0.80，I₂/I₄ 缺）",
}
for sc, cfg in SCENARIOS.items():
    reg = REGIMES[regime_for_scenario[sc]]
    tau, fail = mc(cfg["M"], cfg["A"], reg["cv_m"], cfg["cv_a"],
                   reg["p4"], reg["f4"])
    res = summarize(tau, fail, cfg["baseline_tau"])
    res["regime"] = regime_for_scenario[sc]
    res["licensed_claim"] = licensed_claim(res)
    out["scenarios"][sc] = res

# 2) 固定 S1 基线，单独改变 I₂ 可得性：隔离“可测层”这一因素
cfg = SCENARIOS["S1 台湾芯片"]
for rname, reg in REGIMES.items():
    tau, fail = mc(cfg["M"], cfg["A"], reg["cv_m"], cfg["cv_a"],
                   reg["p4"], reg["f4"])
    res = summarize(tau, fail, cfg["baseline_tau"])
    res["licensed_claim"] = licensed_claim(res)
    out["fixed_S1_by_regime"][rname] = res

# 3) 审查者指定的单项检验：I₂ 仅 ±20%
tau, fail = mc(cfg["M"], cfg["A"], 0.20, 0.0, 0.0, 1.0)
out["review_check_I2_pm20pct"] = {
    "scenario": "S1",
    "tau_10_90": [round(float(np.percentile(tau, 10)), 3),
                  round(float(np.percentile(tau, 90)), 3)],
    "note": "I₂ 取 ±20%（对数正态 1σ 近似对称）时 S1 的 τ 区间；"
            "A 固定，以单独显示 I₂ 的影响。",
}

with open(os.path.join(OUT, "tau_sensitivity.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- 画图
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial",
                                         "DejaVu Sans"],
                     "axes.unicode_minus": False, "font.size": 7,
                     "axes.labelsize": 7, "axes.titlesize": 7.4,
                     "legend.fontsize": 5.4, "axes.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), layout="constrained")
colors = ["#0072B2", "#E69F00", "#D55E00"]
short_regime = ["I2 calibrated", "I2 post-hoc", "I2 missing"]
for ax, (sc, cfg) in zip(axes, SCENARIOS.items()):
    for (rname, reg), c, sr in zip(REGIMES.items(), colors, short_regime):
        tau, _ = mc(cfg["M"], cfg["A"], reg["cv_m"], cfg["cv_a"],
                    reg["p4"], reg["f4"], n=120_000)
        lo = np.percentile(tau, 1)
        x = np.logspace(np.log10(lo), np.log10(np.percentile(tau, 99.5)), 60)
        h, edges = np.histogram(np.clip(tau, x[0], x[-1]), bins=x)
        ax.plot(edges[:-1], h / h.max(), color=c, lw=1.0, label=sr)
    ax.axvline(1.0, color="k", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_title(f"{sc}（基线 τ={cfg['baseline_tau']}）")
    ax.set_xlabel("τ（对数刻度）")
    ax.set_ylabel("归一化频数")
axes[0].legend(loc="upper right")
fig.savefig(os.path.join(FIGS, "tau_sensitivity.png"))
plt.close(fig)

# ---------------------------------------------------------------- 摘要
print("=== τ 敏感性（蒙特卡洛，N=%d）===" % N)
print("--- 三情景（匹配的 I 层可得性）---")
for sc, r in out["scenarios"].items():
    print(f"  {sc}: τ10-90=[{r['p10']},{r['p90']}] P(τ<1)={r['P_tau_lt_1']} "
          f"翻转={r['direction_flip_prob']} I4失效={r['i4_failure_prob']} "
          f"→ {r['licensed_claim']}")
print("--- 固定 S1，仅改变 I₂ 可得性 ---")
for rn, r in out["fixed_S1_by_regime"].items():
    print(f"  {rn}: τ10-90=[{r['p10']},{r['p90']}] "
          f"相对宽度={r['relative_width_10_90']} 翻转={r['direction_flip_prob']} "
          f"→ {r['licensed_claim']}")
print("--- 审查者指定检验：I₂±20% ---")
print("  S1 τ 10-90 =", out["review_check_I2_pm20pct"]["tau_10_90"])
print("[done] analysis/results/tau_sensitivity.json, assets/charts/tau_sensitivity.png")
