#!/usr/bin/env bash
# 刷新外部数据（需联网）。可单独注释掉不想重跑的步骤。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f .env.build ] && . ./.env.build
PY="${PYTHON:-python}"

echo "== World Bank（Gini / 贸易 / 信贷 / 债务）=="
"$PY" analysis/fetch_and_inject.py
echo "== IMF（家庭 / 企业 / 政府债务）=="
"$PY" analysis/fetch_imf.py
echo "== World Bank（通胀 / 利率）=="
"$PY" analysis/fetch_chapter8.py
echo "== 政府支出 + WGI =="
"$PY" analysis/fetch_chapter5.py
echo "== WID 财富与收入 =="
"$PY" analysis/parse_wid.py
echo "== Brent 油价 + WGI xlsx =="
"$PY" analysis/parse_chapter8_inputs.py
echo "== Seshat 中国政体序列 =="
"$PY" analysis/fetch_seshat.py
echo "== 重新生成矢量图 =="
"$PY" analysis/make_figures.py
echo "数据刷新完成。"
