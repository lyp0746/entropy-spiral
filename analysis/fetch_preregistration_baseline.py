# -*- coding: utf-8 -*-
"""
fetch_preregistration_baseline.py —— 抓取 B1—B3 的“当前信息快照”。

目的：在登记时（而非事后）给每一项盲测一份**带时间戳与 vintage 的基线**，
使 2027 年的核销有可比对的起点，并让“我真的在监控”成为可观察的事实。

数据源：
  B1 新兴市场融资：World Bank WDI（外储、短债/外储、汇率、证券投资净流入）
  B2 关键矿产：UN Comtrade 公共预览（HS 280530 稀土、283691 锂），计算进口 HHI
  B3 AI 验证：arXiv API（cs.AI/cs.CL 体量与自指查询计数）

失败时**不伪造数值**：把来源写入 unavailable 并给出原因。FRED/IMF 在本环境
常超时，故只登记其应查询的序列，不计入快照。

输出：
  docs/preregistration/baseline_snapshot.json   （完整快照）
  docs/preregistration/registry.json             （更新 baseline 字段）
  docs/preregistration/checkups.csv              （追加 baseline 行）
"""
import csv
import datetime as dt
import json
import os
import sys
import time

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE = os.path.join(HERE, "docs", "preregistration")
SNAP = os.path.join(PRE, "baseline_snapshot.json")
REGISTRY = os.path.join(PRE, "registry.json")
CHECKUPS = os.path.join(PRE, "checkups.csv")

S = requests.Session()
S.headers.update({"User-Agent": "entropy-spiral/1.0 (preregistration baseline)"})
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")

WB = "https://api.worldbank.org/v2"
EM = ["THA", "IDN", "MYS", "PHL", "VNM", "TUR", "ZAF", "BRA", "IND", "MEX"]
WB_IND = {
    "reserves_months_imports": "FI.RES.TOTL.MO",
    "reserves_usd": "FI.RES.TOTL.CD",
    "short_term_debt_pct_reserves": "DT.DOD.DSTC.IR.ZS",
    "official_fx_lcu_per_usd": "PA.NUS.FCRF",
    "portfolio_equity_net_inflow_usd": "BX.PEF.TOTL.CD",
}
CT_REPORTERS = {"USA": "842", "JPN": "392", "IND": "699", "CHN": "156",
                "DEU": "276", "KOR": "410"}
CT_COMMODITIES = {"rare_earth_280530": "280530", "lithium_283691": "283691"}
CT_YEAR = "2023"
ARXIV = "http://export.arxiv.org/api/query"
ARXIV_QUERIES = {
    "cs.AI": "cat:cs.AI",
    "cs.CL": "cat:cs.CL",
    "large_language_model": 'all:"large language model"',
    "GPT": "all:GPT",
}


def retry(fn, n=4, wait=3):
    last = None
    for i in range(n):
        try:
            return fn()
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:80]}"
            time.sleep(wait * (i + 1) / 2)
    raise RuntimeError(last)


# ---------------------------------------------------------------- B1 World Bank
def wb_indicator(ind_code):
    """返回 {iso: {year, value}}，取最近非空值（date 范围放宽后取最新）。"""
    def call():
        r = S.get(f"{WB}/country/{';'.join(EM)}/indicator/{ind_code}",
                  params={"format": "json", "per_page": 2000}, timeout=60)
        r.raise_for_status()
        return r.json()
    js = retry(call)
    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        return {}
    best = {}
    for row in js[1]:
        if row.get("value") is None:
            continue
        iso, yr = row["countryiso3code"], int(row["date"])
        if iso not in best or yr > best[iso]["year"]:
            best[iso] = {"year": yr, "value": row["value"]}
    return best


def fetch_b1():
    out, unavailable = {}, []
    for name, code in WB_IND.items():
        try:
            out[name] = wb_indicator(code)
        except Exception as e:
            unavailable.append({"indicator": name, "source": "World Bank",
                                "reason": str(e)[:120]})
    return {"indicators": out, "unavailable": unavailable}


# ---------------------------------------------------------------- B2 Comtrade
def ct_preview(reporter, cmd, year=CT_YEAR):
    def call():
        r = S.get("https://comtradeapi.un.org/public/v1/preview/C/A/HS",
                  params={"reporterCode": reporter, "period": year,
                          "cmdCode": cmd, "flowCode": "M"}, timeout=60)
        r.raise_for_status()
        return r.json().get("data", [])
    return retry(call)


def hhi(rows):
    by = {}
    for d in rows:
        pc = d.get("partnerCode")
        if pc in (0, "0", None):
            continue
        v = d.get("primaryValue")
        if not v:
            continue
        by[pc] = by.get(pc, 0.0) + float(v)
    total = sum(by.values())
    if total <= 0:
        return None
    sh = {p: v / total for p, v in by.items()}
    h = sum(s * s for s in sh.values())
    tp, ts = max(sh.items(), key=lambda kv: kv[1])
    return {"total_usd": round(total), "hhi": round(h, 4),
            "top_partner_code": tp, "top_share": round(ts, 4), "n_partners": len(by)}


def fetch_b2():
    res, unavailable = {}, []
    for cname, ccode in CT_COMMODITIES.items():
        res[cname] = {}
        for rname, rcode in CT_REPORTERS.items():
            try:
                h = hhi(ct_preview(rcode, ccode))
                if h:
                    res[cname][rname] = h
            except Exception as e:
                unavailable.append({"reporter": rname, "commodity": cname,
                                    "source": "UN Comtrade preview",
                                    "reason": str(e)[:120]})
            time.sleep(0.8)
    return {"year": CT_YEAR, "commodities": res, "unavailable": unavailable}


# ---------------------------------------------------------------- B3 arXiv
def fetch_b3():
    import re
    res, unavailable = {}, []
    for name, q in ARXIV_QUERIES.items():
        try:
            def call():
                r = S.get(ARXIV, params={"search_query": q, "start": 0,
                                         "max_results": 1}, timeout=45)
                r.raise_for_status()
                return r.text
            txt = retry(call)
            m = re.search(r"<opensearch:totalResults[^>]*>(\d+)</opensearch:totalResults>", txt)
            res[name] = {"total_results": int(m.group(1)) if m else None,
                         "query": q}
        except Exception as e:
            unavailable.append({"query": name, "source": "arXiv API",
                                "reason": str(e)[:120]})
    return {"queries": res, "unavailable": unavailable}


def main():
    snapshot = {"generated_at": NOW, "note": "登记时基线快照；失败来源不伪造数值。"}
    for key, fn in (("B1", fetch_b1), ("B2", fetch_b2), ("B3", fetch_b3)):
        print(f"[fetch] {key} ...")
        try:
            snapshot[key] = fn()
        except Exception as e:
            snapshot[key] = {"error": str(e)[:200]}
            print(f"  [FAIL] {key}: {e}")

    # 汇总不可用来源（含已知常超时的 FRED/IMF）
    snapshot["unavailable_note"] = (
        "本环境 FRED/IMF DataMapper 常超时或 403；核销时应补查："
        "FRED DEXTHUS（泰铢汇率）、DGS10、EMBI 利差；IMF IFS 外储与资本流动。")

    os.makedirs(PRE, exist_ok=True)
    with open(SNAP, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"[done] {SNAP}")

    # 更新 registry.json 的 baseline
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    ref = os.path.relpath(SNAP, HERE).replace("\\", "/")
    for t in reg["tests"]:
        b = t.setdefault("baseline", {})
        b["snapshot_ref"] = ref
        b["fetched_at"] = NOW
        if t["id"] == "B1":
            rm = snapshot.get("B1", {}).get("indicators", {}).get("reserves_months_imports", {})
            b["headline"] = {k: rm[k] for k in ("THA", "IDN", "MYS") if k in rm}
        elif t["id"] == "B2":
            re_ = snapshot.get("B2", {}).get("commodities", {}).get("rare_earth_280530", {})
            b["headline"] = {k: re_[k]["hhi"] for k in ("USA", "JPN", "IND") if k in re_}
        elif t["id"] == "B3":
            q = snapshot.get("B3", {}).get("queries", {})
            b["headline"] = {k: q[k]["total_results"] for k in ("cs.AI", "cs.CL") if k in q}
    with open(REGISTRY, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    print(f"[done] 更新 {REGISTRY}")

    # 追加 baseline 行到 checkups.csv（若尚无 generated_at 同名行）
    rows = []
    if os.path.exists(CHECKUPS):
        with open(CHECKUPS, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    have = {r["test_id"] for r in rows if r.get("note", "").startswith("快照")}
    fields = ["test_id", "check_date", "checker", "status", "indicator",
              "value", "unit", "source", "vintage", "triggered", "note"]
    add = []
    for t in reg["tests"]:
        if t["id"] in have:
            continue
        head = json.dumps(t["baseline"].get("headline", {}), ensure_ascii=False)
        add.append({"test_id": t["id"], "check_date": NOW[:10], "checker": "author",
                    "status": "snapshot", "indicator": "基线快照", "value": head,
                    "unit": "见 snapshot", "source": "WB/Comtrade/arXiv",
                    "vintage": NOW[:7], "triggered": "no",
                    "note": "快照基线（见 baseline_snapshot.json）"})
    if add:
        with open(CHECKUPS, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fields)
            w.writerows(add)
        print(f"[done] 追加 {len(add)} 行基线到 {CHECKUPS}")


if __name__ == "__main__":
    main()
