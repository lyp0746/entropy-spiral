# AGENTS.md — 本仓库工作约定与工具链（记忆）

> pi 会把本文件作为目录级上下文/记忆自动加载（无需项目信任）。改动后新会话生效。

## 工具链（本机实测，2026-10）

- **Git**：`D:\Git\cmd\git.exe`（不在 WSL 的 PATH 里，请用绝对路径 `/mnt/d/Git/cmd/git.exe`）
  - remote：`https://github.com/lyp0746/entropy-spiral.git`，默认分支 `main`
  - 凭据已缓存，可直接 `push`；脚本里加 `GIT_TERMINAL_PROMPT=0` 防卡住
- **Python（分析/构建）**：`/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe`
  - 已装：numpy pandas scipy matplotlib bs4 lxml pypdf requests（**无** weasyprint / markdown）
  - `.env.build` 的 `PYTHON` 已指向该解释器
- **PDF 生成**：`build_book.py --pdf` 调**无头 Chrome**（`C:\Program Files\Google\Chrome\Application\chrome.exe`）
  打印，**不是** weasyprint
- **联网数据源**：World Bank API、UN Comtrade 公共预览
  （`https://comtradeapi.un.org/public/v1/preview/C/A/HS`，无需密钥）、arXiv API **可用**；
  FRED（fred.stlouisfed.org）与 IMF DataMapper 在本环境**常超时或 403**。

## 常用命令

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
GIT="/mnt/d/Git/cmd/git.exe"

"$PY" analysis/audit.py          # 校对：术语/编号/交叉引用 → 刷新 校对清单.md
"$PY" build_markdown.py          # source/ → output/markdown（含 assets 复制）
bash scripts/release.sh          # 全量构建（audit→PDF→EPUB→Markdown）+ 刷新 release/
```

关键分析脚本：
- `analysis/theta_sensitivity.py` —— Θ 六重代理趋势/合成/留一/相关矩阵/**PCA 与平行分析**
- `analysis/tau_sensitivity.py` —— τ=T_min/T_available 的**蒙特卡洛**不确定性传播
- `analysis/preregistration_checkup.py` —— 事前登记账本校验/进度/追加
- `analysis/fetch_preregistration_baseline.py` —— B1–B3 机器基线快照（WB/Comtrade/arXiv）

## 仓库约定

- **`source/*.html` 是唯一权威正文来源**；`output/`、`release/` 是派生产物（见 `.gitignore`）。
- 图表：脚本输出 `analysis/results/*.json` 与 `assets/charts/*.png`；正文用相对路径 `assets/...` 引用。
- 改正文后顺序：`analysis/audit.py`（应无“引用但未定义的表/图”、无“无效章节引用”）→ `build_markdown.py`。
- `docs/preregistration/checkups.csv` 是 **append-only**：只追加，绝不改写旧行。
- 结论标注：证据等级 A/B/C 与概念等级 甲/乙/丙 双重标注；τ、C 只作序数/方向判断。
- 观测窗口：正文 1980—2024；历史延伸与最新数据单独标注。

## 版本脉络

见 `versions/CHANGELOG.md`（最新 v21）。本轮要点：Θ 代理 PCA（表 5.4b）、
τ 的 MC（表 14.6/14.7、图 14.3）、I₂ 校准规则 R1–R5 与偏差符号审计（表 14.8）、
命题 14.2 修订、公开登记与机器基线快照（附录 I）。
