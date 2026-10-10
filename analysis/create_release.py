# -*- coding: utf-8 -*-
"""create_release.py — 用 GCM 提供的凭据创建 GitHub Release 并上传发布产物。

凭据从 .release_token（git credential fill 的输出）读取，用完即删。
"""
import json
import os
import re
import urllib.parse
import urllib.request

REPO = os.environ.get("RELEASE_REPO", "lyp0746/entropy-spiral")
TAG = os.environ.get("RELEASE_TAG", "edition-2026-10-11")
RELEASE_NAME = os.environ.get("RELEASE_NAME", "2026-10-11")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOKEN_FILE = os.path.join(ROOT, ".release_token")


def read_token():
    txt = open(TOKEN_FILE, encoding="utf-8").read()
    m = re.search(r"password=(.+)", txt)
    return m.group(1).strip()


def api(url, token, data=None, method=None, raw=False, content_type=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "entropy-spiral-release",
    }
    if content_type:
        headers["Content-Type"] = content_type
    body = data
    if isinstance(data, dict):
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def create_release_with_retry(token, body):
    payload = {"tag_name": TAG, "target_commitish": os.environ.get("RELEASE_TARGET", "main"),
               "name": RELEASE_NAME, "body": body, "draft": False, "prerelease": False}
    last = None
    for attempt in range(4):
        try:
            return api(f"https://api.github.com/repos/{REPO}/releases", token,
                       data=payload, method="POST")
        except Exception as e:  # 422 when the freshly pushed tag is not yet indexed
            last = e
            import time
            time.sleep(3 * (attempt + 1))
    raise last


def main():
    token = read_token()
    body = os.environ.get("RELEASE_BODY") or (
        "《错位的时间：为什么我们总是来不及》可发布产物。\n\n"
        "**Desynchronized Time: Why We Are Always Too Late — Temporal Mismatch and the "
        "Boundary of Controllability in Social Systems**\n\n"
        "- `entropy-spiral-print.pdf`　印刷版（A4，宋体+Times，四级书签）\n"
        "- `entropy-spiral-ereader.pdf`　电子阅读版（B5）\n"
        "- `entropy-spiral.epub`　EPUB 3（nav + NCX 四级目录）\n"
        "- `entropy-spiral.html` / `entropy-spiral-ereader.html`　网页版（两版式，自包含）\n"
        "- `entropy-spiral.md`　合并全书 Markdown\n"
        "- `entropy-spiral-markdown.zip`　分文件 Markdown（含 assets/）\n"
        "- `cover.svg`　封面矢量图\n"
        "- `README.md` / `修订说明.md` / `数据缺口清单.md` / `欢迎补充数据.md`　读者文档\n\n"
        "五部分、十九章 + 开篇 + 结语 + **后记** + 附录 A–J；正文与元数据不含版本号，"
        "日期为真实完成日期（2026-10-11）。内容许可 CC BY 4.0，代码许可 MIT。\n\n"
        "本书为双轨同版：共同入口（开篇、前言、十分钟读懂本书、理论地图）之后，"
        "普通读者走“快速路径”（每章“快速理解”与“关键产出”框），"
        "学术与实践读者再走“完整路径”（带 ⚙️ 标记的技术小节与附录工具）。"
        "《理论地图》前置“三类概念（甲／乙／丙）与使用规则”。"
        "第五部分“在不可控中行动”（第 12—19 章）给出时间预算与一次完整演练。\n\n"
        "DOI: https://doi.org/10.5281/zenodo.23286403　·　"
        "概念 DOI: https://doi.org/10.5281/zenodo.23217100"
    )
    rel = create_release_with_retry(token, body)
    upload_url = rel["upload_url"].split("{")[0]
    print("release:", rel["html_url"])

    assets = [
        ("release/entropy-spiral-print.pdf", "application/pdf", "entropy-spiral-print.pdf"),
        ("release/entropy-spiral-ereader.pdf", "application/pdf", "entropy-spiral-ereader.pdf"),
        ("release/entropy-spiral.epub", "application/epub+zip", "entropy-spiral.epub"),
        ("release/entropy-spiral.html", "text/html", "entropy-spiral.html"),
        ("release/entropy-spiral-ereader.html", "text/html", "entropy-spiral-ereader.html"),
        ("release/entropy-spiral.md", "text/markdown", "entropy-spiral.md"),
        ("release/entropy-spiral-markdown.zip", "application/zip", "entropy-spiral-markdown.zip"),
        ("release/cover.svg", "image/svg+xml", "cover.svg"),
        ("release/README.md", "text/markdown", "README.md"),
        # 中文文件名在 GitHub 资产名中易出问题（422 / 被改名为 default.md），统一用 ASCII 名
        ("release/修订说明.md", "text/markdown", "REVISION-NOTES.md"),
        ("release/数据缺口清单.md", "text/markdown", "DATA-GAPS.md"),
        ("release/欢迎补充数据.md", "text/markdown", "CONTRIBUTING-DATA.md"),
    ]
    for path, ctype, name in assets:
        p = os.path.join(ROOT, path)
        if not os.path.exists(p):
            print("  skip (missing):", path)
            continue
        data = open(p, "rb").read()
        url = f"{upload_url}?name={urllib.parse.quote(name)}"
        try:
            res = api(url, token, data=data, method="POST",
                      content_type=ctype)
            print(f"  uploaded: {name} ({len(data)//1024} KB) -> {res.get('browser_download_url','')}")
        except Exception as e:
            print(f"  FAILED: {name}: {e}")


if __name__ == "__main__":
    main()
