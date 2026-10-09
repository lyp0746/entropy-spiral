# -*- coding: utf-8 -*-
"""
fetch_seshat.py — 从 Seshat Equinox 2020 数据集中抽取中国政体序列。

产物
----
  data/seshat_cn_polities.csv   中国（汉语系）政体的起止年与存续时长
  data/seshat_cn_summary.json   汇总统计（均值、标准差、变异系数、趋势）

用法
----
  python analysis/fetch_seshat.py
"""
import csv
import json
import os
import statistics

import openpyxl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
XLSX = os.path.join(DATA, "Equinox_on_GitHub_June9_2022.xlsx")

# 帝国期（秦汉以降、以统一/半统一王朝为主）——用于“治乱循环”时长分析
IMPERIAL = [
    ("秦／西汉", "Western Han", -202, 9),
    ("东汉", "Eastern Han", 25, 219),
    ("西晋", "Western Jin", 265, 317),
    ("北魏", "Northern Wei", 386, 557),
    ("隋", "Sui Dynasty", 581, 617),
    ("唐（前期）", "Early Tang Dynasty", 618, 762),
    ("唐（后期）", "Later Tang Dynasty", 763, 907),
    ("北宋", "Northern Song", 960, 1126),
    ("金（后期）", "Later Jin", 1127, 1234),
    ("元", "Yuan Dynasty", 1271, 1367),
    ("明", "Ming Dynasty", 1368, 1643),
    ("清（前期）", "Early Qing", 1644, 1795),
    ("清（后期）", "Late Qing", 1796, 1912),
]


def read_polities():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Polities"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h) if h is not None else "" for h in rows[0]]
    idx = {h: i for i, h in enumerate(hdr)}
    out = []
    for r in rows[1:]:
        if not r or r[idx["PolName"]] is None:
            continue
        genus = (r[idx["Genus"]] or "") if "Genus" in idx else ""
        lang = (r[idx["Language"]] or "") if "Language" in idx else ""
        if genus != "Chinese" and lang != "Chinese":
            continue
        try:
            start, end = float(r[idx["Start"]]), float(r[idx["End"]])
        except (TypeError, ValueError):
            continue
        out.append({
            "NGA": r[idx["NGA"]], "PolName": r[idx["PolName"]],
            "PolID": r[idx["PolID"]], "Start": int(start), "End": int(end),
            "Duration": int(end - start),
            "Complexity": r[idx["Complexity"]],
            "WorldRegion": r[idx["World Region"]],
        })
    return out


def main():
    pol = read_polities()
    by_name = {p["PolName"]: p for p in pol}
    imperial = []
    for label, polname, s, e in IMPERIAL:
        if polname in by_name:
            p = dict(by_name[polname])
            p["Label"] = label
            imperial.append(p)

    with open(os.path.join(DATA, "seshat_cn_polities.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["政权/时期", "Seshat PolName", "起始年", "终止年", "存续年", "复杂度", "NGA"])
        for p in imperial:
            w.writerow([p["Label"], p["PolName"], p["Start"], p["End"],
                        p["Duration"], p["Complexity"], p["NGA"]])
        # 附加非帝国期（先秦）样本，便于对照
        for p in sorted(pol, key=lambda x: x["Start"]):
            if p["PolName"] in {n for _, n, _, _ in IMPERIAL}:
                continue
            w.writerow([p["PolName"], p["PolName"], p["Start"], p["End"],
                        p["Duration"], p["Complexity"], p["NGA"]])

    durs = [p["Duration"] for p in imperial]
    starts = [p["Start"] for p in imperial]
    summary = {
        "n": len(durs),
        "mean_duration": round(statistics.mean(durs), 1),
        "sd_duration": round(statistics.stdev(durs), 1),
        "cv": round(statistics.stdev(durs) / statistics.mean(durs), 3),
        "min": min(durs), "max": max(durs),
        "median": statistics.median(durs),
        "series": [{"label": p["Label"], "start": p["Start"], "duration": p["Duration"]}
                   for p in imperial],
        "note": "Seshat 以‘政体’（polity）为单元，唐、清被拆为前后两段；"
                "因此时长不含统一王朝的完整跨度。变异系数用于说明‘周期’不稳定。",
    }
    with open(os.path.join(DATA, "seshat_cn_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("wrote data/seshat_cn_polities.csv")
    print("wrote data/seshat_cn_summary.json")
    print(json.dumps({k: v for k, v in summary.items() if k != "series"},
                     ensure_ascii=False, indent=2))
    for s in summary["series"]:
        print(f"  {s['label']:<10} {s['start']:>6}  {s['duration']:>4}")


if __name__ == "__main__":
    main()
