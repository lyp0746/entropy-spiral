# -*- coding: utf-8 -*-
"""
术语统一：把 Θ 的主用语统一为"租佃份额"。
规则（上下文感知，避免误伤）：
  - "垄断份额" -> "租佃份额"
  - "垄断×耦合" -> "租佃×耦合"
不改动："反垄断"、"垄断与控制"、"垄断者" 等作为机制的用法。
生成替换日志 analysis/results/glossary_changelog.json。
"""
import json
import os
import re

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(BOOK, "source")
OUT = os.path.join(BOOK, "analysis", "results")
CHAPTERS = [f"ch{i:02d}.html" for i in range(1, 11)]

RULES = [("垄断份额", "租佃份额"), ("垄断×耦合", "租佃×耦合")]
# 术语说明句中的“垄断份额”是有意保留的旧称，不得替换
PROTECT = "“垄断份额”为同义旧称"
MASK = "\x00TERMNOTE\x00"

log = []
for c in CHAPTERS:
    p = os.path.join(CONTENT, c)
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8") as f:
        s = f.read()
    orig = s
    s = s.replace(PROTECT, MASK)
    for a, b in RULES:
        n = s.count(a)
        if n:
            s = s.replace(a, b)
            log.append({"chapter": c, "from": a, "to": b, "count": n})
    s = s.replace(MASK, PROTECT)
    if s != orig:
        with open(p, "w", encoding="utf-8") as f:
            f.write(s)

with open(os.path.join(OUT, "glossary_changelog.json"), "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print("替换日志：")
for r in log:
    print(f"  {r['chapter']}: {r['from']} -> {r['to']} × {r['count']}")
print("总替换：", sum(r["count"] for r in log))
