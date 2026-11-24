#!/bin/sh
# Compile the Overleaf project inside the sharelatex container with its TeX Live
export MSYS_NO_PATHCONV=1
cd /d/desk/llm/ch4/overleaf
docker exec sharelatex rm -rf /tmp/ch4 && docker cp . sharelatex:/tmp/ch4 >/dev/null
docker exec -w /tmp/ch4 sharelatex sh -c 'latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > build.log 2>&1; echo latexmk=$?; grep -E "^!|Error|Undefined control|LaTeX Warning: (Reference|Citation)|Overfull \\hbox \([0-9]{2,}" main.log | sort | uniq -c | head -40'
docker cp sharelatex:/tmp/ch4/main.pdf D:/desk/llm/ch4/main.pdf 2>/dev/null
docker cp sharelatex:/tmp/ch4/main.log D:/desk/llm/ch4/main.log 2>/dev/null
