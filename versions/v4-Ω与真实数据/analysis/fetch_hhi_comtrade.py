# -*- coding: utf-8 -*-
"""
fetch_hhi_comtrade.py — 从 UN Comtrade 拉取按来源国分解的进口额，计算集中度 HHI。

目标：把"供应链集中度"从指示性（质量 C）升级为**可复现的真实数据（质量 A）**。
商品（HS 6 位）：
  8542    集成电路（芯片）
  2709    原油
  280530  稀土金属（HS2017；若不可用回退到 2805）

进口方（Comtrade reporterCode）：
  156 中国 / 842 美国 / 392 日本 / 699 印度 / 97 欧盟（若可用）

输出：data/hhi_chokepoints.csv
  reporter, commodity, year, total_value_usd, hhi, top_partner_code,
  top_share, n_partners, source

HHI = Σ (来源国份额)²，范围 (0,1]；越高越集中。
"""
import csv
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "hhi_chokepoints.csv")
ENVFILE = os.path.join(HERE, ".env.comtrade")

REPORTERS = {"CHN": "156", "USA": "842", "JPN": "392", "IND": "699"}
COMMODITIES = {"chips": "8542", "crude_oil": "2709", "rare_earth": "280530"}
YEAR = "2023"
BASE = "https://comtradeapi.un.org/data/v1/get/C/A/HS"


def load_keys():
    keys = []
    if os.environ.get("COMTRADE_KEY"):
        keys.append(os.environ["COMTRADE_KEY"])
    if os.path.exists(ENVFILE):
        for line in open(ENVFILE, encoding="utf-8"):
            line = line.strip()
            if line.startswith("COMTRADE_KEY") and "=" in line:
                keys.append(line.split("=", 1)[1].strip())
    # 去重保序
    seen, out = set(), []
    for k in keys:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    if not out:
        raise SystemExit("未找到 Comtrade 密钥：请设置 COMTRADE_KEY 或创建 .env.comtrade")
    return out


KEYS = load_keys()


def fetch(reporter, cmd, year=YEAR, retries=3):
    """拉取某 reporter × cmd 的全部伙伴行。"""
    params = {"reporterCode": reporter, "period": year, "cmdCode": cmd,
              "flowCode": "M", "partner2Code": "0", "customsCode": "C00", "motCode": "0"}
    url = BASE + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        key = KEYS[attempt % len(KEYS)]
        req = urllib.request.Request(url, headers={
            "Ocp-Apim-Subscription-Key": key, "User-Agent": "entropy-spiral/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r).get("data", [])
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (401, 403, 429):
                time.sleep(3 + attempt * 3)
            else:
                time.sleep(2)
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(3)
    raise RuntimeError(f"{reporter}/{cmd} 拉取失败：{last}")


def hhi_from_rows(rows):
    """按 partnerCode 汇总 primaryValue，计算 HHI 与首位份额。"""
    by_partner = {}
    for d in rows:
        # 仅保留标准口径（partner2=0, customs=C00, mot=0），避免重复计数
        if str(d.get("partner2Code")) not in ("0", "None") and d.get("partner2Code") is not None:
            continue
        if d.get("customsCode") not in (None, "C00"):
            continue
        if str(d.get("motCode")) not in ("0", "None") and d.get("motCode") is not None:
            continue
        v = d.get("primaryValue")
        if not v:
            continue
        pc = d.get("partnerCode")
        if pc in (0, "0"):        # World 合计，跳过
            continue
        by_partner[pc] = by_partner.get(pc, 0.0) + float(v)
    total = sum(by_partner.values())
    if total <= 0:
        return None
    shares = {p: v / total for p, v in by_partner.items()}
    hhi = sum(s * s for s in shares.values())
    top_p, top_s = max(shares.items(), key=lambda kv: kv[1])
    return {"total": total, "hhi": hhi, "top_partner": top_p,
            "top_share": top_s, "n": len(by_partner)}


def main():
    socket.setdefaulttimeout(90)
    rows_out = []
    for cname, ccode in COMMODITIES.items():
        for rname, rcode in REPORTERS.items():
            try:
                data = fetch(rcode, ccode)
                res = hhi_from_rows(data)
                if not res:
                    print(f"  [skip] {rname}/{cname}: 无有效行")
                    continue
                rows_out.append({
                    "reporter": rname, "commodity": cname, "year": YEAR,
                    "total_value_usd": round(res["total"], 0),
                    "hhi": round(res["hhi"], 4),
                    "top_partner_code": res["top_partner"],
                    "top_share": round(res["top_share"], 4),
                    "n_partners": res["n"],
                    "source": "UN Comtrade (comtradeapi.un.org), HS-6, imports",
                })
                print(f"  [ok] {rname}/{cname}: HHI={res['hhi']:.3f} "
                      f"top={res['top_partner']} ({res['top_share']*100:.1f}%) total=${res['total']/1e9:.1f}B")
            except Exception as e:
                print(f"  [FAIL] {rname}/{cname}: {e}")
            time.sleep(1.2)  # 尊重速率限制

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fields = ["reporter", "commodity", "year", "total_value_usd", "hhi",
              "top_partner_code", "top_share", "n_partners", "source"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)
    print(f"\n[done] 已写 {OUT}（{len(rows_out)} 行，质量 A）")


if __name__ == "__main__":
    main()
