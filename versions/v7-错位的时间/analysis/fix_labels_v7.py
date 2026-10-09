# -*- coding: utf-8 -*-
"""fix_labels_v7.py — 迁移后处理：把"案例/警告/命题/情景/推论 X.Y.Z"标签、
以及"第 X.Y、Z.W 节"这类多节引用，按同一张章节映射表改写。"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "source")
MAP = {1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 11,
       10: 12, 11: 10, 12: 4, 13: 13, 14: 14, 15: 15}


def fix(text):
    # 标签：案例 12.3.1 / 警告 12.7.1 / 命题 15.1 / 情景 11.8.1
    def lab(m):
        ch = MAP.get(int(m.group(2)), int(m.group(2)))
        return f"{m.group(1)} {ch}.{m.group(3)}" + (m.group(4) or "")
    text = re.sub(r'(案例|警告|命题|情景|推论)\s*(\d+)\.(\d+)(\.\d+)?', lab, text)
    # 多节引用：第 3.8、5.4 节
    def multi(m):
        a = MAP.get(int(m.group(1)), int(m.group(1)))
        b = MAP.get(int(m.group(3)), int(m.group(3)))
        return f"第 {a}.{m.group(2)}、{b}.{m.group(4)} 节"
    text = re.sub(r'第 (\d+)\.(\d+)、(\d+)\.(\d+) 节', multi, text)
    return text


def main():
    n = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".html"):
            continue
        p = os.path.join(SRC, fn)
        with open(p, encoding="utf-8") as f:
            t = f.read()
        nt = fix(t)
        if nt != t:
            with open(p, "w", encoding="utf-8") as f:
                f.write(nt)
            n += 1
    print("label-fixed files:", n)


if __name__ == "__main__":
    main()
