# -*- coding: utf-8 -*-
"""
fetch_eu_gas_dependence.py — 欧盟对俄天然气进口依赖的真实序列（Eurostat，质量 A）。

数据源：Eurostat nrg_ti_gas（Imports of natural gas by partner country, annual）
  筛选：geo=EU27_2020, siec=G3000（天然气）, unit=MIO_M3（百万立方米）
  伙伴：RU（俄罗斯）与 TOTAL（合计）
输出：data/eu_gas_ru_share.csv
  year, ru_mio_m3, total_mio_m3, ru_share

用途：为第 8.2 节「能源反馈=两层（mesh 价格 + sequence 物理）」提供可复现的
δ≠0 证据——若俄罗斯份额在 2022 后大幅下降，说明纠错（替代）确实发生。
"""
import csv
import json
import os
import socket
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "eu_gas_ru_share.csv")
BASE = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
        "nrg_ti_gas?format=JSON&lang=EN&geo=EU27_2020&siec=G3000&unit=MIO_M3"
        "&sinceTimePeriod=2019&partner=")


def get(partner):
    req = urllib.request.Request(BASE + partner, headers={"User-Agent": "entropy-spiral/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.load(r)
    times = j["dimension"]["time"]["category"]["index"]
    order = sorted(times.items(), key=lambda kv: kv[1]) if isinstance(times, dict) else list(enumerate(times))
    # 单 partner 时 time 为最快变化维，索引即位置
    vals = j.get("value", {})
    out = {}
    for name, pos in order:
        v = vals.get(str(pos))
        if v is not None:
            out[int(name)] = float(v)
    return out


def main():
    socket.setdefaulttimeout(150)
    ru = get("RU")
    total = get("TOTAL")
    years = sorted(set(ru) & set(total))
    rows = []
    for y in years:
        rows.append({"year": y, "ru_mio_m3": round(ru[y], 1),
                     "total_mio_m3": round(total[y], 1),
                     "ru_share": round(ru[y] / total[y], 4)})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "ru_mio_m3", "total_mio_m3", "ru_share"])
        w.writeheader()
        w.writerows(rows)
    print(f"[done] {OUT}")
    for r in rows:
        print(f"  {r['year']}: RU {r['ru_mio_m3']:>9.0f} / total {r['total_mio_m3']:>9.0f} "
              f"MIO_M3 = {r['ru_share']*100:.1f}%")


if __name__ == "__main__":
    main()
