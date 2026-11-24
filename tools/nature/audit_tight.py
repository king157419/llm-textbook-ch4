"""Run audit_figure_collisions with tight glyph boxes.
Microsoft YaHei's font box (usWinAscent/Descent) is ~1.9 em tall, so get_texttrace boxes of a
line cover the next line and give false text-text overlaps on every multi-line label.
Here the audit falls back to span boxes with PyMuPDF's small glyph heights (the glyph em box)."""
import runpy, sys, pathlib, fitz
fitz.TOOLS.set_small_glyph_heights(True)
fitz.Page.get_texttrace = lambda self, *a, **k: []
sys.argv = ["audit_figure_collisions.py"] + sys.argv[1:]
runpy.run_path(str(pathlib.Path(__file__).with_name("audit_figure_collisions.py")), run_name="__main__")
