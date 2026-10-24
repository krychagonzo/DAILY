# Wektoryzacja ikon PPL: maska kształtu -> potrace (4x, wygładzone) -> SVG
import sys, numpy as np, cv2, potrace
src, mode, color, out, title = sys.argv[1:6]
if mode == "niebieski":            # niebieskie tło na białym (JPG)
    a = cv2.imread(src).astype(np.float32)
    ink = np.clip((a[:, :, 0] - a[:, :, 2]) / (133 - 0) * 255, 0, 255)   # niebieskość
else:                              # biały kształt na przezroczystym (PNG, kanał alfa)
    ink = cv2.imread(src, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32)
g = (255 - ink).astype(np.uint8)   # ciemne = kształt
ys, xs = np.where(g < 128); pad = 10
x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
x1, y1 = min(xs.max() + pad, g.shape[1]), min(ys.max() + pad, g.shape[0])
g = cv2.copyMakeBorder(g[y0:y1, x0:x1], pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
SC = 4
big = cv2.GaussianBlur(cv2.resize(g, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC), (0, 0), 1.5)
path = potrace.Bitmap(big >= 128).trace(turdsize=40, alphamax=1.0, opticurve=True, opttolerance=0.2)
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
 <title>{title}</title>
 <path fill="{color}" fill-rule="evenodd" d="{''.join(d)}"/>
</svg>
''')
print(out, w, h, len(path))
