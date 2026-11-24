#!/bin/sh
# 在容器内循环：编译 -> 找出缺失的 .sty/.cls -> tlmgr 安装对应宏包
cd /tmp/ch4
for n in $(seq 1 25); do
  latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > build.log 2>&1
  miss=$(grep -o "File \`[^']*' not found" main.log | head -1 | sed "s/File \`//; s/' not found//")
  [ -z "$miss" ] && { echo "no missing files"; break; }
  pkg=$(tlmgr search --global --file "/$miss" 2>/dev/null | grep -v '^[[:space:]]' | grep -v '^tlmgr' | head -1 | tr -d ':')
  echo "missing $miss -> $pkg"
  [ -z "$pkg" ] && break
  tlmgr install "$pkg" 2>&1 | tail -1
done
grep -E "^!" main.log | head -5
