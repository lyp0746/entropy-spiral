# 《社会系统熵增螺旋与脆弱性诊断》

> 从周期论破产到局部可描述性框架　·　李毅芃

一部学术专著的写作与构建工程：**单栏、中文主体、出版级排版**，
同时输出**印刷版 PDF、电子阅读版 PDF 与 EPUB 3**。
目录（部分 → 章 → 节 → 子节）在 HTML、PDF 与 EPUB 中**均可逐级跳转**。

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
│   ├── parts.json             # 四部分与章节目录
│   ├── front_copyright.html   # 版权与数据来源页
│   ├── front_executive_summary.html  # 执行摘要（中英）
│   ├── front_preface.html     # 前言
│   ├── ch01.html … ch10.html  # 十章正文
│   └── back_epilogue.html, appendix_*.html
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
├── versions/                  # v1/v2 存档 + CHANGELOG.md
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

## v4 / v5：内容增补

在 v3 基础上补入了真实数据升级、反馈拓扑框架与跨域检验，并配上矢量插图：

| 位置 | 内容 | 新增编号 | 图 |
|---|---|---|---|
| §2.3.1 | 治乱循环的**时长序列**：13 个中国帝制政体（Seshat） | 表 2.3 | 图 2.2 `fig-cycle.svg` |
| §3.8 | **反馈速度与制度同构性**：反馈环指数 Ω、同构脆弱假说 | 定义 3.4 / 3.5，表 3.5 / 3.6 | 图 3.2 `fig-feedback.svg` |
| §3.10 | **超稳定结构**：重置只清状态、不改边界 | 定义 3.3 | — |
| §4.10 | **精英二分**与**权俘获 Φ** | 定义 4.4 / 4.5，表 4.9 / 4.10 | 图 4.2 `fig-bifurcation.svg`、图 4.3 `fig-capture.svg` |
| §5.3 | **反馈拓扑作为中介**：重新解释 I 的零结果 | 表 5.3（框架，无数值） | — |
| §6.3 | **关键商品进口集中度**（UN Comtrade HHI） | 表 6.1c（质量 A） | — |
| §8.2 | **能源案例两层拓扑诊断**：mesh 价格 + sequence 物理，δ≠0 | 表 8.3c（Eurostat，质量 A） | — |
| §8.3 | **AI 案例拓扑诊断**：序列链 + 单点集中（非环形） | — | — |
| §8.4 | **债务案例拓扑诊断**：制度相关 δ | 表 8.7c（债务/GDP + r−g，质量 A） | — |
| §5.3 | **反馈拓扑诊断清单**（操作工具） | 表 5.3b（质量 C） | — |
| §9.7 | **纠错失效（与成功）案例库** | 表 9.5（B/C） | — |
| 附录 D | **跨域探索性检验：粮食与能源**（三轴迁移） | 表 D.1—D.4（质量 C） | 图 D.1、D.2 `fig-food-*.svg` |

**一个诚实的否定性结果**：Seshat 数据显示中国帝制政体的存续时长**没有稳定周期**
（均值 143 年、CV 0.45、趋势斜率 ≈ −0.5 年/百年、Spearman ρ = −0.14）。
“周期加速”未被数据支持；高方差本身即周期论的反证。详见 §2.3.1 与 `versions/CHANGELOG.md`。

**一个真实数据修正**：UN Comtrade（2023）按来源国分解的进口 HHI 显示，
中国芯片进口集中度（0.213）**低于**日本（0.404）与印度（0.333），“中国因芯片而 κ 最高”未被支持；
极端集中出现在稀土（美国 0.975、印度 0.978，几乎全部来自中国）。见 §6.3 表 6.1c 与表 9.4 的 P6.4。

**一个诚实的跨域结果（v5，附录 D）**：把 Θ–I–κ 迁移到粮食（FAOSTAT，8 国）与能源（4 国）后，
三根轴均可操作化，且两域都对 2021—2022 年商品／能源冲击作出反应；但复合指标 V 的**国家排序**
对操作化高度敏感（Θ 用作物 HHI 会抬高稻米出口国），跨域相关在仅 3 个共同国家上不可估计。
结论：框架提供的是可迁移的“诊断轴”，而非可直接比较的“跨域指数”。详见附录 D。

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
- `versions/CHANGELOG.md`　v1 / v2 / v3 / v4 / v5.1 / v5.2 的定位与变化

## 数据体积与清理

原始 FAOSTAT 数据约 4.4 GB，不随项目保存；需要复现粮食检验时运行
`python analysis/fetch_faostat.py` 重新下载并解压。仓库其余内容约 80 MB。

## 发布与分发

`bash scripts/release.sh` 会在 `release/` 生成**只含读者可见内容**的发布包
（PDF / EPUB / HTML / 封面 / 读者说明 / 版本日志），并**明确排除**原始数据
（xlsx / csv / json）、分析脚本与依赖清单。发布包内附 `MANIFEST.txt` 说明包含与排除项。

## 可选管线（LaTeX）

`assets/templates/book-template.tex` 提供 ctexbook 模板（A4、思源宋体/Times、三线表、
tcolorbox 框、按章编号公式）。需要 XeLaTeX：

```bash
cd assets/templates && xelatex book-template.tex && xelatex book-template.tex
```

> 默认管线为 HTML → PDF（Chrome headless），无需 LaTeX 即可复现全部产物。
