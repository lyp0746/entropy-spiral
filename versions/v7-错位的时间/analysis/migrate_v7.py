# -*- coding: utf-8 -*-
"""migrate_v7.py — 把 source/ 从 v6 结构迁移为 v7 结构（本仓库内部使用）。

做两件事：
1) 物理重排章文件（时间维度提前，三轴顺延，方法论四章重排）；
2) 对全部源文件做一次"章节语义重编号"：章号、节号、定义/图/表/式编号、
   交叉引用，一律按同一张映射表改写。

映射（旧章 → 新章）：
    1→1  2→2  3→3  4→5  5→6  6→7  7→8  8→9  9→11
    10→12  11→10  12→4（并入新的"时间层级"章）  13→13  14→14  15→15
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "source")

MAP = {1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 11,
       10: 12, 11: 10, 12: 4, 13: 13, 14: 14, 15: 15}

# 旧章文件 → 新章文件
RENAME = {"ch12.html": "ch04.html", "ch04.html": "ch05.html", "ch05.html": "ch06.html",
          "ch06.html": "ch07.html", "ch07.html": "ch08.html", "ch08.html": "ch09.html",
          "ch09.html": "ch11.html", "ch10.html": "ch12.html", "ch11.html": "ch10.html"}

# 区间引用：语义替换（须先于单章替换执行）
RANGES = [
    ("第 4—6 章", "第 5—7 章"),
    ("第 7—8 章", "第 8—9 章"),
    ("第 9—10 章", "第 11—12 章"),
    ("第 4—8 章", "第 5—9 章"),
    ("第 4—7 章", "第 5—8 章"),
    ("第 11—14 章", "关于时间错配与可控性的诸章"),
    ("第 11—15 章", "关于时间、可控性与理论边界的诸章"),
    ("第 12—13 章", "关于时间错配与可控性的讨论"),
    ("第 11—12 章", "关于时间结构的讨论"),
    # 1—3 / 1—9 在新结构下依然成立，无需改动
]


def rename_files():
    tmp = os.path.join(SRC, "_migrate_tmp")
    os.makedirs(tmp, exist_ok=True)
    for old, new in RENAME.items():
        shutil.copyfile(os.path.join(SRC, old), os.path.join(tmp, new))
    for new in RENAME.values():
        shutil.copyfile(os.path.join(tmp, new), os.path.join(SRC, new))
    shutil.rmtree(tmp)
    print("renamed:", ", ".join(f"{o}->{n}" for o, n in RENAME.items()))


def sub_num(m):
    x = int(m.group(1))
    return str(MAP.get(x, x))


def renumber(text):
    # 0) 区间引用
    for a, b in RANGES:
        text = text.replace(a, b)
    # 1) 章标题统一由第 10 步处理（避免二次映射）
    # 2) h3 文本与锚点
    text = re.sub(r'(<h3[^>]*>)(\d+)\.(\d+)',
                  lambda m: m.group(1) + str(MAP.get(int(m.group(2)), int(m.group(2)))) + "." + m.group(3), text)
    text = re.sub(r'id="sec(\d+)-(\d+)"',
                  lambda m: 'id="sec' + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "-" + m.group(2) + '"', text)
    # 3) h4 文本（含 X.Y.Z）
    text = re.sub(r'(<h4[^>]*>)(\d+)\.(\d+)\.(\d+)',
                  lambda m: m.group(1) + str(MAP.get(int(m.group(2)), int(m.group(2)))) + "." + m.group(3) + "." + m.group(4), text)
    # 4) 交叉引用：第 X.Y 节 / 第 X.Y.Z 节
    text = re.sub(r'第\s*(\d+)\.(\d+)\.(\d+)\s*节',
                  lambda m: "第 " + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "." + m.group(2) + "." + m.group(3) + " 节", text)
    text = re.sub(r'第\s*(\d+)\.(\d+)\s*节',
                  lambda m: "第 " + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "." + m.group(2) + " 节", text)
    # 5) §X.Y
    text = re.sub(r'§\s*(\d+)\.(\d+)',
                  lambda m: "§" + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "." + m.group(2), text)
    # 6) 见 X.Y
    text = re.sub(r'见\s*(\d+)\.(\d+)',
                  lambda m: "见 " + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "." + m.group(2), text)
    # 7) 定义/图/表/式 X.Y（含 a/b/c 后缀）
    text = re.sub(r'(定义|图|表|式)\s*(\d+)\.(\d+)',
                  lambda m: m.group(1) + " " + str(MAP.get(int(m.group(2)), int(m.group(2)))) + "." + m.group(3), text)
    # 8) 式(X.Y)
    text = re.sub(r'式\((\d+)\.(\d+)\)',
                  lambda m: "式(" + str(MAP.get(int(m.group(1)), int(m.group(1)))) + "." + m.group(2) + ")", text)
    # 9) 公式编号 <span class="num">(X.Y)</span>
    text = re.sub(r'(<span class="num">\()(\d+)\.(\d+)(\)</span>)',
                  lambda m: m.group(1) + str(MAP.get(int(m.group(2)), int(m.group(2)))) + "." + m.group(3) + m.group(4), text)
    # 10) 第 X 章（单章；放在最后，避免与"第 X.Y 节"冲突）
    text = re.sub(r'第\s*(\d+)\s*章',
                  lambda m: "第 " + str(MAP.get(int(m.group(1)), int(m.group(1)))) + " 章", text)
    return text


def main():
    rename_files()
    # 先全部计算，成功后再落盘，避免半途失败留下不一致状态
    pending = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".html"):
            continue
        p = os.path.join(SRC, fn)
        with open(p, encoding="utf-8") as f:
            t = f.read()
        nt = renumber(t)
        if nt != t:
            pending.append((p, nt))
    for p, nt in pending:
        with open(p, "w", encoding="utf-8") as f:
            f.write(nt)
    print("renumbered files:", len(pending))


if __name__ == "__main__":
    main()
