# -*- coding: utf-8 -*-
"""
make_figures_action.py —— 行动篇（第 16、19 章）新增矢量插图。

产物（assets/svg/）：
  fig-timebudget-split.svg  T_policy 的三段分解与对应工具（图 16.1）
  fig-action-loop.svg       时间预算的五步闭环与触发/日落时间线（图 19.1）

风格与 make_figures.py 一致（1000px 宽、Microsoft YaHei、白底）。
用法：python analysis/make_figures_action.py
"""
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "assets", "svg")

FONT = "Microsoft YaHei, PingFang SC, sans-serif"
INK, MUTED = "#1a1a1a", "#666"
BLUE, ORANGE, GREEN, RED, GOLD = "#1e88e5", "#e65100", "#009E73", "#c62828", "#b8862f"


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'  <rect width="{w}" height="{h}" fill="#ffffff"/>\n')


def text(x, y, s, size=14, weight="normal", fill=INK, anchor="start"):
    return (f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{s}</text>\n')


# ---------------------------------------------------------------- 图 16.1
def fig_timebudget_split():
    W, H = 1000, 520
    o = [head(W, H)]
    o.append(text(W // 2, 38, "时间预算：把 T_policy 拆成三段，分别压缩", 20, "bold", INK, "middle"))
    o.append(text(W // 2, 64, "发现 → 决策 → 执行，三段各自有对应的前置工具", 13, "", MUTED, "middle"))

    # 时间轴三段
    x0, y0, seg_w, seg_h = 70, 120, 280, 78
    segs = [
        ("发现时间", "从信号出现到被识别", BLUE, "#e3f2fd"),
        ("决策时间", "从识别到作出决定", ORANGE, "#fff3e0"),
        ("执行时间", "从决定到生效", GREEN, "#e8f5e9"),
    ]
    for i, (name, desc, col, bg) in enumerate(segs):
        x = x0 + i * (seg_w + 10)
        o.append(f'  <rect x="{x}" y="{y0}" width="{seg_w}" height="{seg_h}" rx="8" '
                 f'fill="{bg}" stroke="{col}" stroke-width="2"/>\n')
        o.append(text(x + seg_w // 2, y0 + 34, name, 17, "bold", col, "middle"))
        o.append(text(x + seg_w // 2, y0 + 60, desc, 12.5, "", MUTED, "middle"))

    # 工具到分段的箭头
    tools = [
        ("监测指标 + 触发阈值", "把“发现”变成核对而非重新讨论"),
        ("预授权 + 快速通道", "平静时授权，危机时只执行"),
        ("资源前置", "缓冲、备用产能、常设互换线"),
    ]
    for i, (t, d) in enumerate(tools):
        x = x0 + i * (seg_w + 10)
        cx = x + seg_w // 2
        o.append(f'  <line x1="{cx}" y1="{y0 + seg_h + 54}" x2="{cx}" y2="{y0 + seg_h + 10}" '
                 f'stroke="{GOLD}" stroke-width="2" marker-end="url(#arrow)"/>\n')
        o.append(f'  <rect x="{x}" y="{y0 + seg_h + 56}" width="{seg_w}" height="86" rx="8" '
                 f'fill="#fffdf3" stroke="{GOLD}" stroke-width="1.5"/>\n')
        o.append(text(cx, y0 + seg_h + 86, t, 14.5, "bold", "#8a6a14", "middle"))
        o.append(text(cx, y0 + seg_h + 110, d, 12, "", MUTED, "middle"))

    # 底部：三段各自的三道闸
    o.append(f'  <rect x="70" y="430" width="860" height="60" rx="8" fill="#fbfbfb" '
             f'stroke="#ddd" stroke-width="1"/>\n')
    o.append(text(W // 2, 455, "每一段都必须带三道闸：触发条件可判定 · 授权带日落 · 事后公开追责",
                  14, "bold", RED, "middle"))
    o.append(text(W // 2, 477, "没有这三道闸的预授权，不是行动设计，而是权力扩张（§16.3）",
                  12, "", MUTED, "middle"))

    # 箭头定义
    o.append('  <defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="4.5" '
             f'refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{GOLD}"/>'
             '</marker></defs>\n')
    o.append("</svg>\n")
    os.makedirs(SVG, exist_ok=True)
    with open(os.path.join(SVG, "fig-timebudget-split.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-timebudget-split.svg")


# ---------------------------------------------------------------- 图 19.1
def fig_action_loop():
    W, H = 1000, 560
    o = [head(W, H)]
    o.append(text(W // 2, 38, "时间预算的五步闭环", 20, "bold", INK, "middle"))
    o.append(text(W // 2, 64, "诊断 → 分级 → 时间预算 → 登记 → 审查；审查的结果改写下一轮诊断",
                  13, "", MUTED, "middle"))

    steps = [
        ("① 诊断", "测 V、估 τ", BLUE, "#e3f2fd"),
        ("② 分级", "能说到什么程度", "#7b1fa2", "#f3e5f5"),
        ("③ 时间预算", "触发/授权/日落/降级", ORANGE, "#fff3e0"),
        ("④ 登记", "事前写下，不回调", GREEN, "#e8f5e9"),
        ("⑤ 审查", "事后校准与迭代", "#00838f", "#e0f7fa"),
    ]
    bw, gap = 172, 20
    x0 = (W - (bw * 5 + gap * 4)) // 2
    y0, bh = 108, 96
    for i, (name, desc, col, bg) in enumerate(steps):
        x = x0 + i * (bw + gap)
        o.append(f'  <rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="9" '
                 f'fill="{bg}" stroke="{col}" stroke-width="2"/>\n')
        o.append(text(x + bw // 2, y0 + 40, name, 16, "bold", col, "middle"))
        o.append(text(x + bw // 2, y0 + 68, desc, 12, "", MUTED, "middle"))
        if i < 4:
            ax = x + bw + 2
            o.append(f'  <line x1="{ax}" y1="{y0 + bh // 2}" x2="{ax + gap - 4}" y2="{y0 + bh // 2}" '
                     f'stroke="{col}" stroke-width="2" marker-end="url(#a{col[1:]})"/>\n')

    # 回环箭头：审查 → 诊断
    ly = y0 + bh + 40
    o.append(f'  <path d="M{x0 + 4*(bw+gap) + bw//2},{y0+bh} L{x0 + 4*(bw+gap) + bw//2},{ly} '
             f'L{x0 + bw//2},{ly} L{x0 + bw//2},{y0+bh}" fill="none" stroke="{GOLD}" '
             f'stroke-width="2" stroke-dasharray="7 5" marker-end="url(#agold)"/>\n')
    o.append(text(W // 2, ly + 24, "审查结果改写下一轮的诊断与预算（“诊断 → 行动 → 再诊断”）",
                  12.5, "bold", "#8a6a14", "middle"))

    # 时间线：触发 / 日落
    ty = ly + 70
    o.append(f'  <line x1="120" y1="{ty}" x2="880" y2="{ty}" stroke="#333" stroke-width="1.6"/>\n')
    for px, lab, col in ((120, "t₀ 触发", RED), (620, "t₀ + 90 天", GREEN)):
        o.append(f'  <line x1="{px}" y1="{ty - 10}" x2="{px}" y2="{ty + 10}" stroke="{col}" stroke-width="2"/>\n')
        o.append(text(px, ty + 32, lab, 13, "bold", col, "middle"))
    o.append(f'  <rect x="120" y="{ty - 7}" width="500" height="14" fill="#fff3e0" opacity="0.7"/>\n')
    o.append(text(370, ty - 16, "授权生效期", 12.5, "", ORANGE, "middle"))
    o.append(text(370, ty + 52, "触发与日落是“自动”的：不依赖临场决策", 12.5, "", MUTED, "middle"))
    o.append(text(620, ty + 52, "到期自动失效；续期须重新审议", 12.5, "", GREEN, "middle"))

    defs = ['  <defs>\n']
    for col in (BLUE, "#7b1fa2", ORANGE, GREEN):
        defs.append(f'    <marker id="a{col[1:]}" markerWidth="9" markerHeight="9" refX="4.5" '
                    f'refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{col}"/></marker>\n')
    defs.append(f'    <marker id="agold" markerWidth="9" markerHeight="9" refX="4.5" '
                f'refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{GOLD}"/></marker>\n')
    defs.append('  </defs>\n')
    o.append("".join(defs))
    o.append("</svg>\n")
    os.makedirs(SVG, exist_ok=True)
    with open(os.path.join(SVG, "fig-action-loop.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-action-loop.svg")


if __name__ == "__main__":
    fig_timebudget_split()
    fig_action_loop()
