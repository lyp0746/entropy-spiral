#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bridge_csv.py — 通用 CSV → injected.json 桥接器。

用途：你从任意来源（EIA / IMF PCPS / 公司财报 / 手工整理）导出
      "year,value" 两列的 CSV，放入 data/，本脚本按 bridge_map.json
      的映射自动写入 injected.json，键名形如 <prefix>_<year>。

配置：data/bridge_map.json，例如
  {
    "brent_oil.csv":   {"prefix": "brent_oil", "scale": 1},
    "ai_top5.csv":     {"prefix": "ai_top5_share", "scale": 100},
    "wgi_polstab_usa.csv": {"prefix": "us_polstab", "scale": 1}
  }

用法：python analysis/bridge_csv.py
CSV 要求：表头含 year 与 value 两列（顺序不限，大小写不敏感）。
"""
import csv
import json
import os

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BOOK, "data")
MAP_PATH = os.path.join(DATA, "bridge_map.json")

# 默认映射（可被 data/bridge_map.json 覆盖）：对应第8章案例1/2所需的键
DEFAULT_MAP = {
    "brent_oil.csv": {"prefix": "brent_oil", "scale": 1},
    "ai_top5_share.csv": {"prefix": "ai_top5_share", "scale": 100},
    "us_polstab.csv": {"prefix": "us_polstab", "scale": 1},
}

mapping = DEFAULT_MAP
if os.path.exists(MAP_PATH):
    mapping = json.load(open(MAP_PATH, encoding="utf-8"))
else:
    json.dump(DEFAULT_MAP, open(MAP_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[created] {MAP_PATH}（模板，可按需修改）")

inj = json.load(open(os.path.join(DATA, "injected.json"), encoding="utf-8"))
added = {}
for fname, cfg in mapping.items():
    path = os.path.join(DATA, fname)
    if not os.path.exists(path):
        print(f"[skip] {fname}（未找到）")
        continue
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print(f"[warn] {fname} 为空")
        continue
    def col(row, *names):
        for k in row:
            if k.strip().lower() in names:
                return k
        return None
    yk = col(rows[0], "year", "年份", "date")
    vk = col(rows[0], "value", "数值")
    if not yk or not vk:
        print(f"[warn] {fname} 缺少 year/value 列，跳过")
        continue
    n = 0
    for r in rows:
        try:
            y = int(float(str(r[yk]).strip()))
            v = float(str(r[vk]).strip()) * cfg.get("scale", 1)
        except (ValueError, TypeError):
            continue
        inj[f"{cfg['prefix']}_{y}"] = round(v, 2)
        added[f"{cfg['prefix']}_{y}"] = round(v, 2)
        n += 1
    print(f"[ok] {fname} -> {n} 个键（前缀 {cfg['prefix']}）")

json.dump(inj, open(os.path.join(DATA, "injected.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"\n共写入 {len(added)} 个值。下一步：python build_book.py --pdf")
