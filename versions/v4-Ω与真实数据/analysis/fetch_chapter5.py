#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_chapter5.py — 第5章真实数据回填。
  1) World Bank: 政府最终消费支出/GDP（NE.CON.GOV.ZS）—— 制度规模代理
  2) WGI xlsx: 监管质量（rq）、政府效能（ge）—— 制度质量代理
输出注入 injected.json。
"""
import glob
import json
import os
import urllib.request

import pandas as pd

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
inj = {}


def wb(c, i):
    u = f"https://api.worldbank.org/v2/country/{c}/indicator/{i}?format=json&per_page=500"
    d = json.load(urllib.request.urlopen(u, timeout=30))
    return {int(r["date"]): float(r["value"]) for r in d[1] if r["value"] is not None}


# 1) 政府支出/GDP与政府总支出/GDP
for key, c in [("us", "USA"), ("cn", "CHN")]:
    for code, tag in [("NE.CON.GOVT.ZS", "govexp_gdp"), ("GC.XPN.TOTL.GD.ZS", "govexpense_gdp")]:
        for attempt in range(3):
            try:
                s = wb(c, code)
                break
            except Exception as e:
                print(f"  retry {c}/{code}: {str(e)[:40]}")
                s = {}
        path = os.path.join(DATA, f"{key}_{tag}.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("year,value\n")
            for y in sorted(s):
                f.write(f"{y},{s[y]}\n")
        for y in [1980, 2000, 2015, 2023]:
            if y in s:
                inj[f"{key}_{tag}_{y}"] = round(s[y], 1)
        print(f"[wb] {key}_{tag} ({len(s)} rows)")

# 2) WGI 监管质量 / 政府效能（美国）
wgi = glob.glob(os.path.join(DATA, "wgidataset*.csv"))
if wgi:
    for sheet, key in [("rq", "us_regquality"), ("ge", "us_goveff")]:
        df = pd.read_excel(wgi[0], sheet_name=sheet)
        est = [c for c in df.columns
               if "estimate" in c and "Standard" not in c and "Lower" not in c and "Upper" not in c][0]
        us = df[df["Economy (code)"] == "USA"]
        for _, r in us.iterrows():
            inj[f"{key}_{int(r['Year'])}"] = round(float(r[est]), 2)
        print(f"[wgi] {key} ({len(us)} years)")

path = os.path.join(DATA, "injected.json")
d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
d.update(inj)
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n注入", len(inj), "个值")
for k in sorted(inj):
    print(" ", k, "=", inj[k])
