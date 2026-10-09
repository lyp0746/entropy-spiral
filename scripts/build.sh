#!/usr/bin/env bash
# 一键构建：校对 -> 印刷版 PDF -> 电子阅读版 PDF -> EPUB
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f .env.build ] && . ./.env.build
PY="${PYTHON:-python}"

echo "== 1/4 校对 =="
"$PY" analysis/audit.py

echo "== 2/4 印刷版（第一版版式）=="
"$PY" build_book.py --pdf

echo "== 3/4 电子阅读版 =="
"$PY" build_book.py --ereader --pdf

echo "== 4/4 EPUB 3 =="
"$PY" build_epub.py

echo
echo "完成。产物："
ls -lh output/*.pdf output/*.epub output/*.html 2>/dev/null || true
