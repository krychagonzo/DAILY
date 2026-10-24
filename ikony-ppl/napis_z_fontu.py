# Napis "Porty Lotnicze" z konturów fontu Tahoma (Wine, LGPL), ułożony wg dopasowania do źródła
# (skala, pozycje słów, rozstrzał, korekty x liter z napis-tahoma-dopasowanie.json). Wynik: SVG w układzie źródła.
import sys, os, json, pathops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfd
from fontTools.pens.svgPathPen import SVGPathPen
fontp, fitp, out = sys.argv[1:4]
g = sfd.load(fontp); d = json.load(open(fitp)); P, dx = d["P"], d["dx"]
# "y" w Tahomie (oryginał) ma prosty ogonek ścięty poziomo; wersja Wine ma zakrzywiony -> poprawka:
# prawe ramię przedłużone po prostej (nachylenie jak górna część) do linii descendera -429
g[ord("y")]["c"] = [[("m", (1013, 1117)), ("l", (455, -429)), ("l", (287, -429)), ("l", (442, 0)),
                     ("l", (6, 1117)), ("l", (201, 1117)), ("l", (509, 238)), ("l", (818, 1117))]]
p = pathops.Path(); pen = p.getPen(); k = 0
class T:
    def __init__(s, f): s.f = f
    def moveTo(s, a): pen.moveTo(s.f(a))
    def lineTo(s, a): pen.lineTo(s.f(a))
    def curveTo(s, a, b, c): pen.curveTo(s.f(a), s.f(b), s.f(c))
    def closePath(s): pen.closePath()
for wx, w in ((P["x1"], "Porty"), (P["x2"], "Lotnicze")):
    x = 0
    for ch in w:
        off = dx[k]; f = lambda q, x=x, off=off, wx=wx: (wx + (q[0] + x) * P["s"] + off, P["base"] - q[1] * P["s"])
        sfd.draw(g, ord(ch), T(f)); x += g[ord(ch)]["w"] + P["trk"]; k += 1
p = pathops.simplify(p, fix_winding=True)
sp = SVGPathPen(None, ntos=lambda v: f"{v:.2f}"); p.draw(sp)
open(out, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="427"><path d="{sp.getCommands()}"/></svg>\n')
print(out)
