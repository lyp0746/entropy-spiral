# -*- coding: utf-8 -*-
"""
food_energy_validation.py — V5：把 Θ–I–κ 框架迁移到粮食与能源两个领域，做独立验证。

设计原则（与全书一致）：
  * 只用真实、可复现的公开数据；
  * 明确标注每个量的操作化与来源；
  * 不隐藏数据缺口，缺口在输出中显式记录。

粮食（FAOSTAT bulk，已下载于 faostat_data/）：
  Θ_food = 产量集中度 HHI（4 种主粮）
  I_food = 生产者价格波动 CV（滚动 5 年）
  κ_food = 进口依赖度 = 进口量 /（产量 + 进口量）
  V_food = 0.40·Θ + 0.35·I + 0.25·κ   （域特异机制权重，见正文说明）

能源（energy_vulnerability_data/ + World Bank）：
  Θ_energy = 进口依赖 + （1 − 产量安全）
  I_energy = 油气产量的年度波动
  κ_energy = 1 − 出口能力
  V_energy = 0.40·Θ + 0.35·I + 0.25·κ

输出（analysis/results/）：
  food_v_panel.csv, food_v_summary.csv, energy_v_panel.csv,
  cross_system.json

前置：FAOSTAT 批量数据较大（约 4.4 GB），不随项目保存；
先运行 `python analysis/fetch_faostat.py` 下载并解压到 faostat_data/。
"""
import glob
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RESULTS = HERE / "analysis" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# FAOSTAT 真实名称（注意：美国与越南的名称与通用英文不同）
COUNTRIES = {
    "China": "CHN",
    "India": "IND",
    "Brazil": "BRA",
    "United States of America": "USA",
    "Russian Federation": "RUS",
    "Ukraine": "UKR",
    "Thailand": "THA",
    "Viet Nam": "VNM",
}
CROPS = ["Rice", "Wheat", "Maize (corn)", "Soya beans"]
YEARS = list(range(2010, 2025))          # 2025 数据不完整，排除
WEIGHTS = {"theta": 0.40, "I": 0.35, "kappa": 0.25}


def _read(pattern, usecols):
    files = glob.glob(str(HERE / "faostat_data" / pattern))
    if not files:
        raise FileNotFoundError(pattern)
    return pd.read_csv(files[0], usecols=usecols, low_memory=False)


# ------------------------------------------------------------------ 粮食
def build_food_panel():
    print("[food] 读取 FAOSTAT ...")
    qcl = _read("QCL/*.csv", ["Area", "Item", "Element", "Year", "Value"])
    tcl = _read("TCL/*.csv", ["Area", "Item", "Element", "Year", "Value"])
    pp = _read("PP/*.csv", ["Area", "Item", "Element", "Year", "Value"])
    fbs = _read("FBS/*.csv", ["Area", "Item", "Element", "Year", "Value"])

    names = list(COUNTRIES)

    # FBS 库存波动（要素 "Cereals - Excluding Beer"）：年度 |库存变动| / 产量
    fb = fbs[(fbs["Area"].isin(names)) & (fbs["Item"] == "Cereals - Excluding Beer") &
             (fbs["Element"].isin(["Stock Variation", "Production"])) &
             (fbs["Year"].isin(YEARS))]
    fb = fb.pivot_table(index=["Area", "Year"], columns="Element",
                        values="Value", aggfunc="mean").reset_index()
    fb["imbalance"] = fb["Stock Variation"].abs() / fb["Production"].replace(0, np.nan)

    # 产量（吨）
    prod = qcl[(qcl["Area"].isin(names)) & (qcl["Item"].isin(CROPS)) &
               (qcl["Element"] == "Production") & (qcl["Year"].isin(YEARS))]
    prod = prod.groupby(["Area", "Year", "Item"], as_index=False)["Value"].sum()

    # 进口（吨）
    imp = tcl[(tcl["Area"].isin(names)) & (tcl["Item"].isin(CROPS)) &
              (tcl["Element"] == "Import quantity") & (tcl["Year"].isin(YEARS))]
    imp = imp.groupby(["Area", "Year"], as_index=False)["Value"].sum() \
             .rename(columns={"Value": "Imports"})

    # 生产者价格（本币/吨）
    price = pp[(pp["Area"].isin(names)) & (pp["Item"].isin(CROPS)) &
               (pp["Element"] == "Producer Price (LCU/tonne)") & (pp["Year"].isin(YEARS))]
    price = price.groupby(["Area", "Year", "Item"], as_index=False)["Value"].mean()

    rows = []
    for c in names:
        c_prod = prod[prod["Area"] == c]
        c_imp = imp[imp["Area"] == c].set_index("Year")["Imports"]
        c_price = price[price["Area"] == c]

        # 价格指数：每种作物先在本国做 z 方向归一（除以该国该作物全期均值），再等权平均
        idx = {}
        for it in CROPS:
            s = c_price[c_price["Item"] == it].set_index("Year")["Value"]
            if len(s) >= 5 and s.mean() > 0:
                idx[it] = s / s.mean()
        price_index = pd.DataFrame(idx).mean(axis=1, skipna=True) if idx else pd.Series(dtype=float)

        for y in YEARS:
            cy = c_prod[c_prod["Year"] == y]
            total = cy["Value"].sum()
            if total > 0:
                shares = cy["Value"] / total
                theta = float((shares ** 2).sum())
            else:
                theta = np.nan
            imports = float(c_imp.get(y, 0.0) or 0.0)
            kappa = imports / (total + imports) if (total + imports) > 0 else np.nan
            window = price_index[(price_index.index >= y - 4) & (price_index.index <= y)].dropna()
            price_cv = float(window.std() / window.mean()) if len(window) >= 3 and window.mean() > 0 else np.nan

            # 库存波动代理（对全部 8 国可得）
            si = fb[(fb["Area"] == c) & (fb["Year"].between(y - 4, y))]["imbalance"].dropna()
            stock_cv = float(si.std() / si.mean()) if len(si) >= 3 and si.mean() > 0 else np.nan

            parts = [v for v in (price_cv, stock_cv) if not np.isnan(v)]
            I = float(np.mean(parts)) if parts else np.nan
            rows.append({"Country": c, "Year": y, "Theta": theta,
                         "I": I, "price_cv": price_cv, "stock_cv": stock_cv, "Kappa": kappa})

    df = pd.DataFrame(rows)

    # 归一化到 [0,1]（全样本 min-max），再按域特异权重合成
    for col in ["Theta", "I", "Kappa"]:
        s = df[col]
        df[f"{col}_n"] = (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else 0.5

    df["V_food"] = (WEIGHTS["theta"] * df["Theta_n"] +
                    WEIGHTS["I"] * df["I_n"] +
                    WEIGHTS["kappa"] * df["Kappa_n"])
    df.to_csv(RESULTS / "food_v_panel.csv", index=False, encoding="utf-8")

    summ = df.groupby("Country")["V_food"].agg(["mean", "std", "min", "max"]).round(4)
    summ = summ.sort_values("mean", ascending=False)
    summ.to_csv(RESULTS / "food_v_summary.csv", encoding="utf-8")
    trend = df.groupby("Year")["V_food"].mean().round(4)
    print("[food] 国家均值排序：")
    print(summ)
    print("[food] 年度均值：")
    print(trend)
    return df, summ, trend


# ------------------------------------------------------------------ 能源
def build_energy_panel():
    print("\n[energy] 读取快速验证集 + World Bank ...")
    qv = pd.read_csv(HERE / "energy_vulnerability_data" / "02_Quick_Validation_Dataset.csv")
    wb = pd.read_csv(HERE / "energy_vulnerability_data" / "01_WorldBank_Energy_Indicators.csv")

    wb_p = wb.pivot_table(index=["Country", "Year"], columns="Indicator",
                          values="Value", aggfunc="mean").reset_index()

    qv = qv.sort_values(["Country", "Year"]).copy()
    qv["Total_prod"] = qv["Oil_Production_MBPD"].fillna(0) + qv["Gas_Production_BCM"].fillna(0) / 100
    qv["Export_cap"] = qv["Oil_Exports_MBPD"].fillna(0) + qv["Gas_Exports_BCM"].fillna(0) / 100

    def mm(s):
        s = pd.to_numeric(s, errors="coerce")
        return (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0.5

    # Θ = 进口依赖 + 生产不足
    if "Energy_Import_Dependency" in wb_p.columns:
        wb_p["imp_n"] = wb_p.groupby("Year")["Energy_Import_Dependency"].transform(mm)
    else:
        wb_p["imp_n"] = np.nan
    qv["prod_n"] = qv.groupby("Year")["Total_prod"].transform(mm)
    qv["Theta_raw"] = (wb_p.set_index(["Country", "Year"])["imp_n"]
                       .reindex(pd.MultiIndex.from_frame(qv[["Country", "Year"]])).values)
    qv["Theta"] = qv[["Theta_raw"]].assign(prodrisk=1 - qv["prod_n"]).mean(axis=1)

    # I = 产量波动
    for col in ["Oil_Production_MBPD", "Gas_Production_BCM"]:
        qv[f"{col}_chg"] = qv.groupby("Country")[col].pct_change().abs()
    qv["I"] = qv[["Oil_Production_MBPD_chg", "Gas_Production_BCM_chg"]].mean(axis=1, skipna=True)

    # κ = 1 − 出口能力
    qv["Kappa"] = 1 - qv.groupby("Year")["Export_cap"].transform(mm)

    for col in ["Theta", "I", "Kappa"]:
        qv[f"{col}_n"] = qv.groupby("Year")[col].transform(mm)
    qv["V_energy"] = (WEIGHTS["theta"] * qv["Theta_n"] +
                      WEIGHTS["I"] * qv["I_n"] +
                      WEIGHTS["kappa"] * qv["Kappa_n"])

    out = qv[["Country", "Year", "Theta", "I", "Kappa", "V_energy"]]
    out.to_csv(RESULTS / "energy_v_panel.csv", index=False, encoding="utf-8")
    summ = out.groupby("Country")["V_energy"].mean().round(4).sort_values(ascending=False)
    trend = out.groupby("Year")["V_energy"].mean().round(4)
    print("[energy] 国家均值：", dict(summ))
    print("[energy] 年度均值：", dict(trend))
    return out, summ, trend


def cross_system(food, energy):
    # 统一国家名（能源用通用名，粮食用 FAOSTAT 名）
    alias = {"United States": "United States of America", "Russia": "Russian Federation"}
    food = food.copy(); energy = energy.copy()
    energy["Country"] = energy["Country"].replace(alias)
    f = food.groupby("Country")["V_food"].mean()
    e = energy.groupby("Country")["V_energy"].mean()
    common = sorted(set(f.index) & set(e.index))
    if len(common) < 3:
        print("[cross] 共同国家不足")
        return {}
    a = np.array([f[c] for c in common])
    b = np.array([e[c] for c in common])
    pear = float(np.corrcoef(a, b)[0, 1])
    from scipy.stats import spearmanr
    spear = float(spearmanr(a, b).correlation)
    res = {"common": common, "Food": {c: round(f[c], 4) for c in common},
           "Energy": {c: round(e[c], 4) for c in common},
           "pearson": round(pear, 3), "spearman": round(spear, 3), "n": len(common)}
    with open(RESULTS / "cross_system.json", "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    print("[cross] 共同国家:", common)
    print(f"[cross] Pearson={pear:.3f}  Spearman={spear:.3f}  n={len(common)}")
    return res


if __name__ == "__main__":
    food, fsumm, ftrend = build_food_panel()
    energy, esumm, etrend = build_energy_panel()
    cross_system(food, energy)
    print("\n[done] results in analysis/results/")
