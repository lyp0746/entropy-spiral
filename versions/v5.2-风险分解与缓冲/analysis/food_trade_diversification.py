# -*- coding: utf-8 -*-
"""
food_trade_diversification.py — 买家集中度：测“替代性”的商品特异性（V5.1，附录 D.7）。

用 FAOSTAT 详细贸易矩阵（Detailed Trade Matrix）按伙伴国分解的出口量，计算
主要粮食出口国的买家 HHI 与有效买家数（1/HHI）。

数据：faostat_data/TM/…（约 8.5 GB CSV），用 analysis/fetch_faostat.py 的扩展下载。
输出：analysis/results/food_buyer_concentration.csv

注意：FAOSTAT 详细贸易矩阵的**水稻**覆盖严重不全（泰国仅 23 吨），本脚本以
小麦为主；缺失在正文中如实说明。
"""
import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "analysis", "results", "food_buyer_concentration.csv")
REPORTERS = ["Viet Nam", "Russian Federation", "Thailand", "China", "India",
             "Brazil", "United States of America", "Ukraine"]
ITEMS = ["Rice", "Rice; broken", "Rice; milled", "Rice; milled (husked)",
         "Rice; paddy (rice milled equivalent)", "Wheat"]
YEARS = range(2015, 2023)


def main():
    files = glob.glob(os.path.join(HERE, "faostat_data", "TM", "*All_Data*.csv"))
    if not files:
        raise SystemExit("未找到 TM 数据；请先下载 FAOSTAT Detailed Trade Matrix")
    agg = {}
    reader = pd.read_csv(files[0], usecols=["Reporter Countries", "Partner Countries",
                                            "Item", "Element", "Year", "Value"],
                         chunksize=3_000_000, low_memory=False)
    for ch in reader:
        f = ch[(ch["Reporter Countries"].isin(REPORTERS)) & (ch["Item"].isin(ITEMS)) &
               (ch["Element"] == "Export quantity") & (ch["Year"].isin(YEARS))]
        if len(f):
            g = f.groupby(["Reporter Countries", "Item", "Year", "Partner Countries"])["Value"].sum()
            for k, v in g.items():
                agg[k] = agg.get(k, 0) + v
    recs = {}
    for (rep, item, yr, par), v in agg.items():
        recs.setdefault((rep, item, yr), {})[par] = v
    rows = []
    for (rep, item, yr), d in recs.items():
        tot = sum(d.values())
        if tot <= 0:
            continue
        sh = sorted((v / tot for v in d.values()), reverse=True)
        hhi = sum(s * s for s in sh)
        rows.append({"Reporter": rep, "Item": item, "Year": yr,
                     "Total_export_t": round(tot, 1), "HHI": round(hhi, 4),
                     "Eff_partners": round(1 / hhi, 2), "N": len(sh),
                     "Top": round(sh[0], 3)})
    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8")
    print(f"[done] {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
