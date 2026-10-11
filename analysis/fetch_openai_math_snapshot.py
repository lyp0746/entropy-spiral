# -*- coding: utf-8 -*-
"""
fetch_openai_math_snapshot.py —— 抓取 B3 触发事件（openai/math）的快照。

背景：第 11.7.1 节盲测 B3 的触发条件是“任一机构批量发布 >100 篇 AI 生成的
数学／科学初稿”。2026-10-06，OpenAI 在 GitHub 公开 `openai/math` 仓库，
发布 719 篇数学手稿（372 个结果家族、17 个数学领域）。本脚本把该事件固化为
**带时间戳的机器快照**，供 2027 年核销比对。

诚实性说明（重要）：
  该触发事件发生在本书首次提交（2026-10-09）与登记表（2026-10-11）之前，
  因此 B3 **不是对“触发”的事前盲测**，而是对**结果**（热度窗口内完成独立
  验证的比例）的前瞻预测。脚本与快照均记录这一时点差异，不掩盖。

数据源：
  GitHub REST API（openai/math：元数据、README、history、overview.tex）
  arXiv API（cs.AI / cs.CL 体量，B3 基线）

失败时不伪造数值：写入 unavailable 并给出原因。

输出：
  docs/preregistration/openai_math_snapshot.json
"""
import datetime as dt
import json
import os
import re
import sys
import time

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE = os.path.join(HERE, "docs", "preregistration")
OUT = os.path.join(PRE, "openai_math_snapshot.json")

S = requests.Session()
S.headers.update({"User-Agent": "entropy-spiral/1.0 (B3 trigger snapshot)",
                  "Accept": "application/vnd.github+json"})
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")

GH = "https://api.github.com/repos/openai/math"
RAW = "https://raw.githubusercontent.com/openai/math/main"
ARXIV = "http://export.arxiv.org/api/query"
ARXIV_QUERIES = {"cs.AI": "cat:cs.AI", "cs.CL": "cat:cs.CL"}

# 登记的触发条件（取自第 11.7.1 节 / registry.json，不得回改）
REGISTERED_TRIGGER = "任一机构批量发布 >100 篇 AI 生成的数学／科学初稿"


def retry(fn, n=4, wait=3):
    last = None
    for i in range(n):
        try:
            return fn()
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:100]}"
            time.sleep(wait * (i + 1) / 2)
    raise RuntimeError(last)


def gh_meta():
    def call():
        r = S.get(GH, timeout=45)
        r.raise_for_status()
        return r.json()
    d = retry(call)
    keep = ["full_name", "html_url", "description", "created_at", "pushed_at",
            "updated_at", "size", "stargazers_count", "forks_count",
            "subscribers_count", "open_issues_count", "default_branch"]
    out = {k: d.get(k) for k in keep}
    lic = d.get("license") or {}
    out["license"] = lic.get("spdx_id")
    return out


def gh_raw(path):
    def call():
        r = S.get(f"{RAW}/{path}", timeout=60)
        r.raise_for_status()
        return r.text
    return retry(call)


def parse_counts(readme, history, contents=""):
    """从 README / history / CONTENTS 解析手稿数、家族数、形式化比例与撤回修订数。"""
    out = {}
    m = re.search(r"(\d+)\s+manuscripts", readme)
    if m:
        out["manuscripts_readme"] = int(m.group(1))
    m = (re.search(r"(\d+)\s+result families", contents)
         or re.search(r"(\d+)\s+families", readme)
         or re.search(r"(\d+)\s+result families", readme))
    if m:
        out["families"] = int(m.group(1))
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*=\s*~?(\d+)%", history)
    if m:
        out["formalized_topline"] = int(m.group(1))
        out["formalized_denom"] = int(m.group(2))
        out["formalized_pct"] = int(m.group(3))
    m = re.search(r"withdrawn the following (\w+) manuscripts", history)
    if m:
        out["withdrawn_2026_10_07"] = {"three": 3, "one": 1}.get(m.group(1))
    m = re.search(r"revised (\d+) other manuscripts", history)
    if m:
        out["revised_2026_10_07"] = int(m.group(1))
    m = re.search(r"updated (\d+) additional manuscripts", history)
    if m:
        out["citation_updates_2026_10_07"] = int(m.group(1))
    m = re.search(r"additional (\d+) formalizations", history)
    if m:
        out["formalizations_added_2026_10_07"] = int(m.group(1))
    return out


def parse_subjects(overview_tex):
    """从 overview.tex 的 \\cataloguesection{学科}{编号} 解析数学领域（17 个）。"""
    subs = re.findall(r"\\cataloguesection\{([^}]+)\}\{(\d+)\}", overview_tex)
    seen, out = set(), []
    for name, _ in subs:
        n = name.strip()
        if n.lower() not in seen:
            seen.add(n.lower())
            out.append(n)
    return out


def arxiv_counts():
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
            res[name] = int(m.group(1)) if m else None
        except Exception as e:
            unavailable.append({"query": name, "reason": str(e)[:120]})
    return {"queries": res, "unavailable": unavailable}


def main():
    snap = {
        "generated_at": NOW,
        "event": "openai/math 公开发布",
        "registered_trigger": REGISTERED_TRIGGER,
        "pre_registration_caveat": (
            "触发事件（2026-10-06）早于本书首次提交（2026-10-09）与登记表"
            "（2026-10-11）。故 B3 不是对触发的事前盲测，而是对结果"
            "（热度窗口内完成独立验证的比例）的前瞻预测；核销时按此口径报告。"
        ),
        "note": "机器快照；失败来源不伪造数值。",
    }
    errs = []

    print("[fetch] GitHub 元数据 ...")
    try:
        snap["repo"] = gh_meta()
    except Exception as e:
        errs.append({"step": "repo", "reason": str(e)[:150]})

    print("[fetch] README / history / overview.tex ...")
    readme = history = overview_tex = contents = ""
    for path, key in (("README.md", "readme"), ("history.md", "history"),
                      ("overview.tex", "overview_tex"), ("CONTENTS.md", "contents")):
        try:
            v = gh_raw(path)
            if key == "readme":
                readme = v
            elif key == "history":
                history = v
            elif key == "overview_tex":
                overview_tex = v
            else:
                contents = v
        except Exception as e:
            errs.append({"step": path, "reason": str(e)[:150]})

    snap["counts"] = parse_counts(readme, history, contents)
    snap["subjects"] = parse_subjects(overview_tex)
    snap["n_subjects"] = len(snap["subjects"])

    # 保存可审计的原始证据（README/history），供人工复核
    ev = os.path.join(HERE, "data", "oaimath")
    os.makedirs(ev, exist_ok=True)
    for name, txt in (("README.md", readme), ("history.md", history)):
        if txt:
            with open(os.path.join(ev, name), "w", encoding="utf-8") as f:
                f.write(txt)

    print("[fetch] arXiv 体量 ...")
    snap["arxiv"] = arxiv_counts()

    snap["unavailable"] = errs
    os.makedirs(PRE, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=2)
    print(f"[done] {OUT}")
    print(json.dumps({k: snap[k] for k in ("counts", "n_subjects")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
