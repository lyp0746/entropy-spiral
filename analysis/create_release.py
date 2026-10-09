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
TAG = os.environ.get("RELEASE_TAG", "edition-2026-10-09")
RELEASE_NAME = os.environ.get("RELEASE_NAME", "初版（2026-10-09）")
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
        "《错位的时间》可发布产物。\n\n"
        "- `entropy-spiral-print.pdf`　印刷版（A4，宋体+Times，四级书签）\n"
        "- `entropy-spiral-ereader.pdf`　电子阅读版（B5）\n"
        "- `entropy-spiral.epub`　EPUB 3（nav + NCX 四级目录）\n"
        "- `cover.svg`　封面矢量图\n\n"
        "五部分、十五章 + 开篇 + 结语 + **后记** + 附录 A–H；正文与元数据不含版本号，"
        "日期为真实完成日期。内容许可 CC BY 4.0，代码许可 MIT。\n\n"
        "本修订新增：§11.9 操作检验流程、§13.11 学习滞后（二阶时间错配）、"
        "后记《方法论的自限性与伦理立场》。"
    )
    rel = create_release_with_retry(token, body)
    upload_url = rel["upload_url"].split("{")[0]
    print("release:", rel["html_url"])

    assets = [
        ("release/entropy-spiral-print.pdf", "application/pdf"),
        ("release/entropy-spiral-ereader.pdf", "application/pdf"),
        ("release/entropy-spiral.epub", "application/epub+zip"),
        ("release/cover.svg", "image/svg+xml"),
    ]
    for path, ctype in assets:
        p = os.path.join(ROOT, path)
        if not os.path.exists(p):
            print("  skip (missing):", path)
            continue
        name = os.path.basename(path)
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
