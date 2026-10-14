import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
font_path, out_dir = sys.argv[1], sys.argv[2]
f = TTFont(font_path); gs = f.getGlyphSet(); cmap = f.getBestCmap()
HEIGHT_MM = 250.0  # wysokość cyfry
for num in ["1", "4", "18", "30", "32"]:
    x = 0; parts = []; xmin = ymin = 1e9; xmax = ymax = -1e9
    for ch in num:
        g = cmap[ord(ch)]
        bp = BoundsPen(gs); gs[g].draw(bp)
        b = bp.bounds
        xmin, ymin = min(xmin, b[0] + x), min(ymin, b[1]); xmax, ymax = max(xmax, b[2] + x), max(ymax, b[3])
        pen = SVGPathPen(gs); gs[g].draw(pen)
        parts.append((x, pen.getCommands()))
        x += gs[g].width
    s = HEIGHT_MM / (ymax - ymin)
    w, h = (xmax - xmin) * s, HEIGHT_MM
    paths = "\n".join(f'  <path transform="translate({(dx - xmin) * s:.3f},{ymax * s:.3f}) scale({s:.6f},{-s:.6f})" d="{d}"/>' for dx, d in parts)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" viewBox="0 0 {w:.3f} {h:.3f}">
 <title>Numer {num} - Open Sans ExtraBold SemiCondensed, krzywe</title>
 <g fill="#000000">
{paths}
 </g>
</svg>
'''
    open(f"{out_dir}/numer-{num}.svg", "w").write(svg)
    print(num, f"{w:.1f} x {h:.1f} mm")
