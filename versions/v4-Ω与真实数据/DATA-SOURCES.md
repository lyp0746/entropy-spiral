# 数据源详解（DATA-SOURCES）

本书坚持“每个数字都可追溯到来源与脚本”。本文件是 `data/README.md` 的补充，
给出完整清单、许可与更新方式。质量等级定义见 `docs/METHODOLOGY.md`。

## 1. 目录约定

```
data/
├── injected.json                     # 正文占位符的最终取值（构建时注入）
├── world-bank/                       # 世界银行 API 序列（A 级）
├── imf/                              # IMF DataMapper（A 级）
├── wid/                              # WID.world 用户导出（A 级）
├── energy/                           # Brent / WTI 油价（A 级）
├── governance/                       # WGI 治理指标（A 级）
├── seshat/                           # Seshat Equinox 2020（B 级）
└── *.json                            # 各来源的下载指引
```

> 注：为兼容既有脚本，部分文件可能仍位于 `data/` 根目录；`analysis/` 中的路径常量
> 是唯一的“真理来源”。迁移文件时同步更新脚本即可。

## 2. 来源清单

| 数据 | 文件（示例） | 来源 | 获取 | 质量 | 许可 |
|---|---|---|---|---|---|
| 收入 Gini | `usa_gini.csv` | World Bank WDI `SI.POV.GINI` | API | A | CC BY 4.0 |
| 贸易 / FDI | `world_trade_gdp.csv`, `world_fdi_gdp.csv` | World Bank WDI | API | A | CC BY 4.0 |
| 私人部门信贷 | `usa_private_credit_gdp.csv` | World Bank `FS.AST.PRVT.GD.ZS` | API | A | CC BY 4.0 |
| 政府债务（中央） | `usa_gov_debt_gdp.csv` | World Bank `GC.DOD.TOTL.GD.ZS` | API | A | CC BY 4.0 |
| 家庭/企业/广义政府债务 | `imf_usa_*.csv` | IMF DataMapper | API | A | IMF 条款 |
| 通胀 / 实际利率 | `usa_inflation.csv`, `usa_real_rate.csv` | World Bank | API | A | CC BY 4.0 |
| 净财富前 1% 等 | `WID_Data_*.csv` | WID.world | 用户导出 | A | WID 条款 |
| Brent / WTI 油价 | `brent-daily.csv`, `wti-daily.csv` | 公开来源（EIA 等） | 用户导出 | A | 见来源 |
| 治理指标 | `wgidataset_with_sourcedata-2026.csv` | Worldwide Governance Indicators | 用户导出 | A | WGI 条款 |
| 前五大科技公司占比 | `ai_top5_share.csv` | 公开市值整理 | 用户整理 | B | — |
| 政体存续时长 | `Equinox_on_GitHub_June9_2022.xlsx` → `seshat_cn_polities.csv` | Seshat Equinox 2020 | 公开 xlsx + `analysis/fetch_seshat.py` | B | Seshat CC BY |

## 3. 关键实证发现（真实数据）

- **Θ 的双重形态**：净财富前 1% 份额 1980 23.2% → 2015 **35.8%（峰值）** → 2024 34.8%；
  收入前 1% 同期 10.4% → 20.7%；后 50% 收入份额 20.1% → 13.4%（存量走平、流量仍集中）。
- **κ 并非单调**：世界贸易/GDP 持续上升（38.6 → 68.5），但世界 FDI/GDP 于 2000 年见顶（4.62）后降至 1.41。
- **私人风险公共化**：家庭债务 2008 峰值 95.9% → 69.4%；政府债务升至 122.3%。
- **治乱循环无稳定周期（新增）**：13 个中国帝制政体存续时长均值 143 年、CV 0.45、
  趋势斜率 ≈ −0.5 年/百年（Spearman ρ = −0.14，不显著）。
- **κ 节点主导（新增）**：8 个地缘节点的 V 中 γ·κ 占比 48%—59%，一致支持第 7 章 γ&gt;α；
  前三名成员在 γ∈[0.35,0.55] 内稳定，但前两名顺序对 γ 敏感（`analysis/kappa_nodes.py`）。

## 4. 更新工作流

```bash
bash scripts/update-data.sh     # 重跑全部抓取与解析脚本
python analysis/audit.py        # 检查是否有数值缺失或口径变化
bash scripts/build.sh           # 重建 PDF / EPUB
```

## 5. 许可与引用

- World Bank：CC BY 4.0；IMF、WID、WGI、Seshat 各有其条款，使用前请核对。
- **正式出版前**，务必在每个图表下标注**准确来源、检索日期与许可**。
- 第三方数据的著作权与责任归原作者；本书仅做分析与引用。
