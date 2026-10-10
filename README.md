# 《错位的时间：社会系统的熵增螺旋、制度错配与可控性边界》

> 从周期论破产到时间—制度错配的可描述性框架　·　李毅芃

[![内容许可: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![代码许可: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE-MIT)
[![Release](https://img.shields.io/badge/release-PDF%20%7C%20EPUB-brightgreen.svg)](../../releases/latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23276888.svg)](https://doi.org/10.5281/zenodo.23276888)

一部学术专著的写作与构建工程：**单栏、中文主体、出版级排版**，
同时输出**印刷版 PDF、电子阅读版 PDF 与 EPUB 3**。
目录（部分 → 章 → 节 → 子节）在 HTML、PDF 与 EPUB 中**均可逐级跳转**。

**核心主张。** 脆弱性除了结构来源，还有一个独立的时间来源：
时间错配 `τ = T_min / T_available`，可控性 `C = T_policy / T_threat = 1/τ`。
现代社会不是一个钟，而是许多转速不同的钟；错位是结构性的，而非暂时失调。
全书不预测崩溃时点，只做诚实的局部诊断。

- 🚀 **快速开始**　[快速开始](#快速开始)（一条命令构建 PDF/EPUB）
- 📥 **下载**　[`Releases`](../../releases/latest)（印刷版 PDF · 电子阅读版 PDF · EPUB 3 · 封面），或本地 `bash scripts/release.sh` → `release/`
- 🤝 **参与**　[CONTRIBUTING.md](CONTRIBUTING.md) · 数据缺口见 [`docs/DATA-GAPS.md`](docs/DATA-GAPS.md)
- 📚 **引用**　见 [引用](#引用) 与 [`CITATION.cff`](CITATION.cff)

---

## 目录结构

```
entropy-spiral/
├── README.md                  # 本文件
├── build_book.py              # 组装 HTML + 打印 PDF（含分级书签）
├── build_epub.py              # 生成 EPUB 3（nav + NCX 分级目录）
├── requirements.txt
│
├── source/                    # 书稿源文件（唯一正文来源）
│   ├── book.json              # 书名 / 副标题 / 作者 / 内容提要
│   ├── parts.json             # 五部分与章节目录
│   ├── front_copyright.html   # 版权与数据来源页
│   ├── front_executive_summary.html  # 执行摘要（中英）
│   ├── front_preface.html     # 前言
│   ├── ch01.html … ch15.html  # 十五章正文
│   └── back_epilogue.html, appendix_a…g.html
│
├── data/                      # 原始数据与注入值（见 docs/DATA-SOURCES.md）
│   ├── injected.json          # 正文 {{D:key}} 占位符的取值
│   ├── Equinox_on_GitHub_June9_2022.xlsx   # Seshat
│   └── *.csv / *.json
│
├── analysis/                  # 可复现分析脚本
│   ├── fetch_*.py             # 数据抓取
│   ├── parse_*.py             # 数据解析
│   ├── *_analysis.py          # 敏感性 / 复杂度 / κ / V 分析
│   ├── fetch_seshat.py        # 【方案 C】中国政体序列抽取
│   ├── make_figures.py        # 【方案 C】矢量插图生成
│   ├── glossary.py            # 术语统一
│   ├── audit.py               # 全书校对（术语/编号/交叉引用/文献）
│   └── results/               # JSON 结果 + audit.json
│
├── assets/
│   ├── css/                   # paper.css（第一版版式）/ book.css / ereader.css
│   ├── svg/                   # 封面与矢量插图
│   ├── charts/                # 400 dpi PNG 图
│   └── templates/             # 可选 XeLaTeX 模板
│
├── output/                    # 构建产物（见下）
├── release/                   # 发布包（仅读者可见内容，gitignored）
├── versions/                  # 历史版本存档 + CHANGELOG.md
├── docs/                      # 方法论 / 数据源 / 扩展指南 / 政策摘要 / 快速指南
│   ├── METHODOLOGY.md
│   ├── DATA-SOURCES.md
│   ├── EXTENSION-GUIDE.md
│   ├── EXECUTIVE-SUMMARY.md   # 政策版中英摘要
│   ├── QUICK-GUIDE.md         # 5 页操作手册
│   └── READERS.md             # 发布包读者说明
└── scripts/                   # build / update-data / validate / release / export-figures
```

---

## 快速开始

```bash
# 1) 环境（本机使用指定虚拟环境，见 .env.build / .env.build.example）
pip install -r requirements.txt

# 2) 一键构建（校对 → 印刷版 → 电子阅读版 → EPUB）
bash scripts/build.sh

# 3) 组装发布包（只含读者可见内容，排除 xlsx/CSV/脚本/依赖）
bash scripts/release.sh

# 4) 导出 SVG 高分辨率 PNG 备份（约 300 dpi）
bash scripts/export-figures.sh

# 5) 数据刷新（需联网，可选）
bash scripts/update-data.sh

# 6) 质量门禁
bash scripts/validate.sh
```

单独构建：

```bash
python analysis/audit.py            # 校对，生成 校对清单.md
python build_book.py --pdf          # output/book.html + output/book.pdf
python build_book.py --ereader --pdf  # output/book-ereader.*
python build_epub.py                # output/book.epub
```

---

## 构建产物

| 文件 | 版式 | 用途 | 目录 |
|---|---|---|---|
| `output/book.pdf` | **第一版风格**：A4、宋体+Times、10.5pt、1.5 倍行距、35mm 边距 | 打印 / 投稿 | PDF 分级书签（4 级） |
| `output/book.html` | 同上（自包含，图片内嵌） | 网页浏览 | 四级内部链接 |
| `output/book-ereader.pdf` | B5、12pt、1.8 倍行距、斑马纹表格 | 平板 / 屏幕阅读 | PDF 分级书签（4 级） |
| `output/book-ereader.html` | 同上 | 响应式阅读 | 四级内部链接 |
| `output/book.epub` | EPUB 3，可重排 | Kindle / Apple Books / 多看 | nav + NCX 四级目录 |

**字体说明**：正文为中文宋体（SimSun）+ 西文 Times New Roman；
标题为微软雅黑（Microsoft YaHei）/ Arial。**不使用思源（Source Han / Noto）系列**，
以保持第一版的书稿观感。若系统缺少某字体，会按 CSS 回退到 `serif` / `sans-serif`。

---

## 版式规范（第一版）

| 项目 | 取值 |
|---|---|
| 纸张 | A4，上 30mm / 下 32mm / 左右 35mm |
| 正文 | 宋体 + Times，10.5pt，行距 1.5，段距 8pt，两端对齐 |
| 标题 | 微软雅黑/Arial；章 18pt、节 12pt、子节 11pt |
| 表格 | 三线表（顶线/表头线/底线），表头浅灰，数值右对齐 |
| 框 | 定义（蓝）、情景（绿）、警告（橙）、案例（灰），左侧竖线 |
| 公式 | 独立行 + 右对齐编号（章.序） |
| 插图 | 矢量 SVG 优先，位图 400 dpi PNG |

---

## 本书结构（五部分 · 十五章）

《错位的时间》以**时间**为中心线索：脆弱性除了结构来源，还有一个独立的时间来源。
全书不预测崩溃时点，只做“诚实的局部诊断”，并提供可证伪的命题登记簿。

| 部分 | 章 | 内容 |
|---|---|---|
| 一 理论转向与时间问题的发现 | 1—4 | 周期论破产；从周期到螺旋；螺旋的时间结构与熵增机制；**时间层级的社会学（理论中枢）** |
| 二 三个核心变量的时间重读 | 5—7 | Θ 与租佃攫取的**加速度**；I 与制度反应时间的**延长**；κ 与传导的**加速** |
| 三 综合诊断框架 | 8—9 | 脆弱性指标 V；从芯片到知识的**四个案例**；时间维度指标 |
| 四 应用、测试与边界 | 10—12 | 三情景实装检验；发现的逻辑；局部可描述性；行动议程 |
| 五 时间、可控性与现代性诊断 | 13—15 | 可控性边界与控制论；**优雅降级**；**学习滞后（二阶时间错配）**；重新定义 I；六大领域的扩散 |
| 结语与后记 | — | 结语《承认与启蒙》；**后记《方法论的自限性与伦理立场》** |

**核心变量。**

```
时间错配　τ = T_min / T_available
可控性　　C = T_policy / T_threat = 1 / τ
有效适应能力　AC_有效 = AC_名义 × min(1, C)
```

**母题。** 现代社会的脆弱性，来自时间结构与制度结构的永久错配：能加速的子系统
（金融、信息）恰是驱动冲击的一方，不能加速的子系统（政治、心理、生态）恰是
必须作出回应的一方。对 C < 1 的状态，理性策略是**预先减小暴露**，并为不可避免的
失效预设“优雅降级”顺序。

**一个诚实的否定性结果。** Seshat 数据显示中国帝制政体的存续时长**没有稳定周期**
（均值 143 年、CV 0.45、趋势斜率 ≈ −0.5 年/百年、Spearman ρ = −0.14）；
“周期加速”未被数据支持，高方差本身即周期论的反证（§2.3.1）。

**一个真实数据修正。** UN Comtrade（2023）按来源国分解的进口 HHI 显示，
中国芯片进口集中度（0.213）**低于**日本（0.404）与印度（0.333）；
极端集中出现在稀土（美国 0.975、印度 0.978，几乎全部来自中国）（§7.3 表 7.1c、表 11.4 的 P6.4）。

**一个诚实的跨域结果（附录 D）。** 把 Θ–I–κ 迁移到粮食与能源后，三轴均可操作化，
但复合指标 V 的国家排序对操作化高度敏感。结论：框架提供的是可迁移的“诊断轴”，
而非可直接比较的“跨域指数”。

---

## 版本历史

历史版本（v1 治乱循环框架、v2 熵增螺旋、v3 融合初稿、v4 Ω 与真实数据、
v5 风险分解与缓冲、v6 错位的时间）的定位与变化，见 `versions/CHANGELOG.md`。
正式书稿与发布包不包含版本号。

---

## 校准与术语

- 运行 `python analysis/audit.py` 生成 `校对清单.md`（表 A1–A6），
  检查术语一致性、定义/公式/表/图编号、交叉引用与参考文献完整性。
- Θ 的主用语统一为**“租佃份额”**；“垄断份额”为同义旧称（见定义 4.1 与附录 E）。
  运行 `python analysis/glossary.py` 可重新执行统一替换并生成日志。

## 文档

- `docs/EXECUTIVE-SUMMARY.md`　政策版中英摘要（约 2000 词）
- `docs/QUICK-GUIDE.md`　5 页操作手册（五步模板 + 仪表板 + 工作底稿）
- `docs/METHODOLOGY.md`　方法论、证据等级、可证伪登记簿
- `docs/DATA-SOURCES.md`　数据源、许可与更新工作流
- `docs/EXTENSION-GUIDE.md`　如何扩展到其他地区/领域、增章加图
- `docs/READERS.md`　发布包读者说明
- `versions/CHANGELOG.md`　各历史版本的定位与变化

## 数据体积与清理

原始 FAOSTAT 数据约 4.4 GB，不随项目保存；需要复现粮食检验时运行
`python analysis/fetch_faostat.py` 重新下载并解压。仓库其余内容约 80 MB。

## 发布与分发

`bash scripts/release.sh` 会在 `release/` 生成**只含读者可见内容**的发布包
（PDF / EPUB / HTML / 封面 / 读者说明 / 修订说明 / 数据缺口清单 / 贡献指南），
并**明确排除**原始数据（xlsx / csv / json）、分析脚本与依赖清单。发布包内附
`MANIFEST.txt` 说明包含与排除项。

## 引用

若你在研究或写作中使用本书，请引用：

> 李毅芃. 《错位的时间：社会系统的熵增螺旋、制度错配与可控性边界》. 初版, 2026-10-09. CC BY 4.0.
> DOI: [10.5281/zenodo.23276888](https://doi.org/10.5281/zenodo.23276888)

机器可读引用见 [`CITATION.cff`](CITATION.cff)。

- **当前归档 DOI（最新）**：<https://doi.org/10.5281/zenodo.23276888>
- **概念 DOI（无版本，始终指向最新）**：<https://doi.org/10.5281/zenodo.23217100>
- **上一版归档 DOI（已被取代）**：<https://doi.org/10.5281/zenodo.23264927>
- **Zenodo 当前记录**：<https://zenodo.org/records/23276888>

建议：引用具体版本时用**当前归档 DOI**；泛指本作（含未来修订）时用**概念 DOI**。
每次修订在 Zenodo 生成新的归档记录，旧记录保留但标记为已被取代。

## 许可

- **内容**（书稿、图表、文档）：**CC BY 4.0**，见 [`LICENSE`](LICENSE)
- **代码**（`analysis/`、`scripts/`、构建脚本）：**MIT**，见 [`LICENSE-MIT`](LICENSE-MIT)
- **第三方数据**（`data/`）：各有其原始许可，详见 [`docs/DATA-SOURCES.md`](docs/DATA-SOURCES.md)

## 参与贡献

欢迎补充数据、勘误、改进脚本或参与讨论：

- 贡献指南：[`CONTRIBUTING.md`](CONTRIBUTING.md)
- 数据缺口（优先方向）：[`docs/DATA-GAPS.md`](docs/DATA-GAPS.md)、[`docs/OPEN-CONTRIBUTION.md`](docs/OPEN-CONTRIBUTION.md)
- 提交前请运行：`python analysis/audit.py`（必要时 `bash scripts/validate.sh`）

> 一条原则：**把「没测到」和「测到了」一样认真地记录。**

## 可选管线（LaTeX）

`assets/templates/book-template.tex` 提供 ctexbook 模板（A4、思源宋体/Times、三线表、
tcolorbox 框、按章编号公式）。需要 XeLaTeX：

```bash
cd assets/templates && xelatex book-template.tex && xelatex book-template.tex
```

> 默认管线为 HTML → PDF（Chrome headless），无需 LaTeX 即可复现全部产物。
