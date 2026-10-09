# -*- coding: utf-8 -*-
"""
fetch_debt_gdp.py — 五国广义政府总债务/GDP（IMF WEO 序列，经 FRED 发布，质量 A）。

背景：IMF DataMapper API 在本机被 403 拦截；FRED 以 CSV 形式免费镜像
IMF WEO 的“General Government Gross Debt (% of GDP)”序列，故改用此路径，
数据源仍为 IMF WEO。

输出：data/debt_gdp.csv
  country, year, debt_gdp
"""
import csv
import os
import socket
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "debt_gdp.csv")
SERIES = {
    "USA": "GGGDTAUSA188N",
    "JPN": "GGGDTAJPA188N",
    "DEU": "GGGDTADEA188N",
    "GBR": "GGGDTAGBA188N",
    "MEX": "GGGDTAMXA188N",
}


def fred(sid):
    u = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    req = urllib.request.Request(u, headers={"User-Agent": "entropy-spiral/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        txt = r.read().decode("utf-8", "replace")
    out = {}
    for line in txt.strip().splitlines()[1:]:
        p = line.split(",")
        if len(p) == 2 and p[1].strip() not in (".", ""):
            y = int(p[0][:4])
            if 2020 <= y <= 2024:
                out[y] = float(p[1])
    return out


def main():
    socket.setdefaulttimeout(90)
    rows = []
    for c, sid in SERIES.items():
        for y, v in sorted(fred(sid).items()):
            rows.append({"country": c, "year": y, "debt_gdp": round(v, 1)})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["country", "year", "debt_gdp"])
        w.writeheader()
        w.writerows(rows)
    print(f"[done] {OUT}")
    for c in SERIES:
        r = {x["year"]: x["debt_gdp"] for x in rows if x["country"] == c}
        print(f"  {c}: {r}")


if __name__ == "__main__":
    main()
