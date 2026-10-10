# -*- coding: utf-8 -*-
"""
migrate_v12.py — “双轨同版”重构的编号迁移与交叉引用清理脚本。

本轮决定（见重构任务书 §A3）：**保留 ch01—ch15 章号不变**，以避免数百处引用
连锁改动。因此本脚本的“编号映射”是恒等映射；它实际承担三件事：

1. 记录并固化编号映射表 `{旧→新}`（本轮章号恒等；节/表/图编号不变）。
2. 清理“删除第 0 章”后遗留的引用，把它改挂到存留的前置材料
   （《十分钟读懂本书》/《理论地图》）。因该清理已在正文中完成，本脚本用于
   **校验并保证幂等**：再次运行不产生任何变更。
3. 输出变更日志 `analysis/results/migrate_v12.json` 与编号清单，供人工复核。

规则（与任务书一致）：
* 长号优先：替换按“键长度降序”执行，避免 `10.1` 被 `1.1` 污染。
* 跳过 `<code>` / `<pre>` 内的文本，避免误改代码与占位符。
* 幂等：重复运行结果一致（第二次变更数为 0）。
* 纯标准库；Windows Python 用相对路径。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根
SOURCE = os.path.join(HERE, "source")
OUT = os.path.join(HERE, "analysis", "results")

# ---------------------------------------------------------------- 编号映射
# 章号：本轮保持不变（identity）。若将来重排章号，在此填入 {旧: 新} 即可。
CHAPTER_MAP = {str(i): str(i) for i in range(1, 16)}
# 节号 / 表号 / 图号：本轮不迁移。
SECTION_MAP = {}
TABLE_MAP = {}
FIGURE_MAP = {}

# ---------------------------------------------------------------- 文本引用迁移
# “删除第 0 章”后，指向第 0 章的引用改挂到存留的前置材料。
# 键按长度降序替换（长号优先）。
TEXT_MAP = {
    "第 0 章（含图 0.1—0.3）": "十分钟读懂本书（含三个日常故事与图 0.1—0.3）",
    "“十分钟读懂本书”与“第 0 章”": "“十分钟读懂本书”与三个日常故事",
    "第 0 章": "十分钟读懂本书",
}

# 图片文件本身仍保留（图 0.1—0.3 已改挂到《十分钟读懂本书》），仅需保证其被定义。
LEGACY_ANCHORS = ["ch0"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_code(html):
    """把 <code>/<pre> 内容替换为等长占位，保证替换不越界。"""
    def repl(m):
        return "\x00" * len(m.group(0))
    return re.sub(r"<code\b.*?</code>|<pre\b.*?</pre>", repl, html, flags=re.S | re.I)


def ordered_map(d):
    """按“长号优先”返回排序后的 (old, new) 列表。"""
    return sorted(d.items(), key=lambda kv: (-len(kv[0]), kv[0]))


def apply_maps(html, maps):
    """在跳过 <code>/<pre> 的前提下，对 html 施加所有映射，返回 (新 html, 变更列表)。

    做法：把文本切分为“不可替换区”（<code>/<pre>）与“可替换区”，
    只对后者执行长号优先的替换。"""
    parts = []          # [(is_protected, text)]
    pos = 0
    for m in re.finditer(r"<code\b.*?</code>|<pre\b.*?</pre>", html, flags=re.S | re.I):
        if m.start() > pos:
            parts.append((False, html[pos:m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    if pos < len(html):
        parts.append((False, html[pos:]))

    changes = []

    def do_replace(text, mapping, kind):
        for old, new in ordered_map(mapping):
            if old == new:
                continue
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                changes.append({"kind": kind, "from": old, "to": new, "count": n})
        return text

    for i, (protected, text) in enumerate(parts):
        if protected:
            continue
        text = do_replace(text, TEXT_MAP, "text")
        text = do_replace(text, SECTION_MAP, "section")
        text = do_replace(text, TABLE_MAP, "table")
        text = do_replace(text, FIGURE_MAP, "figure")
        parts[i] = (protected, text)

    return "".join(t for _, t in parts), changes


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(f for f in os.listdir(SOURCE)
                   if f.endswith(".html") and (f.startswith("ch") or f.startswith("front") or
                                               f.startswith("appendix") or f.startswith("back")))
    log = {"chapter_map": CHAPTER_MAP, "section_map": SECTION_MAP,
           "table_map": TABLE_MAP, "figure_map": FIGURE_MAP,
           "changes": [], "files_scanned": len(files)}
    total = 0
    for f in files:
        p = os.path.join(SOURCE, f)
        s = load(p)
        new, changes = apply_maps(s, {})
        if changes:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            for c in changes:
                c["file"] = f
            log["changes"].extend(changes)
            total += sum(c["count"] for c in changes)

    # 校验遗留引用
    leftovers = {}
    for f in files:
        s = load(os.path.join(SOURCE, f))
        hits = [pat for pat in LEGACY_ANCHORS if f'id="{pat}"' in s or f"front_{pat}" in s]
        if "front_ch0" in f:
            hits.append("front_ch0")
        for pat in ["第 0 章", "第0章"]:
            if pat in strip_code(s):
                hits.append(pat)
        if hits:
            leftovers[f] = hits

    # 编号清单（图 0.1—0.3 的定义仍在《十分钟读懂本书》）
    fig_defs = []
    for f in files:
        s = load(os.path.join(SOURCE, f))
        for m in re.finditer(r"<b>图\s*(\d+\.\d+)", s):
            fig_defs.append({"figure": m.group(1), "file": f})
    log["figure_definitions"] = fig_defs
    log["leftovers"] = leftovers
    log["total_replacements"] = total
    log["status"] = "no-op (已经迁移，幂等)" if total == 0 else f"applied {total} replacements"

    with open(os.path.join(OUT, "migrate_v12.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print("扫描文件：", log["files_scanned"])
    print("本轮替换数：", total, "（0 表示已迁移，幂等）")
    print("遗留第 0 章引用：", leftovers or "无")
    print("图 0.x 定义位置：", [(d["figure"], d["file"]) for d in fig_defs])
    print("wrote analysis/results/migrate_v12.json")


if __name__ == "__main__":
    sys.exit(main())
