# 数据注入说明（data/）

本目录把**真实数据**注入正文：正文用 `{{D:key}}` 占位符，`injected.json` 提供数值，
`python build_book.py` 自动替换。未引用或未赋值的键会在构建时报告。

## 当前状态：全部已填（83 个真实值，0 待填）

### 抓取脚本（可重跑）

| 脚本 | 来源 | 覆盖 |
|---|---|---|
| `analysis/fetch_and_inject.py` | World Bank API | Gini、贸易/GDP、FDI/GDP、政府债务、私人信贷 |
| `analysis/fetch_imf.py` | IMF DataMapper | 家庭/企业/政府债务 |
| `analysis/fetch_chapter8.py` | World Bank API | 通胀、实际利率、贷款利率 |
| `analysis/parse_wid.py` | 用户导出的 WID CSV | 净财富前1%、收入前1%、后50%收入份额 |

### 已注入的真实序列

| 键（前缀） | 内容 | 来源 | 质量 |
|---|---|---|---|
| `us_gini_*` | 美国收入 Gini | World Bank | A |
| `us_top1_wealth_*` / `us_top1_income_*` / `us_bottom50_income_*` | 净财富前1% / 收入前1% / 后50% 份额 | WID.world | A |
| `world_trade_gdp_*` / `usa_trade_gdp_*` | 贸易开放度 | World Bank | A |
| `world_fdi_gdp_*` | 世界 FDI/GDP | World Bank | A |
| `us_private_credit_gdp_*` | 私人部门信贷/GDP | World Bank | A |
| `us_gov_debt_gdp_*` / `us_gov_debt_imf_*` | 政府债务/GDP（中央 / 广义） | World Bank / IMF | A |
| `us_hh_debt_*` / `us_nfc_debt_*` | 家庭 / 非金融企业债务/GDP | IMF | A |
| `us_inflation_*` / `us_real_rate_*` / `us_lending_rate_*` | 通胀、实际利率、贷款利率 | World Bank | A |

### 原始数据文件（`data/*.csv`）

`usa_gini.csv`、`world_trade_gdp.csv`、`usa_trade_gdp.csv`、`world_fdi_gdp.csv`、
`usa_gov_debt_gdp.csv`、`usa_private_credit_gdp.csv`、`imf_usa_hh_debt.csv`、
`imf_usa_nfc_debt.csv`、`imf_usa_gov_debt_imf.csv`、`usa_inflation.csv`、
`usa_real_rate.csv`、`usa_lending_rate.csv`、`WID_Data_*.csv`（用户导出）。

## 关键实证发现（真实数据）

- **Θ 的双重形态**：净财富前 1% 份额 1980 23.2% → 2015 **35.8%（峰值）** → 2024 34.8%；
  但**收入**前 1% 同期从 10.4% 升至 20.7%，后 50% 收入份额从 20.1% 降至 13.4%——
  存量走平、流量仍集中。
- **κ 并非单调**：世界贸易/GDP 持续上升（38.6→68.5），但世界 FDI/GDP 2000 年见顶（4.62）后降至 1.41。
- **私人风险公共化**：家庭债务 2008 峰值 95.9% 后去杠杆至 69.4%；政府债务升至 122.3%。

## 重跑方式

```bash
python analysis/fetch_and_inject.py     # World Bank
python analysis/fetch_imf.py            # IMF
python analysis/fetch_chapter8.py       # WB 利率/通胀
python analysis/parse_wid.py            # 解析 WID CSV（若更新）
python build_book.py --pdf              # 重建
```

## 中国政体序列（Seshat，方案 C）

| 文件 | 内容 | 来源 | 质量 |
|---|---|---|---|
| `Equinox_on_GitHub_June9_2022.xlsx` | Seshat Equinox 2020 全库 | Seshat | — |
| `seshat_cn_polities.csv` | 13 个中国帝制政体起止年与存续时长 | 由 `analysis/fetch_seshat.py` 抽取 | B |
| `seshat_cn_summary.json` | 均值 / 标准差 / CV 与趋势 | 同上 | B |

重跑：`python analysis/fetch_seshat.py`（同时刷新图 2.2 的数据源）。

## 目录重组说明

项目已重组为 `source/ data/ analysis/ assets/ output/ versions/ docs/ scripts/`。
本目录（`data/`）保留原始 CSV/JSON 与注入值 `injected.json`；
分析结果移至 `analysis/results/`，位图移入 `assets/charts/`。
脚本中的路径常量已同步更新，详见 `docs/DATA-SOURCES.md`。

## 许可与引用

各数据源使用须遵守其许可。正式出版前，务必在图表下标注**准确来源、检索日期与许可**。
