# Dopasowanie konturów fontu do liter z obrazu ("wektoryzacja prowadzona fontem").
# Każdy glif (już ustawiony w miejscu litery) jest odkształcany GŁADKIM polem przesunięć
# (siatka węzłów RBF, mało parametrów) tak, by jego kontur leżał na krawędzi liter w źródle
# (pole odległości ze znakiem liczone z 8x powiększonego obrazu). Ruszane są punkty kontrolne
# krzywych, więc kontur pozostaje złożony z tych samych gładkich krzywych i prostych odcinków.
import sys, os, json, math, numpy as np, cv2, pathops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfd
from scipy.optimize import least_squares
from fontTools.pens.svgPathPen import SVGPathPen
src, fontp, fitp, out = sys.argv[1:5]
# --- pole odległości ze znakiem (px źródła), ujemne wewnątrz liter
a = cv2.imread(src).astype(np.float32)
ink = np.clip((a[:, :, 0] - a[:, :, 2]) / 128, 0, 1); ink[:, :340] = 0
UP = 8
big = cv2.resize(ink, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
big = cv2.GaussianBlur(big, (0, 0), UP * 0.35)
m = (big > 0.5).astype(np.uint8)
din = cv2.distanceTransform(m, cv2.DIST_L2, 5); dout = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
SDF = ((dout - din) / UP).astype(np.float32)
def sdf_at(P):
    # dokładna interpolacja dwuliniowa (cv2.remap ma tylko 1/32 px precyzji)
    x = P[:, 0] * UP - 0.5; y = P[:, 1] * UP - 0.5     # współrz. ciągła X -> indeks piksela 8x
    H_, W_ = SDF.shape
    x = np.clip(x, 0, W_ - 1.001); y = np.clip(y, 0, H_ - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    v00 = SDF[y0, x0]; v01 = SDF[y0, x0 + 1]; v10 = SDF[y0 + 1, x0]; v11 = SDF[y0 + 1, x0 + 1]
    return (v00 * (1 - fx) + v01 * fx) * (1 - fy) + (v10 * (1 - fx) + v11 * fx) * fy
# --- glify ustawione jak w dopasowaniu (skala, pozycje, korekty)
g = sfd.load(fontp); d = json.load(open(fitp)); P_, dx = d["P"], d["dx"]
g[ord("y")]["c"] = [[("m", (1013, 1117)), ("l", (455, -429)), ("l", (287, -429)), ("l", (442, 0)),
                     ("l", (6, 1117)), ("l", (201, 1117)), ("l", (509, 238)), ("l", (818, 1117))]]
sfd.smooth_joins(g)   # usuwa uskoki na styku łuk-prosta (np. bark "n")
placed = []; k = 0
for wx, w in ((P_["x1"], "Porty"), (P_["x2"], "Lotnicze")):
    x = 0
    for ch in w:
        f = lambda q, x=x, off=dx[k], wx=wx: (wx + (q[0] + x) * P_["s"] + off, P_["base"] - q[1] * P_["s"])
        conts = [[(seg[0], [np.array(f(q)) for q in seg[1:]]) for seg in c] for c in g[ord(ch)]["c"]]
        placed.append((ch, conts)); x += g[ord(ch)]["w"] + P_["trk"]; k += 1
def flat_points(conts):
    """lista punktów kontrolnych + macierz próbkowania konturu (próbki = B @ punkty)"""
    pts = []; rows = []
    for c in conts:
        start = len(pts); prev = None
        for seg in c:
            op, ps = seg
            if op == "m": pts.append(ps[0]); prev = len(pts) - 1; first = prev; continue
            if op == "l":
                pts.append(ps[0]); cur = len(pts) - 1
                L = np.linalg.norm(pts[cur] - pts[prev]); n = max(2, int(L / 0.4))
                for t in np.linspace(0, 1, n, endpoint=False): rows.append({prev: 1 - t, cur: t})
                prev = cur
            else:
                i1 = len(pts); pts += ps; i3 = len(pts) - 1
                L = sum(np.linalg.norm(pts[j+1] - pts[j]) for j in (prev, i1, i1 + 1) if j + 1 <= i3 or True) if False else np.linalg.norm(pts[i3] - pts[prev]) * 1.3
                n = max(3, int(L / 0.4))
                for t in np.linspace(0, 1, n, endpoint=False):
                    rows.append({prev: (1-t)**3, i1: 3*(1-t)**2*t, i1+1: 3*(1-t)*t*t, i3: t**3})
                prev = i3
        # zamknięcie
        L = np.linalg.norm(pts[first] - pts[prev]); n = max(2, int(L / 0.4))
        if L > 1e-6:
            for t in np.linspace(0, 1, n, endpoint=False): rows.append({prev: 1 - t, first: t})
    X = np.array(pts); B = np.zeros((len(rows), len(X)))
    for i, r in enumerate(rows):
        for j, v in r.items(): B[i, j] += v
    return X, B
NX, NY = 2, 3
WEIGHT = float(os.environ.get('WEIGHT', '0'))   # wspólna korekta grubości kreski [px]
def outward_normals(conts):
    """normalna na zewnątrz farby dla każdego punktu kontrolnego (konwencja TrueType: farba po prawej
    stronie kierunku obiegu w układzie y-góra; po odwróceniu osi y: n = (d_y, -d_x))"""
    N = []
    for c in conts:
        P = [q for op, ps in c for q in ps]; n = len(P)
        for i in range(n):
            d = P[(i + 1) % n] - P[i - 1]
            if np.linalg.norm(d) < 1e-9: d = P[(i + 2) % n] - P[i - 2]
            v = np.array([d[1], -d[0]]); N.append(v / (np.linalg.norm(v) + 1e-12))
    return np.array(N)
def snap_axes(conts, tol_deg=2.5):
    """odcinki prawie pionowe/poziome -> dokładnie pionowe/poziome (sąsiednie uchwyty krzywych idą razem)"""
    for c in conts:
        P = [q for op, ps in c for q in ps]; n = len(P)
        ops = [op for op, ps in c for _ in ps]
        for i in range(n):
            j = (i + 1) % n
            if ops[j] != "l" and not (j == 0 and ops[0] == "m"): continue
            d = P[j] - P[i]; L = np.linalg.norm(d)
            if L < 2: continue
            ang = math.degrees(math.atan2(d[1], d[0])) % 180
            for axis, k_ in ((0, 1), (90, 0)):
                if min(abs(ang - axis), 180 - abs(ang - axis)) < tol_deg:
                    mval = (P[i][k_] + P[j][k_]) / 2
                    for idx in (i, j):
                        delta = mval - P[idx][k_]; P[idx][k_] = mval
                        for nb in ((idx - 1) % n, (idx + 1) % n):   # uchwyt krzywej przy tym punkcie
                            if ops[nb] == "c" and nb not in (i, j): P[nb][k_] += delta   # uchwyt krzywej razem z punktem (bez załamania)
    return conts
res_conts = []
for ch, conts in placed:
    X, B = flat_points(conts); Nrm = outward_normals(conts)
    c0 = X.mean(0); Xc = X - c0
    x0, y0 = X.min(0) - 3; x1, y1 = X.max(0) + 3
    gx = np.linspace(x0, x1, NX); gy = np.linspace(y0, y1, NY)
    nodes = np.array([(u, v) for v in gy for u in gx]); sig = max(x1 - x0, y1 - y0) * 0.5
    Phi = np.exp(-((X[:, None, :] - nodes[None]) ** 2).sum(-1) / (2 * sig * sig)); Phi /= Phi.sum(1, keepdims=True)
    K = len(nodes)
    def apply(u):
        A = np.array([[1 + u[0], u[1]], [u[2], 1 + u[3]]])
        return c0 + Xc @ A.T + u[4:6] + WEIGHT * Nrm + Phi @ u[7:].reshape(-1, 2)
    def resid(u):
        r = sdf_at(B @ apply(u))
        reg = np.concatenate([15 * u[0:4], 0.01 * u[4:6], [10 * u[6]], 0.4 * u[7:]])
        return np.concatenate([r, reg])
    u0 = np.zeros(7 + 2 * K); r0 = resid(u0)
    sol = least_squares(resid, u0, x_scale=1.0, max_nfev=600)
    Xn = apply(sol.x)
    e0 = np.sqrt(np.mean(r0[:len(B)] ** 2)); e1 = np.sqrt(np.mean(resid(sol.x)[:len(B)] ** 2))
    print(f"{ch}: błąd krawędzi {e0:.2f} -> {e1:.2f} px | skala x {1+sol.x[0]:.3f} y {1+sol.x[3]:.3f} pochylenie {sol.x[1]:.3f} przesunięcie {sol.x[4]:+.2f},{sol.x[5]:+.2f} px")
    it = iter(Xn); nc = []
    for c in conts:
        cc = []
        for op, ps in c: cc.append((op, [np.array(next(it)) for _ in ps]))
        nc.append(cc)
    res_conts.append(snap_axes(nc))
p = pathops.Path(); pen = p.getPen()
for conts in res_conts:
    for c in conts:
        for op, ps in c:
            if op == "m": pen.moveTo(tuple(ps[0]))
            elif op == "l": pen.lineTo(tuple(ps[0]))
            else: pen.curveTo(*[tuple(q) for q in ps])
        pen.closePath()
p = pathops.simplify(p, fix_winding=True)
sp = SVGPathPen(None, ntos=lambda v: f"{v:.2f}"); p.draw(sp)
open(out, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="427" viewBox="0 0 1000 427"><path d="{sp.getCommands()}"/></svg>\n')
print(out)
