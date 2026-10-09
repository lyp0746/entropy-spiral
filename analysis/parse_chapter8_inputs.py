#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_chapter8_inputs.py — 解析用户提供的第8章案例数据并注入 injected.json。
  1) brent-daily.csv      日度 Brent 油价 -> 年度均值 -> brent_oil_<year>
  2) wgidataset...xlsx     WGI 'pv'（政治稳定）美国 -> us_polstab_<year>
  3) ai_top5_share.csv     前五大科技市值占比 -> ai_top5_share_<year>
"""
import csv
import glob
import json
import os
import statistics as st

import pandas as pd

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
inj = {}

# 1) Brent 日度 -> 年度均值
bfile = os.path.join(DATA, "brent-daily.csv")
if os.path.exists(bfile):
    by_year = {}
    for row in csv.DictReader(open(bfile, encoding="utf-8-sig")):
        d, p = row.get("Date"), row.get("Price")
        if not d or p in (None, "", "."):
            continue
        try:
            y = int(d[:4]); v = float(p)
        except ValueError:
            continue
        by_year.setdefault(y, []).append(v)
    for y, vs in by_year.items():
        inj[f"brent_oil_{y}"] = round(st.mean(vs), 1)
    print(f"[brent] 年度均值 {len(by_year)} 年（{min(by_year)}—{max(by_year)}）")

# 2) WGI 政治稳定（美国）
wgi = glob.glob(os.path.join(DATA, "wgidataset*.csv"))
if wgi:
    df = pd.read_excel(wgi[0], sheet_name="pv")
    est = [c for c in df.columns if "estimate" in c and "Standard" not in c and "Lower" not in c and "Upper" not in c][0]
    us = df[(df["Economy (code)"] == "USA") | (df["Economy (name)"] == "United States")]
    for _, r in us.iterrows():
        inj[f"us_polstab_{int(r['Year'])}"] = round(float(r[est]), 2)
    print(f"[wgi] 美国政治稳定 {len(us)} 年（{int(us['Year'].min())}—{int(us['Year'].max())}）")

# 3) AI top5 市值占比
afile = os.path.join(DATA, "ai_top5_share.csv")
if os.path.exists(afile):
    for row in csv.DictReader(open(afile, encoding="utf-8-sig")):
        y = row.get("year") or row.get("Year")
        v = row.get("value") or row.get("top5_market_cap_share") or row.get("top5_share_pct")
        if y and v:
            inj[f"ai_top5_share_{int(float(y))}"] = round(float(v), 1)
    print(f"[ai] 注入 {sum(1 for k in inj if k.startswith('ai_top5_share'))} 年")

path = os.path.join(DATA, "injected.json")
d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
d.update(inj)
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n共注入 {len(inj)} 个值。示例：",
      {k: inj[k] for k in list(sorted(inj))[:6]})
