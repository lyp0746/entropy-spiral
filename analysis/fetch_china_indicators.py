# -*- coding: utf-8 -*-
"""
fetch_china_indicators.py —— 抓取中国（CHN）的 Θ/κ 相关开放指标。

目的：为书中“中国耦合结构与抽取结构”提供可复现的 A/B 级开放数据；
覆盖 World Bank WDI（贸易/外资/信贷/Gini/制造业/宽带）与 UN Comtrade
（关键商品进口来源 HHI）。缺口（如中国广义政府债务/GDP 无开放 WDI 序列）
**不伪造**，在 unavailable 中列明。

输出：data/china_indicators.json
用法：python analysis/fetch_china_indicators.py
"""
import datetime as dt
import json
import os
import time

import requests

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "china_indicators.json")

S = requests.Session()
S.headers.update({"User-Agent": "entropy-spiral/1.0 (china indicators)"})
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")

WB = "https://api.worldbank.org/v2"
CT = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"

WB_IND = {
    "trade_pct_gdp": "NE.TRD.GNFS.ZS",
    "exports_pct_gdp": "NE.EXP.GNFS.ZS",
    "imports_pct_gdp": "NE.IMP.GNFS.ZS",
    "fdi_net_inflow_pct_gdp": "BX.KLT.DINV.WD.GD.ZS",
    "private_credit_pct_gdp": "FS.AST.PRVT.GD.ZS",
    "gini": "SI.POV.GINI",
    "manufacturing_pct_gdp": "NV.IND.MANF.ZS",
    "gross_capital_formation_pct_gdp": "NE.GDI.TOTL.ZS",
    "internet_users_pct": "IT.NET.USER.ZS",
    "broadband_per100": "IT.NET.BBND.P2",
}
CT_COMMODITIES = {
    "chips_854231": "854231",
    "rare_earth_280530": "280530",
    "iron_ore_260111": "260111",
    "crude_oil_270900": "270900",
    "soybean_120190": "120190",
}


def retry(fn, n=5, wait=5):
    last = None
    for i in range(n):
        try:
            return fn()
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
            time.sleep(wait)
    raise RuntimeError(last)


def wb(ind):
    def call():
        r = S.get(f"{WB}/country/CHN/indicator/{ind}",
                  params={"format": "json", "per_page": 200, "date": "1990:2024"}, timeout=60)
        r.raise_for_status()
        return r.json()
    js = retry(call)
    rows = [(int(x["date"]), x["value"]) for x in (js[1] or []) if x.get("value") is not None]
    rows.sort()
    return rows


def ct_hhi(cmd, year="2023"):
    def call():
        r = S.get(CT, params={"reporterCode": "156", "period": year,
                              "cmdCode": cmd, "flowCode": "M"}, timeout=60)
        if r.status_code == 429:
            raise RuntimeError("HTTP 429 (rate limited)")
        r.raise_for_status()
        return r.json().get("data", [])
    data = retry(call)
    names = {d.get("partnerCode"): d.get("partnerDesc") for d in data}
    by = {}
    for d in data:
        pc = d.get("partnerCode")
        v = d.get("primaryValue")
        if pc in (0, "0", None) or not v:
            continue
        by[pc] = by.get(pc, 0.0) + float(v)
    tot = sum(by.values())
    if tot <= 0:
        return None
    sh = {p: v / tot for p, v in by.items()}
    hhi = sum(s * s for s in sh.values())
    tp, ts = max(sh.items(), key=lambda kv: kv[1])
    return {"year": year, "hhi": round(hhi, 3), "top_partner": names.get(tp, tp),
            "top_share": round(ts, 3), "n_partners": len(by)}


def main():
    snap = {"generated_at": NOW, "note": "中国开放指标；失败/缺口不伪造。"}
    wb_out, unavailable = {}, []
    for name, code in WB_IND.items():
        print(f"[WB] {name} ...")
        try:
            wb_out[name] = wb(code)
        except Exception as e:
            unavailable.append({"indicator": name, "code": code, "reason": str(e)[:120]})
    snap["worldbank"] = wb_out

    ct_out = {}
    for name, code in CT_COMMODITIES.items():
        print(f"[Comtrade] {name} ...")
        try:
            ct_out[name] = ct_hhi(code)
        except Exception as e:
            unavailable.append({"commodity": name, "code": code, "source": "Comtrade", "reason": str(e)[:120]})
        time.sleep(3)
    snap["comtrade_import_hhi"] = ct_out

    snap["unavailable"] = unavailable
    snap["known_gap"] = ("中国广义政府债务/GDP 无 WB WDI 开放序列；IMF WEO 在本环境常超时，"
                         "故不填入，标注为数据缺口而非伪造。")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=2)
    print(f"[done] {OUT}")


if __name__ == "__main__":
    main()
