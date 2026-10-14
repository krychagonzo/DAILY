import sys, json, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *; from rules import build
font, srcp, pp, out = sys.argv[1:5]
src = cv2.imread(srcp, 0); top, bot = comps_of(src)
def ratio(w, ch):
    f = inst(font, w); _, Ib = rec(f, "I"); _, gb = rec(f, ch); return (gb[2]-gb[0]) / Ib[3]
R = build({"A": ratio(760, "A")}, {"A": ratio(450, "A")}); P = json.load(open(pp))
g = layout(font, src, 760, 450, R, params=P)
c = top + bot; pad = 40
X0 = min(b[0] for b in c) - pad; Y0 = min(b[1] for b in c) - pad
X1 = max(b[0] + b[2] for b in c) + pad; Y1 = max(b[1] + b[3] for b in c) + pad
sh = [(n, [(op, [(x - X0, y - Y0) for x, y in pts]) for op, pts in v]) for n, v in g]
W, H = X1 - X0, Y1 - Y0
open(out, "w").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
 <title>A CERTAIN ERA VINTAGE</title>
 <path fill="#000000" d="{to_d(sh)}"/>
</svg>
''')
print(W, H, X0, Y0)
