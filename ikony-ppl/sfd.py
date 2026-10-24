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
