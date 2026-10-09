#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_imf.py — 从 IMF DataMapper API 抓取美国三类债务序列并写入 injected.json。
指标：HH_LS（家庭债务/GDP）、NFC_LS（非金融企业债务/GDP）、
      GGXWDG_NGDP（广义政府总债务/GDP）。
"""
import json
import os
import urllib.request

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
IMF = "https://www.imf.org/external/datamapper/api/v1/{ind}/USA"
IND = {"hh_debt": "HH_LS", "nfc_debt": "NFC_LS", "gov_debt_imf": "GGXWDG_NGDP"}
YEARS = [1980, 1990, 2000, 2008, 2015, 2020, 2024]

series = {}
for key, code in IND.items():
    last = None
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(IMF.format(ind=code), timeout=45))
            s = d["values"][code]["USA"]
            series[key] = {int(y): float(v) for y, v in s.items()}
            break
        except Exception as e:
            last = e
            print(f"  retry {key} ({attempt+1}/4): {str(e)[:50]}")
    if key not in series:
        raise SystemExit(f"failed {key}: {last}")
    path = os.path.join(DATA, f"imf_usa_{key}.csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write("year,value\n")
        for y in sorted(series[key]):
            f.write(f"{y},{series[key][y]}\n")
    print(f"[saved] imf_usa_{key}.csv ({len(series[key])} rows)")

inj = {}
for key, s in series.items():
    for y in YEARS:
        if y in s:
            inj[f"us_{key}_{y}"] = round(s[y], 1)

path = os.path.join(DATA, "injected.json")
existing = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
existing.update(inj)
with open(path, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print("\n写入 injected.json：")
for k in sorted(inj):
    print(f"  {k} = {inj[k]}")
