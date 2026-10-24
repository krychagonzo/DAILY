# Wektoryzacja ikon PPL z czyszczeniem geometrii (logo: gładkie krzywe, proste odcinki, idealne koło)
#  1. maska kształtu; pierścień przy krawędzi koła przedłużony radialnie
#  2. kontury subpikselowe (skimage) na 4x powiększonej, lekko rozmytej masce
#  3. wykrycie narożników; między narożnikami: odcinek (jeśli prosto) albo wygładzone
#     krzywe Béziera dopasowane algorytmem Schneidera (mało punktów = gładko)
#  4. kąty odcinków dociągnięte do 0°/90° i do wspólnego kąta kursywy; wierzchołki = przecięcia
#  5. wynik ∩ idealne koło (pathops) - krawędź koła jest matematycznie okrągła
import sys, math, numpy as np, cv2
from skimage.measure import find_contours
import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

src, mode, color, out, title = sys.argv[1:6]
SMOOTH = float(sys.argv[6]) if len(sys.argv) > 6 else 2.5     # siła wygładzania (px oryginału)
FIT_ERR = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6    # tolerancja dopasowania krzywych (px)

def cross2(a, b): return a[0]*b[1] - a[1]*b[0]

# ---------- 1. maska
TEXT_ONLY = mode == "tekst"   # sam napis (niebieski), bez koła
if mode in ("niebieski", "tekst"):
    a = cv2.imread(src).astype(np.float32)
    ink = np.clip((a[:, :, 0] - a[:, :, 2]) / 133 * 255, 0, 255)
else:
    ink = cv2.imread(src, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32)
ink = ink.astype(np.uint8)
PAD = 12
ink = cv2.copyMakeBorder(ink, PAD, PAD, PAD, PAD, cv2.BORDER_CONSTANT, value=0)
H, W = ink.shape

# ---------- koło: dopasowanie do zewnętrznych konturów dużych kształtów
if TEXT_ONLY:
    cx, cy, R = -1e5, -1e5, 1.0
else:
    cs, _ = cv2.findContours((ink > 128).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    amax = max(cv2.contourArea(c) for c in cs)
    P = np.concatenate([c[:, 0, :] for c in cs if cv2.contourArea(c) > 0.2 * amax]).astype(np.float64)
    hull = cv2.convexHull(P.astype(np.float32))[:, 0, :]
    cx, cy = hull.mean(0); R = np.median(np.hypot(P[:, 0]-cx, P[:, 1]-cy)); thr = R * 0.2
    for it in range(30):
        d = np.abs(np.hypot(P[:, 0]-cx, P[:, 1]-cy) - R); keep = d < thr
        q = P[keep]; A_ = np.c_[2*q[:, 0], 2*q[:, 1], np.ones(len(q))]; b_ = (q**2).sum(1)
        cx, cy, c = np.linalg.lstsq(A_, b_, rcond=None)[0]; R = math.sqrt(c + cx*cx + cy*cy)
        thr = max(1.0, thr * 0.7)
    R += 0.5
if not TEXT_ONLY: print(f"koło: środek ({cx-PAD:.2f},{cy-PAD:.2f}) r={R:.2f}")

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.hypot(xx - cx, yy - cy); Rin = R - 1.5
mx = np.where(rr > Rin, cx + (xx - cx) / np.maximum(rr, 1e-3) * Rin, xx).astype(np.float32)
my = np.where(rr > Rin, cy + (yy - cy) / np.maximum(rr, 1e-3) * Rin, yy).astype(np.float32)
ring = (rr > Rin) & (rr < R + 4)
ink = np.where(ring, cv2.remap(ink, mx, my, cv2.INTER_LINEAR), ink).astype(np.uint8)

# ---------- 2. kontury subpikselowe
SC = 4
big = cv2.resize(ink, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC).astype(np.float32)
big = cv2.GaussianBlur(big, (0, 0), 1.2 * SC / 4)
big = np.pad(big, 2)
raw = [c[:, ::-1] / SC - 2 / SC for c in find_contours(big, 128) if len(c) > 40]   # (x,y) w px oryginału

def resample(c, step=0.5):
    c = c[:-1] if np.allclose(c[0], c[-1]) else c
    seg = np.linalg.norm(np.diff(np.vstack([c, c[:1]]), axis=0), axis=1)
    s = np.r_[0, np.cumsum(seg)]; L = s[-1]; n = max(int(L / step), 12)
    t = np.linspace(0, L, n, endpoint=False)
    cc = np.vstack([c, c[:1]])
    return np.c_[np.interp(t, s, cc[:, 0]), np.interp(t, s, cc[:, 1])], L

# ---------- 3. narożniki + dopasowanie
def turning(pts, k):
    a = np.roll(pts, k, 0); b = np.roll(pts, -k, 0)
    v1 = pts - a; v2 = b - pts
    ang = np.arctan2(v1[:, 0]*v2[:, 1] - v1[:, 1]*v2[:, 0], (v1*v2).sum(1))
    return np.degrees(np.abs(ang))

def find_corners(pts):
    n = len(pts); k = 6  # 3 px
    t = turning(pts, k)
    cand = [i for i in range(n) if t[i] > CORNER_DEG and t[i] == max(t[(i + j) % n] for j in range(-k, k + 1))]
    # dokładniejsze położenie: najostrzejszy punkt w małym oknie
    t2 = turning(pts, 2)
    out = []
    for i in cand:
        j = max(range(i - 3, i + 4), key=lambda q: t2[q % n]) % n
        if not out or (j - out[-1]) % n > 4: out.append(j)
    return sorted(set(out))

def smooth_open(p, sig):
    if len(p) < 5 or sig <= 0: return p
    sig = min(sig, (len(p) - 2) / 3.0); r = min(int(3 * sig) + 1, len(p) - 2); w = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); w /= w.sum()
    pp = np.vstack([np.repeat(p[:1], r, 0), p, np.repeat(p[-1:], r, 0)])
    # odbicie punktowe na końcach, żeby końce (narożniki) zostały na miejscu
    pp[:r] = 2 * p[0] - p[r:0:-1]; pp[-r:] = 2 * p[-1] - p[-2:-r-2:-1]
    out = np.c_[np.convolve(pp[:, 0], w, "valid"), np.convolve(pp[:, 1], w, "valid")]
    out[0], out[-1] = p[0], p[-1]
    return out

def smooth_closed(p, sig):
    r = int(3 * sig) + 1; w = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); w /= w.sum()
    pp = np.vstack([p[-r:], p, p[:r]])
    return np.c_[np.convolve(pp[:, 0], w, "valid"), np.convolve(pp[:, 1], w, "valid")]

# --- Schneider: dopasowanie krzywych Béziera
def bez(ctrl, t):
    t = np.asarray(t)[:, None]; p0, p1, p2, p3 = ctrl
    return (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
def bez_d(ctrl, t):
    t = np.asarray(t)[:, None]; p0, p1, p2, p3 = ctrl
    return 3*(1-t)**2*(p1-p0) + 6*(1-t)*t*(p2-p1) + 3*t**2*(p3-p2)
def bez_dd(ctrl, t):
    t = np.asarray(t)[:, None]; p0, p1, p2, p3 = ctrl
    return 6*(1-t)*(p2-2*p1+p0) + 6*t*(p3-2*p2+p1)
def chord_u(p):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]; return d / d[-1]
def gen_bez(p, u, t1, t2):
    p0, p3 = p[0], p[-1]
    A1 = t1[None, :] * (3*(1-u)**2*u)[:, None]; A2 = t2[None, :] * (3*(1-u)*u**2)[:, None]
    C = np.array([[(A1*A1).sum(), (A1*A2).sum()], [(A1*A2).sum(), (A2*A2).sum()]])
    tmp = p - bez(np.array([p0, p0, p3, p3]), u)
    X = np.array([(A1*tmp).sum(), (A2*tmp).sum()])
    det = C[0, 0]*C[1, 1] - C[0, 1]*C[1, 0]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        a1 = (X[0]*C[1, 1] - X[1]*C[0, 1]) / det; a2 = (C[0, 0]*X[1] - C[1, 0]*X[0]) / det
    else: a1 = a2 = seg / 3
    if a1 < 1e-6 * seg or a2 < 1e-6 * seg or a1 > seg * 2 or a2 > seg * 2: a1 = a2 = seg / 3
    return np.array([p0, p0 + t1*a1, p3 + t2*a2, p3])
def reparam(ctrl, p, u):
    d = bez(ctrl, u) - p; d1 = bez_d(ctrl, u); d2 = bez_dd(ctrl, u)
    num = (d*d1).sum(1); den = (d1*d1).sum(1) + (d*d2).sum(1)
    return np.clip(u - np.where(np.abs(den) > 1e-12, num / den, 0), 0, 1)
def max_err(ctrl, p, u):
    e = np.linalg.norm(bez(ctrl, u) - p, axis=1); i = int(np.argmax(e)); return e[i], i
def unit(v): n = np.linalg.norm(v); return v / n if n > 1e-12 else v
def fit_cubic(p, t1, t2, err):
    if len(p) == 2:
        dist = np.linalg.norm(p[1]-p[0]) / 3; return [np.array([p[0], p[0]+t1*dist, p[1]+t2*dist, p[1]])]
    u = chord_u(p); ctrl = gen_bez(p, u, t1, t2); e, split = max_err(ctrl, p, u)
    if e < err: return [ctrl]
    if e < err * 4:
        for _ in range(20):
            u = reparam(ctrl, p, u); ctrl = gen_bez(p, u, t1, t2); e, split = max_err(ctrl, p, u)
            if e < err: return [ctrl]
    split = min(max(split, 1), len(p) - 2)
    tc = unit(p[split-1] - p[split+1])
    return fit_cubic(p[:split+1], t1, tc, err) + fit_cubic(p[split:], -tc, t2, err)
def end_tangent(p, start=True, k=6):
    k = min(k, len(p) - 1)
    return unit(p[k] - p[0]) if start else unit(p[-1-k] - p[-1])

def dist_line(p, a, b):
    d = b - a; L = np.linalg.norm(d); return abs(cross2(d, p - a)) / L if L > 1e-9 else np.linalg.norm(p - a)

SIG = SMOOTH / 0.5   # w próbkach (krok 0.5 px)
LINE_TOL, LINE_MIN, BOW_TOL = 0.8, 20.0, 0.35
CORNER_DEG = float(sys.argv[8]) if len(sys.argv) > 8 else 45.0   # próg kąta narożnika [°]

def tls(p):
    """prosta najlepszego dopasowania; zwraca też miarę 'nieprostoliniowości':
    max(odchyłka) oraz strzałkę wygięcia z dopasowania paraboli (wykrywa łagodne łuki)"""
    m = p.mean(0); _, _, vt = np.linalg.svd(p - m); d = vt[0]; nrm = np.array([-d[1], d[0]])
    r = (p - m) @ nrm; dev = np.abs(r).max()
    sx = (p - m) @ d; length = sx.max() - sx.min()
    if axis_like(d) and length > 30 and len(p) >= 8:   # krawędź pozioma/pionowa/kursywa: w logo prosta z założenia
        a = np.polyfit(sx, r, 2)[0]
        if abs(a) * (length / 2) ** 2 < (1.2 if length > 60 else 0.6): return m, d, dev * LINE_TOL / 1.6 if dev <= 1.6 else 1e9
    if len(p) >= 8:
        a = np.polyfit(sx, r, 2)[0]; half = length / 2
        if abs(a) * half * half > max(BOW_TOL, 0.004 * length): return m, d, 1e9
    # tolerancja rośnie z długością (długie krawędzie w JPG bywają minimalnie wygięte)
    return m, d, dev * LINE_TOL / max(LINE_TOL, 0.006 * length)

def axis_like(d):
    a = math.degrees(math.atan2(d[1], d[0])) % 180
    return any(min(abs(a - c) % 180, 180 - abs(a - c) % 180) < 3.0 for c in AXES)

def longest_run(p):
    """najdłuższy ciągły fragment p, który mieści się w pasie LINE_TOL wokół prostej"""
    n = len(p); best = (0, 0); i = 0
    minlen = int(LINE_MIN / 0.5)
    while i < n - minlen:
        j = i + minlen
        if tls(p[i:j])[2] > LINE_TOL: i += 2; continue
        step = 8
        while j < n:
            j2 = min(n, j + step)
            if tls(p[i:j2])[2] <= LINE_TOL: j = j2
            elif step > 1: step //= 2
            else: break
        if j - i > best[1] - best[0]: best = (i, j)
        i = j
    return best

def line_through(p):
    m, d, _ = tls(p)
    a = m + d * ((p[0] - m) @ d); b = m + d * ((p[-1] - m) @ d)
    return a, b

def find_runs(seg, off=0):
    """wszystkie rozłączne proste fragmenty (najdłuższe najpierw)"""
    if len(seg) * 0.5 < LINE_MIN: return []
    i, j = longest_run(seg)
    if (j - i) * 0.5 < LINE_MIN: return []
    return find_runs(seg[:i], off) + [(off + i, off + j)] + find_runs(seg[j:], off + j)

def fit_curve(seg, t_in, t_out):
    sp = smooth_open(seg, SIG)
    ti = t_in if t_in is not None else end_tangent(sp, True)
    to = t_out if t_out is not None else end_tangent(sp, False)
    return [["C", *b] for b in fit_cubic(sp, ti, to, FIT_ERR)]

def fit_span(seg):
    """seg: punkty od narożnika do narożnika -> odcinki proste + gładkie krzywe"""
    if len(seg) < 3 or tls(seg)[2] <= LINE_TOL: return [["L", seg[0], seg[-1]]]
    runs = find_runs(seg)
    # krótkie poziome/pionowe/kursywa krawędzie przy narożniku (min. 6 px)
    def edge_run(fwd):
        best = None
        for k in range(12, min(len(seg) - 2, 60)):
            part = seg[:k] if fwd else seg[-k:]
            m_, d_, _ = tls(part); nrm = np.array([-d_[1], d_[0]])
            if not axis_like(d_) or np.abs((part - m_) @ nrm).max() > 0.45: break
            best = k
        return best
    if not runs or runs[0][0] > 1:
        k = edge_run(True)
        if k and (not runs or k < runs[0][0]): runs.insert(0, (0, k))
    if not runs or runs[-1][1] < len(seg) - 2:
        k = edge_run(False)
        if k and (not runs or len(seg) - k > runs[-1][1]): runs.append((len(seg) - k, len(seg)))
    # dwa sąsiednie odcinki prawie w tym samym kierunku = fasetowanie łuku -> odrzuć
    def ang(r): a_, b_ = line_through(seg[r[0]:r[1]]); return math.degrees(math.atan2(*(b_ - a_)[::-1]))
    changed = True
    while changed:
        changed = False
        for k in range(len(runs) - 1):
            d = abs((ang(runs[k]) - ang(runs[k+1]) + 180) % 360 - 180)
            if d < 15 and tls(seg[runs[k][0]:runs[k+1][1]])[2] <= LINE_TOL:
                runs[k] = (runs[k][0], runs[k+1][1]); del runs[k+1]; changed = True; break   # współliniowe -> jeden odcinek
            if d < 15:
                # zostaw dłuższy tylko jeśli jest wyraźnie dłuższy; inaczej usuń oba
                l1 = runs[k][1] - runs[k][0]; l2 = runs[k+1][1] - runs[k+1][0]
                if l1 > 2.5 * l2: del runs[k+1]
                elif l2 > 2.5 * l1: del runs[k]
                else: del runs[k:k+2]
                changed = True; break
    # krótki odcinek bez narożnika na żadnym końcu leży na łuku -> to nie jest prosta
    runs = [(i, j) for (i, j) in runs if (j - i) * 0.5 >= 40 or i <= 1 or j >= len(seg) - 2]
    out = []; pos = 0; t_prev = None; start_pt = seg[0]
    for (i, j) in runs:
        a, b = line_through(seg[i:j]); d = unit(b - a)
        if i <= 1: a = seg[0]
        if i > 1: out += fit_curve(np.vstack([start_pt[None], seg[pos+1:i], a[None]]), t_prev, -d)
        endb = seg[-1] if j >= len(seg) - 1 else b
        out.append(["L", a, endb]); pos = j; t_prev = d; start_pt = endb
    if pos < len(seg) - 1:
        out += fit_curve(np.vstack([start_pt[None], seg[pos+1:]]), t_prev, None)
    return out

AXES = [0.0, 90.0]
def fit_all():
    contours = []
    for c in raw:
        pts, L = resample(c)
        corners = find_corners(pts)
        prims = []
        if not corners:
            sp = smooth_closed(pts, SIG)
            # zamknięta krzywa: rozetnij w punkcie 0, styczne ciągłe
            tc = unit(sp[1] - sp[-1]); closed = np.vstack([sp, sp[:1]])
            for b in fit_cubic(closed, tc, -tc, FIT_ERR): prims.append(["C", *b])
        else:
            n = len(pts)
            for ci in range(len(corners)):
                i0, i1 = corners[ci], corners[(ci + 1) % len(corners)]
                idx = [(i0 + j) % n for j in range(((i1 - i0) % n or n) + 1)]
                prims += fit_span(pts[idx])
        contours.append(prims)
    
    
    return contours

def italic_angle(cs):
    ls = [(math.degrees(math.atan2(s_[2][1]-s_[1][1], s_[2][0]-s_[1][0])) % 180, np.linalg.norm(s_[2]-s_[1]))
          for p in cs for s_ in p if s_[0] == "L"]
    sl = [(a_, L_) for a_, L_ in ls if L_ > 15 and (60 < a_ < 87 or 93 < a_ < 120)]
    if len(sl) < 3: return None
    angs = np.array([a_ for a_, _ in sl]); ws = np.array([l_ for _, l_ in sl]); sel = np.abs(angs - np.median(angs)) < 3
    return float(np.average(angs[sel], weights=ws[sel])) if sel.sum() >= 3 else None
contours = fit_all()
it = None if TEXT_ONLY else italic_angle(contours)
if it is not None:
    AXES.append(it); contours = fit_all()
# ---------- 4. kąty odcinków: 0/90 + kursywa
lines = [(s, math.degrees(math.atan2(s[2][1]-s[1][1], s[2][0]-s[1][0])) % 180, np.linalg.norm(s[2]-s[1]))
         for p in contours for s in p if s[0] == "L"]
cands = [0.0, 90.0]
sl = [(ang, L) for _, ang, L in lines if L > 15 and (60 < ang < 87 or 93 < ang < 120)]
if len(sl) >= 3 and not TEXT_ONLY:
    angs = np.array([a for a, _ in sl]); ws = np.array([l for _, l in sl]); sel = np.abs(angs - np.median(angs)) < 3
    if sel.sum() >= 3: cands.append(float(np.average(angs[sel], weights=ws[sel]))); print(f"kąt kursywy: {cands[-1]:.2f}°")
def adiff(a, b): d = abs(a - b) % 180; return min(d, 180 - d)
# obrót wokół końca, który styka się z krzywą (żeby styk krzywa-prosta pozostał gładki);
# gdy oba końce są narożnikami albo oba stykają się z krzywymi - wokół środka
for prims in contours:
    n_ = len(prims)
    for i, s in enumerate(prims):
        if s[0] != "L": continue
        L = np.linalg.norm(s[2] - s[1]); ang = math.degrees(math.atan2(s[2][1]-s[1][1], s[2][0]-s[1][0])) % 180
        best = min(cands, key=lambda c: adiff(ang, c)); dth = adiff(ang, best)
        prev_c = prims[i-1][0] == "C"; next_c = prims[(i+1) % n_][0] == "C"
        if prev_c != next_c: arm = L
        else: arm = L / 2
        if dth < 3.0 and arm * math.sin(math.radians(dth)) < 2.0:
            th = math.radians(best); dv = np.array([math.cos(th), math.sin(th)])
            if np.dot(dv, s[2] - s[1]) < 0: dv = -dv
            if prev_c and not next_c: s[2] = s[1] + dv * L
            elif next_c and not prev_c: s[1] = s[2] - dv * L
            else:
                m = (s[1] + s[2]) / 2; s[1], s[2] = m - dv*L/2, m + dv*L/2

def isect_ll(a0, a1, b0, b1):
    d1, d2 = a1 - a0, b1 - b0; den = cross2(d1, d2)
    if abs(den) / (np.linalg.norm(d1)*np.linalg.norm(d2) + 1e-12) < math.sin(math.radians(4)): return None
    return a0 + cross2(b0 - a0, d2) / den * d1
def proj_l(p, a0, a1):
    d = unit(a1 - a0); return a0 + d * ((p - a0) @ d)
for prims in contours:
    n_ = len(prims)
    if n_ < 2: continue
    newv = []
    for i in range(n_):
        a, b = prims[i], prims[(i+1) % n_]; v = (a[-1] + b[1]) / 2
        if a[0] == "L" and b[0] == "L":
            q = isect_ll(a[1], a[2], b[1], b[2]); v = q if q is not None and np.linalg.norm(q - v) < 4 else v
        elif a[0] == "L": v = proj_l(v, a[1], a[2])
        elif b[0] == "L": v = proj_l(v, b[1], b[2])
        newv.append(v)
    for i in range(n_):
        a, b = prims[i], prims[(i+1) % n_]; v = newv[i]
        if a[0] == "C": a[3] = a[3] + (v - a[4]); a[4] = v
        else: a[2] = v
        if b[0] == "C": b[2] = b[2] + (v - b[1]); b[1] = v
        else: b[1] = v
        # krzywa przy odcinku: styczna dokładnie wzdłuż odcinka (gładkie przejście)
        if a[0] == "C" and b[0] == "L":
            t = unit(b[2] - b[1]); h = np.linalg.norm(a[3] - a[4])
            if np.dot(unit(a[4] - a[3]), t) > math.cos(math.radians(20)): a[3] = a[4] - t * h
        if a[0] == "L" and b[0] == "C":
            t = unit(a[2] - a[1]); h = np.linalg.norm(b[2] - b[1])
            if np.dot(unit(b[2] - b[1]), t) > math.cos(math.radians(20)): b[2] = b[1] + t * h

# ---------- 4b. krótkie krzywe-„schodki” przy odcinkach wchłonięte w odcinek
def absorb(prims):
    changed = True
    while changed and len(prims) > 3:
        changed = False
        n_ = len(prims)
        for i in range(n_):
            c, l = prims[i], prims[(i+1) % n_]
            for (c, l, c_first) in ((prims[i], prims[(i+1) % n_], True), (prims[(i+1) % n_], prims[i], False)):
                if not (c[0] == "C" and l[0] == "L"): continue
                ctrl = np.array(c[1:]); chord = np.linalg.norm(ctrl[3] - ctrl[0])
                if chord > 30: continue
                a0, a1 = l[1], l[2]; dv = unit(a1 - a0)
                q = bez(ctrl, np.linspace(0, 1, 15))
                dmax = max(dist_line(p_, a0, a1) for p_ in q)
                if dmax > 2.0: continue
                if prims[(i - 1) % n_ if c_first else (i + 2) % n_][0] != "C": continue   # tylko między krzywą a odcinkiem
                far = ctrl[0] if c_first else ctrl[3]          # koniec krzywej daleko od odcinka
                newp = a0 + dv * ((far - a0) @ dv)
                # sąsiad po drugiej stronie krzywej
                if c_first:
                    j = (i - 1) % n_; nb = prims[j]; l[1] = newp
                    if nb[0] == "C":
                        h = np.linalg.norm(nb[4] - nb[3]); nb[3] = newp - dv * max(h, 1e-3); nb[4] = newp
                    else: nb[2] = newp
                    del prims[i]
                else:
                    j = (i + 2) % n_; nb = prims[j]; l[2] = newp
                    if nb[0] == "C":
                        h = np.linalg.norm(nb[2] - nb[1]); nb[2] = newp + dv * max(h, 1e-3); nb[1] = newp
                    else: nb[1] = newp
                    del prims[(i + 1) % n_]
                changed = True; break
            if changed: break
    return prims
contours = [absorb(p) for p in contours]

# ---------- 5. ∩ idealne koło
shape = pathops.Path(); shape.fillType = pathops.FillType.EVEN_ODD
for prims in contours:
    shape.moveTo(*prims[0][1])
    for s_ in prims:
        if s_[0] == "L": shape.lineTo(*s_[2])
        else: shape.cubicTo(*s_[2], *s_[3], *s_[4])
    shape.close()
k = 0.5522847498 * R
circ = pathops.Path()
circ.moveTo(cx + R, cy)
circ.cubicTo(cx + R, cy + k, cx + k, cy + R, cx, cy + R)
circ.cubicTo(cx - k, cy + R, cx - R, cy + k, cx - R, cy)
circ.cubicTo(cx - R, cy - k, cx - k, cy - R, cx, cy - R)
circ.cubicTo(cx + k, cy - R, cx + R, cy - k, cx + R, cy)
circ.close()
res = pathops.op(shape, circ, pathops.PathOp.INTERSECTION, fix_winding=True)
rest = pathops.op(shape, circ, pathops.PathOp.DIFFERENCE, fix_winding=True)
rp = RecordingPen(); rest.draw(rp)
cont, cur = [], []
for op_, pts in rp.value:
    cur.append((op_, pts))
    if op_ in ("closePath", "endPath"): cont.append(cur); cur = []
final = pathops.Path(); fp = final.getPen(); res.draw(fp)
for c_ in cont:   # elementy poza kołem (tekst) - bez zmian
    pa = [p for _, ps in c_ for p in ps]
    if pa and min(math.hypot(p[0]-cx, p[1]-cy) for p in pa) > R + 3:
        for op_, pts in c_: getattr(fp, op_)(*pts)
sp = SVGPathPen(None, ntos=lambda v: f"{v:.2f}")
final.draw(TransformPen(sp, (1, 0, 0, 1, -PAD, -PAD)))
w, h = W - 2*PAD, H - 2*PAD
open(out, "w").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
 <title>{title}</title>
 <path fill="{color}" d="{sp.getCommands()}"/>
</svg>
''')
nL = sum(s[0] == "L" for p in contours for s in p); nC = sum(s[0] == "C" for p in contours for s in p)
print(out, w, h, f"kontury {len(contours)}, odcinki {nL}, krzywe {nC}")
