# -*- coding: utf-8 -*-
"""
v_uncertainty_decomposition.py —— 脆弱性 V 的不确定性来源分解。

问题（审稿意见）：V 的置信区间主要由哪个子变量驱动？是 Θ、I、κ 还是 ι？
本书已对 τ 做过 MC（tau_sensitivity.py），但未对 V 做来源分解。本脚本补上。

方法：
  V = α·Θ + β·I + γ·κ + λ·(Θ×κ)          （式 8.1）
  V_ι = V · [1 + β_ι(1 − ι)]              （式 8.2）
  对每个输入赋对数正态/正态不确定性，MC 传播，按“一阶方差贡献”分解：
      share_i ≈ Var(去掉 x_i 的波动后的条件方差下降) / Var(V)
  即用“冻结一个变量”的方差下降近似一阶贡献（可复现、无需 Sobol 库）。

关键设定（全部显式标注，质量 C，非拟合）：
  - 名义水平：第 8 章七系统（v_framework.py 的同名输入）。
  - 权重：α=0.30, β=0.05, γ=0.45, λ=0.20（第 8 章表 8.2 的默认方案）。
  - 三档 I 可测性制度（对应 S1/S2/S3 的 I 层可得性）：
      Regime A（S1，I₁+I₃ 可测、I₂ 事后）    CV_I=0.20
      Regime B（S2，I₂ 仅少数同类事件）      CV_I=0.45
      Regime C（S3，仅 I₁ 可测）            CV_I=0.80
  - 其余轴（本书口径）：CV_Θ=0.30（代理共线、水平不可比）、
    CV_κ=0.20（HHI 可测、传导速度粗糙）、CV_ι=0.25（定性输入）。

输出：analysis/results/v_uncertainty_decomposition.json
      assets/charts/v_uncertainty_decomposition.png
"""
import json
import os
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "analysis", "results")
FIGS = os.path.join(HERE, "assets", "charts")

RNG = np.random.default_rng(20261011)
N = 200_000

W = {"alpha": 0.30, "beta": 0.05, "gamma": 0.45, "lam": 0.20, "beta_iota": 0.5}

SYSTEMS = {
    "美国":   {"Theta": 0.75, "I": 0.82, "kappa": 0.82, "iota": 0.60},
    "欧盟":   {"Theta": 0.62, "I": 0.88, "kappa": 0.85, "iota": 0.65},
    "英国":   {"Theta": 0.63, "I": 0.72, "kappa": 0.78, "iota": 0.68},
    "中国":   {"Theta": 0.68, "I": 0.71, "kappa": 0.71, "iota": 0.70},
    "俄罗斯": {"Theta": 0.78, "I": 0.60, "kappa": 0.55, "iota": 0.45},
    "日本":   {"Theta": 0.55, "I": 0.65, "kappa": 0.70, "iota": 0.80},
    "印度":   {"Theta": 0.60, "I": 0.55, "kappa": 0.50, "iota": 0.55},
}

REGIMES = {
    "A（S1：I₁+I₃ 可测，I₂ 事后）": {"cv_I": 0.20},
    "B（S2：I₂ 仅少数同类事件）":   {"cv_I": 0.45},
    "C（S3：仅 I₁ 可测）":          {"cv_I": 0.80},
}
CV = {"Theta": 0.30, "kappa": 0.20, "iota": 0.25}


def sample(level, cv, n=N):
    """对数正态：CV → 对数标准差，均值≈level。"""
    if cv <= 0:
        return np.full(n, level)
    s = np.sqrt(np.log(1 + cv ** 2))
    mu = np.log(level) - 0.5 * s ** 2
    return RNG.lognormal(mu, s, n)


def V_of(theta, i, kappa, iota):
    v = W["alpha"] * theta + W["beta"] * i + W["gamma"] * kappa + W["lam"] * theta * kappa
    return v * (1 + W["beta_iota"] * (1 - iota))


def shares(nominal, cv_I):
    """返回 Var(V_ι) 的一阶方差贡献占比（冻结法）。"""
    theta, i, kappa, iota = nominal["Theta"], nominal["I"], nominal["kappa"], nominal["iota"]
    x = {
        "Theta": sample(theta, CV["Theta"]),
        "I": sample(i, cv_I),
        "kappa": sample(kappa, CV["kappa"]),
        "iota": sample(iota, CV["iota"]),
    }
    V = V_of(x["Theta"], x["I"], x["kappa"], x["iota"])
    var_full = float(np.var(V))
    out = {}
    for k in ["Theta", "I", "kappa", "iota"]:
        # 冻结该轴：用其名义值替换波动
        args = dict(x); args[k] = np.full(N, nominal[k])
        vk = V_of(args["Theta"], args["I"], args["kappa"], args["iota"])
        out[k] = max(0.0, var_full - float(np.var(vk))) / var_full
    s = sum(out.values())
    if s > 0:
        out = {k: v / s for k, v in out.items()}
    return {"V_iota_mean": round(float(np.mean(V)), 3),
            "V_iota_sd": round(float(np.std(V)), 3),
            "V_iota_p10_p90": [round(float(np.percentile(V, 10)), 3),
                               round(float(np.percentile(V, 90)), 3)],
            "shares": {k: round(v, 3) for k, v in out.items()}}


def main():
    res = {"method": "MC + 一阶（冻结法）方差分解", "N": N, "weights": W,
           "cv_fixed_axes": CV, "regimes": {}, "note": "所有 CV 与权重为显式约定值（质量 C），非拟合。"}
    for rname, rc in REGIMES.items():
        per_system, agg = {}, {"Theta": 0.0, "I": 0.0, "kappa": 0.0, "iota": 0.0}
        for sname, nom in SYSTEMS.items():
            r = shares(nom, rc["cv_I"])
            per_system[sname] = r
            for k in agg:
                agg[k] += r["shares"][k]
        for k in agg:
            agg[k] = round(agg[k] / len(SYSTEMS), 3)
        res["regimes"][rname] = {"by_system": per_system, "mean_share": agg}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "v_uncertainty_decomposition.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print("=== V 的不确定性来源（七系统平均）===")
    for rname, r in res["regimes"].items():
        s = r["mean_share"]
        print(f"{rname}: Θ {s['Theta']:.0%} | I {s['I']:.0%} | κ {s['kappa']:.0%} | ι {s['iota']:.0%}")

    # 图：三档制度下各轴方差占比
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        labels = ["Θ", "I", "κ", "ι"]
        keys = ["Theta", "I", "kappa", "iota"]
        fig, ax = plt.subplots(figsize=(7.2, 4.0))
        xpos = np.arange(len(REGIMES))
        bottom = np.zeros(len(REGIMES))
        colors = ["#3a6ea5", "#c94f4f", "#009E73", "#b8862f"]
        for k, lab, c in zip(keys, labels, colors):
            vals = np.array([res["regimes"][r]["mean_share"][k] for r in REGIMES])
            ax.bar(xpos, vals, bottom=bottom, label=lab, color=c)
            bottom += vals
        ax.set_xticks(xpos)
        ax.set_xticklabels(["S1\nI₂ 可事后校准", "S2\nI₂ 样本少", "S3\n仅 I₁ 可测"], fontsize=9)
        ax.set_ylabel("Var(V) 一阶贡献占比")
        ax.set_title("V 的不确定性主要来自哪根轴？——随 I 可测性变化", fontsize=11)
        ax.legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.12))
        os.makedirs(FIGS, exist_ok=True)
        fig.tight_layout()
        fig.savefig(os.path.join(FIGS, "v_uncertainty_decomposition.png"), dpi=160)
        print("[fig] assets/charts/v_uncertainty_decomposition.png")
    except Exception as e:
        print("[fig skipped]", repr(e)[:80])
    print("[done] analysis/results/v_uncertainty_decomposition.json")


if __name__ == "__main__":
    main()
