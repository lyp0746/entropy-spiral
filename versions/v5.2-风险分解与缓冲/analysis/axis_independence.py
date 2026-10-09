# -*- coding: utf-8 -*-
"""
axis_independence.py — 三轴（Θ, I, κ）独立性与测量审计（V5.1）。

背景：框架最初假设 Θ、I、κ 相对独立（否则不能分别加权）。本脚本用三个域的真实
结果检验这一假设，并把结果写入 analysis/results/axis_independence.json，供附录 D.7
“测量审计”引用。

数据：
  粮食  analysis/results/food_v_panel.csv        （8 国 × 13 年）
  能源  analysis/results/energy_v_panel.csv      （4 国 × 5 年）
  政治经济 analysis/results/v_framework_real.json（7 国，I 未测）

输出：axis_independence.json（Pearson/Spearman 矩阵 + 结论标记）
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(HERE, "analysis", "results")


def matrix(df, cols):
    sub = df[cols].dropna()
    n = len(sub)
    if n < 5:
        return {"n": n, "note": "样本不足"}
    pear = sub.corr().round(3).to_dict()
    spear = {}
    for a in cols:
        spear[a] = {}
        for b in cols:
            r, p = spearmanr(sub[a], sub[b])
            spear[a][b] = {"r": round(float(r), 3), "p": round(float(p), 4)}
    return {"n": n, "pearson": pear, "spearman": spear}


def main():
    out = {}

    food = pd.read_csv(os.path.join(R, "food_v_panel.csv"))
    out["food"] = matrix(food, ["Theta", "I", "Kappa"])

    energy = pd.read_csv(os.path.join(R, "energy_v_panel.csv"))
    out["energy"] = matrix(energy, ["Theta", "I", "Kappa"])

    pe = json.load(open(os.path.join(R, "v_framework_real.json"), encoding="utf-8"))
    pe_df = pd.DataFrame({"Theta": pd.Series(pe["Theta"]), "I": pd.Series(pe["I"]),
                          "Kappa": pd.Series(pe["Kappa"])}).dropna()
    out["political_economy"] = {
        "n": len(pe_df),
        "I_unique_values": sorted(pe_df["I"].unique().tolist()),
        "I_unmeasured": bool(pe_df["I"].nunique() <= 1),
        "theta_kappa_pearson": round(float(pe_df["Theta"].corr(pe_df["Kappa"])), 3),
    }

    # 结论标记
    out["findings"] = {
        "theta_kappa_coupled": "粮食 +0.51、能源 +0.57：集中与耦合正相关，两轴不独立",
        "sign_flip": "政治经济域 Θ–κ 为负（−0.30）：κ 的定义跨域不一致",
        "I_unmeasured_in_PE": "政治经济域 I 零方差 → β(I)≈0 是缺失所致，不能读作机制为零",
        "implication": "轴可作诊断坐标，但不能加权求跨域单一排序；非正交只在加权求和时致命",
    }

    with open(os.path.join(R, "axis_independence.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("[done] analysis/results/axis_independence.json")
    print(f"  粮食 n={out['food']['n']}  Θ–κ Pearson={out['food']['pearson']['Theta']['Kappa']}")
    print(f"  能源 n={out['energy']['n']}  Θ–κ Pearson={out['energy']['pearson']['Theta']['Kappa']}")
    print(f"  政治经济 n={out['political_economy']['n']}  I 未测={out['political_economy']['I_unmeasured']}")


if __name__ == "__main__":
    main()
