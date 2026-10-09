#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_wid.py — 解析用户从 WID.world 导出的 CSV，注入 injected.json。
识别：净个人财富前1%份额（shweal_p99p100）、税前国民收入前1%与后50%份额。
"""
import csv
import glob
import json
import os

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")

TARGETS = {
    "shweal_p99p100": ("us_top1_wealth", 100),   # 转百分数
    "sptinc_p99p100_992": ("us_top1_income", 100),
    "sptinc_p0p50_992": ("us_bottom50_income", 100),
}
YEARS = [1980, 1990, 2000, 2010, 2015, 2020, 2022, 2024]

found = {key: {} for key, _ in TARGETS.values()}
for f in sorted(glob.glob(os.path.join(DATA, "WID_Data_*.csv"))):
    for row in csv.reader(open(f, encoding="utf-8-sig"), delimiter=";"):
        if len(row) < 5:
            continue
        var = row[1].split("\n")[0].strip()
        for code, (key, scale) in TARGETS.items():
            if var.startswith(code):
                try:
                    y, v = int(row[3]), float(row[4])
                except ValueError:
                    continue
                if y in YEARS:
                    found[key][y] = round(v * scale, 1)

inj = {}
for key, s in found.items():
    for y, v in s.items():
        inj[f"{key}_{y}"] = v

path = os.path.join(DATA, "injected.json")
d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
d.update(inj)
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("WID 解析结果：")
for key in found:
    print(f"  {key}: {found[key]}")
print(f"\n注入 {len(inj)} 个真实值到 injected.json")
