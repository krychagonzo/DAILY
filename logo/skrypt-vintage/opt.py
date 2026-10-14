import sys, json; sys.path.insert(0, sys.argv[1])
from lib import *; from rules import build
font, srcp, out = sys.argv[2:5]
src = cv2.imread(srcp, 0); top, bot = comps_of(src)
def ratio(w, ch):
    f = inst(font, w); _, Ib = rec(f, "I"); _, gb = rec(f, ch); return (gb[2]-gb[0]) / Ib[3]
R = build({"A": ratio(760, "A")}, {"A": ratio(450, "A")})
S = src < 128
def glyph_score(idx, box, P):
    g = layout(font, src, 760, 450, R, params=P, only=idx)
    x, y, w, h = [int(v) for v in box[:4]]; m = 8; X0, Y0 = x - m, y - m
    sh = [(n, [(op, [(px - X0, py - Y0) for px, py in pts]) for op, pts in v]) for n, v in g]
    cov = raster(sh, (h + 2*m, w + 2*m)) > 0.5
    s = S[Y0:Y0+h+2*m, X0:X0+w+2*m]
    return (s & cov).sum() / (s | cov).sum()
P = {}
boxes = top + bot; text = "ACERTAINERA" + "VINTAGE"
for idx, (box, ch) in enumerate(zip(boxes, text)):
    tag = ("B" if idx < 11 else "L") + ch
    names = sorted({r[6] for r in R.get(tag, [])})
    best = glyph_score(idx, box, P); b0 = best
    for step in (0.04, 0.02, 0.01, 0.005, 0.0025):
        improved = True
        while improved and names:
            improved = False
            for n in names:
                for d in (step, -step):
                    Q = dict(P); Q[n] = Q.get(n, 0) + d; s = glyph_score(idx, box, Q)
                    if s > best + 1e-5: best, P, improved = s, Q, True; break
    print(idx, ch, round(b0, 4), "->", round(best, 4), {n: round(P.get(n, 0), 4) for n in names}, flush=True)
json.dump(P, open(out, "w"), indent=1)
