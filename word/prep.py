# Flatten the ch4 LaTeX into one pandoc-friendly file: figures -> PNG,
# tcolorboxes -> quotes, \ref resolved to the printed numbers.
import re, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(r"D:\desk\llm\ch4\overleaf")
OUT = pathlib.Path(r"D:\desk\llm\ch4\word")
CH = 4

order = re.findall(r"\\input\{(sections/[^}]+)\}", (ROOT / "main.tex").read_text("utf-8"))
src = "\n".join((ROOT / f"{s}.tex").read_text("utf-8") for s in order)

# 1. figures: replace \input{figs/x} with a PNG figure, keep caption + label
fig_no = 0
def fig(m):
    global fig_no
    fig_no += 1
    t = (ROOT / f"{m.group(1)}.tex").read_text("utf-8")
    cap = re.search(r"\\caption\{(.*)\}\s*\n\s*\\label", t, re.S).group(1)
    lab = re.search(r"\\label\{([^}]+)\}", t).group(1)
    return (f"\\begin{{figure}}\n\\centering\n\\includegraphics[width=0.9\\linewidth]{{figs/fig{fig_no:02d}.png}}\n"
            f"\\caption{{{cap}}}\\label{{{lab}}}\n\\end{{figure}}")
src = re.sub(r"\\input\{(figs/[^}]+)\}", fig, src)

# 2. walk the document in order to number labels
labels, cnt = {}, dict(sec=0, sub=0, fig=0, tab=0, eq=0, ex=0)
cur = None
tok = re.compile(r"\\(section|subsection)\*?\{|\\begin\{(figure|table|equation|example)\}(\[[^\]]*\]\{([^}]+)\})?|\\label\{([^}]+)\}|\\end\{equation\}")
for m in tok.finditer(src):
    if m.group(1) == "section" and not src[m.start():m.end()].endswith("*{"):
        cnt["sec"] += 1; cnt["sub"] = 0; cur = f"{CH}.{cnt['sec']}"
    elif m.group(1) == "subsection" and not src[m.start():m.end()].endswith("*{"):
        cnt["sub"] += 1; cur = f"{CH}.{cnt['sec']}.{cnt['sub']}"
    elif m.group(2) == "figure": cnt["fig"] += 1; cur = f"{CH}-{cnt['fig']}"
    elif m.group(2) == "table": cnt["tab"] += 1; cur = f"{CH}-{cnt['tab']}"
    elif m.group(2) == "equation": cnt["eq"] += 1; cur = f"{CH}-{cnt['eq']}"
    elif m.group(2) == "example":
        cnt["ex"] += 1; labels[m.group(4)] = f"{CH}-{cnt['ex']}"
    elif m.group(5): labels.setdefault(m.group(5), cur)

# 2b. hard-code heading numbers (pandoc would restart at 1)
s_no = sub_no = 0
def head(m):
    global s_no, sub_no
    if m.group(2): return m.group(0)
    if m.group(1) == "section":
        s_no += 1; sub_no = 0; num = f"{CH}.{s_no}"
    else:
        sub_no += 1; num = f"{CH}.{s_no}.{sub_no}"
    return f"\\{m.group(1)}*{{{num}\\quad "
src = re.sub(r"\\(section|subsection)(\*)?\{", head, src)
src = re.sub(r"\\chapter\{", rf"\\chapter*{{第 {CH} 章\\quad ", src)

# 3. equations: add visible tags, drop labels inside
eq_no = 0
def eq(m):
    global eq_no
    eq_no += 1
    body = re.sub(r"\\label\{[^}]+\}", "", m.group(1))
    return f"\\[\n{body.strip()} \\tag{{{CH}-{eq_no}}}\n\\]"
src = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", eq, src, flags=re.S)

# 4. figure / table captions get their printed number
for kind, word in (("figure", "图"), ("table", "表")):
    n = 0
    def cap(m):
        global n
        n += 1
        return f"{m.group(1)}\\caption{{{word} {CH}-{n}\\quad "
    src = re.sub(rf"(\\begin\{{{kind}\}}.*?)\\caption\{{", cap, src, flags=re.S)

# 5. resolve refs
def ref(m):
    k = m.group(1)
    if k not in labels: print("unresolved", k); return "??"
    return labels[k]
src = re.sub(r"\\ref\{([^}]+)\}", ref, src)
src = re.sub(r"\\label\{[^}]+\}", "", src)

# 6. boxes -> quotes with bold titles
ex_no = 0
def exbox(m):
    global ex_no
    ex_no += 1
    return f"\\begin{{quote}}\n\\textbf{{例 {CH}-{ex_no}\\quad {m.group(1)}}}\n\n"
src = re.sub(r"\\begin\{example\}\[([^\]]*)\]\{[^}]*\}", exbox, src)
src = src.replace("\\begin{pitfall}", "\\begin{quote}\n\\textbf{辨析}\\quad ")
src = src.replace("\\begin{keypoints}", "\\begin{quote}\n\\textbf{本节要点}\n\n")
src = src.replace("\\begin{guide}", "\\begin{quote}\n")
src = re.sub(r"\\end\{(example|pitfall|keypoints|guide)\}", r"\\end{quote}", src)
src = re.sub(r"\\begin\{minipage\}\[c\]\{0\.3\\linewidth\}\\centering\\locator\{\d\}\\end\{minipage\}", "", src)
src = re.sub(r"\\begin\{minipage\}(\[[^\]]*\])?\{[^}]*\}|\\end\{minipage\}|\\hfill", "", src)
src = re.sub(r"\\locator\{\d\}", "", src)

# 6b. tabularx -> plain tabular (pandoc cannot parse the Y column / @{})
def tabx(m):
    spec = m.group(1).replace("@{}", "")
    spec = re.sub(r">\{[^}]*\}p\{[^}]*\}", "l", spec)
    spec = spec.replace("Y", "l").replace("X", "l")
    return f"\\begin{{tabular}}{{{spec.strip()}}}"
src = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*(?:\{[^{}]*\})?[^{}]*\})*)\}", tabx, src)
src = src.replace("\\end{tabularx}", "\\end{tabular}")
src = re.sub(r"\\begin\{longtable\}\{[^\n]*\}", "\\\\begin{longtable}{lll}", src)

# 7. simple macros pandoc does not know
src = re.sub(r"\\guideitem\{([^}]*)\}\{", r"\\par\\textbf{\1}\\quad{", src)
src = src.replace("\\quad", "\u3000")  # pandoc drops \quad; use a full-width space
src = re.sub(r"\\(term|emph)\{", r"\\textbf{", src)
src = re.sub(r"\\en\{", r"{", src)
src = re.sub(r"\\(heiti|songti|kaishu|fangsong|small|footnotesize)\b\s*", "", src)
src = re.sub(r"\\(markright|addcontentsline\{toc\}\{section\})\{[^}]*\}", "", src)
src = re.sub(r"\\(Needspace|needspace)\{[^}]*\}", "", src)

doc = ("\\documentclass{article}\n\\usepackage{graphicx,booktabs,longtable,amsmath}\n"
       "\\begin{document}\n" + src + "\n\\end{document}\n")
(OUT / "ch4_flat.tex").write_text(doc, "utf-8")
print("labels", len(labels), "figs", fig_no, "eqs", eq_no, "examples", ex_no)
