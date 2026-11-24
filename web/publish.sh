#!/usr/bin/env bash
# 一键更新在线教材：LaTeX → 网页 → 推送到 GitHub Pages
# 网址：https://king157419.github.io/zero2hero/
# 用法（Git Bash）：bash D:/desk/llm/ch4/web/publish.sh [--no-convert]
#   默认先运行 convert.py（overleaf/*.tex → .qmd），再 quarto render，再推送 gh-pages 分支。
#   注意：convert.py 读的是 main.aux 里的编号；如果改了 LaTeX 的章节/图表结构，先在 Overleaf 重新编译并更新 main.aux。
set -euo pipefail
WEB="D:/desk/llm/ch4/web"
REPO="D:/desk/llm/zero2hero"
PAGES="D:/desk/llm/.pages-worktree"
QUARTO="D:/desk/llm/.tools/quarto/bin/quarto.exe"
PY="D:/conda/miniconda3/python.exe"
GIT="git -c http.sslBackend=openssl"

cd "$WEB"
if [ "${1:-}" != "--no-convert" ]; then "$PY" -I convert.py; fi
"$QUARTO" render

# gh-pages 分支放在单独的工作目录里，不影响 zero2hero 的其他分支
if [ ! -d "$PAGES/.git" ] && [ ! -f "$PAGES/.git" ]; then
  cd "$REPO"
  $GIT fetch origin gh-pages 2>/dev/null || true
  if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
    git worktree add "$PAGES" -B gh-pages origin/gh-pages
  else
    git worktree add --orphan -b gh-pages "$PAGES"
  fi
fi

# 2026-11-16 起网站是全书（第 1～8 章），第 4 章只是其中一部分。
# 不再单独推送第 4 章，否则会把整站覆盖成只有第 4 章；改由全书脚本合并后推送。
bash D:/desk/llm/book/publish.sh --no-pdf
