# -*- coding: utf-8 -*-
"""
export_figures.py — 把 assets/svg/*.svg 导出为高分辨率 PNG（约 300 dpi 备份）。

用无头 Chrome/Edge 渲染，输出到 output/figures/。供投稿或印刷备用。

用法：python analysis/export_figures.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "assets", "svg")
OUT = os.path.join(HERE, "output", "figures")
TMP = os.path.join(HERE, ".tmpfig")

W = 1800  # 约 300 dpi @ 145mm 宽

CHROME_CANDS = [
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def winpath(p):
    if os.name == "nt":
        return p.replace("/", "\\")
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        return p[5].upper() + ":" + p[6:].replace("/", "\\")
    return p


def main():
    browser = next((c for c in CHROME_CANDS if os.path.exists(c)), None)
    if not browser:
        print("未找到 Chrome/Edge，跳过导出")
        return
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for name in sorted(os.listdir(SVG)):
        if not name.endswith(".svg"):
            continue
        with open(os.path.join(SVG, name), encoding="utf-8") as f:
            head = f.read(400)
        m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', head)
        vw, vh = (float(m.group(1)), float(m.group(2))) if m else (1000.0, 620.0)
        h = int(W * vh / vw)
        stem = name[:-4]
        html = os.path.join(TMP, stem + ".html")
        with open(html, "w", encoding="utf-8") as f:
            f.write(
                '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
                "html,body{margin:0;padding:0}img{width:%dpx;display:block}</style></head>"
                '<body><img src="file:///%s"></body></html>'
                % (W, os.path.join(SVG, name).replace("\\", "/"))
            )
        out = os.path.join(OUT, stem + ".png")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--window-size={W},{h}",
                        f"--screenshot={winpath(out)}",
                        "file:///" + winpath(html).replace("\\", "/")],
                       check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("  ", stem + ".png", f"({W}x{h})")
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    os.rmdir(TMP)
    print("导出完成：output/figures/")


if __name__ == "__main__":
    main()
