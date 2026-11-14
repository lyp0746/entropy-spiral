# analysis/results —— 中间文件的来源与重建

本目录的文件分两类：**可现算的**（脚本在仓库内，跑一遍就有）与**需外部输入的**（要自己取数）。
凡是后者，这里写明取什么、怎么对上，避免“表注指着一个仓库里没有的文件”。

## pool_coded.csv（2026-11-13 重建，口径已按 Seshat 文献的通行做法固定）

**数据在库里。** 原始 `data/Equinox_on_GitHub_June9_2022.xlsx`（4.7 MB）一直在仓库中；缺的只是提取层。
`analysis/build_pool.py` 现在把它变成 `pool_coded.csv`，`analysis/complexity_analysis.py` 再读它出表 6.1 与图 6.1。

**口径（这一版的规则，写死在脚本头部注释里）**

1. 单位是**政体**，不是政体×时期：取 Seshat 给出的 `Peak Date` 那一行（缺则取最后一行）。
2. 剔除**考古分期**（`Complexity = Early`）：它们的“存续”是分期长度，不是政体寿命。
3. 剔除**重复／准政体**（`Dupl = y`）。
4. `s_lawcomposite` = 成文（LegCode）、法院（Court）、法官（Judge）、律师（Lawyer）四项非缺失均值；
   编码按 Seshat 通行折算（present 1／inferred present 0.75／inferred absent 0.25／absent 0），
   `-999` 为缺失。

**与 2026-10 发表值的差异（已按新口径改写正文，不是留存两套数）**

| 口径 | n（adm／s／c） | ρ(与 logT) | 二次项 |
|---|---|---|---|
| 旧（逐政体×时期，未剔重复） | 205／198／189 | −0.00／−0.09／−0.13 | adm 不显著，看起来像“没关系” |
| **新（政体级，Peak Date，剔考古与重复）** | **167／156／148** | **−0.25／−0.28／−0.24** | 三项**都为正**（凸），adm／s 显著；倒 U 不成立，方向相反 |

结论没变（倒 U 不被支持），但强度与解释变了（从“零结果”变成“显著负平均、且微凸”）。表 6.1、图 6.1、
第 6 章三点报告与第 3 章、第 2 章的相应表述已同步；CHANGELOG 有完整记录。

## 其余文件（可现算）

| 文件 | 由谁生成 |
|---|---|
| `kappa.json`、`kappa_nodes.json` | `analysis/kappa_analysis.py` |
| `theta_sensitivity.json` | `analysis/theta_sensitivity.py` |
| `v_framework.json`、`v_framework_real.json` | `analysis/v_framework.py`、`analysis/v_framework_real.py` |
| `tau_sensitivity.json` | `analysis/tau_sensitivity.py` |
| `v_uncertainty_decomposition.json` | `analysis/v_uncertainty_decomposition.py` |
| `axis_independence.json`、`cross_system.json` | 见各脚本头部说明 |
| `food_*`、`energy_v_panel.csv`、`reserves_psd.csv` | `analysis/fetch_*.py` + 各验证脚本（需联网取官方数据） |
| `audit.json` | `analysis/audit.py` |
