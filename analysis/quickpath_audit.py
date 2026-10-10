# -*- coding: utf-8 -*-
"""
quickpath_audit.py — 双轨“快速路径自洽性”审计器。

双轨设计约定：
  快速路径 = 章首【快速理解】框 + ⚙️ 完整路径标记之前的非技术正文 + 章末【关键产出】框。
  完整路径 = 快速路径 + ⚙️ 之后的全部技术小节 + 附录工具。

本审计回答一个问题：**只读快速路径，能否得到一条自洽（不矛盾、不悬空）的论证？**
它不判断“够不够深”，只判断“有没有断裂”——即关键产出中的每个结论，
是否在快速路径内有至少一句可支撑的陈述。

输出：
  analysis/results/quickpath_audit.json
  快速路径自洽性审计.md

检查项：
  Q1 快速路径字数（与全章对比）
  Q2 关键产出每一项在快速路径中是否有支撑信号（概念词命中）
  Q3 快速路径是否出现“仅在 ⚙️ 中定义”的悬空概念（如首次出现的核心符号无解释）
  Q4 快速路径是否引用了 ⚙️ 之后才出现的小节/表/图（前向引用）
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
OUT = os.path.join(ROOT, "analysis", "results")
GEAR = "⚙️ 完整路径"

# 核心概念及其“解释性关键词”：若快速路径要自洽，关键产出用到该概念时，
# 快速路径内应出现其中至少一个词（解释或定义）。
CONCEPTS = {
    "Θ": ["租佃", "垄断", "剩余", "抽取"],
    "I": ["协调", "制度", "组织", "反应时间", "协调时间"],
    "κ": ["耦合", "传导", "依赖"],
    "V": ["脆弱", "应变", "冲击"],
    "τ": ["时间错配", "可容许时间", "来得及"],
    "C": ["可控性", "来得及", "窗口"],
    "ι": ["一致性", "政治"],
}


def strip_tags(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h))


def read(f):
    with open(os.path.join(SRC, f), encoding="utf-8") as fh:
        return fh.read()


def extract_box(s, marker):
    """取形如 <div class="note"><b>本章的关键产出…</b>…</div> 的框文本。"""
    m = re.search(r'<div class="(?:note|scenario)">.*?</div>', s, re.S)
    return m.group(0) if m else ""


def find_box(s, starts_with):
    """找到 <div class="..."> 内 <b> 文本以 starts_with 开头的框。"""
    for m in re.finditer(r'<div class="(?:note|scenario)">(.*?)</div>', s, re.S):
        if starts_with in strip_tags(m.group(1))[:40]:
            return m.group(0)
    return ""


def key_output_items(s):
    box = find_box(s, "本章的关键产出")
    if not box:
        return []
    items = re.findall(r"<li>(.*?)</li>", box, re.S)
    return [re.sub(r"\s+", " ", strip_tags(i)).strip() for i in items]


def main():
    os.makedirs(OUT, exist_ok=True)
    chapters = sorted(f for f in os.listdir(SRC) if re.fullmatch(r"ch\d+\.html", f))
    report = {"chapters": []}
    for f in chapters:
        s = read(f)
        total = strip_tags(s)
        # 快速路径：⚙️ 之前的正文
        idx = s.find(GEAR)
        fast_html = s[:idx] if idx > 0 else s
        scen = find_box(s, "快速理解")
        ko = find_box(s, "本章的关键产出")
        fast_text = strip_tags(fast_html) + "\n" + strip_tags(scen) + "\n" + strip_tags(ko)

        items = key_output_items(s)
        # Q2：每个关键产出条目的概念词覆盖
        item_check = []
        for it in items:
            hit = {}
            for sym, words in CONCEPTS.items():
                if sym in it or any(w in it for w in words):
                    hit[sym] = any(w in fast_text for w in words) or (sym in fast_text)
            missing = [sym for sym, ok in hit.items() if not ok]
            item_check.append({"item": it[:80], "concepts": list(hit), "unsupported": missing})

        # Q3：快速路径中首次出现、但解释只在 ⚙️ 后的核心符号
        full_text = strip_tags(s)
        undefined = []
        for sym, words in CONCEPTS.items():
            if sym in fast_text and not any(w in fast_text for w in words):
                undefined.append(sym)

        # Q4：快速路径（含关键产出）中的前向引用
        # 抓取引用对象（定义/表/图/式/节），判断其“定义位置”是否位于 ⚙️ 之后。
        refs = set()
        for pat in [r"定义\s*(\d+\.\d+)", r"表\s*(\d+\.\d+)", r"图\s*(\d+\.\d+)",
                    r"式\((\d+\.\d+)\)", r"§\s*(\d+\.\d+)", r"第\s*(\d+\.\d+)\s*节"]:
            refs.update(re.findall(pat, fast_text))
        # 每个对象在全文中的首次出现位置
        first_pos = {}
        for kind, pat in [("def", r"定义\s*(\d+\.\d+)"), ("tab", r'<caption class="cap"><b>表\s*(\d+\.\d+)'),
                          ("fig", r'<b>图\s*(\d+\.\d+)'), ("eq", r'<span class="num">\((\d+\.\d+)\)</span>'),
                          ("sec", r'<h[34][^>]*>\s*(\d+\.\d+)')]:
            for m in re.finditer(pat, s):
                first_pos.setdefault(m.group(1), m.start() if idx < 0 else min(m.start(), first_pos.get(m.group(1), 10**9)))
        fwd = sorted(r for r in refs if r in first_pos and idx > 0 and first_pos[r] >= idx)

        report["chapters"].append({
            "file": f,
            "fast_chars": len(fast_text),
            "full_chars": len(full_text),
            "fast_ratio": round(len(fast_text) / max(1, len(full_text)), 3),
            "key_output_items": item_check,
            "undefined_concepts": sorted(set(undefined)),
            "forward_refs_into_gear": sorted(set(fwd)),
            "has_declaration": "完整路径补充" in fast_text,
        })

    with open(os.path.join(OUT, "quickpath_audit.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    # Markdown 报告
    L = ["# 快速路径自洽性审计\n",
         "自动生成。快速路径 = 章首【快速理解】+ ⚙️ 之前正文 + 章末【关键产出】。",
         "本表只标记“断裂”（前向引用、未解释符号），不评价“深浅”。\n",
         "| 章 | 快速/全章字数 | 占比 | 快速路径未解释的符号 | 指向 ⚙️ 之后的前向引用 | 判定 |",
         "|---|---:|---:|---|---|---|"]
    n_break = 0
    for c in report["chapters"]:
        fwd = c["forward_refs_into_gear"]
        und = c["undefined_concepts"]
        declared = c.get("has_declaration")
        if declared:
            verdict = "已声明"
        elif fwd or und:
            verdict = "需补声明"
            n_break += 1
        else:
            verdict = "自洽"
        L.append(f"| {c['file']} | {c['fast_chars']}/{c['full_chars']} | {c['fast_ratio']:.0%} | "
                 f"{', '.join(und) or '—'} | "
                 f"{', '.join(fwd) or '—'} | {verdict} |")
    L.append(f"\n**仍需补声明的章：{n_break}/{len(report['chapters'])}**（已声明 = 关键产出框内已给出“完整路径补充”声明）\n")
    with open(os.path.join(ROOT, "快速路径自洽性审计.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    print("chapters:", len(report["chapters"]))
    print("chapters needing declaration:", n_break)
    print("wrote analysis/results/quickpath_audit.json + 快速路径自洽性审计.md")


if __name__ == "__main__":
    sys.exit(main())
