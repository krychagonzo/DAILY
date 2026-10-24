# minimalny parser FontForge SFD: kontury (m/l/c) + szerokości, wg kodu Unicode
import re
def load(path):
    g = {}; cur = None; inspl = False
    for line in open(path, encoding="latin-1"):
        line = line.rstrip("\n")
        if line.startswith("StartChar:"): cur = {"w": 0, "c": [], "u": None, "ref": []}
        elif cur is None: continue
        elif line.startswith("Encoding:"): cur["u"] = int(line.split()[2]) if int(line.split()[2]) >= 0 else int(line.split()[1])
        elif line.startswith("Width:"): cur["w"] = int(line.split()[1])
        elif line.startswith("Refer:"):
            p = line.split(); cur["ref"].append((int(p[1]), [float(v) for v in p[4:10]]))
        elif line == "SplineSet": inspl = True
        elif line == "EndSplineSet": inspl = False
        elif inspl:
            t = line.split()
            if not t: continue
            if "m" in t: cur["c"].append([("m", (float(t[0]), float(t[1])))])
            elif "l" in t: cur["c"][-1].append(("l", (float(t[0]), float(t[1]))))
            elif "c" in t: v = list(map(float, t[:6])); cur["c"][-1].append(("c", (v[0], v[1]), (v[2], v[3]), (v[4], v[5])))
        elif line == "EndChar":
            g[cur["u"]] = cur; cur = None
    return g
def draw(g, code, pen, glyphs=None):
    gl = g[code]
    for c in gl["c"]:
        for seg in c:
            if seg[0] == "m": pen.moveTo(seg[1])
            elif seg[0] == "l": pen.lineTo(seg[1])
            else: pen.curveTo(seg[1], seg[2], seg[3])
        pen.closePath()

def load_ufo(path):
    """UFO -> ten sam format co load(): {unicode: {"w":, "c": [[("m",p),("l",p),("c",a,b,c)...]]}}"""
    from fontTools.ufoLib import UFOReader
    from fontTools.pens.basePen import BasePen
    r = UFOReader(path); gs = r.getGlyphSet(); cmap = r.getCharacterMapping()
    class P(BasePen):
        def __init__(s): super().__init__(gs); s.c = []
        def _moveTo(s, p): s.c.append([("m", p)])
        def _lineTo(s, p): s.c[-1].append(("l", p))
        def _curveToOne(s, a, b, c): s.c[-1].append(("c", a, b, c))
        def _closePath(s): pass
        def _endPath(s): pass
    out = {}
    for u, names in cmap.items():
        if u > 0x17F: continue
        gl = gs[names[0]]; p = P(); gl.draw(p)
        out[u] = {"w": gl.width, "c": p.c}
    return out
def load_any(path):
    return load_ufo(path) if path.rstrip("/").endswith(".ufo") else load(path)

def smooth_joins(g, max_deg=15.0):
    """Wine-Tahoma ma miejscami krzywe wchodzące w proste odcinki pod lekkim kątem (uskok, np. bark "n").
    Gdy krzywa i odcinek spotykają się prawie stycznie (< max_deg), uchwyt krzywej zostaje ustawiony
    dokładnie w kierunku odcinka (z zachowaniem długości) -> gładkie przejście."""
    import math
    fixed = 0
    for gl in g.values():
        for c in gl["c"]:
            n = len(c)
            for i in range(1, n):
                for (a, b) in ((c[i-1], c[i]), (c[i], c[i-1] if False else c[(i+1) % n] if i + 1 < n else None)):
                    pass
            # przejdź po kolejnych parach segmentów (z punktem wspólnym)
            segs = c
            for i in range(1, n):
                prev, cur = segs[i-1], segs[i]
                p_end = prev[-1] if prev[0] != "c" else prev[3]
                # line -> curve: uchwyt cur[1] wzdłuż kierunku odcinka prev
                if prev[0] == "l" and cur[0] == "c" and i >= 2:
                    a0 = segs[i-2][-1] if segs[i-2][0] != "c" else segs[i-2][3]
                    d = (p_end[0] - a0[0], p_end[1] - a0[1]); h = (cur[1][0] - p_end[0], cur[1][1] - p_end[1])
                    L, H = math.hypot(*d), math.hypot(*h)
                    if L > 1 and H > 1:
                        ang = math.degrees(math.acos(max(-1, min(1, (d[0]*h[0] + d[1]*h[1]) / (L * H)))))
                        if 0.01 < ang < max_deg:
                            segs[i] = ("c", (p_end[0] + d[0] / L * H, p_end[1] + d[1] / L * H), cur[2], cur[3]); fixed += 1
                # curve -> line: uchwyt prev[2] przeciwnie do kierunku następnego odcinka
                nxt = segs[i]
                if prev[0] == "c" and nxt[0] == "l":
                    e = prev[3]; d = (nxt[1][0] - e[0], nxt[1][1] - e[1]); h = (prev[2][0] - e[0], prev[2][1] - e[1])
                    L, H = math.hypot(*d), math.hypot(*h)
                    if L > 1 and H > 1:
                        ang = math.degrees(math.acos(max(-1, min(1, -(d[0]*h[0] + d[1]*h[1]) / (L * H)))))
                        if 0.01 < ang < max_deg:
                            segs[i-1] = ("c", prev[1], (e[0] - d[0] / L * H, e[1] - d[1] / L * H), e); fixed += 1
            # zawinięcie: ostatnia krzywa kończy się w punkcie startu, a pierwszy segment to odcinek
            last = segs[-1]
            if last[0] == "c" and n > 2 and segs[1][0] == "l" and math.hypot(last[3][0] - segs[0][1][0], last[3][1] - segs[0][1][1]) < 0.5:
                e = last[3]; d = (segs[1][1][0] - e[0], segs[1][1][1] - e[1]); h = (last[2][0] - e[0], last[2][1] - e[1])
                L, H = math.hypot(*d), math.hypot(*h)
                if L > 1 and H > 1:
                    ang = math.degrees(math.acos(max(-1, min(1, -(d[0]*h[0] + d[1]*h[1]) / (L * H)))))
                    if 0.01 < ang < max_deg:
                        segs[-1] = ("c", last[1], (e[0] - d[0] / L * H, e[1] - d[1] / L * H), e); fixed += 1
    return fixed
