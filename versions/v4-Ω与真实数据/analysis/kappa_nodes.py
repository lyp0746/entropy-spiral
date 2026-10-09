# -*- coding: utf-8 -*-
"""
kappa_nodes.py — κ 脆弱节点的 V 框架应用与权重敏感性（第 8.2.1—8.2.4 节支撑）。

输入：指示性赋值（质量 C）的地理—经济节点，维度为
    Θ（租佃/资源租金集中）  I（组织复杂度）  κ（耦合/传导）  ι（政治一致性）
输出：
    analysis/results/kappa_nodes.json    V、V_ι、成分贡献与 γ 敏感性
    assets/svg/fig-kappa-nodes.svg       成分堆叠条形图（展示 γ·κ 的主导性）

用法：python analysis/kappa_nodes.py
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "analysis", "results")
SVG = os.path.join(HERE, "assets", "svg")
os.makedirs(OUT, exist_ok=True)

# 指示性赋值（质量 C）：用于演示结构，不可引用数值
NODES = {
    "霍尔木兹海峡": {"ch": "能源·商品", "Theta": 0.70, "I": 0.40, "kappa": 0.92, "iota": 0.35},
    "黑海粮食走廊": {"ch": "粮食·商品", "Theta": 0.60, "I": 0.40, "kappa": 0.82, "iota": 0.30},
    "马六甲海峡":   {"ch": "航运·商品", "Theta": 0.55, "I": 0.45, "kappa": 0.88, "iota": 0.40},
    "台湾海峡":     {"ch": "芯片·商品", "Theta": 0.68, "I": 0.60, "kappa": 0.89, "iota": 0.50},
    "巴拿马运河":   {"ch": "航运·商品", "Theta": 0.50, "I": 0.45, "kappa": 0.80, "iota": 0.55},
    "美元清算系统": {"ch": "金融·货币", "Theta": 0.80, "I": 0.75, "kappa": 0.87, "iota": 0.45},
    "海湾劳务走廊": {"ch": "人口·汇款", "Theta": 0.60, "I": 0.35, "kappa": 0.72, "iota": 0.42},
    "非洲矿产走廊": {"ch": "资源·商品", "Theta": 0.66, "I": 0.35, "kappa": 0.70, "iota": 0.32},
}
W = {"alpha": 0.30, "beta": 0.05, "gamma": 0.45, "lam": 0.20}
BETA_IOTA = 0.5


def parts(s, w):
    return {
        "alpha_theta": w["alpha"] * s["Theta"],
        "beta_I": w["beta"] * s["I"],
        "gamma_kappa": w["gamma"] * s["kappa"],
        "lam_cross": w["lam"] * s["Theta"] * s["kappa"],
    }


def V(s, w):
    return sum(parts(s, w).values())


def V_iota(s, w):
    return V(s, w) * (1 + BETA_IOTA * (1 - s["iota"]))


def main():
    R = {"weights": W, "beta_iota": BETA_IOTA, "note": "指示性赋值，质量 C，不可引用数值",
         "nodes": {}}
    for name, s in NODES.items():
        p = parts(s, W)
        R["nodes"][name] = {
            "channel": s["ch"], "Theta": s["Theta"], "I": s["I"],
            "kappa": s["kappa"], "iota": s["iota"],
            "V": round(V(s, W), 3), "V_iota": round(V_iota(s, W), 3),
            "share_gamma_kappa": round(p["gamma_kappa"] / V(s, W), 3),
            "parts": {k: round(v, 3) for k, v in p.items()},
        }
    R["rank_V_iota"] = sorted(R["nodes"], key=lambda k: -R["nodes"][k]["V_iota"])

    # γ 敏感性：α = 0.75 − γ（保持总和为 1），β、λ 固定
    sens = {}
    for g in (0.35, 0.45, 0.55):
        w = dict(W, gamma=g, alpha=round(0.75 - g, 2))
        vals = {k: V_iota(s, w) for k, s in NODES.items()}
        sens[f"{g:.2f}"] = {"weights": w,
                            "rank": sorted(vals, key=lambda k: -vals[k]),
                            "V_iota": {k: round(v, 3) for k, v in vals.items()}}
    R["gamma_sensitivity"] = sens
    top3_sets = {tuple(sorted(v["rank"][:3])) for v in sens.values()}
    R["top3_set_stable"] = len(top3_sets) == 1
    R["top3_set"] = sorted(top3_sets)[0] if len(top3_sets) == 1 else None
    R["top2_order_stable"] = len({tuple(v["rank"][:2]) for v in sens.values()}) == 1

    with open(os.path.join(OUT, "kappa_nodes.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)

    print("V (结构) / V_ι（含一致性调节）:")
    for k in R["rank_V_iota"]:
        n = R["nodes"][k]
        print(f"  {k:<12} V={n['V']:.2f}  V_ι={n['V_iota']:.2f}  "
              f"γκ占比={n['share_gamma_kappa']*100:.0f}%")
    print("γ 敏感性：前3名成员稳定:", R["top3_set_stable"], R["top3_set"])
    print("γ 敏感性：前2名顺序稳定:", R["top2_order_stable"])
    for g, v in sens.items():
        print(f"  γ={g}: {v['rank']}")

    draw_svg(R)
    return R


def draw_svg(R):
    Wd, Ht = 1000, 680
    nodes = [k for k in R["nodes"]]
    # 按 V_iota 降序
    order = R["rank_V_iota"]
    vmax = max(R["nodes"][k]["V_iota"] for k in nodes) * 1.12
    x0, x1, ytop, rowh = 250, 900, 120, 58
    COL = {"alpha_theta": "#3a6ea5", "beta_I": "#9db8e0",
           "gamma_kappa": "#c94f4f", "lam_cross": "#e0a86a"}
    LBL = {"alpha_theta": "α·Θ（租佃）", "beta_I": "β·I（复杂度）",
           "gamma_kappa": "γ·κ（耦合）", "lam_cross": "λ·Θκ（交互）"}
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Ht}" '
         f'width="{Wd}" height="{Ht}" font-family="\'Microsoft YaHei\',\'SimHei\',sans-serif">',
         f'<rect width="{Wd}" height="{Ht}" fill="#ffffff"/>']
    o.append('<text x="500" y="40" font-size="21" font-weight="700" fill="#1a1a1a" '
             'text-anchor="middle">全球 κ 脆弱节点：V 的成分分解（指示性）</text>')
    o.append('<text x="500" y="66" font-size="14.5" fill="#666" text-anchor="middle">'
             '每个条形为 V 的四个成分（式 7.1）；红段 γ·κ 在各节点均占主导，'
             '支持第 7 章 γ&gt;α 的机制推导</text>')
    # 图例
    lx = 250
    for key in ("alpha_theta", "beta_I", "gamma_kappa", "lam_cross"):
        o.append(f'<rect x="{lx}" y="84" width="16" height="16" fill="{COL[key]}"/>')
        o.append(f'<text x="{lx+22}" y="97" font-size="13.5" fill="#333">{LBL[key]}</text>')
        lx += 175
    # 轴
    scale = (x1 - x0) / vmax
    o.append(f'<line x1="{x0}" y1="{ytop-14}" x2="{x0}" y2="{ytop+len(order)*rowh}" '
             f'stroke="#333" stroke-width="1.2"/>')
    for i, name in enumerate(order):
        n = R["nodes"][name]
        y = ytop + i * rowh
        o.append(f'<text x="{x0-14}" y="{y+24}" font-size="15.5" fill="#1a1a1a" '
                 f'text-anchor="end">{name}</text>')
        o.append(f'<text x="{x0-14}" y="{y+43}" font-size="12.5" fill="#888" '
                 f'text-anchor="end">{n["channel"]}</text>')
        cx = x0
        for key in ("alpha_theta", "beta_I", "gamma_kappa", "lam_cross"):
            wpx = n["parts"][key] * (1 + R["beta_iota"] * (1 - n["iota"])) * scale
            o.append(f'<rect x="{cx:.1f}" y="{y+6}" width="{wpx:.1f}" height="30" '
                     f'fill="{COL[key]}"/>')
            cx += wpx
        o.append(f'<text x="{cx+8:.1f}" y="{y+27}" font-size="14" font-weight="700" '
                 f'fill="#1a1a1a">V_ι={n["V_iota"]:.2f}</text>')
    o.append(f'<text x="{x0-14}" y="{ytop+len(order)*rowh+22}" font-size="13" fill="#666" '
             f'text-anchor="end">V_ι = V·[1+0.5(1−ι)]</text>')
    o.append(f'<text x="{x1}" y="{ytop+len(order)*rowh+22}" font-size="13" fill="#666" '
             f'text-anchor="end">κ 权重 γ=0.45；指示性输入（质量 C），数值不可引用</text>')
    o.append("</svg>\n")
    with open(os.path.join(SVG, "fig-kappa-nodes.svg"), "w", encoding="utf-8") as f:
        f.write("".join(o))
    print("wrote assets/svg/fig-kappa-nodes.svg")


if __name__ == "__main__":
    main()
