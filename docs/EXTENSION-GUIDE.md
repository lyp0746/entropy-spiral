# 扩展指南（EXTENSION-GUIDE）

本书的框架是**局部可描述性**，其价值在于可以被复制到新的领域、地区与指标。
本文件说明如何扩展，而不破坏既有结构。

## 1. 扩展到其他地区 / 文明

框架不依赖中国案例的结论，只依赖三根轴的判定程序：

1. **选轴**：为新地区找 Θ、I、κ 的代理（若无货币化数据，Θ 可用土地租佃、贡赋、特许权比例替代）。
2. **定等级**：按 A/B/C 标注每个代理，C 级只作方向判断。
3. **走五步模板**：直接套用附录 B.6 的诊断模板（界定边界 → 四维赋值 → 计算 V 与敏感性 → 情景与监测信号 → 登记与复检），可参照表 B.1 的两个填写范例。
4. **建登记簿**：把“什么观测会否证本框架”写成前瞻条目（可参考第 11 章表 11.4）。
5. **输出**：新增数据放 `data/`，脚本放 `analysis/`，图放 `assets/charts/`（或 `assets/svg/`），正文放 `source/`。

> 节点级案例（如第 9.2 节的八个 κ 节点）可用 `analysis/kappa_nodes.py` 生成；
> 仪表板规范见附录 B.7，监测指标与阈值应在看信号之前登记。

## 2. 增加一个新代理

以“平台抽租份额”为例：

```python
# analysis/fetch_platform_rent.py
# 1) 读取 data/platform_rent.csv
# 2) 计算方向检验（Spearman ρ + Theil–Sen）
# 3) 写入 data/injected.json 的键，例如 plat_rent_2024
```

然后在正文用占位符引用：`{{D:plat_rent_2024}}`，构建时会自动注入。
若新增图表，请同步更新 `校对清单.md` 的编号（运行 `analysis/audit.py` 自动核对）。

## 3. 增加一章

1. 在 `source/` 新建 `ch11.html`，首行用
   `<h2 class="chapter">第 10 章　标题</h2>`，
   节标题用 `<h3>10.1　…</h3>`，子节用 `<h4>10.1.1　…</h4>`。
2. 在 `source/parts.json` 对应 part 的 `chapters` 加入：
   ```json
   {"no": "11", "title": "标题", "file": "ch11.html", "written": true,
    "sections": ["11.1 …", "11.2 …"]}
   ```
3. 重新构建：`bash scripts/build.sh`。
   目录（四级）、PDF 书签、EPUB nav 会自动更新。

## 4. 插图规范

- 矢量优先：手写或由 `analysis/make_figures.py` 生成 SVG，放入 `assets/svg/`。
- 位图（PNG）放入 `assets/charts/`，正文用 `<img class="fig" src="assets/charts/xxx.png">`。
- 字体只用 `Microsoft YaHei` / `SimSun` / `Times New Roman`（与第一版一致）。
- 每张图必须有 `<div class="cap"><b>图 X.Y　标题</b>…</div>`，图号连续。

## 5. 版式定制

| 需求 | 修改位置 |
|---|---|
| 正文字体 / 字号 / 行距 | `assets/css/paper.css`（`body`、`h1..h5`） |
| 电子阅读版 | `assets/css/ereader.css` |
| 目录层级缩进 | `assets/css/book.css` 的 `.toc .l1..l4` |
| 纸张与页边距 | `assets/css/paper.css` 的 `@page` |
| 封面 | `assets/svg/cover.svg` |

## 6. 质量门禁

提交前运行：

```bash
bash scripts/validate.sh
```

它会检查：术语一致性、定义/公式/表/图编号、交叉引用、参考文献完整性，
以及 EPUB 的 XML 合法性与 mimetype 正确性。

## 7. 长期维护建议

- 用 Git 管理 `source/`、`analysis/`、`data/`（原始数据）与 `docs/`；忽略 `output/`。
- 每次重大改版在 `versions/` 留一份 PDF 快照，并在 `versions/CHANGELOG.md` 记录定位变化。
- 每季度重跑 `scripts/update-data.sh`，核对登记簿中的前瞻命题。
