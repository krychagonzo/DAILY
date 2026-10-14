import sys, numpy as np, cv2, potrace
src, out = sys.argv[1], sys.argv[2]
g = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
ys, xs = np.where(g < 128); pad = 20
x0, x1, y0, y1 = xs.min()-pad, xs.max()+pad, ys.min()-pad, ys.max()+pad
g = g[y0:y1, x0:x1]
SC = 4
big = cv2.resize(g, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
big = cv2.GaussianBlur(big, (0, 0), 1.2)
bmp = potrace.Bitmap(big >= 128)
path = bmp.trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.2)
d = []
for c in path:
    s = c.start_point; d.append(f"M{s.x/SC:.2f},{s.y/SC:.2f}")
    for seg in c.segments:
        if seg.is_corner:
            d.append(f"L{seg.c.x/SC:.2f},{seg.c.y/SC:.2f}L{seg.end_point.x/SC:.2f},{seg.end_point.y/SC:.2f}")
        else:
            d.append(f"C{seg.c1.x/SC:.2f},{seg.c1.y/SC:.2f} {seg.c2.x/SC:.2f},{seg.c2.y/SC:.2f} {seg.end_point.x/SC:.2f},{seg.end_point.y/SC:.2f}")
    d.append("Z")
h, w = g.shape
open(out, "w").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
 <title>A Certain Era VINTAGE - logo, krzywe</title>
 <path fill="#000000" fill-rule="evenodd" d="{''.join(d)}"/>
</svg>
''')
print("ok", w, h, len(path))
