# Império de Ideias — EP01 Kodak — renderizador 2D (skia)
import skia, math, json, sys, os, random, subprocess
import numpy as np

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.environ.get("FONTDIR", os.path.join(BASE, "fonts"))
TIM = json.load(open(os.path.join(BASE, "timing.json")))
LINES = {l["i"]: (l["start"], l["end"]) for l in TIM["lines"]}
TOTAL = TIM["total"]
WORDS = json.load(open(os.path.join(BASE, "words.json"))) if os.path.exists(os.path.join(BASE, "words.json")) else []

def C(h, a=255):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))
BG, OR, GD, WH, EB, GR = "#111827", "#FF6B35", "#FBBF24", "#F9FAFB", "#3B82F6", "#374151"
SKIN, HAIR, SHIRT, TIE = "#E9B98F", "#2B1E16", "#EEF2F7", "#1F2A44"

TF_TITLE = skia.Typeface.MakeFromFile(os.path.join(FONTDIR, "Anton-Regular.ttf"))
TF_BODY = skia.Typeface.MakeFromFile(os.path.join(FONTDIR, "Montserrat-ExtraBold.ttf"))
TF_BODYM = skia.Typeface.MakeFromFile(os.path.join(FONTDIR, "Montserrat-SemiBold.ttf"))

# ---------- utils ----------
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def eo(t): t = cl(t); return 1 - (1 - t) ** 3
def eio(t): t = cl(t); return 3 * t * t - 2 * t * t * t
def back(t):
    t = cl(t); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def prog(t, a, b): return cl((t - a) / max(1e-6, b - a))
def P(color, a=255, stroke=0, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Color=C(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p
def rrect(cv, x, y, w, h, r, paint): cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)
def lin(x0, y0, x1, y1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [C(*c) if isinstance(c, tuple) else C(c) for c in cols], pos))
    return p
def rad(x, y, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r, [C(*c) if isinstance(c, tuple) else C(c) for c in cols], pos))
    return p
def glow(color, a, blur):
    p = P(color, a); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur)); return p
def path(pts, close=True):
    pa = skia.Path(); pa.moveTo(*pts[0])
    for q in pts[1:]: pa.lineTo(*q)
    if close: pa.close()
    return pa

def text_w(s, tf, size):
    return skia.Font(tf, size).measureText(s)
def text(cv, s, x, y, tf, size, color, a=255, align="c", shadow=True, stroke=0, scolor="#000000"):
    f = skia.Font(tf, size); f.setEdging(skia.Font.Edging.kAntiAlias)
    w = f.measureText(s)
    xx = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    if shadow:
        sp = P("#000000", int(a * 0.55)); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.06))
        cv.drawString(s, xx + size * 0.03, y + size * 0.05, f, sp)
    if stroke:
        cv.drawString(s, xx, y, f, P(scolor, a, stroke=stroke))
    cv.drawString(s, xx, y, f, P(color, a))
    return w

def rich(cv, parts, x, y, tf, size, a=255, stroke=0):
    """parts: list of (text, color). centered at x"""
    f = skia.Font(tf, size)
    tot = sum(f.measureText(s) for s, _ in parts)
    xx = x - tot / 2
    for s, col in parts:
        text(cv, s, xx, y, tf, size, col, a, align="l", stroke=stroke)
        xx += f.measureText(s)

# ---------- grain / vignette ----------
rng = np.random.default_rng(7)
GRAINS = []
for k in range(6):
    n = (rng.random((H // 2, W // 2)) * 255).astype(np.uint8)
    rgba = np.dstack([n, n, n, np.full_like(n, 255)])
    GRAINS.append(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType))
def post(cv, t):
    g = GRAINS[int(t * FPS) % len(GRAINS)]
    p = skia.Paint(); p.setAlphaf(0.045); p.setBlendMode(skia.BlendMode.kOverlay)
    cv.drawImageRect(g, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H * 0.45, H * 0.75, [(BG, 0), (BG, 0), ("#000000", 150)], [0, 0.55, 1]))

# ---------- characters ----------
def sasson(cv, x, y, s=1.0, t=0.0, look=0.0, arm=0.0, mouth=0.0, brow=0.0, blink_seed=0.0, hold=None):
    """x,y = feet-ish center of torso bottom. arm: 0 down .. 1 raised forward"""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    breathe = math.sin(t * 2.2) * 3
    # torso
    cv.translate(0, breathe * 0.3)
    torso = skia.Path(); torso.moveTo(-120, 0); torso.cubicTo(-125, -150, -95, -250, 0, -255); torso.cubicTo(95, -250, 125, -150, 120, 0); torso.close()
    cv.drawPath(torso, P(SHIRT)); cv.drawPath(torso, P("#C9D2DE", 255, stroke=5))
    cv.drawPath(path([(-14, -245), (14, -245), (24, -60), (0, -30), (-24, -60)]), P(TIE))
    cv.drawPath(path([(-40, -250), (0, -215), (-10, -260)]), P("#D7DEE8"))
    cv.drawPath(path([(40, -250), (0, -215), (10, -260)]), P("#D7DEE8"))
    # neck + head
    rrect(cv, -24, -290, 48, 50, 18, P("#D9A57C"))
    cv.save(); cv.translate(look * 10, -370 + breathe * 0.2)
    cv.drawOval(skia.Rect.MakeXYWH(-80, -95, 160, 185), P(SKIN))
    cv.drawOval(skia.Rect.MakeXYWH(-92, -10, 26, 40), P("#DDA882")); cv.drawOval(skia.Rect.MakeXYWH(66, -10, 26, 40), P("#DDA882"))
    hair = skia.Path(); hair.moveTo(-84, -5); hair.cubicTo(-100, -90, -50, -125, 0, -118); hair.cubicTo(60, -125, 105, -85, 86, -5)
    hair.cubicTo(78, -55, 40, -70, 10, -62); hair.cubicTo(-20, -78, -60, -60, -84, -5); hair.close()
    cv.drawPath(hair, P(HAIR))
    ex = look * 8
    bl = 1.0
    ph = (t + blink_seed) % 3.7
    if ph < 0.12: bl = 0.15
    for sx in (-30, 30):
        cv.drawOval(skia.Rect.MakeXYWH(sx - 9 + ex, 8 - 11 * bl, 18, 22 * bl), P("#1A1410"))
        cv.drawCircle(sx - 3 + ex, 4, 3.5 * bl, P(WH, 220))
        cv.drawLine(sx - 16, -18 - brow * 8 + (sx > 0) * brow * 4, sx + 16, -20 - brow * 6, P(HAIR, 255, stroke=7))
    cv.drawPath(path([(ex - 4, 22), (ex + 2, 48), (ex - 8, 50)], close=False), P("#C98F68", 255, stroke=5))
    mw = 28 + mouth * 8
    mp = skia.Path(); mp.moveTo(-mw / 2 + ex, 64); mp.quadTo(ex, 64 + 10 + mouth * 14, mw / 2 + ex, 64)
    if mouth > 0.3:
        mp.close(); cv.drawPath(mp, P("#7A2E22"))
    else:
        cv.drawPath(mp, P("#8A4A36", 255, stroke=6))
    cv.restore()
    # arms
    for side in (-1, 1):
        a = arm if side == 1 else arm * 0.6
        sx, sy = side * 105, -220
        ang = math.radians(lerp(100 if side == 1 else 80, -20 if side == 1 else 200, 0) )
        ex_ = sx + side * lerp(25, 10, a); ey_ = sy + lerp(110, 40, a)
        hx = sx + side * lerp(20, -40, a) + (0 if side == 1 else 0); hy = sy + lerp(215, 30, a)
        if side == -1: hx = sx + side * lerp(20, -50, a); hy = sy + lerp(215, 60, a)
        cv.drawPath(path([(sx, sy), (ex_, ey_), (hx, hy)], close=False), P(SHIRT, 255, stroke=46))
        cv.drawPath(path([(sx, sy), (ex_, ey_), (hx, hy)], close=False), P("#C9D2DE", 255, stroke=4))
        cv.drawCircle(hx, hy, 22, P(SKIN))
        if side == 1 and hold: hold(cv, hx, hy)
    cv.restore()

def executive(cv, x, y, s, t, suit, hair, bald=False, glasses=False, brow=0.0, mouth=0.0, seed=0.0, shush=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    br = math.sin(t * 1.8 + seed) * 2
    torso = skia.Path(); torso.moveTo(-130, 0); torso.cubicTo(-130, -150, -100, -240, 0, -245); torso.cubicTo(100, -240, 130, -150, 130, 0); torso.close()
    cv.drawPath(torso, P(suit))
    cv.drawPath(path([(-30, -240), (0, -150), (30, -240)]), P("#E5E7EB"))
    cv.drawPath(path([(-10, -235), (10, -235), (14, -160), (0, -140), (-14, -160)]), P("#7F1D1D"))
    cv.drawPath(path([(-60, -235), (0, -120), (-25, -240)]), P("#00000033"))
    cv.save(); cv.translate(0, -340 + br)
    cv.drawOval(skia.Rect.MakeXYWH(-78, -92, 156, 180), P("#E2AE86" if seed < 2 else "#C98E64"))
    if not bald:
        hp = skia.Path(); hp.moveTo(-80, 0); hp.cubicTo(-95, -85, -40, -112, 10, -108); hp.cubicTo(70, -110, 95, -70, 80, 0); hp.cubicTo(70, -50, 0, -70, -80, 0); hp.close()
        cv.drawPath(hp, P(hair))
    else:
        cv.drawPath(path([(-82, 10), (-80, -30), (-62, -20), (-64, 20)]), P(hair)); cv.drawPath(path([(82, 10), (80, -30), (62, -20), (64, 20)]), P(hair))
    for sx in (-28, 28):
        cv.drawOval(skia.Rect.MakeXYWH(sx - 8, 4, 16, 14), P("#1A1410"))
        tilt = brow * (8 if sx < 0 else -8)
        cv.drawLine(sx - 18, -16 + tilt, sx + 18, -16 - tilt, P(hair if not bald else "#5B4636", 255, stroke=8))
        if glasses: cv.drawCircle(sx, 11, 22, P("#111111", 255, stroke=5))
    if glasses: cv.drawLine(-6, 11, 6, 11, P("#111111", 255, stroke=5))
    mp = skia.Path(); mp.moveTo(-22, 58); mp.quadTo(0, 58 - 8 + mouth * 18, 22, 52)
    cv.drawPath(mp, P("#7A3B2A", 255, stroke=6))
    cv.restore()
    if shush > 0:
        hx, hy = lerp(90, 8, eo(shush)), lerp(-60, -280, eo(shush))
        cv.drawPath(path([(110, -200), (hx + 20, hy + 60), (hx, hy)], close=False), P(suit, 255, stroke=44))
        rrect(cv, hx - 16, hy - 40, 26, 70, 13, P("#E2AE86"))
    cv.restore()

# ---------- props ----------
def film_can(cv, x, y, s, a=255, crack=0.0, t=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-150, -200, 300, 400), lin(-150, 0, 150, 0, [("#B7791F", a), (GD, a), ("#FDE68A", a), (GD, a), ("#B7791F", a)], [0, .3, .45, .6, 1]))
    rrect(cv, -165, -235, 330, 50, 14, lin(-165, 0, 165, 0, [("#4B5563", a), ("#9CA3AF", a), ("#4B5563", a)]))
    rrect(cv, -165, 185, 330, 50, 14, lin(-165, 0, 165, 0, [("#4B5563", a), ("#9CA3AF", a), ("#4B5563", a)]))
    rrect(cv, -40, -275, 80, 50, 10, P("#6B7280", a))
    cv.drawRect(skia.Rect.MakeXYWH(-150, -60, 300, 120), P(OR, a))
    for k in range(5): cv.drawRect(skia.Rect.MakeXYWH(-150 + k * 66, -60, 30, 120), P("#E85A28", a))
    # film tongue
    tp = skia.Path(); tp.moveTo(150, 110); tp.lineTo(260, 110); tp.lineTo(260, 170); tp.lineTo(150, 170); tp.close()
    cv.drawPath(tp, P("#3A2A1A", a))
    for k in range(6): rrect(cv, 160 + k * 17, 116, 9, 10, 2, P("#C8A27A", a)); rrect(cv, 160 + k * 17, 154, 9, 10, 2, P("#C8A27A", a))
    if crack > 0:
        rnd = random.Random(3)
        for k in range(int(26 * crack)):
            px = rnd.uniform(-150, 150); py = rnd.uniform(-200, 200)
            sz = rnd.choice([14, 18, 24, 30])
            fly = cl(crack * 1.6 - rnd.random() * 0.6)
            cv.drawRect(skia.Rect.MakeXYWH(px + fly * rnd.uniform(-300, 300), py - fly * rnd.uniform(100, 500), sz, sz), P(EB, int(a * (1 - fly * 0.6))))
        cp = skia.Path(); cp.moveTo(-20, -200)
        pts = [(-20, -200), (10, -120), (-30, -40), (25, 30), (-10, 110), (20, 200)]
        n = max(2, int(len(pts) * cl(crack * 2)))
        for q in pts[1:n]: cp.lineTo(*q)
        cv.drawPath(cp, glow(EB, int(a), 10)); cv.drawPath(cp, P("#BFDBFE", a, stroke=6))
    cv.restore()

def proto_camera(cv, x, y, s, t=0.0, rec=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rrect(cv, -170, -110, 250, 220, 14, lin(0, -110, 0, 110, ["#9CA3AF", "#6B7280"]))
    rrect(cv, -170, -110, 250, 220, 14, P("#374151", 255, stroke=5))
    for k in range(6): cv.drawLine(-150, -80 + k * 14, -60, -80 + k * 14, P("#4B5563", 255, stroke=3))
    cv.drawCircle(-110, 40, 52, P("#1F2937")); cv.drawCircle(-110, 40, 40, rad(-120, 30, 40, ["#60A5FA", "#1E3A8A", "#0B1220"])); cv.drawCircle(-122, 26, 9, P(WH, 200))
    # cassette deck on side
    rrect(cv, 80, -90, 120, 180, 10, P("#4B5563")); rrect(cv, 92, -60, 96, 64, 6, P("#111827"))
    for cx in (115, 165):
        cv.save(); cv.translate(cx, -28); cv.rotate(t * 360 * (0.6 + rec))
        cv.drawCircle(0, 0, 14, P(WH));
        for k in range(3): cv.rotate(120); cv.drawRect(skia.Rect.MakeXYWH(-2, -14, 4, 8), P("#111827"))
        cv.restore()
    cv.drawCircle(175, 50, 9, P("#EF4444" if (rec > 0 and int(t * 4) % 2 == 0) else "#7F1D1D"))
    # circuit board top
    rrect(cv, -120, -150, 170, 40, 6, P("#065F46"))
    for k in range(7): cv.drawRect(skia.Rect.MakeXYWH(-110 + k * 23, -144, 12, 10), P("#111827"))
    cv.restore()

def toaster(cv, x, y, s):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rrect(cv, -140, -100, 280, 200, 60, lin(0, -100, 0, 100, ["#E5E7EB", "#9CA3AF"]))
    rrect(cv, -90, -100, 60, 18, 8, P("#1F2937")); rrect(cv, 30, -100, 60, 18, 8, P("#1F2937"))
    rrect(cv, 130, -10, 30, 14, 6, P("#374151"))
    cv.drawOval(skia.Rect.MakeXYWH(-90, -60, 50, 30), P(WH, 120))
    cv.restore()

def crt(cv, x, y, s, t, screen=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rrect(cv, -230, -190, 460, 360, 30, lin(0, -190, 0, 170, ["#7C5A3A", "#4A3220"]))
    rrect(cv, -195, -160, 320, 280, 40, P("#0B0F17"))
    sc = skia.Rect.MakeXYWH(-182, -148, 294, 256)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(sc, 34, 34), doAntiAlias=True)
    cv.drawRect(sc, P("#0A1A12"))
    if screen: screen(cv, sc)
    for k in range(0, 256, 6): cv.drawRect(skia.Rect.MakeXYWH(-182, -148 + k, 294, 2), P("#000000", 45))
    cv.drawRect(sc, rad(-35, -20, 230, [("#9FE8C4", 30), ("#000000", 0), ("#000000", 120)], [0, .6, 1]))
    cv.restore()
    for k in range(4): cv.drawCircle(178, -110 + k * 55, 16, P("#2B1D12"))
    cv.drawLine(-120, -190, -190, -300, P("#9CA3AF", 255, stroke=6)); cv.drawLine(-60, -190, 10, -310, P("#9CA3AF", 255, stroke=6))
    cv.restore()

PIX = None
def pixel_face(cv, rect, reveal, n=20):
    global PIX
    if PIX is None:
        g = np.zeros((n, n))
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
        face = np.exp(-(((xx - .5) / .22) ** 2 + ((yy - .45) / .28) ** 2))
        hair = (np.exp(-(((xx - .5) / .3) ** 2 + ((yy - .25) / .2) ** 2)) > .5) * .6
        body = (yy > .78) * (np.abs(xx - .5) < .35) * .5
        g = np.clip(face * .9 + body - hair * .3 + 0.08, 0, 1)
        g[int(n * .42), int(n * .38)] = .1; g[int(n * .42), int(n * .62)] = .1; g[int(n * .62), int(n * .45):int(n * .56)] = .25
        PIX = g
    cw, ch = rect.width() / n, rect.height() / n
    tot = n * n; shown = int(tot * reveal)
    for k in range(shown):
        r, c = divmod(k, n)
        v = int(PIX[r, c] * 230)
        cv.drawRect(skia.Rect.MakeXYWH(rect.left() + c * cw, rect.top() + r * ch, cw + .5, ch + .5), skia.Paint(Color=skia.Color(v, v, v)))

def phone(cv, x, y, s, glowa=255, col=EB):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rrect(cv, -45, -85, 90, 170, 16, P("#0B0F17")); rrect(cv, -39, -76, 78, 150, 10, lin(0, -76, 0, 76, [(col, glowa), ("#93C5FD", glowa)]))
    cv.drawCircle(0, 0, 14, P(WH, int(glowa * .8), stroke=4))
    cv.restore()

def coin(cv, x, y, s, t):
    w = abs(math.cos(t * 6)) * 40 * s + 4
    cv.drawOval(skia.Rect.MakeXYWH(x - w, y - 40 * s, 2 * w, 80 * s), P(GD)); cv.drawOval(skia.Rect.MakeXYWH(x - w * .7, y - 28 * s, 1.4 * w, 56 * s), P("#F59E0B"))

def tag(cv, s, x, y, size=34, col=GD, a=255, bg="#111827"):
    f = skia.Font(TF_BODY, size); w = f.measureText(s)
    rrect(cv, x - w / 2 - 26, y - size - 6, w + 52, size + 30, (size + 30) / 2, P(bg, int(a * .85)))
    rrect(cv, x - w / 2 - 26, y - size - 6, w + 52, size + 30, (size + 30) / 2, P(col, a, stroke=3))
    text(cv, s, x, y + 2, TF_BODY, size, col, a, shadow=False)

def title(cv, s, y, size, col=WH, a=255, x=W / 2, stroke=0):
    text(cv, s, x, y, TF_TITLE, size, col, a, stroke=stroke)

def bgfill(cv, top="#0B1120", bottom=BG):
    cv.drawRect(skia.Rect.MakeWH(W, H), lin(0, 0, 0, H, [top, bottom]))

def stars(cv, t, n=60, seed=1, a=120):
    r = random.Random(seed)
    for k in range(n):
        x = r.uniform(0, W); y = r.uniform(0, H * .55); tw = .5 + .5 * math.sin(t * r.uniform(1, 3) + k)
        cv.drawCircle(x, y, r.uniform(1, 2.6), P(WH, int(a * tw)))

def light_rays(cv, x, y, t, col=GD, a=40):
    cv.save(); cv.translate(x, y); cv.rotate(t * 8)
    for k in range(12):
        cv.rotate(30); cv.drawPath(path([(0, 0), (-60, -1400), (60, -1400)]), P(col, a))
    cv.restore()

# ---------- scenes ----------
def S(i): return LINES[i]

def sc_hook(cv, t):
    a, b = S(1)
    bgfill(cv, "#0A0F1E", "#111827"); stars(cv, t)
    # city skyline 70s
    r = random.Random(5); x = 0
    while x < W:
        w = r.randint(70, 150); h = r.randint(150, 420)
        cv.drawRect(skia.Rect.MakeXYWH(x, 1480 - h, w, h + 500), P("#0E1526"))
        for wy in range(int(1480 - h + 20), 1460, 40):
            for wx in range(int(x + 12), int(x + w - 15), 28):
                if r.random() < .35: cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 12, 18), P(GD, 90))
        x += w + 6
    cv.drawRect(skia.Rect.MakeXYWH(0, 1470, W, 500), P("#0A0F1A"))
    light_rays(cv, W / 2, 900, t, GD, 22)
    cv.drawCircle(W / 2, 900, 420, glow(GD, 60, 120))
    sw = prog(t, a + 2.0, b + 0.2)
    s = lerp(0.9, 1.25, eo(prog(t, 0, 3))) + math.sin(t * 2) * .01
    film_can(cv, W / 2, 1000 + math.sin(t * 1.5) * 8, s * 1.2, crack=sw, t=t)
    # blue pixel wave swallowing
    if sw > 0:
        rr = random.Random(9)
        for k in range(160):
            px = rr.uniform(0, W); base = rr.uniform(0, 1)
            yy = H - (H * 1.2) * eio(sw) + base * 500
            sz = rr.choice([20, 30, 40])
            cv.drawRect(skia.Rect.MakeXYWH(px, yy, sz, sz), P(EB, int(200 * rr.uniform(.4, 1))))
        cv.drawRect(skia.Rect.MakeXYWH(0, H - (H * 1.2) * eio(sw) + 500, W, H), P("#1D4ED8", 230))
    k1 = eo(prog(t, a + 0.2, a + 0.7))
    title(cv, "ESSA EMPRESA", 360 - (1 - k1) * 40, 92, WH, int(255 * k1))
    k2 = back(prog(t, a + 0.9, a + 1.4))
    title(cv, "INVENTOU O FUTURO", 480, 118 * (0.6 + 0.4 * k2), OR, int(255 * cl(k2)))

def sc_market(cv, t):
    a, b = S(2)
    bgfill(cv, "#1A1407", "#111827")
    # shop window shelf of film boxes
    cv.save(); cv.translate(0, math.sin(t) * 4)
    for row in range(4):
        y = 980 + row * 150
        cv.drawRect(skia.Rect.MakeXYWH(60, y + 110, W - 120, 16), P("#5B3A1E"))
        for col in range(7):
            x = 90 + col * 135; k = row * 7 + col
            lit = k < int(28 * .9 * eo(prog(t, a + 1.6, a + 3.6)))
            boxcol = GD if lit else "#4B5563"
            rrect(cv, x, y, 110, 110, 8, P(boxcol)); cv.drawRect(skia.Rect.MakeXYWH(x, y + 40, 110, 30), P(OR if lit else "#374151"))
    cv.restore()
    cv.drawRect(skia.Rect.MakeXYWH(40, 940, W - 80, 640), P(WH, 18)); cv.drawRect(skia.Rect.MakeXYWH(40, 940, W - 80, 640), P("#8B5E34", 255, stroke=16))
    k = eo(prog(t, a, a + .5)); title(cv, "ANOS 70", 330, 80, WH, int(255 * k))
    n = int(90 * eo(prog(t, a + 1.6, a + 3.6)))
    pop = back(prog(t, a + 1.6, a + 2.1))
    if t > a + 1.5:
        title(cv, f"{n}%", 640, 260 * (.7 + .3 * pop), GD, 255)
        text(cv, "do filme fotográfico vendido nos EUA", W / 2, 740, TF_BODY, 40, WH, int(255 * eo(prog(t, a + 2.2, a + 2.7))))
        text(cv, "(estimativa de mercado, meados dos anos 70)", W / 2, 800, TF_BODYM, 28, "#9CA3AF", int(255 * eo(prog(t, a + 2.6, a + 3.1))), shadow=False)

def lab_bg(cv, t, lamp=1.0):
    bgfill(cv, "#0B1222", "#111827")
    cv.drawRect(skia.Rect.MakeXYWH(0, 1300, W, 700), lin(0, 1300, 0, 1920, ["#3A2614", "#24170C"]))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1290, W, 24), P("#5B3A1E"))
    # shelves w/ equipment
    for k, (x, y, w, h) in enumerate([(60, 700, 300, 200), (720, 640, 300, 260), (80, 440, 220, 150)]):
        rrect(cv, x, y, w, h, 12, P("#1F2937")); rrect(cv, x + 20, y + 20, w - 40, h - 70, 8, P("#052E1B"))
        wp = skia.Path();
        for i in range(60):
            xx = x + 20 + (w - 40) * i / 59; yy = y + 20 + (h - 70) / 2 + math.sin(i * .5 + t * (3 + k)) * (h - 90) / 3
            (wp.moveTo if i == 0 else wp.lineTo)(xx, yy)
        cv.drawPath(wp, glow("#34D399", 200, 4)); cv.drawPath(wp, P("#6EE7B7", 255, stroke=3))
        for j in range(3): cv.drawCircle(x + 40 + j * 40, y + h - 25, 10, P(OR if j == 0 else "#6B7280"))
    # lamp glow
    cv.drawCircle(W / 2 + 200, 1150, 520, rad(W / 2 + 200, 1150, 520, [(GD, int(70 * lamp)), (GD, 0)]))

def sc_lab(cv, t):
    a, b = S(3)
    lab_bg(cv, t)
    lt = t - a
    arm = eo(prog(t, a + 3.2, a + 4.2))
    def hold(cv2, hx, hy):
        if arm > .3:
            rrect(cv2, hx - 26, hy - 60, 52, 40, 6, P("#111827")); rrect(cv2, hx - 16, hy - 52, 32, 24, 3, P(EB))
            cv2.drawCircle(hx, hy - 40, 60, glow(EB, int(140 * arm), 30))
    sasson(cv, W / 2, 1560, 1.55, t, look=math.sin(lt * .8) * .4, arm=arm, mouth=.1, brow=arm * .6, hold=hold)
    k = back(prog(t, a, a + .6)); title(cv, "1975", 400, 200 * (.6 + .4 * k), GD, int(255 * cl(k)))
    k2 = eo(prog(t, a + 1.6, a + 2.2))
    if k2 > 0:
        tag(cv, "STEVEN SASSON", W / 2, 560, 44, OR, int(255 * k2))
        text(cv, "engenheiro da Kodak", W / 2, 640, TF_BODYM, 34, WH, int(255 * k2))
    k3 = eo(prog(t, a + 4.0, a + 4.6))
    if k3 > 0: tag(cv, "MISSÃO: um novo sensor (CCD)", W / 2, 760, 34, OR, int(255 * k3))

def sc_camera(cv, t):
    a, b = S(4)
    lab_bg(cv, t, .6)
    k = eo(prog(t, a - .2, a + .6))
    rrect(cv, 0, 1150, W, 40, 0, P("#5B3A1E"))
    proto_camera(cv, lerp(-300, 380, k), 1000, 1.5, t)
    k2 = back(prog(t, a + 1.2, a + 1.8))
    if k2 > 0: toaster(cv, 830, 1060, 1.1 * cl(k2, 0, 1.2))
    if t > a + 1.3:
        tag(cv, "tamanho de uma torradeira", W / 2, 620, 40, GD, int(255 * eo(prog(t, a + 1.4, a + 1.9))))
        text(cv, "≈ 3,6 kg · 16 pilhas AA", W / 2, 720, TF_BODY, 36, WH, int(255 * eo(prog(t, a + 1.8, a + 2.3))))
    title(cv, "O PROTÓTIPO", 420, 110, WH, int(255 * eo(prog(t, a, a + .5))))

def sc_pixels(cv, t):
    a, b = S(5)
    bgfill(cv, "#06100C", "#0B1222")
    rev = eo(prog(t, a + .1, a + 1.6))
    crt(cv, W / 2, 1040, 1.8, t, screen=lambda c2, sc: pixel_face(c2, skia.Rect.MakeXYWH(sc.left() + 37, sc.top() + 8, 240, 240), rev))
    k = back(prog(t, a, a + .5))
    title(cv, "100 × 100", 360, 170 * (.6 + .4 * cl(k)), GD, int(255 * cl(k)))
    text(cv, "PIXELS · PRETO E BRANCO", W / 2, 440, TF_BODY, 42, WH, int(255 * eo(prog(t, a + .8, a + 1.3))))
    # cassette + timer
    tt = prog(t, a + 2.4, b - 0.2)
    if t > a + 2.2:
        al = int(255 * eo(prog(t, a + 2.2, a + 2.6)))
        rrect(cv, 300, 1480, 480, 230, 20, P("#1F2937", al)); rrect(cv, 340, 1510, 400, 110, 10, P("#E5E7EB", al))
        for cx in (430, 650):
            cv.save(); cv.translate(cx, 1565); cv.rotate(t * 300)
            cv.drawCircle(0, 0, 38, P("#111827", al))
            for kk in range(6): cv.rotate(60); cv.drawRect(skia.Rect.MakeXYWH(-4, -36, 8, 14), P(WH, al))
            cv.restore()
        sec = 23 * tt
        title(cv, f"{sec:04.1f}s", 1690, 80, OR, al)

def sc_nofilm(cv, t):
    a, b = S(6)
    bgfill(cv, "#1C0F0A", "#111827")
    k = back(prog(t, a - .1, a + .4))
    film_can(cv, W / 2, 930, .9 * cl(k, 0, 1.2), t=t)
    st = eo(prog(t, a + .4, a + .8))
    if st > 0:
        cv.drawCircle(W / 2, 930, 330, P("#EF4444", 255, stroke=36))
        cv.drawLine(W / 2 - 233 * st, 930 + 233 * st, W / 2 + 233 * st * (2 * st - 1) if False else W / 2 - 233 + 466 * st, 930 + 233 - 466 * st, P("#EF4444", 255, stroke=36))
    title(cv, "SEM FILME", 480, 170, OR, int(255 * eo(prog(t, a + .3, a + .7))))

def sc_board(cv, t):
    a, b = S(7)
    bgfill(cv, "#1A1A2E", "#111827")
    # wall panels
    for k in range(6): cv.drawRect(skia.Rect.MakeXYWH(k * 190, 300, 170, 900), P("#1F2440"))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1180, W, 800), P("#151A2C"))
    sh = eo(prog(t, a + 2.3, a + 2.9))
    executive(cv, 230, 1270, 1.0, t, "#374151", "#6B7280", bald=True, glasses=True, brow=.8, seed=0)
    executive(cv, 520, 1250, 1.05, t, "#1F2937", "#111111", brow=.5, mouth=.2, seed=1.3, shush=sh)
    executive(cv, 810, 1270, 1.0, t, "#4B5563", "#9CA3AF", brow=.9, seed=2.5)
    # table
    tp = path([(-40, 1250), (W + 40, 1250), (W + 40, 1420), (-40, 1420)]); cv.drawPath(tp, lin(0, 1250, 0, 1420, ["#7C4A21", "#4A2A10"]))
    cv.drawRect(skia.Rect.MakeXYWH(-40, 1250, W + 80, 18), P("#A0612C"))
    proto_camera(cv, 560, 1180, .55, t)
    # Sasson foreground (back-ish view, smaller at right bottom)
    sasson(cv, 900, 1960, 1.25, t, look=-1, arm=.2, mouth=0, brow=-.2)
    k = eo(prog(t, a + .1, a + .6)); title(cv, "A REAÇÃO DOS CHEFES", 370, 92, WH, int(255 * k))
    kb = back(prog(t, a + 1.6, a + 2.2))
    if kb > 0:
        cv.save(); cv.translate(W / 2, 640); cv.scale(cl(kb, 0, 1.2), cl(kb, 0, 1.2))
        rrect(cv, -430, -150, 860, 260, 50, P(WH)); cv.drawPath(path([(-40, 105), (40, 105), (20, 200)]), P(WH))
        text(cv, "“Bonitinho...", 0, -40, TF_TITLE, 96, BG, shadow=False)
        text(cv, "mas não conte pra ninguém.”", 0, 60, TF_BODY, 50, OR, shadow=False)
        cv.restore()
        text(cv, "segundo o relato de Sasson", W / 2, 445, TF_BODYM, 32, "#CBD5E1", int(255 * eo(prog(t, a + 2.2, a + 2.7))))

def sc_business(cv, t):
    a, b = S(8)
    bgfill(cv, "#0B1120", "#111827")
    title(cv, "O PROBLEMA ERA O NEGÓCIO", 380, 84, WH, int(255 * eo(prog(t, a, a + .5))))
    # HQ building
    bx = W / 2; cv.drawRect(skia.Rect.MakeXYWH(bx - 170, 1150, 340, 450), P("#1E293B"))
    for yy in range(1180, 1580, 60):
        for xx in range(int(bx - 140), int(bx + 140), 70): cv.drawRect(skia.Rect.MakeXYWH(xx, yy, 40, 34), P(GD, 120))
    cv.drawPath(path([(bx - 200, 1150), (bx, 1040), (bx + 200, 1150)]), P("#334155"))
    labels = [("FILME", 230), ("PAPEL", 540), ("REVELAÇÃO", 850)]
    for idx, (lab, x) in enumerate(labels):
        st = a + 1.3 + idx * .65
        k = back(prog(t, st, st + .5))
        if k <= 0: continue
        cv.save(); cv.translate(x, 760); cv.scale(cl(k, 0, 1.2), cl(k, 0, 1.2))
        cv.drawCircle(0, 0, 110, P(GR)); cv.drawCircle(0, 0, 110, P(GD, 255, stroke=6))
        if idx == 0:
            rrect(cv, -45, -60, 90, 120, 10, P(GD)); cv.drawRect(skia.Rect.MakeXYWH(-45, -15, 90, 30), P(OR))
        elif idx == 1:
            cv.save(); cv.rotate(-8); rrect(cv, -55, -45, 110, 90, 6, P(WH)); rrect(cv, -45, -35, 90, 60, 4, P(EB)); cv.restore()
        else:
            cv.drawPath(path([(-25, -60), (25, -60), (25, -10), (55, 60), (-55, 60), (-25, -10)]), P("#A7F3D0")); cv.drawRect(skia.Rect.MakeXYWH(-50, 20, 100, 40), P("#10B981"))
        cv.restore()
        text(cv, lab, x, 930, TF_BODY, 38, WH, int(255 * cl(k)))
        # coins flowing to HQ
        for j in range(4):
            ph = ((t - st) * .9 + j * .25) % 1
            if t > st + .3:
                cx = lerp(x, bx, ph); cy = lerp(960, 1200, ph) - math.sin(ph * math.pi) * 120
                coin(cv, cx, cy, .5, t + j)

def sc_patent(cv, t):
    a, b = S(9)
    bgfill(cv, "#0F172A", "#111827")
    # document
    k = eo(prog(t, a - .1, a + .5))
    cv.save(); cv.translate(W / 2, lerp(1300, 980, k)); cv.rotate(-4)
    rrect(cv, -300, -380, 600, 760, 16, P("#F3EBD7"))
    text(cv, "PATENTE", 0, -280, TF_TITLE, 90, BG, shadow=False)
    text(cv, "câmera eletrônica de imagens estáticas", 0, -215, TF_BODYM, 26, "#374151", shadow=False)
    for j in range(9): cv.drawRect(skia.Rect.MakeXYWH(-240, -150 + j * 44, 480 - (j % 3) * 60, 12), P("#C9BFA6"))
    proto_camera(cv, 0, 290, .45, t)
    stamp = back(prog(t, a + .9, a + 1.3))
    if stamp > 0:
        cv.save(); cv.translate(150, 160); cv.rotate(-14); s = lerp(2.2, 1, cl(stamp)); cv.scale(s, s)
        rrect(cv, -130, -55, 260, 110, 14, P("#DC2626", 230, stroke=10)); text(cv, "1978", 0, 30, TF_TITLE, 84, "#DC2626", 230, shadow=False)
        cv.restore()
    cv.restore()
    if t > a + 1.6:
        for j in range(10):
            ph = ((t - a - 1.6) * .7 + j * .1) % 1
            coin(cv, 150 + (j * 97) % 800, lerp(380, 1800, ph), .7, t + j)
    sw = eo(prog(t, a + 2.6, a + 3.2))
    if sw > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG, int(200 * sw)))
        cv.drawPath(path([(W / 2 - 80, 0), (W / 2 + 80, 0), (W / 2 + 330, 1500), (W / 2 - 330, 1500)]), P(GD, int(60 * sw)))
        film_can(cv, W / 2, 1150, .95 * sw, t=t)
        cv.drawOval(skia.Rect.MakeXYWH(W / 2 - 320, 1460, 640, 80), P("#000000", int(120 * sw)))
        title(cv, "MAS A APOSTA SEGUIU NO FILME", 460, 76, OR, int(255 * sw))
    else:
        title(cv, "PATENTEOU E LUCROU", 360, 96, GD, int(255 * eo(prog(t, a + .3, a + .8))))

def sc_digital(cv, t):
    a, b = S(10)
    bgfill(cv, "#0A1025", "#0B1222")
    stars(cv, t, 40, 3)
    rise = eo(prog(t, a, a + 2.0))
    # old factory dark
    fade = 1 - .7 * prog(t, a + 1.5, a + 3.5)
    cv.drawRect(skia.Rect.MakeXYWH(200, 900, 680, 560), P("#1F2937", int(255 * fade)))
    for k in range(4): cv.drawRect(skia.Rect.MakeXYWH(230 + k * 160, 760, 60, 160), P("#111827", int(255 * fade)))
    film_can(cv, W / 2, 1120, .55, a=int(255 * fade), t=t)
    r = random.Random(11)
    for k in range(26):
        x = r.uniform(40, W - 40); base = r.uniform(1350, 1800); dl = r.uniform(0, .5)
        yy = lerp(2100, base, eo(prog(t, a + dl, a + dl + 1.2)))
        cv.drawCircle(x, yy + 30, 70, glow(EB, 70, 30))
        phone(cv, x, yy, r.uniform(.7, 1.1))
    k = eo(prog(t, a, a + .5)); title(cv, "O MUNDO VIROU DIGITAL", 360, 90, EB, int(255 * k))
    kc = back(prog(t, a + 1.9, a + 2.4))
    if kc > 0:
        cv.save(); cv.translate(W / 2, 640); cv.scale(cl(kc, 0, 1.2), cl(kc, 0, 1.2))
        rrect(cv, -260, -170, 520, 330, 30, P(WH)); rrect(cv, -260, -170, 520, 90, 30, P("#DC2626")); cv.drawRect(skia.Rect.MakeXYWH(-260, -110, 520, 30), P("#DC2626"))
        text(cv, "JANEIRO", 0, -105, TF_BODY, 44, WH, shadow=False)
        text(cv, "2012", 0, 100, TF_TITLE, 170, BG, shadow=False)
        cv.restore()
        tag(cv, "pedido de recuperação judicial (Chapter 11, EUA)", W / 2, 920, 30, OR, int(255 * eo(prog(t, a + 2.8, a + 3.3))))

def sc_reflect(cv, t):
    a, b = S(11)
    bgfill(cv, "#0B1120", "#111827")
    # left: future (blue glow), right: past (film can dimming)
    cv.drawCircle(260, 900, 520, rad(260, 900, 520, [(EB, 110), (EB, 0)]))
    past = 1 - .6 * prog(t, a + 1.8, b)
    film_can(cv, 800, 950, .7, a=int(255 * past), t=t)
    crt(cv, 270, 960, .9, t, screen=lambda c2, sc: pixel_face(c2, skia.Rect.MakeXYWH(sc.left() + 37, sc.top() + 8, 240, 240), 1.0))
    sasson(cv, W / 2 + 20, 1990, 1.05, t, look=-1.2 + 1.8 * eio(prog(t, a + 1.6, a + 2.4)), arm=0, mouth=0, brow=.3)
    title(cv, "VIU O FUTURO PRIMEIRO.", 380, 96, EB, int(255 * eo(prog(t, a, a + .5))))
    k = eo(prog(t, a + 1.7, a + 2.2)); title(cv, "O DIFÍCIL FOI LARGAR O PASSADO.", 490, 70, GD, int(255 * k))

def sc_end(cv, t):
    a, b = S(12)
    bgfill(cv, "#111827", "#0B1120")
    light_rays(cv, W / 2, 1000, t, OR, 14)
    k = back(prog(t, a, a + .6))
    cv.save(); cv.translate(W / 2, 820); cv.scale(cl(k, 0, 1.2), cl(k, 0, 1.2))
    title(cv, "QUAL GIGANTE", -120, 140, WH, x=0); title(cv, "DE HOJE ESTÁ", 30, 140, WH, x=0)
    title(cv, "COMETENDO O", 180, 140, WH, x=0); title(cv, "MESMO ERRO?", 330, 150, OR, x=0)
    cv.restore()
    kc = eo(prog(t, a + 1.6, a + 2.1))
    if kc > 0: tag(cv, "responda nos comentários", W / 2, 1330, 36, GD, int(255 * kc))
    kl = eo(prog(t, b + .1, b + .6))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG, int(255 * kl)))
        logo(cv, W / 2, 900, 1.0, int(255 * kl))

def logo(cv, x, y, s, a=255):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(path([(-70, 40), (-70, -20), (-35, 10), (0, -50), (35, 10), (70, -20), (70, 40)]), P(GD, a))
    cv.drawCircle(0, -70, 14, P(OR, a))
    text(cv, "IMPÉRIO DE IDEIAS", 0, 150, TF_TITLE, 96, WH, a)
    text(cv, "histórias extraordinárias por trás de grandes negócios", 0, 215, TF_BODYM, 28, "#CBD5E1", a, shadow=False)
    cv.restore()

SCENES = [  # (scene_fn, start, end)
    (sc_hook, 0.0, S(2)[0] - .15),
    (sc_market, S(2)[0] - .15, S(3)[0] - .1),
    (sc_lab, S(3)[0] - .1, S(4)[0] - .1),
    (sc_camera, S(4)[0] - .1, S(5)[0] - .1),
    (sc_pixels, S(5)[0] - .1, S(6)[0] - .1),
    (sc_nofilm, S(6)[0] - .1, S(7)[0] - .2),
    (sc_board, S(7)[0] - .2, S(8)[0] - .2),
    (sc_business, S(8)[0] - .2, S(9)[0] - .15),
    (sc_patent, S(9)[0] - .15, S(10)[0] - .15),
    (sc_digital, S(10)[0] - .15, S(11)[0] - .2),
    (sc_reflect, S(11)[0] - .2, S(12)[0] - .2),
    (sc_end, S(12)[0] - .2, TOTAL),
]
XF = 0.35  # transition length

# ---------- subtitles ----------
CHUNKS = {
 1: [("Essa empresa", 2), ("inventou o *futuro*...", 3), ("e acabou", 2), ("*engolida* por ele.", 3)],
 2: [("Anos 70.", 2), ("A *Kodak* vende", 3), ("cerca de *90%*", 5), ("do filme fotográfico", 3), ("dos Estados Unidos.", 3)],
 3: [("Em *1975*,", 7), ("o engenheiro", 2), ("*Steven Sasson*", 2), ("recebe uma missão:", 3), ("descobrir o que fazer", 4), ("com um novo", 3), ("*sensor eletrônico*.", 2)],
 4: [("Ele cria uma câmera", 4), ("do tamanho de", 3), ("uma *torradeira*.", 2)],
 5: [("*100 × 100* pixels.", 4), ("Preto e branco.", 3), ("*23 segundos*", 4), ("para gravar cada foto", 4), ("numa fita cassete.", 3)],
 6: [("Sem um único", 3), ("rolo de *filme*.", 3)],
 7: [("Segundo Sasson,", 2), ("a reação dos chefes foi:", 5), ("“*Bonitinho*...", 1), ("mas não conte", 3), ("pra *ninguém*.”", 2)],
 8: [("O problema", 2), ("era o *negócio*.", 3), ("A Kodak vivia", 3), ("de vender *filme*,", 3), ("*papel* e *revelação*.", 3)],
 9: [("A empresa *patenteou*", 3), ("a invenção", 2), ("e *lucrou* com ela.", 4), ("Mas seguiu apostando", 3), ("no *filme*.", 2)],
 10: [("O mundo virou *digital*.", 4), ("E, em *2012*,", 6), ("a Kodak pediu", 3), ("*recuperação judicial*.", 2)],
 11: [("Ela viu o *futuro*", 4), ("primeiro.", 1), ("O difícil foi", 3), ("largar o *passado*.", 3)],
 12: [("Qual gigante de hoje", 4), ("está cometendo", 2), ("o mesmo *erro*?", 3)],
}
SPOKEN = {
 1: "Essa empresa inventou o futuro e acabou engolida por ele",
 2: "Anos setenta A Kodak vende cerca de noventa por cento do filme fotográfico dos Estados Unidos",
 3: "Em mil novecentos e setenta e cinco o engenheiro Steven Sasson recebe uma missão descobrir o que fazer com um novo sensor eletrônico",
 4: "Ele cria uma câmera do tamanho de uma torradeira",
 5: "Cem por cem pixels Preto e branco Vinte e três segundos para gravar cada foto numa fita cassete",
 6: "Sem um único rolo de filme",
 7: "Segundo Sasson a reação dos chefes foi Bonitinho mas não conte pra ninguém",
 8: "O problema era o negócio A Kodak vivia de vender filme papel e revelação",
 9: "A empresa patenteou a invenção e lucrou com ela Mas seguiu apostando no filme",
 10: "O mundo virou digital E em dois mil e doze a Kodak pediu recuperação judicial",
 11: "Ela viu o futuro primeiro O difícil foi largar o passado",
 12: "Qual gigante de hoje está cometendo o mesmo erro",
}
def build_subs():
    subs = []
    for i, chunks in CHUNKS.items():
        toks = SPOKEN[i].split(); assert sum(n for _, n in chunks) == len(toks), (i, sum(n for _, n in chunks), len(toks))
        a, b = LINES[i]
        ws = [w for w in WORDS if w[0] >= a - .25 and w[0] < b + .1]
        # cumulative char fraction -> time map from whisper words
        if ws:
            tot = sum(len(w[2]) for w in ws); acc = 0; pts = []
            for w in ws: pts.append((acc / tot, w[0])); acc += len(w[2])
            pts.append((1.0, ws[-1][1]))
        else:
            pts = [(0, a), (1, b)]
        def tm(f):
            for (f0, t0), (f1, t1) in zip(pts, pts[1:]):
                if f <= f1: return t0 + (t1 - t0) * ((f - f0) / max(1e-6, f1 - f0))
            return pts[-1][1]
        totc = sum(len(x) for x in toks); k = 0; c = 0
        starts = []
        for disp, n in chunks:
            starts.append(tm(c / totc)); c += sum(len(x) for x in toks[k:k + n]); k += n
        for j, (disp, n) in enumerate(chunks):
            st = max(a - .05, starts[j]); en = starts[j + 1] if j + 1 < len(chunks) else b + .15
            subs.append((st, en, disp))
    return subs
SUBS = build_subs()

def draw_sub(cv, t):
    for st, en, disp in SUBS:
        if st <= t < en:
            k = eo(prog(t, st, st + .12))
            parts = []; hi = False
            for seg in disp.split("*"):
                if seg: parts.append((seg, (GD if "%" in seg or any(ch.isdigit() for ch in seg) else OR) if hi else WH))
                hi = not hi
            y = 1420 + (1 - k) * 14
            f = skia.Font(TF_BODY, 64); tw = sum(f.measureText(s) for s, _ in parts)
            rrect(cv, W / 2 - tw / 2 - 30, y - 70, tw + 60, 96, 24, P("#0B0F19", int(205 * k)))
            rich(cv, parts, W / 2, y, TF_BODY, 64, int(255 * k), stroke=0)
            return

def watermark(cv, t):
    if t < TOTAL - 1.4:
        text(cv, "IMPÉRIO DE IDEIAS", W / 2, 190, TF_TITLE, 34, WH, 120, shadow=False)

def frame(cv, t):
    cv.clear(C(BG))
    for idx, (fn, s, e) in enumerate(SCENES):
        if s - XF <= t < e:
            if t < s:  # incoming during previous scene's tail -> skip, handled below
                continue
            # camera push
            u = prog(t, s, e)
            cv.save(); z = 1.0 + .05 * u
            cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-W / 2 + math.sin(t * .7) * 6, -H / 2)
            fn(cv, t); cv.restore()
            # transition into next scene
            if idx + 1 < len(SCENES) and t >= e - XF:
                nfn, ns, ne = SCENES[idx + 1]
                k = eio(prog(t, e - XF, e))
                cv.save(); cv.clipRect(skia.Rect.MakeXYWH(0, 0, W * k, H))
                cv.save(); cv.translate(W / 2, H / 2); cv.translate(-W / 2, -H / 2); nfn(cv, max(t, ns)); cv.restore()
                cv.restore()
                cv.drawRect(skia.Rect.MakeXYWH(W * k - 14, 0, 28, H), glow(OR, int(200 * math.sin(k * math.pi)), 18))
            break
    post(cv, t)
    watermark(cv, t)
    draw_sub(cv, t)

def render(out, t0=0, t1=None, step=1):
    t1 = TOTAL if t1 is None else t1
    surf = skia.Surface(W, H)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out + ".tmp.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for n in range(n0, n1, step):
        with surf as cv: frame(cv, n / FPS)
        pr.stdin.write(surf.makeImageSnapshot().tobytes())
    pr.stdin.close(); assert pr.wait() == 0
    os.replace(out + ".tmp.mp4", out)

def still(t, out):
    surf = skia.Surface(W, H)
    with surf as cv: frame(cv, t)
    surf.makeImageSnapshot().save(out, skia.kJPEG, 88)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for t in sys.argv[2:]: still(float(t), f"still_{float(t):05.2f}.jpg")
    elif mode == "seg":
        render(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    elif mode == "subs":
        for s in SUBS: print(f"{s[0]:6.2f} {s[1]:6.2f} {s[2]}")
