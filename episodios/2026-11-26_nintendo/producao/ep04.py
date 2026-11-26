# Império de Ideias — EP04 Nintendo — estilo PREMIUM (estética documental / editorial)
import sys, os, json, math, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R
from render import (skia, np, W, H, FPS, C, P, rrect, lin, rad, glow, path, cl, lerp, eo, eio, back, prog, GRAINS)

FD = os.path.join(HERE, "fonts")
TF_B = skia.Typeface.MakeFromFile(os.path.join(FD, "BebasNeue-Regular.ttf"))
TF_SB = skia.Typeface.MakeFromFile(os.path.join(FD, "Montserrat-SemiBold.ttf"))
TF_MD = skia.Typeface.MakeFromFile(os.path.join(FD, "Montserrat-Medium.ttf"))
TF_XB = skia.Typeface.MakeFromFile(os.path.join(FD, "Montserrat-ExtraBold.ttf"))

BG0, BG1 = "#07090F", "#0E1320"
GD, OR, WH, EB = "#FBBF24", "#FF6B35", "#F9FAFB", "#3B82F6"
MUT, LINE, PAPER, INK = "#9CA3AF", "#263042", "#ECE6D8", "#1B1F27"

TIM = json.load(open(os.path.join(HERE, "timing.json")))
L = {l["i"]: (l["start"], l["end"]) for l in TIM["lines"]}
TOTAL = TIM["total"]
WORDS = json.load(open(os.path.join(HERE, "words.json")))

def wt(word, after):
    for w in WORDS:
        if w[0] >= after - .05 and word.lower() in w[2].lower(): return w[0]
    return after

# ---------- tipografia ----------
def tw(s, tf, size, track=0):
    f = skia.Font(tf, size); return f.measureText(s) + track * max(0, len(s) - 1)
def txt(cv, s, x, y, tf, size, color, a=255, align="c", track=0, shadow=True):
    f = skia.Font(tf, size); f.setEdging(skia.Font.Edging.kAntiAlias)
    w = tw(s, tf, size, track)
    xx = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    def draw(px, py, paint):
        if track == 0: cv.drawString(s, px, py, f, paint); return
        cx = px
        for ch in s:
            cv.drawString(ch, cx, py, f, paint); cx += f.measureText(ch) + track
    if shadow:
        sp = P("#000000", int(a * .6)); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * .08))
        draw(xx, y + size * .04, sp)
    draw(xx, y, P(color, a))
    return w
def rich(cv, parts, x, y, tf, size, a=255, track=0):
    tot = sum(tw(s, tf, size, track) for s, _ in parts) + track * (len(parts) - 1) * 0
    xx = x - tot / 2
    for s, col in parts:
        txt(cv, s, xx, y, tf, size, col, a, align="l", track=track); xx += tw(s, tf, size, track)
def reveal_txt(cv, s, x, y, tf, size, color, p, track=0):
    """revela letra a letra com leve subida"""
    n = len(s); f = skia.Font(tf, size); w = tw(s, tf, size, track); cx = x - w / 2
    for i, ch in enumerate(s):
        k = eo(cl(p * n * 1.0 - i * .9, 0, 1))
        if k > 0: txt(cv, ch, cx, y + (1 - k) * 18, tf, size, color, int(255 * k), align="l")
        cx += f.measureText(ch) + track

# ---------- traços progressivos ----------
def plen(pa):
    m = skia.PathMeasure(pa, False, 1); tot = 0
    while True:
        tot += m.getLength()
        if not m.nextContour(): break
    return max(tot, 1)
def stroke(cv, paths, p, color, width=3, a=255, glow_a=0):
    lens = [plen(x) for x in paths]; T = sum(lens); done = p * T
    for pa, ln in zip(paths, lens):
        q = cl(done / ln); done -= ln
        if q <= 0: break
        pt = P(color, a, stroke=width)
        if q < 1: pt.setPathEffect(skia.DashPathEffect.Make([ln * q, ln + 1], 0))
        if glow_a:
            g = P(color, glow_a, stroke=width * 3); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
            if q < 1: g.setPathEffect(skia.DashPathEffect.Make([ln * q, ln + 1], 0))
            cv.drawPath(pa, g)
        cv.drawPath(pa, pt)
def RR(x, y, w, h, r):
    pa = skia.Path(); pa.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return pa
def CIR(x, y, r):
    pa = skia.Path(); pa.addCircle(x, y, r); return pa
def LN(*pts): return path(pts, close=False)

# ---------- ilustrações em linha (estilo técnico) ----------
def camera_paths():
    ps = [RR(-260, -150, 380, 300, 18), RR(-210, -215, 250, 60, 8)]
    for k in range(9): ps.append(LN((-195 + k * 26, -215), (-195 + k * 26, -235)))
    ps += [CIR(-150, 40, 80), CIR(-150, 40, 58), CIR(-150, 40, 26)]
    for k in range(5): ps.append(LN((-40, -110 + k * 22), (90, -110 + k * 22)))
    ps += [RR(140, -130, 170, 260, 12), RR(160, -95, 130, 80, 8), CIR(195, -55, 20), CIR(255, -55, 20), CIR(260, 80, 9)]
    return ps
CAM = camera_paths()
def camera_art(cv, x, y, s, p, color=GD, width=3, glitch=0.0, t=0.0, glow_a=60):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if glitch > 0:
        j = random.Random(int(t * 30))
        for col, dx in ((EB, -10), (OR, 10)):
            cv.save(); cv.translate(dx * glitch + j.uniform(-6, 6) * glitch, j.uniform(-4, 4) * glitch)
            stroke(cv, CAM, p, col, width / s, int(170 * glitch)); cv.restore()
    stroke(cv, CAM, p, color, width / s, 255, glow_a)
    # bobinas girando
    if p >= 1:
        for cx in (195, 255):
            cv.save(); cv.translate(cx, -55); cv.rotate(t * 200)
            for k in range(3): cv.rotate(120); cv.drawLine(0, 0, 0, -16, P(color, 255, stroke=width / s))
            cv.restore()
    cv.restore()

def film_paths():
    return [RR(-90, -130, 180, 260, 16), RR(-105, -150, 210, 30, 8), RR(-105, 120, 210, 30, 8), RR(-30, -175, 60, 25, 6),
            LN((90, 60), (190, 60), (190, 110), (90, 110))] + [RR(100 + k * 18, 70, 8, 8, 2) for k in range(5)]
FILM = film_paths()
def film_art(cv, x, y, s, p, color=GD, width=3, a=255, glow_a=50):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, FILM, p, color, width / s, a, glow_a); cv.restore()

def phone_art(cv, x, y, s, p, color=EB, a=255):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    stroke(cv, [RR(-45, -90, 90, 180, 14), LN((-15, -78), (15, -78)), CIR(0, 0, 18)], p, color, 3 / s, a, 40); cv.restore()

# ---------- cenário base ----------
def background(cv, t, tint="#0E1320", grid=False, grid_col="#16233A"):
    cv.drawRect(skia.Rect.MakeWH(W, H), lin(0, 0, 0, H, [BG0, tint, BG0], [0, .5, 1]))
    if grid:
        for x in range(0, W + 1, 60): cv.drawLine(x, 0, x, H, P(grid_col, 120, stroke=1))
        for y in range(0, H + 1, 60): cv.drawLine(0, y, W, y, P(grid_col, 120, stroke=1))
    # luz ambiente que respira
    cx = W * (.5 + .25 * math.sin(t * .23)); cy = H * (.42 + .05 * math.cos(t * .31))
    cv.drawCircle(cx, cy, 900, rad(cx, cy, 900, [(GD, 20), (GD, 0)]))

def finish(cv, t):
    g = GRAINS[int(t * FPS) % len(GRAINS)]
    p = skia.Paint(); p.setAlphaf(.075); p.setBlendMode(skia.BlendMode.kOverlay)
    cv.drawImageRect(g, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H * .45, H * .72, [("#000000", 0), ("#000000", 0), ("#000000", 190)], [0, .5, 1]))

CHAPTERS = [(1, 2, "PRÓLOGO", "1975 — 2012"), (3, 6, "01  A INVENÇÃO", "1975"), (7, 8, "02  A REUNIÃO", "1975"),
            (9, 10, "03  A APOSTA", "1978"), (11, 13, "04  O DESFECHO", "2012")]
def chrome(cv, t):
    if t > TOTAL - 1.6: return
    # barra de progresso (retenção)
    rrect(cv, 80, 236, W - 160, 4, 2, P(WH, 40)); rrect(cv, 80, 236, (W - 160) * cl(t / (TOTAL - 1.6)), 4, 2, P(GD))
    txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 200, TF_SB, 24, WH, 150, track=6, shadow=False)
    for a_, b_, name, yr in CHAPTERS:
        if L[a_][0] - .15 <= t < (L[b_ + 1][0] - .15 if b_ + 1 in L else TOTAL):
            k = eo(prog(t, L[a_][0] - .15, L[a_][0] + .3))
            txt(cv, name, 80, 290, TF_SB, 24, GD, int(255 * k), align="l", track=5, shadow=False)
            txt(cv, yr, W - 80, 290, TF_SB, 24, MUT, int(255 * k), align="r", track=5, shadow=False)

def kicker(cv, s, y, a=255, col=GD):
    w = tw(s, TF_SB, 26, 6)
    cv.drawLine(W / 2 - w / 2 - 70, y - 9, W / 2 - w / 2 - 20, y - 9, P(col, a, stroke=2))
    cv.drawLine(W / 2 + w / 2 + 20, y - 9, W / 2 + w / 2 + 70, y - 9, P(col, a, stroke=2))
    txt(cv, s, W / 2, y, TF_SB, 26, col, a, track=6, shadow=False)

def card(cv, x, y, w, h, a=255, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    sh = P("#000000", int(a * .55)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    rrect(cv, -w / 2 + 10, -h / 2 + 24, w, h, 6, sh)
    rrect(cv, -w / 2, -h / 2, w, h, 6, lin(0, -h / 2, 0, h / 2, [(PAPER, a), ("#DED6C4", a)]))
    return cv  # caller must restore



# ======================= EP04 — NINTENDO =======================
CHAPTERS = [(1, 2, "PRÓLOGO", "1889 — 1981"), (3, 5, "01  AS CARTAS", "1889 — 1959"), (6, 7, "02  AS APOSTAS", "ANOS 60"),
            (8, 11, "03  A VIRADA", "1965 — 1966"), (12, 14, "04  O FUTURO", "1980 — 1981")]
RED = "#DC2626"

def lerp_col(c1, c2, u):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02X}" for x, y in zip(a, b))

# ---------- ilustrações em traço técnico ----------
def hanafuda_paths(motif=0):
    ps = [RR(-110, -170, 220, 340, 14), RR(-96, -156, 192, 312, 8)]
    if motif == 0:   # lua sobre colina
        ps += [CIR(0, -40, 62), LN((-96, 90), (-40, 30), (10, 70), (60, 20), (96, 60))]
        for k in range(4): ps.append(LN((-80 + k * 50, 156), (-60 + k * 50, 110)))
    elif motif == 1:  # flor de cerejeira
        for k in range(5):
            ang = math.radians(k * 72 - 90); ps.append(CIR(46 * math.cos(ang), -30 + 46 * math.sin(ang), 30))
        ps += [CIR(0, -30, 12), LN((0, 20), (-20, 150)), LN((-10, 90), (50, 120))]
    else:             # pássaro / grou estilizado
        ps += [LN((-70, 40), (0, -60), (70, 40)), LN((0, -60), (10, -110), (34, -118)), CIR(0, 80, 40), LN((-96, 130), (96, 130))]
    return ps
HANA = [hanafuda_paths(k) for k in range(3)]
def hanafuda(cv, x, y, s, p, motif=0, color=GD, rot=0, a=255, glow_a=50, fill=None):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    if fill is not None and p > .2: cv.drawPath(HANA[motif][0], P(fill, int(a * cl((p - .2) * 2))))
    stroke(cv, HANA[motif], p, color, 3 / s, a, glow_a); cv.restore()

def taxi_paths():
    ps = [RR(-180, -20, 360, 90, 18), path([(-110, -20), (-70, -95), (70, -95), (110, -20)], close=True),
          LN((0, -95), (0, -20)), CIR(-105, 75, 36), CIR(105, 75, 36), CIR(-105, 75, 14), CIR(105, 75, 14), RR(-40, -135, 80, 36, 6)]
    return ps
TAXI = taxi_paths()
def bowl_paths():
    pa = skia.Path(); pa.moveTo(-150, -10); pa.cubicTo(-140, 120, 140, 120, 150, -10); pa.close()
    ps = [pa, RR(-60, 100, 120, 22, 8)]
    for k in range(3):
        sp = skia.Path(); x0 = -50 + k * 50; sp.moveTo(x0, -40); sp.cubicTo(x0 - 25, -80, x0 + 25, -110, x0, -150); ps.append(sp)
    ps += [LN((60, -150), (190, -40)), LN((90, -160), (205, -55))]
    return ps
BOWL = bowl_paths()
def icon(cv, ps, x, y, s, p, color=GD, a=255, glow_a=40):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, ps, p, color, 3 / s, a, glow_a); cv.restore()

def gear_path(r=120, teeth=12, d=24):
    pts = []
    for k in range(teeth * 4):
        ang = 2 * math.pi * k / (teeth * 4); rr = r + (d if (k % 4) in (1, 2) else 0)
        pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    return [path(pts), CIR(0, 0, r * .35), CIR(0, 0, r * .7)]
GEAR = gear_path(); GEAR_S = gear_path(70, 9, 18)
def gear(cv, x, y, s, p, rot, color=GD, a=255, small=False, glow_a=40):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    stroke(cv, GEAR_S if small else GEAR, p, color, 3 / s, a, glow_a); cv.restore()

def tongs(cv, x, y, s, ext, p=1.0, color=GD, a=255, grab=0.0, glow_a=60):
    """braço extensível (pantógrafo) genérico; ext 0..1"""
    n = 5; l = 70; th = math.radians(62 - 50 * ext); dx = l * math.cos(th); dy = l * math.sin(th)
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    ps = []
    for k in range(n):
        ps.append(LN((k * dx, -dy), ((k + 1) * dx, dy))); ps.append(LN((k * dx, dy), ((k + 1) * dx, -dy)))
    ps += [LN((0, -dy), (-60, -dy - 30), (-110, -dy - 30)), LN((0, dy), (-60, dy + 30), (-110, dy + 30)),
           CIR(-120, -dy - 30, 14), CIR(-120, dy + 30, 14)]
    ex = n * dx; op = 34 * (1 - grab) + 12
    c1 = skia.Path(); c1.moveTo(ex, -dy); c1.cubicTo(ex + 40, -dy - 10, ex + 70, -op, ex + 70, -8)
    c2 = skia.Path(); c2.moveTo(ex, dy); c2.cubicTo(ex + 40, dy + 10, ex + 70, op, ex + 70, 8)
    ps += [c1, c2]
    stroke(cv, ps, p, color, 4 / s, a, glow_a)
    if p >= 1:
        for k in range(n + 1):
            for sy in (-1, 1): cv.drawCircle(k * dx, sy * dy, 6 / s * 1.4, P(color, a))
    cv.restore()
    return x + (ex + 70) * s

def handheld(cv, x, y, s, p, color=EB, a=255, glow_a=50, t=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    ps = [RR(-230, -130, 460, 260, 26), RR(-120, -95, 240, 160, 10), LN((-185, -20), (-185, 40)), LN((-215, 10), (-155, 10)),
          CIR(175, -5, 18), CIR(195, 40, 18), LN((-60, 100), (-20, 100)), LN((20, 100), (60, 100))]
    stroke(cv, ps, p, color, 3 / s, a, glow_a)
    if p >= 1:  # pixel piscando na tela (genérico)
        if int(t * 4) % 2 == 0: cv.drawRect(skia.Rect.MakeXYWH(-30, -30, 24, 24), P(color, a))
        cv.drawRect(skia.Rect.MakeXYWH(20, 10, 24, 24), P(color, int(a * .6)))
    cv.restore()

def xmark(cv, x, y, sz, q, col=OR):
    if q <= 0: return
    stroke(cv, [LN((x - sz, y - sz), (x + sz, y + sz)), LN((x + sz, y - sz), (x - sz, y + sz))], q, col, 10, 255, 120)

def redacted_who(cv, t, y, k, reveal=0.0):
    if k <= 0: return
    cv.save(); cv.translate(0, (1 - k) * 60)
    card(cv, W / 2, y, 860, 400, int(255 * cl(k)), rot=-1.5)
    al = int(255 * cl(k))
    txt(cv, "ARQUIVO NINTENDO  ·  KYOTO, ANOS 60", -390, -140, TF_SB, 21, "#6B6455", al, align="l", track=3, shadow=False)
    cv.drawLine(-390, -118, 390, -118, P("#B8AE98", al, stroke=2))
    txt(cv, "QUEM SALVOU A NINTENDO:", -390, -62, TF_XB, 28, INK, al, align="l", track=1, shadow=False)
    if reveal > 0:
        txt(cv, "GUNPEI YOKOI", -390, 40, TF_B, 120, INK, al, align="l", shadow=False)
        k2 = eo(cl(reveal * 2 - 1))
        txt(cv, "O HOMEM DA MANUTENÇÃO", -390, 115, TF_B, 62, OR, int(al * k2), align="l", track=2, shadow=False)
    for j, (x0, w0, y0, h0) in enumerate(((-390, 640, -32, 95), (-390, 740, 68, 66))):
        r = cl(reveal * 1.6 - j * .5); ww = w0 * (1 - eio(r))
        if ww > 1:
            rrect(cv, x0 + w0 - ww, y0, ww, h0, 4, P("#0B0D12", al))
            if 0 < r < 1: cv.drawRect(skia.Rect.MakeXYWH(x0 + w0 - ww - 6, y0, 12, h0), glow(OR, 230, 10))
    txt(cv, "CONFIDENCIAL ATÉ A VIRADA" if reveal <= 0 else "REVELADO", 390, 175, TF_SB, 18, "#8A8272", al, align="r", track=4, shadow=False)
    cv.restore(); cv.restore()

def brand(cv, y, a=255, size=230, col=GD):
    txt(cv, "NINTENDO", W / 2, y, TF_B, size, col, a, track=12)

# ---------- cenas ----------
def s_hook(cv, t):
    a, b = L[1]; te = wt("errou", a + 2)
    background(cv, t, "#14110A")
    kicker(cv, "ANTES DO MARIO", 400, 255)
    brand(cv, 590, 255, 240)
    # leque de cartas hanafuda (desenhando-se, já visíveis no 1º quadro)
    p = eio(prog(t, 0, 1.3)) * .65 + .35
    for j, (dx, rot, m) in enumerate(((-200, -14, 1), (0, 0, 0), (200, 14, 2))):
        hanafuda(cv, W / 2 + dx, 900 + abs(dx) * .12, .78, p, m, GD if j == 1 else "#D6B98C", rot=rot, glow_a=60)
    cv.save(); cv.translate(W / 2, 1185); cv.rotate(-5)
    rrect(cv, -420, -72, 840, 132, 10, P("#0B0D12", 220)); rrect(cv, -420, -72, 840, 132, 10, P(OR, 255, stroke=6))
    txt(cv, "VENDIA BARALHO", 0, 32, TF_B, 112, OR, 255, track=5); cv.restore()
    q = eo(prog(t, te - .1, te + .3))
    txt(cv, "E ERROU FEIO TENTANDO MUDAR", W / 2, 1320, TF_SB, 30, WH, int(255 * q), track=4, shadow=False)

def s_teaser(cv, t):
    a, b = L[2]; tn = wt("ninguém", a)
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .4)); txt(cv, "A SALVAÇÃO VEIO", W / 2, 430, TF_B, 96, MUT, int(255 * k), track=4)
    txt(cv, "DE QUEM NINGUÉM", W / 2, 545, TF_B, 116, WH, int(255 * eo(prog(t, tn - .2, tn + .2))), track=3)
    redacted_who(cv, t, 880, back(prog(t, a + .4, a + 1.0)))
    kicker(cv, "ESPERAVA", 1210, int(255 * eo(prog(t, wt("esperava", a) - .1, wt("esperava", a) + .3))), OR)

def s_1889(cv, t):
    a, b = L[3]; tf = wt("Fusajiro", a + 1); th = wt("hanafuda", tf)
    background(cv, t, "#0B1A2E", grid=True)
    kicker(cv, "KYOTO  ·  JAPÃO", 410, int(255 * eo(prog(t, a, a + .4))))
    p = eio(prog(t, a + .1, a + 2.2)); yr = int(round(1800 + 89 * p))
    txt(cv, str(yr), W / 2, 680, TF_B, 280, GD if p >= 1 else WH, int(255 * eo(prog(t, a, a + .3))), track=8)
    q = eo(prog(t, tf - .1, tf + .3))
    txt(cv, "FUSAJIRO YAMAUCHI", W / 2, 780, TF_B, 80, WH, int(255 * q), track=5)
    ph = eio(prog(t, th - .5, th + 1.2))
    for j, (dx, m) in enumerate(((-240, 1), (0, 0), (240, 2))):
        hanafuda(cv, W / 2 + dx, 1060, .55, cl(ph * 1.4 - j * .2), m, GD, rot=(j - 1) * 6, glow_a=50)
    txt(cv, "HANAFUDA  ·  CARTAS DE FLORES", W / 2, 1265, TF_SB, 26, "#D6B98C", int(255 * eo(prog(t, th, th + .4))), track=4, shadow=False)

def s_1949(cv, t):
    a, b = L[4]; th = wt("Hiroshi", a); tv = wt("vinte", th)
    background(cv, t)
    k = eo(prog(t, a, a + .3)); txt(cv, "1949", W / 2, 560, TF_B, 260, WH, int(255 * k), track=8)
    txt(cv, "O NETO ASSUME", W / 2, 650, TF_SB, 30, GD, int(255 * eo(prog(t, a + .4, a + .8))), track=6, shadow=False)
    q = back(prog(t, th - .2, th + .3))
    if q > 0:
        cv.save(); cv.translate(W / 2, 860); s_ = cl(q, 0, 1.12); cv.scale(s_, s_)
        txt(cv, "HIROSHI YAMAUCHI", 0, 0, TF_B, 120, WH, 255, track=5); cv.restore()
    qq = eo(prog(t, tv - .2, tv + .1)); n = int(round(22 * eio(prog(t, tv - .2, tv + .6))))
    if qq > 0:
        txt(cv, f"{n}", W / 2, 1150, TF_B, 260, GD, int(255 * qq), track=6)
        txt(cv, "ANOS DE IDADE", W / 2, 1240, TF_B, 64, WH, int(255 * qq), track=6)

def s_1959(cv, t):
    a, b = L[5]; td = wt("Disney", a)
    background(cv, t, "#120F1F")
    k = eo(prog(t, a, a + .3)); txt(cv, "1959", W / 2, 520, TF_B, 220, WH, int(255 * k), track=8)
    kicker(cv, "LICENCIAMENTO", 600, int(255 * eo(prog(t, a + .3, a + .7))))
    p = eio(prog(t, a + .2, td + .3))
    hanafuda(cv, W / 2 - 230, 930, .62, p, 0, "#D6B98C", rot=-8, glow_a=30)
    q = back(prog(t, td - .25, td + .25))
    if q > 0:
        cv.save(); cv.translate(W / 2 + 120, 920); cv.rotate(6); s_ = cl(q, 0, 1.1); cv.scale(s_, s_)
        rrect(cv, -150, -220, 300, 440, 18, P("#0B0D12", 230)); rrect(cv, -150, -220, 300, 440, 18, P(GD, 255, stroke=5))
        rrect(cv, -128, -198, 256, 396, 10, P(GD, 120, stroke=2))
        txt(cv, "DISNEY", 0, 30, TF_B, 110, GD, 255, track=6); cv.restore()
    txt(cv, "PERSONAGENS NAS CARTAS", W / 2, 1265, TF_B, 72, WH, int(255 * eo(prog(t, td + .2, td + .6))), track=4)

def bets(cv, t, a, appear, fail=None):
    items = [(TAXI, "TÁXI", W / 2 - 290, 900, .62), (BOWL, "ARROZ INSTANTÂNEO", W / 2 + 230, 900, .62)]
    for j, (ps, lab, x, y, s) in enumerate(items):
        q = appear[j]
        if q <= 0: continue
        dim = fail[j] if fail else 0
        col = lerp_col(GD, "#4B5563", dim)
        icon(cv, ps, x, y, s, q, col, glow_a=int(40 * (1 - dim)))
        txt(cv, lab, x, y + 150, TF_B, 52, lerp_col(WH, MUT, dim), int(255 * eo(q)), track=3)
        if fail: xmark(cv, x, y, 110, fail[j])

def s_bets(cv, t):
    a, b = L[6]; tt = wt("táxi", a); ta = wt("arroz", tt)
    background(cv, t, "#0E1320")
    k = eo(prog(t, a, a + .3)); txt(cv, "DEPOIS, APOSTA", W / 2, 450, TF_B, 110, WH, int(255 * k), track=5)
    txt(cv, "EM TUDO", W / 2, 570, TF_B, 130, GD, int(255 * eo(prog(t, wt("tudo", a) - .1, wt("tudo", a) + .3))), track=6)
    kicker(cv, "ANOS 60  ·  DIVERSIFICAÇÃO", 650, int(255 * eo(prog(t, a + .5, a + .9))))
    bets(cv, t, a, [eio(prog(t, tt - .2, tt + .9)), eio(prog(t, ta - .2, ta + .9))])

def s_fail(cv, t):
    a, b = L[7]; tf = wt("fracassa", a); ts = wt("sessenta", tf); td = wt("despenca", ts)
    background(cv, t, "#120C0C")
    k = eo(prog(t, a, a + .3)); txt(cv, "QUASE TUDO", W / 2, 450, TF_B, 110, WH, int(255 * k), track=5)
    txt(cv, "FRACASSA", W / 2, 570, TF_B, 130, OR, int(255 * eo(prog(t, tf - .1, tf + .3))), track=6)
    u = eio(prog(t, ts - .3, ts + .3))
    cv.save(); cv.translate(0, -60 * u);
    a_ = int(255 * (1 - u))
    if a_ > 5:
        lay = skia.Paint(); lay.setAlphaf(1 - u); cv.saveLayer(None, lay)
        bets(cv, t, a, [1, 1], [eo(prog(t, tf - .2, tf + .2)), eo(prog(t, tf + .05, tf + .45))]); cv.restore()
    cv.restore()
    if u > 0:
        txt(cv, "1964", W / 2, 760, TF_B, 140, WH, int(255 * u), track=8)
        p = eio(prog(t, td - .4, td + .7))
        pts = [(150, 830), (330, 860), (470, 845), (620, 960), (760, 1010), (930, 1160)]
        for j in range(4): cv.drawLine(150, 850 + j * 100, 930, 850 + j * 100, P(LINE, int(160 * u), stroke=1))
        hanafuda(cv, 150, 830, .22, u, 0, "#D6B98C", glow_a=0)
        stroke(cv, [path(pts, close=False)], p, OR, 8, 255, 120)
        if p >= 1:
            cv.save(); cv.translate(930, 1160); cv.rotate(math.degrees(math.atan2(150, 170)))
            cv.drawPath(path([(10, 0), (-30, -22), (-30, 22)]), P(OR)); cv.restore()
        txt(cv, "MERCADO DE BARALHO EM QUEDA", W / 2, 1270, TF_B, 66, WH, int(255 * eo(prog(t, td - .1, td + .3))), track=4)

def s_tension(cv, t):
    a, b = L[8]
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#040508"))
    hb = max(0, math.sin((t - a) * 2 * math.pi * 1.2)) ** 10
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, H * .7, [("#000000", 0), ("#3A0A00", int(140 * hb))]))
    gear(cv, W / 2, 950, 1.6, 1.0, t * 8, "#1F2937", glow_a=0)
    reveal_txt(cv, "E AQUI", W / 2, 880, TF_B, 140, WH, prog(t, a, a + .5), track=6)
    reveal_txt(cv, "A HISTÓRIA VIRA", W / 2, 1020, TF_B, 130, OR, prog(t, a + .6, a + 1.4), track=4)

def s_yokoi(cv, t):
    a, b = L[9]; tg = wt("Gunpei", a); tm = wt("máquinas", tg)
    background(cv, t, "#0B1A2E", grid=True)
    kicker(cv, "1965  ·  FÁBRICA DE CARTAS", 400, int(255 * eo(prog(t, a, a + .4))))
    redacted_who(cv, t, 700, 1.0, reveal=prog(t, tg - .1, tg + 1.2))
    q = eio(prog(t, tm - .5, tm + .6))
    gear(cv, W / 2 - 110, 1090, .9, q, t * 40, GD); gear(cv, W / 2 + 95, 1050, .9, q, -t * 55 + 20, GD, small=True)
    txt(cv, "CUIDAVA DAS MÁQUINAS", W / 2, 1270, TF_B, 70, WH, int(255 * eo(prog(t, tm - .1, tm + .3))), track=4)

def s_arm(cv, t):
    a, b = L[10]; tb = wt("braço", a); tp = wt("presidente", tb); tf = wt("fabricar", tp)
    background(cv, t, "#0B1A2E", grid=True)
    k = eo(prog(t, a, a + .3)); txt(cv, "NAS HORAS VAGAS", W / 2, 440, TF_B, 100, MUT, int(255 * k), track=5)
    q = eo(prog(t, tb - .2, tb + .3))
    txt(cv, "UM BRAÇO EXTENSÍVEL", W / 2, 560, TF_B, 110, WH, int(255 * q), track=4)
    p = eio(prog(t, a + .2, tb + .6)); ext = .5 + .5 * math.sin((t - tb) * 2.2) if t > tb + .6 else 0
    ext = eio(prog(t, tb + .3, tb + 1.2)) * (.75 + .25 * math.sin((t - tb) * 3))
    tongs(cv, 230, 930, 1.35, ext, p, GD)
    qs = back(prog(t, tp - .2, tp + .25))
    if qs > 0:
        cv.save(); cv.translate(W / 2, 1220); cv.rotate(-5); s_ = 1 + .5 * (1 - cl(qs)); cv.scale(s_, s_)
        ka = cl(qs * 3)
        rrect(cv, -380, -70, 760, 124, 10, P("#0B0D12", int(220 * ka))); rrect(cv, -380, -70, 760, 124, 10, P(GD, int(255 * ka), stroke=6))
        txt(cv, "MANDA FABRICAR", 0, 28, TF_B, 100, GD, int(255 * cl(qs * 3)), track=6); cv.restore()

def s_ultra(cv, t):
    a, b = L[11]; tu = wt("Ultra", a); tn = wt("Nintendo", tu); tbq = wt("brinquedos", tn)
    background(cv, t, "#14110A")
    q = back(prog(t, tu - .2, tu + .25))
    if q > 0:
        cv.save(); cv.translate(W / 2, 520); s_ = cl(q, 0, 1.12); cv.scale(s_, s_)
        txt(cv, "ULTRA HAND", 0, 0, TF_B, 190, GD, 255, track=8); cv.restore()
        txt(cv, "1966", W / 2, 610, TF_SB, 36, WH, int(255 * cl(q)), track=10, shadow=False)
    g = eio(prog(t, a + 1.0, a + 1.8))
    ext = eio(prog(t, a, a + 1.0))
    tip = tongs(cv, 230, 880, 1.3, ext, 1.0, GD, grab=g)
    bx = tip - 20 + 0
    cv.drawCircle(bx, 880, 40, P(OR, 255)); cv.drawCircle(bx, 880, 40, P(WH, 120, stroke=3))
    qb = eo(prog(t, tn - .2, tn + .3))
    txt(cv, "A NINTENDO VIRA", W / 2, 1130, TF_B, 84, MUT, int(255 * qb), track=4)
    txt(cv, "FÁBRICA DE BRINQUEDOS", W / 2, 1250, TF_B, 100, WH, int(255 * eo(prog(t, tbq - .3, tbq + .1))), track=4)

def s_future(cv, t):
    a, b = L[12]; tg = wt("Game", a); to = wt("oitenta", tg); td = wt("Donkey", to); tm = wt("Mario", td)
    background(cv, t)
    y = 430; x0, x1 = 120, W - 120; p = eio(prog(t, a, a + 1.0))
    cv.drawLine(x0, y, x0 + (x1 - x0) * p, y, P(WH, 200, stroke=3))
    for lab, fx, col, tt in (("1889", 0, MUT, a), ("1966", .45, GD, a), ("1980", .8, EB, tg), ("1981", 1, OR, to)):
        if p >= fx - .001 and t >= tt - .1:
            xx = x0 + (x1 - x0) * fx; cv.drawCircle(xx, y, 12, P(col)); cv.drawCircle(xx, y, 26, P(col, 120, stroke=2))
            txt(cv, lab, xx, y - 48, TF_B, 52, col, 255, track=2)
    qg = eio(prog(t, tg - .2, tg + 1.0))
    handheld(cv, W / 2, 760, .9, qg, EB, t=t)
    txt(cv, "GAME & WATCH", W / 2, 960, TF_B, 100, WH, int(255 * eo(prog(t, tg - .1, tg + .3))), track=5)
    txt(cv, "CRIADO POR YOKOI  ·  1980", W / 2, 1015, TF_SB, 26, EB, int(255 * eo(prog(t, tg + .2, tg + .6))), track=4, shadow=False)
    qd = back(prog(t, td - .2, td + .3))
    if qd > 0:
        cv.save(); cv.translate(W / 2, 1180); s_ = cl(qd, 0, 1.1); cv.scale(s_, s_)
        txt(cv, "DONKEY KONG  ·  1981", 0, 0, TF_B, 96, GD, 255, track=4); cv.restore()
    txt(cv, "ESTREIA O FUTURO MARIO", W / 2, 1270, TF_B, 64, OR, int(255 * eo(prog(t, tm - .3, tm + .1))), track=4)

def s_reflect(cv, t):
    a, b = L[13]; tn = wt("nasceu", a + 1)
    background(cv, t, "#14110A")
    k = eo(prog(t, a, a + .4)); txt(cv, "A IDEIA QUE SALVOU", W / 2, 470, TF_B, 110, WH, int(255 * k), track=5)
    txt(cv, "A NINTENDO", W / 2, 600, TF_B, 140, GD, int(255 * eo(prog(t, a + .4, a + .8))), track=6)
    u = eio(prog(t, tn - .4, tn + .6))
    gear(cv, W / 2 - 120, 930, 1.0, 1.0, t * 30, lerp_col(MUT, GD, u), glow_a=int(80 * u))
    gear(cv, W / 2 + 105, 890, 1.0, 1.0, -t * 42 + 20, lerp_col(MUT, GD, u), small=True, glow_a=int(80 * u))
    q = eo(prog(t, tn - .1, tn + .3))
    txt(cv, "NASCEU NO", W / 2, 1180, TF_B, 96, MUT, int(255 * q), track=5)
    txt(cv, "CHÃO DA FÁBRICA.", W / 2, 1290, TF_B, 110, GD, int(255 * eo(prog(t, tn + .4, tn + .8))), track=5)

def s_end(cv, t):
    a, b = L[14]; tv = wt("Qual", a)
    background(cv, t)
    for i_, (s, col) in enumerate((("QUAL EMPRESA", WH), ("MUDOU MAIS QUE", WH), ("A NINTENDO?", GD))):
        q = eo(prog(t, tv - .1 + i_ * .25, tv + .3 + i_ * .25))
        txt(cv, s, W / 2, 720 + i_ * 160 + (1 - q) * 20, TF_B, 140, col, int(255 * q), track=4)
    hanafuda(cv, W / 2, 1140, .3, eio(prog(t, a + .4, a + 1.4)), 0, GD, glow_a=40)
    kicker(cv, "CONTA NOS COMENTÁRIOS", 1290, int(255 * eo(prog(t, tv + 1.0, tv + 1.4))))
    kl = eio(prog(t, b + .2, b + .7))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG0, int(255 * kl)))
        cv.drawLine(W / 2 - 200 * kl, 1010, W / 2 + 200 * kl, 1010, P(GD, int(255 * kl), stroke=2))
        txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 980, TF_B, 120, WH, int(255 * kl), track=8)
        txt(cv, "HISTÓRIAS EXTRAORDINÁRIAS POR TRÁS DE GRANDES NEGÓCIOS", W / 2, 1060, TF_SB, 20, MUT, int(255 * kl), track=4, shadow=False)

FNS = [s_hook, s_teaser, s_1889, s_1949, s_1959, s_bets, s_fail, s_tension, s_yokoi, s_arm, s_ultra, s_future, s_reflect, s_end]
SCENES = []
for i_, fn in enumerate(FNS, start=1):
    s0 = 0.0 if i_ == 1 else L[i_][0] - .1
    e0 = TOTAL if i_ == len(FNS) else L[i_ + 1][0] - .1
    SCENES.append((fn, s0, e0))
XF = .3


CHUNKS = {
 1: [("Antes do *Mario*,", 3), ("a *Nintendo* vendia *baralho*.", 4), ("E *errou feio*", 3), ("tentando mudar.", 2)],
 2: [("A *salvação* veio", 3), ("de quem *ninguém esperava*.", 4)],
 3: [("*Kyoto*, *1889*.", 7), ("*Fusajiro Yamauchi*", 2), ("fabrica *hanafuda*,", 2), ("um baralho japonês.", 3)],
 4: [("Em *1949*,", 4), ("assume o neto *Hiroshi*,", 4), ("com *22 anos*.", 5)],
 5: [("Em *1959*,", 4), ("ele põe *personagens*", 3), ("da *Disney* nas cartas.", 4)],
 6: [("Depois, aposta *em tudo*:", 4), ("*táxi*,", 1), ("*arroz instantâneo*.", 2)],
 7: [("Quase tudo *fracassa*.", 3), ("Em *1964*,", 4), ("o baralho *despenca*.", 3)],
 8: [("E aqui a história *vira*.", 5)],
 9: [("Em *1965*,", 4), ("chega *Gunpei Yokoi*,", 3), ("para cuidar das *máquinas*", 4), ("de cartas.", 2)],
 10: [("Nas *horas vagas*,", 3), ("ele monta", 2), ("um *braço extensível*.", 3), ("O *presidente* vê", 3), ("e manda *fabricar*.", 3)],
 11: [("Vira a *Ultra Hand*,", 4), ("em *1966*.", 4), ("E a Nintendo vira", 4), ("fábrica de *brinquedos*.", 3)],
 12: [("Depois, *Yokoi* cria", 3), ("o *Game & Watch*.", 4), ("E em *1981*,", 5), ("*Donkey Kong* estreia", 3), ("o futuro *Mario*.", 3)],
 13: [("A ideia que salvou", 4), ("a *Nintendo*", 2), ("nasceu no *chão da fábrica*.", 5)],
 14: [("E você?", 2), ("Qual *empresa*", 2), ("mudou mais que a *Nintendo*?", 5)],
}
SPOKEN = {l["i"]: l["text"] for l in TIM["lines"]}
R.CHUNKS, R.SPOKEN, R.LINES, R.WORDS = CHUNKS, SPOKEN, L, WORDS
SUBS = R.build_subs()

def draw_sub(cv, t):
    for st, en, disp in SUBS:
        if st <= t < en:
            k = eo(prog(t, st, st + .1))
            parts = []; hi = False
            for seg in disp.split("*"):
                if seg: parts.append((seg, GD if hi else WH))
                hi = not hi
            size = 58; tot = sum(tw(s, TF_SB, size) for s, _ in parts)
            if tot > 940: size = size * 940 / tot
            rich(cv, parts, W / 2, 1450 + (1 - k) * 10, TF_SB, size, int(255 * k))
            return

def frame(cv, t):
    cv.clear(C(BG0))
    for idx, (fn, s, e) in enumerate(SCENES):
        if s <= t < e or (idx == len(SCENES) - 1 and t >= s):
            u = prog(t, s, e)
            cv.save(); z = 1.0 + .04 * u
            cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-W / 2, -H / 2)
            fn(cv, t); cv.restore()
            if idx + 1 < len(SCENES) and t >= e - XF:  # transição: cortina de luz + fade
                nfn = SCENES[idx + 1][0]; k = eio(prog(t, e - XF, e))
                lay = skia.Paint(); lay.setAlphaf(k)
                cv.saveLayer(None, lay); nfn(cv, max(t, SCENES[idx + 1][1])); cv.restore()
                cv.drawRect(skia.Rect.MakeWH(W, H), P(WH, int(28 * math.sin(k * math.pi))))
            break
    # faixa escura para legibilidade das legendas
    cv.drawRect(skia.Rect.MakeXYWH(0, 1300, W, 300), lin(0, 1300, 0, 1600, [("#000000", 0), ("#000000", 150), ("#000000", 0)], [0, .55, 1]))
    finish(cv, t); chrome(cv, t); draw_sub(cv, t)

def render(out, t0, t1):
    surf = skia.Surface(W, H)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out + ".tmp.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        with surf as cv: frame(cv, n / FPS)
        pr.stdin.write(surf.makeImageSnapshot().tobytes())
    pr.stdin.close(); assert pr.wait() == 0
    os.replace(out + ".tmp.mp4", out)

def still(t, out):
    surf = skia.Surface(W, H)
    with surf as cv: frame(cv, t)
    surf.makeImageSnapshot().save(out, skia.kJPEG, 90)


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "still":
        for t in sys.argv[2:]: still(float(t), os.path.join(HERE, f"still_{float(t):05.2f}.jpg"))
    elif m == "seg":
        render(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    elif m == "subs":
        for s in SUBS: print(f"{s[0]:6.2f} {s[1]:6.2f} {s[2]}")
