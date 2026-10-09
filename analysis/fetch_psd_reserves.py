# -*- coding: utf-8 -*-
"""
fetch_psd_reserves.py — 缓冲（Reserves）的实测：粮食期末库存（USDA PS&D，质量 A/B）。

五因素模型中最后未测的一项。数据源：USDA FAS Production, Supply and Distribution
(PS&D) 全量 CSV（公开、无需密钥）：
  https://apps.fas.usda.gov/psdonline/downloads/psd_alldata_csv.zip

指标：
  BufferMonths      = Ending Stocks / Domestic Consumption × 12（国内消费可支撑月数）
  ExportCoverMonths = Ending Stocks / Exports × 12（出口可支撑月数；出口国更相关）

输出：analysis/results/reserves_psd.csv
"""
import os
import urllib.request
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "analysis", "results", "reserves_psd.csv")
DIR = os.path.join(HERE, "data", "psd")
URL = "https://apps.fas.usda.gov/psdonline/downloads/psd_alldata_csv.zip"
ATTR = ["Ending Stocks", "Domestic Consumption", "Exports", "Production"]
CASES = [("Wheat", ["Russia", "Ukraine", "United States"]),
         ("Rice, Milled", ["Vietnam", "Thailand", "India"])]


def main():
    os.makedirs(DIR, exist_ok=True)
    csv = os.path.join(DIR, "psd_alldata.csv")
    if not os.path.exists(csv):
        zp = os.path.join(DIR, "psd.zip")
        print("downloading PS&D (~10MB)...")
        urllib.request.urlretrieve(URL, zp)
        with zipfile.ZipFile(zp) as z:
            z.extractall(DIR)
        os.remove(zp)
    df = pd.read_csv(csv, usecols=["Commodity_Description", "Country_Name", "Market_Year",
                                   "Attribute_Description", "Value"], low_memory=False)
    rows = []
    for comm, countries in CASES:
        sub = df[(df.Commodity_Description == comm) & (df.Country_Name.isin(countries)) &
                 (df.Attribute_Description.isin(ATTR)) & (df.Market_Year.between(2018, 2022))]
        piv = sub.pivot_table(index=["Country_Name", "Market_Year"],
                              columns="Attribute_Description", values="Value",
                              aggfunc="last").reset_index()
        for _, r in piv.iterrows():
            es, dc, ex = r.get("Ending Stocks"), r.get("Domestic Consumption"), r.get("Exports")
            rows.append({"Commodity": comm, "Country": r["Country_Name"],
                         "Year": int(r["Market_Year"]),
                         "EndingStocks_kt": round(es, 0) if pd.notna(es) else None,
                         "DomCons_kt": round(dc, 0) if pd.notna(dc) else None,
                         "Exports_kt": round(ex, 0) if pd.notna(ex) else None,
                         "BufferMonths": round(es / dc * 12, 1) if dc and pd.notna(es) else None,
                         "ExportCoverMonths": round(es / ex * 12, 1) if ex and pd.notna(es) else None})
    out = pd.DataFrame(rows).sort_values(["Commodity", "Country", "Year"])
    out.to_csv(OUT, index=False, encoding="utf-8")
    print(f"[done] {OUT} ({len(out)} rows)")
    print(out[out.Year == 2022].to_string(index=False))


if __name__ == "__main__":
    main()
