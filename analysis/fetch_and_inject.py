#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_and_inject.py — 从 World Bank API 抓取真实序列，写入 data/*.csv，
并据此更新 data/injected.json（供 build_book.py 注入正文占位符）。

覆盖指标：
  SI.POV.GINI       美国收入 Gini
  NE.TRD.GNFS.ZS    贸易开放度（WLD, USA）—— 商品耦合 κ 的代理
  BX.KLT.DINV.CD.WD FDI 净流入（WLD）；配合 NY.GDP.MKTP.CD 得 FDI/GDP —— 金融耦合代理
  GC.DOD.TOTL.GD.ZS 中央政府债务/GDP（USA）
  FS.AST.PRVT.GD.ZS 私人部门信贷/GDP（USA）

用法: python analysis/fetch_and_inject.py
"""
import json
import os
import urllib.request

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
os.makedirs(DATA, exist_ok=True)


def wb(country, ind):
    url = (f"https://api.worldbank.org/v2/country/{country}/indicator/"
           f"{ind}?format=json&per_page=500")
    d = json.load(urllib.request.urlopen(url, timeout=25))
    return {int(r["date"]): float(r["value"]) for r in d[1] if r["value"] is not None}


def save_csv(name, series):
    path = os.path.join(DATA, name)
    rows = sorted(series.items())
    with open(path, "w", encoding="utf-8") as f:
        f.write("year,value\n")
        for y, v in rows:
            f.write(f"{y},{v}\n")
    print(f"[saved] {name} ({len(rows)} rows)")
    return series


fetch = {}
print("fetching World Bank series ...")
fetch["usa_gini"] = save_csv("usa_gini.csv", wb("US", "SI.POV.GINI"))
fetch["world_trade_gdp"] = save_csv("world_trade_gdp.csv", wb("WLD", "NE.TRD.GNFS.ZS"))
fetch["usa_trade_gdp"] = save_csv("usa_trade_gdp.csv", wb("USA", "NE.TRD.GNFS.ZS"))
fetch["world_fdi"] = wb("WLD", "BX.KLT.DINV.CD.WD")
fetch["world_gdp"] = wb("WLD", "NY.GDP.MKTP.CD")
fetch["usa_gov_debt_gdp"] = save_csv("usa_gov_debt_gdp.csv", wb("USA", "GC.DOD.TOTL.GD.ZS"))
fetch["usa_private_credit_gdp"] = save_csv("usa_private_credit_gdp.csv",
                                           wb("USA", "FS.AST.PRVT.GD.ZS"))

# FDI / GDP（世界）作为金融耦合代理
fdi_ratio = {y: 100 * fetch["world_fdi"][y] / fetch["world_gdp"][y]
             for y in fetch["world_fdi"] if y in fetch["world_gdp"] and fetch["world_gdp"][y]}
save_csv("world_fdi_gdp.csv", fdi_ratio)


def at(s, *years):
    return {f"y{y}": round(s[y], 2) for y in years if y in s}


inj = {}
inj.update({f"us_gini_{y}": round(fetch["usa_gini"][y], 1)
            for y in (1980, 2000, 2015, 2024) if y in fetch["usa_gini"]})
inj.update({f"world_trade_gdp_{y}": round(fetch["world_trade_gdp"][y], 1)
            for y in (1980, 2000, 2015, 2025) if y in fetch["world_trade_gdp"]})
inj.update({f"usa_trade_gdp_{y}": round(fetch["usa_trade_gdp"][y], 1)
            for y in (1980, 2000, 2015, 2024) if y in fetch["usa_trade_gdp"]})
inj.update({f"world_fdi_gdp_{y}": round(fdi_ratio[y], 2)
            for y in (1980, 2000, 2015, 2024) if y in fdi_ratio})
inj.update({f"us_gov_debt_gdp_{y}": round(fetch["usa_gov_debt_gdp"][y], 1)
            for y in (1995, 2008, 2015, 2024) if y in fetch["usa_gov_debt_gdp"]})
inj.update({f"us_private_credit_gdp_{y}": round(fetch["usa_private_credit_gdp"][y], 1)
            for y in (1980, 2000, 2015, 2024) if y in fetch["usa_private_credit_gdp"]})

# 合并进 injected.json（保留已有的手工键）
path = os.path.join(DATA, "injected.json")
existing = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        existing = json.load(f)
existing.update(inj)
with open(path, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print("\n写入 injected.json 的真实值：")
for k in sorted(inj):
    print(f"  {k} = {inj[k]}")
print(f"\n共 {len(inj)} 个真实值已写入。下一步：python build_book.py --pdf")
