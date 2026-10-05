#!/usr/bin/env python3
"""
Deterministic "hand-engraving" composite of the A Certain Era / VINTAGE logo
onto the silver tray photo.  Needs: pip install numpy opencv-python-headless

Usage:
    python3 make_composite.py                 # default variant (see VARIANT)
    python3 make_composite.py third           # "A Certain Era" ~1/3 of inner oval
    python3 make_composite.py cartouche       # fits inside existing dotted cartouche
    python3 make_composite.py cartouche 7     # ... with another random seed

Outputs (in OUT_DIR, suffixed with variant name):
    engraving-layer-<v>.png     RGBA layer in image space (white lines, alpha = strength)
    engraving-lines-<v>.png     the clean line intensity map (grey, for inspection)
    composite-<v>.png           full-resolution composite
    composite-<v>-zoom.png      close-up crop (2x)
    mask-inpaint-<v>.png        white = area an AI inpaint may touch (for flux-pro-fill)
"""
import sys, os, math
import numpy as np
import cv2

# ----------------------------------------------------------------- parameters
HERE      = os.path.dirname(os.path.abspath(__file__))
BASE_IMG  = os.path.join(HERE, '..', '00-materialy', 'input', 'tacka.jpg')
LOGO_IMG  = os.path.join(HERE, '..', '00-materialy', 'input', 'logo-a-certain-era.png')
OUT_DIR   = HERE

VARIANT   = sys.argv[1] if len(sys.argv) > 1 else 'cartouche'
SEED      = int(sys.argv[2]) if len(sys.argv) > 2 else (4 if VARIANT == 'patina' else 3)

# Geometry (pixels of the 2076x2576 original). Estimated by eye:
#   inner flat oval: left end ~(330,1466), right end ~(1784,1286) -> ~1465 px long, tilted ~-7 deg
#   dotted central cartouche: outer ~913..1300 x 1190..1403, centre ~(1106,1296)
CENTER        = (1106, 1300)    # where the centre of the text block lands
if VARIANT == 'patina':
    CENTER    = (1062, 1302)    # centre of the inner oval (same spot as sesje/05 A-nb2-seed44-FINAL)
APPARENT_TILT = -7.0            # deg, image-space slope of the tray's long axis (neg = right side up)
FORESHORTEN   = 0.84            # vertical squash from camera tilt (1 = straight top-down)
KEYSTONE      = 0.985           # far(top) edge width / near(bottom) edge width over the text height
TEXT_WIDTH    = {'third': 420, 'cartouche': 290, 'patina': 590}[VARIANT]   # px width of "A Certain Era" before squash
VINTAGE_SCALE = 1.12            # VINTAGE line slightly enlarged vs logo (engravers keep small caps legible)
LINE_GAP_ADD  = 0.30            # extra gap between the two lines (fraction of cap height)

# Engraved line look (final image pixels)
SS            = 4               # supersampling factor for drawing
LINE_W        = 1.7             # core width of a burin cut
LINE_GAIN     = 0.30            # how far toward white the cut lifts the metal (existing lines ~0.15-0.25)
DARK_EDGE     = 7.0             # grey levels of faint shadow on one side of the cut (0 = off)
DARK_DIR      = (0.0, 1.0)      # unit vector (x,y) image space: shadow side (light from top)
WOBBLE_AMP    = 0.40            # px, slow hand wobble
WOBBLE_SCALE  = 16.0            # px, wavelength-ish of wobble
TREMOR_AMP    = 0.07            # px, fine tremor
BASELINE_AMP  = 1.6             # px, slow baseline drift across the line of text
LETTER_JIT    = (0.7, 0.6, 1.3) # per-letter sigma: dx px, dy px, rotation deg
OPACITY_RANGE = (0.50, 1.0)     # along-stroke strength variation (wear / pressure)
GAP_FRACTION  = 0.04            # fraction of stroke length that skips/worn away
N_RECUTS      = 4               # number of doubled (re-cut) segments
N_SLIPS       = 3               # tiny burin overshoot tails at stroke ends
SPARKLE       = 0.28            # multiplicative frosted glint noise amplitude
FINAL_BLUR    = 0.40            # gaussian sigma to match photo softness
JPEG_ROUNDTRIP= 92              # re-encode composite through JPEG at this quality (0 = off)

# Cartouche clearing (fade existing floral lines under/around the text)
# For 'third' the text is larger than the existing dotted cartouche, so we engrave a NEW
# double-line oval frame (same burin look) around the text and remove the old floral lines
# inside it -- exactly what an engraver adding a presentation inscription would do.
CLEAR         = {'third': True, 'cartouche': False, 'patina': False}[VARIANT]
FRAME_AXES    = (272, 142)      # px semi-axes of the new oval frame (tray plane, pre-squash);
                                # chosen to enclose the text AND the old dotted cartouche completely
BORDER_GAP    = 5.0             # px between the two frame lines (0 = single line)
CLEAR_FEATHER = 1.5             # px soft edge of the cleared zone (just inside the frame)
CLEAR_AMOUNT  = 1.0             # 1 = old lines fully removed inside the frame

# ---- 'patina' mode (dark tarnished channel, style of 00-materialy/input/referencja-styl-graweru*.jpg)
# Usage: python3 make_composite.py patina [seed] [depth] [out-name]
PAT_OUT_DIR   = os.path.join(HERE, '..', 'sesje', '06-styl-z-referencji-ciemna-patyna')
PAT_DEPTH     = float(sys.argv[3]) if len(sys.argv) > 3 else 0.46   # mean multiply-darkening inside the channel
PAT_NAME      = sys.argv[4] if len(sys.argv) > 4 else 'B-lokalna-patyna-FINAL'
PAT_THRESH    = 0.58            # glyph threshold (>0.5 = slightly thinner than the logo strokes)
PAT_FLOOR     = 0.55            # tarnish on the channel floor relative to the walls
PAT_RAGGED    = 0.16            # edge raggedness (threshold perturbation of the glyph mask)
PAT_WOBBLE    = 0.35            # px, slow hand wobble of the channel
PAT_CHIPS     = 0.035           # fraction of stroke area chipped/worn through to bare metal
PAT_CHIP_DEPTH= 0.7             # how much of the channel a chip removes (1 = bare metal)
PAT_UNDERCUT  = (0.55, 1.0)     # depth multiplier range from slow noise (shallow/under-cut parts)
PAT_MOTTLE    = 0.32            # amplitude of low-frequency tarnish mottling
PAT_WORN      = 0.25            # fraction of channel with lighter polished-out spots
PAT_WALL      = 0.22            # extra darkening along the shadowed wall
PAT_WALL_SHIFT= 1.2             # px, mask shift that creates the wall band
PAT_HIGHLIGHT = 0.16            # faint lit lip on the opposite edge (fraction toward white)
PAT_LIGHT_DIR = (0.0, 1.0)      # image-space direction from the dark wall to the lit lip
PAT_TINT      = (1.0, 0.97, 0.93)  # BGR relative darkening: tarnish slightly warm graphite
PAT_FLORAL    = 0.8             # re-added share of the floral engraving highlights under the letters
PAT_SCR_BRIGHT= 6.0             # grey levels a scratch adds on bare metal
PAT_SCRATCHES = 34              # fine surface scratches across the text zone
PAT_SPECKS    = 35              # small tarnish specks around/in the letters
PAT_BLUR      = 0.65            # gaussian sigma (phone softness)
PAT_GRAIN     = 1.1             # grey-level std of grain re-added in darkened areas
PAT_FEATHER   = 6.0             # px feather of the edited zone (outside it pixels are bit-identical)

rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------- helpers
def smooth_noise(shape, scale, rng):
    """Zero-mean, unit-std smooth noise with feature size ~scale px."""
    h, w = shape
    small = rng.standard_normal((max(2, int(h / scale) + 3), max(2, int(w / scale) + 3))).astype(np.float32)
    up = cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
    up = cv2.GaussianBlur(up, (0, 0), scale * 0.35 + 0.5)
    up -= up.mean(); up /= (up.std() + 1e-6)
    return up

def zhang_suen(img):
    """Skeletonise a binary uint8 (0/1) image. Vectorised Zhang-Suen."""
    img = img.copy().astype(np.uint8)
    img = np.pad(img, 1)
    while True:
        changed = False
        for step in range(2):
            P = img
            p2 = P[:-2, 1:-1]; p3 = P[:-2, 2:]; p4 = P[1:-1, 2:]; p5 = P[2:, 2:]
            p6 = P[2:, 1:-1]; p7 = P[2:, :-2]; p8 = P[1:-1, :-2]; p9 = P[:-2, :-2]
            c = P[1:-1, 1:-1]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(n.astype(np.int32) for n in nb)
            seq = nb + [p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.int32) for i in range(8))
            if step == 0:
                m = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                m = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            if m.any():
                changed = True
                img[1:-1, 1:-1][m] = 0
        if not changed:
            break
    return img[1:-1, 1:-1]

def line_from_skeleton(skel, width_px):
    """Soft anti-aliased line of given width (in the same pixel units) along skeleton."""
    inv = (1 - skel).astype(np.uint8)
    d = cv2.distanceTransform(inv, cv2.DIST_L2, 5)
    r = width_px / 2.0
    return np.clip(1.0 - (d - r + 1.0) / 2.0, 0, 1).astype(np.float32) ** 1.3

def tray_homography(w, h):
    """Map rectangle (0,0)-(w,h) of the flat text plane into the photo."""
    th = math.radians(math.degrees(math.atan(math.tan(math.radians(APPARENT_TILT)) / FORESHORTEN)))
    c, s = math.cos(th), math.sin(th)
    pts = []
    for (x, y) in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y = x - w / 2, y - h / 2
        # keystone in the tray plane: rows nearer the top (far) are narrower
        k = 1 + (1 - KEYSTONE) * (Y / h)
        X *= k
        rx, ry = c * X - s * Y, s * X + c * Y
        pts.append((CENTER[0] + rx, CENTER[1] + ry * FORESHORTEN))
    src = np.float32([(0, 0), (w, 0), (w, h), (0, h)])
    return cv2.getPerspectiveTransform(src, np.float32(pts))

def render_patina(work):
    """Full-width engraved channel with dark tarnish, warped onto the tray. Writes outputs, no return."""
    r = rng
    Hs, Ws = work.shape
    gx, gy = np.meshgrid(np.arange(Ws, dtype=np.float32), np.arange(Hs, dtype=np.float32))
    # ragged, soft-edged channel (flat text plane, SS supersampled)
    soft = cv2.GaussianBlur(work, (0, 0), 0.5 * SS)
    en = 0.6 * smooth_noise(work.shape, 1.3 * SS, r) + 0.4 * smooth_noise(work.shape, 4.0 * SS, r)
    ch = np.clip((soft - PAT_THRESH + PAT_RAGGED * en) / 0.10 + 0.5, 0, 1)
    dx = smooth_noise(work.shape, 16 * SS, r) * PAT_WOBBLE * SS
    dy = smooth_noise(work.shape, 16 * SS, r) * PAT_WOBBLE * SS
    ch = cv2.remap(ch, gx + dx, gy + dy, cv2.INTER_LINEAR)
    # wear: small chips worn through to bare metal + slow under-cut (shallow) regions
    chip = smooth_noise(work.shape, 2.2 * SS, r)
    thr = np.quantile(chip[ch > 0.5], PAT_CHIPS)
    ch *= 1 - PAT_CHIP_DEPTH * (1 - np.clip((chip - thr) / 0.25, 0, 1))   # chips worn shallow, not cut through
    und = smooth_noise(work.shape, 26 * SS, r)
    depth = PAT_UNDERCUT[0] + (PAT_UNDERCUT[1] - PAT_UNDERCUT[0]) * (0.5 + 0.5 * np.tanh(1.3 * und + 0.6))
    # cross-section profile: tarnish collects along both walls, the floor is lighter / polished
    dist = cv2.distanceTransform((ch > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    hw = np.quantile(dist[dist > 0], 0.97) + 1e-3
    pr = np.clip(dist / hw, 0, 1)
    wallprof = 1 - np.clip((pr - 0.15) / 0.55, 0, 1) ** 1.2          # 1 at the walls, 0 on the floor
    hf, wf = int(Hs / SS), int(Ws / SS)
    wp_f = cv2.resize(wallprof * (ch > 0.5), (wf, hf), interpolation=cv2.INTER_AREA)
    ch_f = cv2.resize(ch, (wf, hf), interpolation=cv2.INTER_AREA)
    dp_f = cv2.resize(depth, (wf, hf), interpolation=cv2.INTER_AREA)

    base = cv2.imread(BASE_IMG)
    basef = base.astype(np.float32)
    Hb, Wb = base.shape[:2]
    Hm = tray_homography(wf, hf)
    A = cv2.warpPerspective(ch_f, Hm, (Wb, Hb), flags=cv2.INTER_LINEAR)
    WP = cv2.warpPerspective(wp_f, Hm, (Wb, Hb), flags=cv2.INTER_LINEAR)
    D = cv2.warpPerspective(dp_f, Hm, (Wb, Hb), flags=cv2.INTER_LINEAR, borderValue=1.0)
    ys, xs = np.where(A > 0.05)
    x0, x1, y0, y1 = xs.min() - 60, xs.max() + 60, ys.min() - 60, ys.max() + 60
    sl = (slice(y0, y1), slice(x0, x1))
    a, d, wp, bf = A[sl], D[sl], WP[sl], basef[sl]
    h, w = a.shape

    # tarnish texture: low-frequency mottling + speckle, lighter polished-out spots
    low = smooth_noise((h, w), 7.0, r); mid = smooth_noise((h, w), 2.2, r)
    speck = r.standard_normal((h, w)).astype(np.float32)
    worn_n = smooth_noise((h, w), 5.0, r)
    worn = np.clip((worn_n - np.quantile(worn_n, 1 - PAT_WORN)) / 0.5, 0, 1)
    prof = PAT_FLOOR + (1 - PAT_FLOOR) * np.clip(wp / np.maximum(a, 0.05), 0, 1)
    tarn = PAT_DEPTH * d * prof * (1 + PAT_MOTTLE * low + 0.14 * mid + 0.10 * speck) * (1 - 0.6 * worn)
    # groove wall: band along the shadow-side edge (mask shifted ~1 px toward the lit wall)
    ldx, ldy = PAT_LIGHT_DIR
    sh = cv2.warpAffine(a, np.float32([[1, 0, ldx * PAT_WALL_SHIFT], [0, 1, ldy * PAT_WALL_SHIFT]]), (w, h))
    wall = np.clip(a - sh, 0, 1)
    lip = np.clip(sh - a, 0, 1) * np.clip(1 - 0.6 * worn, 0, 1)
    dark = np.clip(a * tarn + wall * PAT_WALL * d, 0, 0.85)

    # tarnish specks (in and around letters, denser near strokes)
    near = cv2.GaussianBlur(cv2.dilate((a > 0.2).astype(np.uint8), np.ones((25, 25), np.uint8)).astype(np.float32), (0, 0), 6)
    sp = np.zeros((h, w), np.float32)
    cand = np.argwhere(near > 0.3)
    for k in r.choice(len(cand), PAT_SPECKS, replace=False):
        py, px = cand[k]
        rad = r.uniform(0.6, 1.8)
        cv2.ellipse(sp, (int(px * 4), int(py * 4)), (int(rad * 4 * r.uniform(0.7, 1.4)), int(rad * 4)), r.uniform(0, 180), 0, 360,
                    float(r.uniform(0.08, 0.30)), -1, cv2.LINE_AA, 2)
    sp = cv2.GaussianBlur(sp, (0, 0), 0.5)
    dark = np.clip(dark + sp * (1 - a), 0, 0.85)

    # fine surface scratches running across the letters: lift tarnish where they cross
    sc = np.zeros((h * 4, w * 4), np.float32)
    cy0, cx0 = (ys.mean() - y0), (xs.mean() - x0)
    for _ in range(PAT_SCRATCHES):
        ang = math.radians(r.normal(-12, 40))
        L = r.uniform(40, 220)
        px, py = cx0 + r.uniform(-0.55, 0.55) * (xs.max() - xs.min()), cy0 + r.uniform(-0.6, 0.6) * (ys.max() - ys.min())
        p0 = (int((px - L / 2 * math.cos(ang)) * 16), int((py - L / 2 * math.sin(ang)) * 16))
        p1 = (int((px + L / 2 * math.cos(ang)) * 16), int((py + L / 2 * math.sin(ang)) * 16))
        cv2.line(sc, p0, p1, float(r.uniform(0.35, 1.0)), 1, cv2.LINE_AA, 2)
    sc = cv2.resize(sc, (w, h), interpolation=cv2.INTER_AREA) * 4.0
    sc = np.clip(sc * (0.5 + 0.5 * np.clip(smooth_noise((h, w), 12, r) + 0.8, 0, 1.5)), 0, 1)
    dark = dark * (1 - 0.8 * sc)

    dark = cv2.GaussianBlur(dark, (0, 0), PAT_BLUR)
    lip = cv2.GaussianBlur(lip, (0, 0), PAT_BLUR)
    tint = np.float32(PAT_TINT)[None, None, :]
    out = bf * (1 - dark[..., None] * tint)
    # keep the old floral cuts faintly readable under the tarnish (re-add part of their high-pass)
    hp = bf - cv2.GaussianBlur(bf, (0, 0), 3.0)
    out = out + PAT_FLORAL * np.clip(dark * 2, 0, 1)[..., None] * np.clip(hp, 0, None)
    out = out + PAT_HIGHLIGHT * lip[..., None] * (248 - out)
    out = out + PAT_SCR_BRIGHT * sc[..., None] * (1 - a[..., None])           # scratches faintly bright on bare metal
    grain = cv2.GaussianBlur(r.standard_normal((h, w)).astype(np.float32), (0, 0), 0.6)
    grain /= grain.std()
    out = out + grain[..., None] * PAT_GRAIN * np.clip(dark * 2.5, 0, 1)[..., None]

    # feathered edit zone: text + specks + scratches; everything else bit-identical
    zone = np.zeros((h, w), np.float32)
    ex, ey = int(cx0), int(cy0)
    cv2.ellipse(zone, (ex, ey), (int((xs.max() - xs.min()) / 2 + 40), int((ys.max() - ys.min()) / 2 + 34)), APPARENT_TILT, 0, 360, 1, -1)
    zone = cv2.GaussianBlur(zone, (0, 0), PAT_FEATHER)
    res = bf + (out - bf) * zone[..., None]
    res = np.clip(np.round(res), 0, 255).astype(np.uint8)
    final = base.copy()
    final[sl] = np.where(zone[..., None] > 1e-3, res, base[sl])

    os.makedirs(PAT_OUT_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(PAT_OUT_DIR, PAT_NAME + '.png'), final)
    zx0, zy0 = int(xs.mean() - 400), int(ys.mean() - 190)
    crop = final[zy0:zy0 + 380, zx0:zx0 + 800]
    zname = PAT_NAME.replace('-FINAL', '') + '-zblizenie.png'
    cv2.imwrite(os.path.join(PAT_OUT_DIR, zname), cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
    diff = np.any(final != base, axis=2)
    dy_, dx_ = np.where(diff)
    print('patina done', PAT_NAME, 'text bbox', xs.min(), xs.max(), ys.min(), ys.max(),
          '| changed px', int(diff.sum()), 'bbox', dx_.min(), dx_.max(), dy_.min(), dy_.max())

# ----------------------------------------------------------------- 1. logo -> per-letter jittered mask
logo = cv2.imread(LOGO_IMG, cv2.IMREAD_GRAYSCALE)
ink = (logo < 128).astype(np.uint8)
ys, xs = np.where(ink)
ink = ink[ys.min() - 20: ys.max() + 21, xs.min() - 20: xs.max() + 21]
n, lab, st, cen = cv2.connectedComponentsWithStats(ink, connectivity=8)

# find the split between line 1 (A Certain Era) and line 2 (VINTAGE)
rows = ink.sum(1); filled = np.where(rows > 0)[0]
gaps = np.where(np.diff(filled) > 5)[0]
split_y = (filled[gaps[0]] + filled[gaps[0] + 1]) // 2
x1s = [st[i, 0] for i in range(1, n) if st[i, 1] < split_y]
x2s = [st[i, 0] + st[i, 2] for i in range(1, n) if st[i, 1] < split_y]
line1_w = max(x2s) - min(x1s)

s_final = TEXT_WIDTH / line1_w           # logo px -> final (pre-squash) px
S = s_final * SS                         # logo px -> work px
H0, W0 = ink.shape
Wk, Hk = int(W0 * S) + 1, int(H0 * S * 1.35) + 40

# group components into letters (i-dot with its stem): overlap in x and same line
groups = {}
for i in range(1, n):
    x, y, w, h, a = st[i]
    line = 0 if y < split_y else 1
    key = None
    for k, (gx0, gx1, gl) in list(groups.items()):
        if gl == line and min(gx1, x + w) - max(gx0, x) > 0.5 * min(w, gx1 - gx0):
            key = k; break
    if key is None:
        groups[i] = (x, x + w, line); key = i
    else:
        gx0, gx1, gl = groups[key]; groups[key] = (min(gx0, x), max(gx1, x + w), gl)
member = {}
for i in range(1, n):
    x, y, w, h, a = st[i]; line = 0 if y < split_y else 1
    for k, (gx0, gx1, gl) in groups.items():
        if gl == line and x >= gx0 - 1 and x + w <= gx1 + 1:
            member[i] = k; break

phase = rng.uniform(0, 2 * np.pi)
work = np.zeros((Hk, Wk), np.float32)
line2_shift = 0
for k, (gx0, gx1, gl) in groups.items():
    comps = [i for i in member if member[i] == k]
    m = np.isin(lab, comps).astype(np.uint8) * 255
    ys_, xs_ = np.where(m > 0)
    cx, cy = xs_.mean(), ys_.mean()
    jx, jy, jr = rng.normal(0, LETTER_JIT[0]), rng.normal(0, LETTER_JIT[1]), rng.normal(0, LETTER_JIT[2])
    drift = BASELINE_AMP * math.sin(2 * np.pi * cx / W0 * 0.9 + phase) + (0.6 * BASELINE_AMP * math.sin(2 * np.pi * cx / W0 * 2.3 + 2 * phase))
    sc = S * (VINTAGE_SCALE if gl == 1 else 1.0)
    # where letter centre lands in work space
    if gl == 1:
        # VINTAGE: scale around the logo's line-2 centre
        l2x = np.mean([st[i, 0] + st[i, 2] / 2 for i in range(1, n) if st[i, 1] >= split_y])
        l2y_top = min(st[i, 1] for i in range(1, n) if st[i, 1] >= split_y)
        gap = (l2y_top - split_y)
        tx = l2x * S + (cx - l2x) * sc
        ty = (l2y_top + gap * LINE_GAP_ADD * 3) * S + (cy - l2y_top) * sc
    else:
        tx, ty = cx * S, cy * S
    tx += jx * SS; ty += (jy + drift) * SS
    M = cv2.getRotationMatrix2D((cx, cy), jr, sc)
    M[0, 2] += tx - cx; M[1, 2] += ty - cy
    warped = cv2.warpAffine(m, M, (Wk, Hk), flags=cv2.INTER_LINEAR)
    work = np.maximum(work, warped.astype(np.float32) / 255)

mask = (work > 0.5).astype(np.uint8)
ys, xs = np.where(mask)
pad = int(12 * SS)
padx = pady = pad
if CLEAR:
    padx = max(pad, int((FRAME_AXES[0] + 8) * SS - (xs.max() - xs.min()) / 2))
    pady = max(pad, int((FRAME_AXES[1] + 8) * SS - (ys.max() - ys.min()) / 2))
mask = np.pad(mask, ((pady, pady), (padx, padx)))
mask = mask[ys.min(): ys.max() + 2 * pady, xs.min(): xs.max() + 2 * padx]
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

if VARIANT == 'patina':
    # full-width strokes (not skeleton): hand the soft jittered glyph mask to the patina renderer
    work_c = np.pad(work, ((pady, pady), (padx, padx)))[ys.min(): ys.max() + 2 * pady, xs.min(): xs.max() + 2 * padx]
    render_patina(work_c)
    sys.exit(0)

# ----------------------------------------------------------------- 2. centreline (single burin cut)
skel = zhang_suen(mask)
Hs, Ws = skel.shape
if CLEAR:
    ax, ay = int(FRAME_AXES[0] * SS), int(FRAME_AXES[1] * SS)
    cv2.ellipse(skel, (Ws // 2, Hs // 2), (ax, ay), 0, 0, 360, 1, 1)
    if BORDER_GAP > 0:
        g_ = int(BORDER_GAP * SS)
        cv2.ellipse(skel, (Ws // 2, Hs // 2), (ax - g_, ay - g_), 0, 0, 360, 1, 1)
    zone_plane = np.zeros((Hs, Ws), np.float32)
    cv2.ellipse(zone_plane, (Ws // 2, Hs // 2), (ax + int(1.5 * SS), ay + int(1.5 * SS)), 0, 0, 360, 1, -1)

# endpoints (for slips) & skeleton pixel list
nb = cv2.filter2D(skel.astype(np.float32), -1, np.ones((3, 3), np.float32)) - skel
endpoints = np.argwhere((skel == 1) & (nb == 1))
skel_pts = np.argwhere(skel == 1)

# burin slips: short straight overshoot along the stroke tangent
slips = np.zeros_like(skel)
if len(endpoints):
    for idx in rng.choice(len(endpoints), size=min(N_SLIPS, len(endpoints)), replace=False):
        ey, ex = endpoints[idx]
        nbh = skel_pts[(np.abs(skel_pts[:, 0] - ey) < 8 * SS) & (np.abs(skel_pts[:, 1] - ex) < 8 * SS)]
        v = np.array([ey, ex]) - nbh.mean(0)
        if np.linalg.norm(v) < 1e-3: continue
        v /= np.linalg.norm(v)
        L = rng.uniform(1.5, 3.5) * SS
        bend = rng.normal(0, 0.15)
        p1 = (int(ex + (v[1] + bend * v[0]) * L), int(ey + (v[0] - bend * v[1]) * L))
        cv2.line(slips, (int(ex), int(ey)), p1, 1, 1)

# ----------------------------------------------------------------- 3. hand irregularity
def warp_wobble(img, amp, scale, seed_rng):
    dx = smooth_noise(img.shape, scale * SS, seed_rng) * amp * SS
    dy = smooth_noise(img.shape, scale * SS, seed_rng) * amp * SS
    dx += smooth_noise(img.shape, 2.0 * SS, seed_rng) * TREMOR_AMP * SS
    dy += smooth_noise(img.shape, 2.0 * SS, seed_rng) * TREMOR_AMP * SS
    gx, gy = np.meshgrid(np.arange(img.shape[1], dtype=np.float32), np.arange(img.shape[0], dtype=np.float32))
    return cv2.remap(img, gx + dx, gy + dy, cv2.INTER_LINEAR)

lw = LINE_W * SS
cut = line_from_skeleton(skel, lw)
slip = line_from_skeleton(slips, lw * 0.8) * 0.55
cut = np.maximum(cut, slip)

# re-cut (doubled) segments: a second pass slightly offset, only locally
recut = np.zeros_like(cut)
for _ in range(N_RECUTS):
    py, px = skel_pts[rng.integers(len(skel_pts))]
    off = rng.normal(0, 1, 2); off = off / np.linalg.norm(off) * rng.uniform(1.1, 1.8) * SS
    Mt = np.float32([[1, 0, off[0]], [0, 1, off[1]]])
    shifted = cv2.warpAffine(cut, Mt, (Ws, Hs))
    blob = np.zeros_like(cut); cv2.ellipse(blob, (int(px), int(py)), (int(rng.uniform(5, 11) * SS),) * 2, 0, 0, 360, 1, -1)
    blob = cv2.GaussianBlur(blob, (0, 0), 3 * SS)
    recut = np.maximum(recut, shifted * blob * rng.uniform(0.45, 0.75))
cut = np.maximum(cut, recut)

cut = warp_wobble(cut, WOBBLE_AMP, WOBBLE_SCALE, rng)

# along-stroke strength (pressure / wear) and gaps
op = smooth_noise(cut.shape, 14 * SS, rng)
op = OPACITY_RANGE[0] + (OPACITY_RANGE[1] - OPACITY_RANGE[0]) * (0.5 + 0.5 * np.tanh(op * 1.1))
gapn = smooth_noise(cut.shape, 3.0 * SS, rng)
thr = np.quantile(gapn[cut > 0.5], GAP_FRACTION)
gapmask = np.clip((gapn - thr) / 0.35, 0, 1)
cut *= op * gapmask

# downsample to final scale (area filter = proper anti-aliasing)
hf, wf = int(Hs / SS), int(Ws / SS)
lines = cv2.resize(cut, (wf, hf), interpolation=cv2.INTER_AREA)

# frosted sparkle: pixel-level multiplicative noise + rare bright glints
spark = 1 + SPARKLE * rng.standard_normal(lines.shape).astype(np.float32)
glint = (rng.random(lines.shape) > 0.985).astype(np.float32) * 0.8
lines = np.clip(lines * (spark + glint), 0, 1.4)

# ----------------------------------------------------------------- 4. perspective onto the tray
base = cv2.imread(BASE_IMG).astype(np.float32)
Hb, Wb = base.shape[:2]
Hm = tray_homography(wf, hf)
layer = cv2.warpPerspective(lines, Hm, (Wb, Hb), flags=cv2.INTER_LINEAR)
layer = cv2.GaussianBlur(layer, (0, 0), FINAL_BLUR)
# text-block mask (for clearing & inpaint mask)
block = cv2.warpPerspective(np.ones((hf, wf), np.float32), Hm, (Wb, Hb))

# ----------------------------------------------------------------- 5. optional cartouche clearing
out = base.copy()
ys, xs = np.where(layer > 0.05)
ecx, ecy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
eax, eay = (xs.max() - xs.min()) / 2, (ys.max() - ys.min()) / 2
if CLEAR:
    zsmall = cv2.resize(zone_plane, (wf, hf), interpolation=cv2.INTER_AREA)
    zone = cv2.warpPerspective(zsmall, Hm, (Wb, Hb))
    zone = cv2.GaussianBlur(zone, (0, 0), CLEAR_FEATHER) * CLEAR_AMOUNT
    # remove old engraved lines: detect them (bright thin = top-hat), inpaint, then
    # rebuild a smooth metal base + re-synthesised grain so the patch is not plasticky
    g = cv2.cvtColor(base.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    th_ = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, np.ones((11, 11), np.uint8))
    linemask = ((th_ > 4) & (zone > 0.01)).astype(np.uint8) * 255
    linemask = cv2.dilate(linemask, np.ones((5, 5), np.uint8))
    clean = cv2.inpaint(base.astype(np.uint8), linemask, 6, cv2.INPAINT_TELEA).astype(np.float32)
    clean = cv2.medianBlur(clean.astype(np.uint8), 9).astype(np.float32)
    clean = cv2.GaussianBlur(clean, (0, 0), 3.0)
    # grain statistics from a line-free part of the original metal
    hp = base - cv2.GaussianBlur(base, (0, 0), 1.0)
    free = (linemask == 0) & (zone > 0.5)
    gstd = hp[free].std(0) if free.sum() > 100 else np.float32([2, 2, 2])
    n_ = rng.standard_normal((Hb, Wb)).astype(np.float32)
    n_ = cv2.GaussianBlur(n_, (0, 0), 0.7); n_ /= n_.std()
    clean = clean + n_[..., None] * gstd[None, None, :] * 0.9
    out = base * (1 - zone[..., None]) + clean * zone[..., None]

# ----------------------------------------------------------------- 6. blend the cut
L = layer[..., None]
lift = LINE_GAIN * (248 - out) * L                        # frosted pale cut, tends toward neutral white
tint = np.float32([1.0, 1.0, 1.02])                       # BGR, a hair warm like the existing lines
out = out + lift * tint
if DARK_EDGE > 0:
    sh = cv2.warpAffine(layer, np.float32([[1, 0, DARK_DIR[0] * 1.2], [0, 1, DARK_DIR[1] * 1.2]]), (Wb, Hb))
    edge = np.clip(sh - layer, 0, 1)
    out -= DARK_EDGE * edge[..., None]
out = np.clip(out, 0, 255).astype(np.uint8)
if JPEG_ROUNDTRIP:
    ok, enc = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, JPEG_ROUNDTRIP])
    dec = cv2.imdecode(enc, cv2.IMREAD_COLOR)
    # only take the re-encoded pixels near the edit, keep rest pixel-identical
    near = cv2.GaussianBlur(cv2.dilate((block > 0).astype(np.uint8), np.ones((61, 61), np.uint8)).astype(np.float32), (0, 0), 8)
    if CLEAR: near = np.maximum(near, cv2.dilate(zone, np.ones((41, 41), np.uint8)))
    out = (out * (1 - near[..., None]) + dec * near[..., None]).astype(np.uint8)

# ----------------------------------------------------------------- 7. save
v = VARIANT
cv2.imwrite(os.path.join(OUT_DIR, f'engraving-lines-{v}.png'), np.clip(lines / 1.4 * 255, 0, 255).astype(np.uint8))
rgba = np.dstack([np.full((Hb, Wb), 255, np.uint8)] * 3 + [np.clip(layer * LINE_GAIN * 255 * 2, 0, 255).astype(np.uint8)])
cv2.imwrite(os.path.join(OUT_DIR, f'engraving-layer-{v}.png'), rgba)
cv2.imwrite(os.path.join(OUT_DIR, f'composite-{v}.png'), out)
cx0, cy0 = int(ecx - 380), int(ecy - 220)
crop = out[cy0:cy0 + 440, cx0:cx0 + 760]
cv2.imwrite(os.path.join(OUT_DIR, f'composite-{v}-zoom.png'), cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
# inpaint mask: text block + generous margin, soft edge (white = editable)
im = np.zeros((Hb, Wb), np.float32)
cv2.ellipse(im, (int(ecx), int(ecy)), (int(eax + 28), int(eay + 24)), APPARENT_TILT, 0, 360, 1, -1)
im = cv2.GaussianBlur(im, (0, 0), 6)
cv2.imwrite(os.path.join(OUT_DIR, f'mask-inpaint-{v}.png'), (im * 255).astype(np.uint8))
print('done', v, 'text bbox', xs.min(), xs.max(), ys.min(), ys.max())
# tight mask: only the cuts + 6 px (re-texture lines without letting the model redraw glyphs)
tight = cv2.dilate((layer * LINE_GAIN * 255 * 2 > 10).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
cv2.imwrite(os.path.join(OUT_DIR, f'mask-inpaint-tight-{v}.png'), cv2.GaussianBlur(tight, (0, 0), 2))
