# -*- coding: utf-8 -*-
"""
fetch_debt_rg.py — 债务纠错制度的真实输入：r − g（质量 A）。

组成：
  r = 10 年期国债收益率年均值（FRED，OECD long-term government bond yields）
  g = 名义 GDP 增速（World Bank：实际增长 NY.GDP.MKTP.KD.ZG × GDP平减指数 NY.GDP.DEFL.KD.ZG）
  r − g = 上述之差（个百分点）；r<g 表示“增长快于利率”，债务比率自然稀释。

输出：data/debt_rg.csv
  country, year, yield_10y, real_growth, deflator, nominal_growth, r_minus_g

说明：央行持债比例不在此脚本内（各国发布口径不一），在正文以定性/已知比例给出。
"""
import csv
import io
import json
import os
import socket
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "debt_rg.csv")

COUNTRIES = {"USA": "US", "JPN": "JP", "DEU": "DE", "GBR": "GB", "MEX": "MX"}
FRED_YIELD = {"USA": "IRLTLT01USM156N", "JPN": "IRLTLT01JPM156N",
              "DEU": "IRLTLT01DEM156N", "GBR": "IRLTLT01GBM156N",
              "MEX": "IRLTLT01MXM156N"}


def fred_monthly(series):
    u = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    req = urllib.request.Request(u, headers={"User-Agent": "entropy-spiral/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        txt = r.read().decode("utf-8", "replace")
    by_year = {}
    for line in txt.strip().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) != 2 or parts[1].strip() in (".", ""):
            continue
        y = int(parts[0][:4])
        if 2019 <= y <= 2024:
            by_year.setdefault(y, []).append(float(parts[1]))
    return {y: sum(v) / len(v) for y, v in by_year.items()}


def wb(ind, code):
    u = (f"https://api.worldbank.org/v2/country/{code}/indicator/{ind}"
         f"?format=json&per_page=200&date=2019:2024")
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "es/1.0"}),
                                        timeout=60) as r:
                j = json.load(r)
            return {int(d["date"]): d["value"] for d in (j[1] or []) if d.get("value") is not None}
        except Exception:
            time.sleep(2 + a * 2)
    return {}


def main():
    socket.setdefaulttimeout(90)
    rows = []
    for name, code in COUNTRIES.items():
        y = fred_monthly(FRED_YIELD[name])
        rg = wb("NY.GDP.MKTP.KD.ZG", code)
        df = wb("NY.GDP.DEFL.KD.ZG", code)
        for yr in range(2020, 2025):
            if yr not in y or yr not in rg:
                continue
            nominal = ((1 + rg[yr] / 100) * (1 + df.get(yr, 0) / 100) - 1) * 100
            rows.append({
                "country": name, "year": yr,
                "yield_10y": round(y[yr], 2),
                "real_growth": round(rg[yr], 2),
                "deflator": round(df.get(yr, float("nan")), 2) if yr in df else "",
                "nominal_growth": round(nominal, 2),
                "r_minus_g": round(y[yr] - nominal, 2),
            })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["country", "year", "yield_10y", "real_growth",
                                          "deflator", "nominal_growth", "r_minus_g"])
        w.writeheader()
        w.writerows(rows)
    print(f"[done] {OUT}  ({len(rows)} rows)")
    # 五年均值汇总
    agg = {}
    for r in rows:
        agg.setdefault(r["country"], []).append(r)
    for c, rs in agg.items():
        yr = sum(x["yield_10y"] for x in rs) / len(rs)
        ng = sum(x["nominal_growth"] for x in rs) / len(rs)
        print(f"  {c}: 10y={yr:.2f}%  nominal_g={ng:.2f}%  r-g={yr-ng:+.2f}pp")


if __name__ == "__main__":
    main()
