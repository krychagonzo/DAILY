import sys, cv2, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
font, src, out = sys.argv[1:4]
g = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
n, lab, st, _ = cv2.connectedComponentsWithStats((g < 128).astype(np.uint8), 8)
comps = sorted([st[i] for i in range(1, n) if st[i][4] > 50], key=lambda s: (s[1] > 350, s[0]))
top, bot = comps[:11], comps[11:]
fonts = {w: instantiateVariableFont(TTFont(font), {"wght": w}) for w in (720, 450)}
def glyph(f, ch):
    gs = f.getGlyphSet(); gn = f.getBestCmap()[ord(ch)]
    p = BoundsPen(gs); gs[gn].draw(p); return gs, gn, p.bounds
def capbase(row):
    ys = [c[1] for c in row]; hs = [c[3] for c in row]
    # cap top / baseline from flat letters (exclude round overshoot): use median
    t = int(np.median(ys)); b = int(np.median([y+h for y, h in zip(ys, hs)])); return t, b
paths = []
for row, text, w in ((top, "ACERTAINERA", 720), (bot, "VINTAGE", 450)):
    f = fonts[w]; t, b = capbase(row)
    _, _, Ib = glyph(f, "I"); s = (b - t) / (Ib[3] - Ib[1])   # cap height scale
    for c, ch in zip(row, text):
        gs, gn, gb = glyph(f, ch)
        gw = (gb[2] - gb[0]) * s
        sx = min(1.08, max(0.92, c[2] / gw)) * s          # dopasowanie szerokości ±8 %
        cx = c[0] + c[2] / 2
        tx = cx - (gb[0] + gb[2]) / 2 * sx
        pen = SVGPathPen(gs)
        gs[gn].draw(TransformPen(pen, (sx, 0, 0, -s, tx, b)))
        paths.append(pen.getCommands())
xs = [c[0] for c in comps]; xe = [c[0] + c[2] for c in comps]; ys = [c[1] for c in comps]; ye = [c[1] + c[3] for c in comps]
pad = 40; X0, Y0, X1, Y1 = min(xs) - pad, min(ys) - pad, max(xe) + pad, max(ye) + pad
open(out, "w").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{X1-X0}" height="{Y1-Y0}" viewBox="{X0} {Y0} {X1-X0} {Y1-Y0}">
 <title>A CERTAIN ERA VINTAGE - logo, krzywe</title>
 <path fill="#000000" d="{" ".join(paths)}"/>
</svg>
''')
print("ok", X1-X0, Y1-Y0)
