import cv2, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
SRC = None
def comps_of(g):
    n, lab, st, _ = cv2.connectedComponentsWithStats((g < 128).astype(np.uint8), 8)
    c = sorted([st[i] for i in range(1, n) if st[i][4] > 50], key=lambda s: (s[1] > 350, s[0]))
    return c[:11], c[11:]
_fc = {}
def inst(path, w):
    k = (path, w)
    if k not in _fc:
        from fontTools.ttLib.removeOverlaps import removeOverlaps
        f = instantiateVariableFont(TTFont(path), {"wght": w}); removeOverlaps(f); _fc[k] = f
    return _fc[k]
def rec(f, ch):
    gs = f.getGlyphSet(); gn = f.getBestCmap()[ord(ch)]
    p = RecordingPen(); gs[gn].draw(p); b = BoundsPen(gs); gs[gn].draw(b)
    return p.value, b.bounds
def capb(row):
    return int(np.median([c[1] for c in row])), int(np.median([c[1] + c[3] for c in row]))
def layout(font, src_img, wb=720, wl=450, edits={}, fit=True, params={}, only=None):
    gi = -1
    """returns list of contours (each list of segments in image coords) + svg d"""
    top, bot = comps_of(src_img)
    glyphs = []
    for row, text, w, tag in ((top, "ACERTAINERA", wb, "B"), (bot, "VINTAGE", wl, "L")):
        f = inst(font, w); t, b = capb(row)
        _, Ib = rec(f, "I"); capH = Ib[3] - Ib[1]; s = (b - t) / capH
        for i, (c, ch) in enumerate(zip(row, text)):
            gi += 1
            if only is not None and gi != only: continue
            v, gb = rec(f, ch)
            if tag == 'L' and ch == 'G' and params.get('Gbar'): v = g_hook(v, gb, capH, params['Gbar'])
            gw = (gb[2] - gb[0]) * s
            sx = (min(1.08, max(0.92, c[2] / gw)) if fit else 1) * s
            tx = c[0] + c[2] / 2 - (gb[0] + gb[2]) / 2 * sx
            ed = edits.get(f"{tag}{i}", edits.get(f"{tag}{ch}", []))
            def T(p, gb=gb, sx=sx, tx=tx, ed=ed, s=s, b=b):
                x, y = p
                nx = (x - gb[0]) / (gb[2] - gb[0]); ny = y / capH
                for (ylo, yhi, xlo, xhi, kx, ky, pn, *fall) in ed:
                    p_ = params.get(pn, 0.0)
                    if fall:   # płynne wygaszenie: pełne przesunięcie przy y_full, zero przy y_zero
                        yf, yz = fall[0]; p_ *= min(1, max(0, (yz - ny) / (yz - yf)))
                    if ylo <= ny <= yhi and xlo <= nx <= xhi:
                        x += kx * p_ * capH; y += ky * p_ * capH
                return (x * sx + tx, b - y * s)
            glyphs.append((tag + ch + str(i), [(op, [T(p) for p in pts]) for op, pts in v]))
    return glyphs
def to_d(glyphs):
    out = []
    for _, v in glyphs:
        for op, pts in v:
            P = " ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
            if op == "moveTo": out.append("M" + P)
            elif op == "lineTo": out.append("L" + P)
            elif op == "curveTo": out.append("C" + P)
            elif op == "qCurveTo":
                # expand implied on-curve points
                ps = pts
                for k in range(len(ps) - 1):
                    a = ps[k]; e = ps[k + 1] if k == len(ps) - 2 else ((ps[k][0] + ps[k+1][0]) / 2, (ps[k][1] + ps[k+1][1]) / 2)
                    out.append(f"Q{a[0]:.2f} {a[1]:.2f} {e[0]:.2f} {e[1]:.2f}")
            elif op in ("closePath", "endPath"): out.append("Z")
    return "".join(out)
def flatten(v, N=12):
    polys = []; cur = []; last = None
    for op, pts in v:
        if op == "moveTo": cur = [pts[0]]; last = pts[0]
        elif op == "lineTo": cur.append(pts[0]); last = pts[0]
        elif op == "curveTo":
            p0 = np.array(last); p1, p2, p3 = map(np.array, pts)
            for t in np.linspace(0, 1, N)[1:]:
                cur.append(tuple((1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t*t*p2 + t**3*p3))
            last = pts[-1]
        elif op == "qCurveTo":
            ps = list(pts)
            for k in range(len(ps) - 1):
                a = np.array(ps[k]); e = np.array(ps[k+1]) if k == len(ps) - 2 else (np.array(ps[k]) + np.array(ps[k+1])) / 2
                p0 = np.array(last)
                for t in np.linspace(0, 1, N)[1:]:
                    cur.append(tuple((1-t)**2*p0 + 2*(1-t)*t*a + t*t*e))
                last = tuple(e)
        elif op in ("closePath", "endPath"):
            if cur: polys.append(cur); cur = []
    return polys
def raster(glyphs, shape, ss=4):
    acc = np.zeros((shape[0]*ss, shape[1]*ss), np.int16)
    for _, v in glyphs:
        for poly in flatten(v):
            a = np.array(poly) 
            area = 0.5 * np.sum(a[:-1,0]*a[1:,1] - a[1:,0]*a[:-1,1]) + 0.5*(a[-1,0]*a[0,1]-a[0,0]*a[-1,1])
            m = np.zeros_like(acc, np.uint8)
            cv2.fillPoly(m, [np.round((a * ss - 0.5*0) ).astype(np.int32)], 1, lineType=cv2.LINE_8)
            acc += np.where(area > 0, 1, -1) * m.astype(np.int16)
    cov = (acc != 0).astype(np.float32)
    return cv2.resize(cov, (shape[1], shape[0]), interpolation=cv2.INTER_AREA)
def score(src, cov, boxes):
    S = src < 128; R = cov > 0.5
    res = []
    for c in boxes:
        x, y, w, h = c[:4]; sl = (slice(y-6, y+h+6), slice(x-6, x+w+6))
        res.append(((S[sl] & R[sl]).sum() / (S[sl] | R[sl]).sum()))
    return res

def g_hook(v, gb, capH, d):
    """wydłuża poprzeczkę G w lewo, zachowując prostokątny kształt (pozioma belka + pionowy trzon)"""
    W = gb[2] - gb[0]; out = []
    xs = [p[0] for op, pts in v if op == "lineTo" for p in pts]
    xR = max(xs)
    for op, pts in v:
        if op == "lineTo":
            x, y = pts[0]; nx = (x - gb[0]) / W; ny = y / capH
            if 0.7 < nx < 0.9 and 0.45 < ny < 0.55:
                t = xR - x                     # grubość trzonu = grubość belki
                out += [("lineTo", [(x, y - t)]), ("lineTo", [(x + d * capH, y - t)]), ("lineTo", [(x + d * capH, y)])]
                continue
        out.append((op, pts))
    return out
