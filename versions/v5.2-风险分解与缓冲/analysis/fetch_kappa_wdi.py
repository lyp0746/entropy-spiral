# -*- coding: utf-8 -*-
"""
fetch_kappa_wdi.py — 从 World Bank WDI 抓取 κ 的真实分量（质量 A）。

本脚本只使用**可公开验证的官方指标**，不写入任何手工估算值：
  NE.TRD.GNFS.ZS   贸易总额（出口+进口）/ GDP      → κ_trade
  EG.IMP.CONS.ZS   净能源进口 / 能源使用            → κ_energy
  TM.VAL.FUEL.ZS.UN 燃料进口 / 商品进口             → κ_fuel
  NE.EXP.GNFS.ZS   出口 / GDP                       → 参考
  NE.IMP.GNFS.ZS   进口 / GDP                       → 参考

重要说明（诚实边界）：
  * 供应链来源集中度（HHI）**不在本脚本内**，因为 WDI 无此指标；
    它需要 UN Comtrade / WITS（API key）或 BACI 批量数据，另行标注质量。
  * 因此本脚本产出的 composite 是"部分 κ"（贸易+能源+燃料），
    不得当作完整 κ 使用；引用时须注明缺 supply concentration 分量。

用法：
  python analysis/fetch_kappa_wdi.py            # 抓取并写 data/kappa_wdi.csv
  python analysis/fetch_kappa_wdi.py --year 2023
"""
import argparse
import json
import os
import socket
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "kappa_wdi.csv")

# WDI 端点接受 ISO3 / WB 聚合码；返回的 country.id 为两位码。
CODES = "USA;CHN;EUU;JPN;IND"
CODE2NAME = {"US": "USA", "CN": "CHN", "EU": "EU", "JP": "JPN", "IN": "IND"}

INDICATORS = {
    "NE.TRD.GNFS.ZS": ("kappa_trade", "贸易总额/GDP (%)"),
    "EG.IMP.CONS.ZS": ("kappa_energy", "净能源进口/能源使用 (%)"),
    "TM.VAL.FUEL.ZS.UN": ("kappa_fuel", "燃料进口/商品进口 (%)"),
    "NE.EXP.GNFS.ZS": ("exports_gdp", "出口/GDP (%)"),
    "NE.IMP.GNFS.ZS": ("imports_gdp", "进口/GDP (%)"),
}


def fetch(indicator, year=None, retries=4):
    """抓取单一指标；year=None 时取最近非空值（mrnev=1）。"""
    date = f"&date={year}" if year else "&mrnev=1"
    url = (f"https://api.worldbank.org/v2/country/{CODES}/indicator/{indicator}"
           f"?format=json&per_page=500{date}")
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "entropy-spiral/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                payload = json.load(r)
            if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
                return []
            rows = []
            for d in payload[1]:
                if d.get("value") is None:
                    continue
                cid = d["country"]["id"]
                rows.append({
                    "country": CODE2NAME.get(cid, cid),
                    "indicator": indicator,
                    "year": int(d["date"]),
                    "value": float(d["value"]),
                })
            return rows
        except Exception as e:  # 网络抖动时重试
            last = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"{indicator} 抓取失败：{type(last).__name__}: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None,
                    help="指定年份；缺省取各指标最近非空年")
    args = ap.parse_args()

    socket.setdefaulttimeout(60)
    all_rows = []
    for code in INDICATORS:
        rows = fetch(code, args.year)
        all_rows.extend(rows)
        print(f"  [ok] {code}: {len(rows)} 行")

    # 透视：country × 分量（最近年份）
    latest = {}
    for r in all_rows:
        key = (r["country"], r["indicator"])
        if key not in latest or r["year"] > latest[key]["year"]:
            latest[key] = r

    by_country = {}
    for (country, code), r in latest.items():
        col = INDICATORS[code][0]
        by_country.setdefault(country, {})[col] = r["value"]
        by_country[country].setdefault("_years", {})[col] = r["year"]

    # 归一化到 [0,1]，用于分量比较（能源净进口可为负 → 截断为 0）
    def norm(v):
        return max(0.0, min(1.0, v / 100.0))

    # 部分 κ：仅贸易(0.5) + 能源(0.3) + 燃料(0.2)。缺失 supply concentration。
    W = {"kappa_trade": 0.5, "kappa_energy": 0.3, "kappa_fuel": 0.2}

    lines = ["country,kappa_trade_pct,kappa_energy_pct,kappa_fuel_pct,"
             "kappa_partial,year_trade,year_energy,year_fuel,data_quality,note"]
    for country in sorted(by_country, key=lambda c: -(
            W["kappa_trade"] * norm(by_country[c].get("kappa_trade", 0))
            + W["kappa_energy"] * norm(by_country[c].get("kappa_energy", 0))
            + W["kappa_fuel"] * norm(by_country[c].get("kappa_fuel", 0)))):
        d = by_country[country]
        parts = [norm(d.get(k, 0)) * w for k, w in W.items()]
        kp = sum(parts)
        yr = d.get("_years", {})
        lines.append(
            f"{country},{d.get('kappa_trade','')},{d.get('kappa_energy','')},"
            f"{d.get('kappa_fuel','')},{kp:.3f},{yr.get('kappa_trade','')},"
            f"{yr.get('kappa_energy','')},{yr.get('kappa_fuel','')},A,"
            f"仅贸易+能源+燃料;缺供应链集中度(HHI)")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n[done] 已写 {OUT}（质量 A，真实序列）")
    print("  注意：kappa_partial 不含供应链集中度，不是完整 κ。\n")
    for row in lines[1:]:
        c = row.split(",")[0]
        print(f"  {c}: partial κ = {row.split(',')[4]}")


if __name__ == "__main__":
    main()
