"""用 DeepSeek 对各节 LaTeX 源文件做语言润色（只改措辞与语病，不改结构与公式）。

用法: DEEPSEEK_API_KEY=... python polish_deepseek.py <源目录> <输出目录> [文件名...]
输出目录中每个文件旁会生成 .check.txt，列出 LaTeX 结构的差异（应为空）。
"""
import json, os, re, sys, urllib.request, collections

API = "https://api.deepseek.com/chat/completions"
SYSTEM = """你是一位资深的中文科技教材编辑。用户会给你一段 LaTeX 源码，是一本大学教材《大语言模型原理与技术》第4章“大模型计算系统”的一节。
你的任务：只做语言层面的润色——修正语病、搭配不当、主谓宾残缺、指代不清、逻辑连接词误用和不必要的口语化表达，使行文符合正式中文教材的规范。
硬性要求：
1. 不增删知识点，不改变任何技术事实、数字、公式和结论。
2. 所有 LaTeX 命令、环境、\\label、\\ref、\\eqref、\\cite、\\input、数学公式（$...$、\\[...\\]、equation、align 等）、代码块（lstlisting）必须原样保留，一个字符都不能改。
3. 不改变段落划分与环境结构，不添加 Markdown，不添加任何解释。
4. 中文与英文/数字之间保持原有的空格习惯；使用中文全角标点。
5. 如果某句已经通顺准确，就保持不动；宁可少改，不要过度改写。
只输出润色后的完整 LaTeX 源码，不要用代码块包裹。"""

def call(text, key):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        "temperature": 0.2, "max_tokens": 8000,
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.loads(r.read())["choices"][0]["message"]["content"]
    out = re.sub(r"^```(?:latex|tex)?\s*\n", "", out.strip())
    out = re.sub(r"\n```\s*$", "", out)
    return out.rstrip() + "\n"

def skeleton(s):
    """提取不允许被改动的结构元素。"""
    toks = re.findall(r"\\[A-Za-z@]+\*?", s)
    keyed = re.findall(r"\\(?:label|ref|eqref|cite|input|begin|end)\{[^}]*\}", s)
    math = re.findall(r"\$[^$]*\$", s)
    return collections.Counter(toks), collections.Counter(keyed), collections.Counter(math)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    files = sys.argv[3:] or sorted(f for f in os.listdir(src) if f.endswith(".tex"))
    key = os.environ["DEEPSEEK_API_KEY"]
    os.makedirs(dst, exist_ok=True)
    for f in files:
        s = open(os.path.join(src, f), encoding="utf-8").read()
        print("polishing", f, len(s), flush=True)
        for attempt in range(4):
            try:
                out = call(s, key)
                break
            except Exception as e:  # 网络偶发中断时重试
                print("  retry", attempt + 1, e, flush=True)
        else:
            continue
        open(os.path.join(dst, f), "w", encoding="utf-8").write(out)
        a, b = skeleton(s), skeleton(out)
        lines = []
        for name, x, y in zip(("commands", "keyed", "math"), a, b):
            if x != y:
                lines.append(f"[{name}] removed: {dict(x - y)}\n[{name}] added: {dict(y - x)}")
        open(os.path.join(dst, f + ".check.txt"), "w", encoding="utf-8").write("\n".join(lines))
        print("  structure diff:", "NONE" if not lines else "SEE CHECK FILE", flush=True)

if __name__ == "__main__":
    main()
