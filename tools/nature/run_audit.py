"""Split figaudit.pdf into one cropped PDF per figure, run the nature-figure audits,
and add book-specific checks (type sizes, bold use, text colours, centring)."""
import collections, json, subprocess, sys
from pathlib import Path
import fitz

HERE = Path(__file__).parent
SRC = HERE / "figaudit.pdf"
OUT = HERE / "figs"; OUT.mkdir(exist_ok=True)
NAMES = ["fig-roofline", "fig-overview", "fig-chips", "fig-memory", "fig-interconnect", "fig-stack",
         "fig-parallel", "fig-zero", "fig-prefill", "fig-kv", "fig-app", "fig-case"]
INK = {0x1A1A1A, 0x000000}
doc = fitz.open(SRC)
pages = [p for p in doc if p.get_drawings() or p.get_text().strip()]
report = {}
for name, page in zip(NAMES, pages):
    dr = page.get_drawings()
    ruler = min(dr, key=lambda d: d["rect"].y0)["rect"]           # white \textwidth rule
    rects = [d["rect"] for d in dr if d["rect"].y0 > ruler.y1 + 1]
    words = page.get_text("dict")["blocks"]
    spans = [s for b in words for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()]
    for s in spans: rects.append(fitz.Rect(s["bbox"]))
    bb = fitz.Rect(rects[0])
    for r in rects[1:]: bb |= r
    off = (bb.x0 + bb.x1) / 2 - (ruler.x0 + ruler.x1) / 2
    # cropped single-figure PDF
    one = fitz.open(); one.insert_pdf(doc, from_page=page.number, to_page=page.number)
    one[0].set_cropbox(bb + (-2, -2, 2, 2))
    f = OUT / f"{name}.pdf"; one.save(f)
    # book checks
    sizes = collections.Counter(round(s["size"], 1) for s in spans)
    fonts = collections.Counter(s["font"].split("+")[-1] for s in spans)
    bold = sorted({s["text"] for s in spans if "bold" in s["font"].lower() or "bd" in s["font"].lower()})
    colours = collections.Counter(f"#{s['color']:06X}" for s in spans)
    res = {"width_mm": round(bb.width / 72 * 25.4, 1), "center_offset_mm": round(off / 72 * 25.4, 1),
           "sizes_pt": dict(sizes), "fonts": dict(fonts), "bold_text": bold, "text_colours": dict(colours)}
    for script in ["audit_figure_collisions.py", "audit_pdf_text.py"]:
        r = subprocess.run([sys.executable, str(HERE / script), str(f)], capture_output=True, text=True, encoding="utf8")
        res[script] = {"exit": r.returncode, "out": (r.stdout + r.stderr).strip().splitlines()[-25:]}
    report[name] = res
(HERE / "audit_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf8")
for n, r in report.items():
    print(f"== {n}: width {r['width_mm']} mm, centre offset {r['center_offset_mm']} mm, sizes {r['sizes_pt']}, "
          f"colours {r['text_colours']}, collisions exit {r['audit_figure_collisions.py']['exit']}, text exit {r['audit_pdf_text.py']['exit']}")
    print("   bold:", r["bold_text"][:12])
