# Składa logo "PPL Porty Lotnicze": wygładzony znak z ppl-logo.svg (dopasowany do koła w źródle)
# + napis zwektoryzowany przez wektoryzuj.py (tryb "tekst"). Wynik: jedna ścieżka, przycięta z marginesem.
import sys, re, pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
znak_svg, tekst_svg, cx, cy, r, color, out = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:6]), sys.argv[6], sys.argv[7]
ZCX, ZCY, ZR = 512.30, 385.99, 299.18           # koło w ppl-logo.svg
s = r / ZR
def path_of(f):
    return re.search(r' d="([^"]+)"', open(f).read()).group(1)
p = pathops.Path(); pen = p.getPen()
parse_path(path_of(znak_svg), TransformPen(pen, (s, 0, 0, s, cx - ZCX * s, cy - ZCY * s)))
parse_path(path_of(tekst_svg), pen)
x0, y0, x1, y1 = p.bounds; M = 20
sp = SVGPathPen(None, ntos=lambda v: f"{v:.2f}")
p.draw(TransformPen(sp, (1, 0, 0, 1, M - x0, M - y0)))
W, H = round(x1 - x0 + 2 * M), round(y1 - y0 + 2 * M)
open(out, "w").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
 <title>PPL Porty Lotnicze</title>
 <path fill="{color}" d="{sp.getCommands()}"/>
</svg>
''')
print(out, W, H)
