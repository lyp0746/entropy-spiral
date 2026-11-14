# -*- coding: utf-8 -*-
"""从仓库内的 Seshat Equinox 归档重建「政体复杂度—存续」池（第 6 章表 6.1／图 6.1）。

口径（按 Seshat 文献的通行做法，2026-11 重定）
------------------------------------------------
1. **单位是政体，不是政体×时期**。Seshat 为每个政体给出 "Peak Date"，政体级分析取
   Peak Date 那一行（缺则取该政体最后一行）。
2. **排除考古分期**（Complexity = Early）：它们的“存续”是考古学分期长度，不是政体寿命。
3. **排除重复／准政体**（Dupl = y）。
4. 编码按 Seshat 的通行折算：present = 1、inferred present = 0.75、inferred absent = 0.25、
   absent = 0（本脚本从 TSDat123 的数值列直接读，-999 视为缺失）。
5. `s_lawcomposite` = 成文（LegCode）、法院（Court）、法官（Judge）、律师（Lawyer）四项的非缺失均值。

**与 2026-10 发表值不同，这是有意的。** 发表值是逐“政体×时期”取行、且未排除重复政体，得到
n = 205 / 198 / 189、ρ ≈ −0.00 / −0.09 / −0.13。按上面的通行口径重算得 n = 167 / 156 / 148、
ρ ≈ −0.25 / −0.28 / −0.24：方向一致（负），强度明显更强。表 6.1 与正文已按本口径改写（见 CHANGELOG）。

输出：analysis/results/pool_coded.csv

用法：python analysis/build_pool.py && python analysis/complexity_analysis.py
"""
import collections
import os

import numpy as np
import pandas as pd

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BOOK, "data", "Equinox_on_GitHub_June9_2022.xlsx")
OUT = os.path.join(BOOK, "analysis", "results", "pool_coded.csv")

LAW = ("LegCode", "Court", "Judge", "Lawyer")   # 成文、法院、法官、律师


def build():
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, read_only=True)

    pol = [r for r in list(wb["Polities"].iter_rows(values_only=True))[1:] if r[1]]
    info = {r[2]: dict(nga=r[0], comp=r[6], dupl=r[7], start=r[3], end=r[4]) for r in pol}

    ws = wb["Equinox2020_CanonDat"]
    it = ws.iter_rows(values_only=True)
    next(it)
    peak = {}
    for r in it:
        if r[4] == "Peak Date":
            try:
                peak[r[1]] = float(r[5])
            except Exception:
                pass

    ws2 = wb["TSDat123"]
    it2 = ws2.iter_rows(values_only=True)
    hdr = [str(h) for h in next(it2)]
    ix = {h: i for i, h in enumerate(hdr)}
    per = collections.defaultdict(list)
    for r in it2:
        per[r[1]].append(r)

    def num(v):
        try:
            x = float(v)
        except Exception:
            return None
        return None if x == -999 else x

    rows, dropped = [], collections.Counter()
    for pid, rs in per.items():
        h = info.get(pid)
        if not h:
            dropped["未在 Polities 中"] += 1
            continue
        if h["comp"] == "Early":
            dropped["考古分期"] += 1
            continue
        if h["dupl"] == "y":
            dropped["重复／准政体"] += 1
            continue
        try:
            T = float(h["end"]) - float(h["start"])
        except Exception:
            dropped["无年代"] += 1
            continue
        if T <= 0:
            dropped["时长非正"] += 1
            continue
        pick = rs[-1]
        if pid in peak:
            cand = [r for r in rs if num(r[ix["Time"]]) is not None
                    and abs(num(r[ix["Time"]]) - peak[pid]) < 1e-6]
            if cand:
                pick = cand[0]
        law = [num(pick[ix[k]]) for k in LAW]
        law = [x for x in law if x is not None]
        rows.append(dict(polity=pid, NGA=h["nga"], T=T, arch_period=0,
                         adm=num(pick[ix["AdmLev"]]),
                         c_bureau=num(pick[ix["FullTBur"]]),
                         s_lawcomposite=float(np.mean(law)) if law else np.nan,
                         s_main=num(pick[ix["LegCode"]])))

    df = pd.DataFrame(rows)
    # 只保留至少有一个复杂度代理的政体（与图 6.1 的三个面板对应）
    df = df[df[["adm", "c_bureau", "s_lawcomposite"]].notna().any(axis=1)].copy()
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print("wrote", OUT, len(df), "个政体")
    print("  剔除：", dict(dropped))
    for c in ("adm", "c_bureau", "s_lawcomposite"):
        print(f"  {c:16s} n={int(df[c].notna().sum()):3d}")


if __name__ == "__main__":
    build()
