#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_chapter8.py — 为第8章案例3（债务永续）实装真实数据。
来源：World Bank WDI（通胀、利率）+ IMF DataMapper（已在 fetch_imf.py 落库）。
"""
import json
import os
import urllib.request

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")


def wb(c, i):
    u = f"https://api.worldbank.org/v2/country/{c}/indicator/{i}?format=json&per_page=500"
    d = json.load(urllib.request.urlopen(u, timeout=30))
    return {int(r["date"]): float(r["value"]) for r in d[1] if r["value"] is not None}


inj = {}
for key, code, years in [("inflation", "FP.CPI.TOTL.ZG", [2008, 2015, 2020, 2023, 2024]),
                         ("real_rate", "FR.INR.RINR", [2008, 2015, 2020]),
                         ("lending_rate", "FR.INR.LEND", [2008, 2015, 2020])]:
    s = wb("USA", code)
    path = os.path.join(DATA, f"usa_{key}.csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write("year,value\n")
        for y in sorted(s):
            f.write(f"{y},{s[y]}\n")
    for y in years:
        if y in s:
            inj[f"us_{key}_{y}"] = round(s[y], 2)
    print(f"[saved] usa_{key}.csv ({len(s)} rows)")

path = os.path.join(DATA, "injected.json")
d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
d.update(inj)
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n写入：", {k: inj[k] for k in sorted(inj)})
