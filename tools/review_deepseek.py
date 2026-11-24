"""让 DeepSeek 逐句审读各节 LaTeX 源文件，输出“问题句—问题—修改建议”清单（JSON），由人工判断后采纳。

用法: DEEPSEEK_API_KEY=... python review_deepseek.py <源目录> <输出 json> [文件名...]
"""
import json, os, re, sys, urllib.request

API = "https://api.deepseek.com/chat/completions"
SYSTEM = """你是一位严格的中文科技教材审校编辑，负责审读大学教材《大语言模型原理与技术》第4章“大模型计算系统”的 LaTeX 源码。
请逐句检查正文中的语言问题，包括：语病（成分残缺、搭配不当、语序不当、句式杂糅）、主语与谓语不匹配（例如“模型包含……运算”这类把过程当作组成部分的说法）、指代不清、逻辑关系词误用、前后表述不一致、口语化或宣传腔、冗余重复、不符合教材规范的表达，以及明显的技术表述不严谨之处。
忽略 LaTeX 命令、公式和代码本身，只看它们所在句子的中文表达。
输出严格的 JSON：{"issues":[{"original":"原句中出现问题的最短连续片段，必须与源码逐字一致（可包含其中的 LaTeX 命令）","problem":"问题说明","suggestion":"替换 original 的修改后片段，保留其中所有 LaTeX 命令"}]}
没有问题就返回 {"issues":[]}。不要输出 JSON 以外的任何内容。"""

def call(text, key):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        "temperature": 0.1, "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(json.loads(r.read())["choices"][0]["message"]["content"])

def main():
    src, out = sys.argv[1], sys.argv[2]
    files = sys.argv[3:]
    key = os.environ["DEEPSEEK_API_KEY"]
    result = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    for f in files:
        s = open(os.path.join(src, f), encoding="utf-8").read()
        for attempt in range(4):
            try:
                r = call(s, key); break
            except Exception as e:
                print("  retry", f, attempt + 1, e, flush=True)
        else:
            continue
        issues = r.get("issues", [])
        for it in issues:
            it["found"] = it.get("original", "") in s
        result[f] = issues
        print(f, len(issues), "issues", flush=True)
        json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
