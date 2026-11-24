# Império de Ideias — EP01 Kodak — versão PREMIUM (estética documental / editorial)
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


# ======================= EP02 — DASSLER: ADIDAS x PUMA =======================
CHAPTERS = [(1, 2, "PRÓLOGO", "1924 — 2009"), (3, 5, "01  A FÁBRICA", "1924"), (6, 8, "02  A RUPTURA", "1948"),
            (9, 11, "03  A CIDADE DIVIDIDA", "HERZOGENAURACH"), (12, 14, "04  O FIM DA BRIGA", "1974 — 2009")]
RIV = "#60A5FA"

def shoe_paths():
    sole = skia.Path(); sole.moveTo(-250, 60); sole.lineTo(230, 60); sole.cubicTo(270, 60, 280, 30, 255, 10); sole.lineTo(-240, 10); sole.cubicTo(-265, 20, -265, 55, -250, 60)
    up = skia.Path(); up.moveTo(-240, 10); up.cubicTo(-250, -60, -230, -120, -170, -130); up.lineTo(-90, -125)
    up.cubicTo(-60, -60, 20, -40, 120, -30); up.cubicTo(200, -22, 250, -5, 255, 10)
    ps = [sole, up, LN((-90, -125), (-40, -140), (-20, -120))]
    for k in range(5): ps.append(LN((-70 + k * 28, -95 + k * 10), (-40 + k * 28, -105 + k * 10)))
    ps.append(LN((-230, -20), (-160, -25)))
    for k in range(6): ps.append(LN((-200 + k * 80, 60), (-206 + k * 80, 84)))
    return ps
SHOE = shoe_paths()
def shoe_art(cv, x, y, s, p, color=GD, width=3, a=255, glow_a=50, flip=False):
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s); stroke(cv, SHOE, p, color, width / s, a, glow_a); cv.restore()

def factory_paths():
    ps = [LN((-200, 120), (-200, -40), (-140, -100), (-140, -40), (-80, -100), (-80, -40), (-20, -100), (-20, -40), (40, -100), (40, -40), (200, -40), (200, 120), (-200, 120)),
          RR(90, -200, 50, 160, 4)]
    for k in range(4): ps.append(RR(-170 + k * 90, 10, 50, 60, 3))
    ps.append(RR(-30, 60, 60, 60, 2))
    return ps
FAC = factory_paths()
def factory_art(cv, x, y, s, p, color=GD, a=255, glow_a=40, smoke_t=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, FAC, p, color, 3 / s, a, glow_a)
    if smoke_t is not None and p >= 1:
        for k in range(4):
            u = (smoke_t * .35 + k / 4) % 1
            cv.drawCircle(115 + 25 * math.sin(u * 6 + k), -220 - u * 180, 16 + u * 30, P(color, int(a * .35 * (1 - u)), stroke=2 / s))
    cv.restore()

def river_path(x, y0, y1, amp=40):
    pa = skia.Path(); pa.moveTo(x, y0); n = 12
    for k in range(1, n + 1):
        yy = y0 + (y1 - y0) * k / n; xm = x + (amp if k % 2 else -amp)
        pa.quadTo(xm, yy - (y1 - y0) / n / 2, x, yy)
    return pa
def river(cv, t, x, y0, y1, p, a=255):
    pa = river_path(x, y0, y1)
    stroke(cv, [pa], p, RIV, 26, int(a * .25)); stroke(cv, [pa], p, RIV, 4, a, 60)
    if p >= 1:
        m = skia.PathMeasure(pa, False, 1); ln = m.getLength()
        for j in range(10):
            d = ((t * .08 + j / 10) % 1) * ln; pos = m.getPosTan(d)
            if pos: cv.drawCircle(pos[0].x(), pos[0].y(), 4, glow(WH, int(180 * a / 255), 3))

def stone_paths():
    pa = skia.Path(); pa.moveTo(-90, 140); pa.lineTo(-90, -40); pa.cubicTo(-90, -150, 90, -150, 90, -40); pa.lineTo(90, 140); pa.close()
    return [pa, LN((0, -80), (0, 20)), LN((-35, -45), (35, -45)), LN((-140, 140), (140, 140))]
STONE = stone_paths()
def stone_art(cv, x, y, s, p, color=WH, a=255):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, STONE, p, color, 3 / s, a, 40); cv.restore()

def medal_art(cv, x, y, s, p, a=255):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    stroke(cv, [LN((-30, -150), (0, -60), (30, -150)), CIR(0, 0, 60), CIR(0, 0, 44)], p, GD, 3 / s, a, 60)
    if p >= 1: txt(cv, "1", 0, 22, TF_B, 60, GD, a, shadow=False)
    cv.restore()

def redacted_where(cv, t, y, k, reveal=0.0):
    if k <= 0: return
    cv.save(); cv.translate(0, (1 - k) * 60)
    card(cv, W / 2, y, 860, 420, int(255 * cl(k)), rot=-1.5)
    al = int(255 * cl(k))
    txt(cv, "ARQUIVO DASSLER  ·  HERZOGENAURACH, ALEMANHA", -390, -150, TF_SB, 21, "#6B6455", al, align="l", track=3, shadow=False)
    cv.drawLine(-390, -128, 390, -128, P("#B8AE98", al, stroke=2))
    txt(cv, "A PROVA MAIS FORTE DA BRIGA ESTÁ EM:", -390, -70, TF_XB, 28, INK, al, align="l", track=1, shadow=False)
    if reveal > 0:
        txt(cv, "UM CEMITÉRIO.", -390, 40, TF_B, 120, INK, al, align="l", shadow=False)
        k2 = eo(cl(reveal * 2 - 1))
        txt(cv, "MESMO LUGAR  ·  LADOS OPOSTOS", -390, 120, TF_B, 64, OR, int(al * k2), align="l", track=2, shadow=False)
    for j, (x0, w0, y0, h0) in enumerate(((-390, 640, -30, 95), (-390, 760, 70, 70))):
        r = cl(reveal * 1.6 - j * .5); ww = w0 * (1 - eio(r))
        if ww > 1:
            rrect(cv, x0 + w0 - ww, y0, ww, h0, 4, P("#0B0D12", al))
            if 0 < r < 1: cv.drawRect(skia.Rect.MakeXYWH(x0 + w0 - ww - 6, y0, 12, h0), glow(OR, 230, 10))
    txt(cv, "CONFIDENCIAL ATÉ O FIM DO VÍDEO" if reveal <= 0 else "REVELADO", 390, 185, TF_SB, 18, "#8A8272", al, align="r", track=4, shadow=False)
    cv.restore(); cv.restore()

def split_line(cv, t, p, col=GD):
    y0, y1 = 340, 1300
    cv.drawLine(W / 2, y0, W / 2, y0 + (y1 - y0) * p, P(col, 200, stroke=3))
    cv.drawLine(W / 2, y0, W / 2, y0 + (y1 - y0) * p, glow(col, 90, 10))

# ---------- cenas ----------
def s_hook(cv, t):
    a, b = L[1]; tc = wt("cidade", a + 2.0)
    background(cv, t)
    sp = eio(prog(t, tc - .3, tc + .6))  # separação
    pf = eio(prog(t, .1, 2.0))
    cv.save(); cv.translate(-sp * 120, 0); factory_art(cv, W / 2 - 110, 1060, 1.1, pf, GD, smoke_t=t); cv.restore()
    cv.save(); cv.translate(sp * 120, 0); cv.clipRect(skia.Rect.MakeXYWH(W / 2 + sp * 120 - 110 + 0, 0, W, H))
    cv.restore()
    if sp > 0:
        # rachadura laranja no meio
        pa = path([(W / 2 - 110 + 0, 800), (W / 2 - 130, 900), (W / 2 - 95, 990), (W / 2 - 125, 1090), (W / 2 - 105, 1200)], close=False)
        stroke(cv, [pa], sp, OR, 5, 255, 120)
    k1 = eo(prog(t, a, a + .4)); txt(cv, "DOIS IRMÃOS.", W / 2, 480 - (1 - k1) * 20, TF_B, 120, WH, int(255 * k1), track=4)
    k2 = eo(prog(t, wt("fábrica", a) - .1, wt("fábrica", a) + .3)); txt(cv, "UMA FÁBRICA.", W / 2, 610, TF_B, 120, GD, int(255 * k2), track=4)
    if t >= tc - .2:
        k4 = back(prog(t, tc - .2, tc + .2))
        cv.save(); cv.translate(W / 2, 735); s_ = .8 + .2 * cl(k4, 0, 1.15); cv.scale(s_, s_)
        txt(cv, "E UMA CIDADE DIVIDIDA", 0, 0, TF_B, 96, OR, int(255 * cl(k4)), track=3); cv.restore()

def s_teaser(cv, t):
    a, b = L[2]
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .4)); txt(cv, "A PROVA MAIS FORTE", W / 2, 430, TF_B, 80, MUT, int(255 * k), track=4)
    txt(cv, "ESTÁ ESCONDIDA AQUI.", W / 2, 540, TF_B, 110, WH, int(255 * eo(prog(t, a + .4, a + .9))), track=3)
    redacted_where(cv, t, 900, back(prog(t, a + .5, a + 1.1)))
    kicker(cv, "VOCÊ DESCOBRE PERTO DO FIM", 1240, int(255 * eo(prog(t, a + 1.8, a + 2.2))))

def s_1924(cv, t):
    a, b = L[3]
    background(cv, t, "#0B1A2E", grid=True)
    kicker(cv, "BAVIERA  ·  ALEMANHA", 430, int(255 * eo(prog(t, a, a + .4))))
    p = eio(prog(t, a + .2, a + 1.6)); yr = int(round(1900 + 24 * p))
    txt(cv, str(yr), W / 2, 790, TF_B, 330, GD if p >= 1 else WH, int(255 * eo(prog(t, a, a + .3))), track=8)
    shoe_art(cv, W / 2, 1100, 1.4, eio(prog(t, a + .6, b + .4)), "#BFDBFE", 3, glow_a=70)

def s_brothers(cv, t):
    a, b = L[4]; tl = wt("lavanderia", a); tcr = wt("cria", tl); tv = wt("vende", tcr)
    background(cv, t, "#0B1A2E", grid=True)
    k = eo(prog(t, a, a + .5))
    if k > 0:
        x0 = 100; y0 = 470
        cv.drawRect(skia.Rect.MakeXYWH(x0, y0 - 70, 6, 150 * k), P(GD))
        txt(cv, "ADI & RUDOLF DASSLER", x0 + 34 - (1 - k) * 30, y0, TF_B, 90, WH, int(255 * k), align="l", track=3)
        txt(cv, "IRMÃOS  ·  SAPATEIROS", x0 + 36, y0 + 58, TF_SB, 26, GD, int(255 * k), align="l", track=4, shadow=False)
    q = eo(prog(t, tl - .1, tl + .4))
    if q > 0:
        rrect(cv, W / 2 - 330, 610, 660, 70, 35, P(WH, int(20 * q))); rrect(cv, W / 2 - 330, 610, 660, 70, 35, P(GD, int(200 * q), stroke=2))
        txt(cv, "LAVANDERIA DA CASA DA MÃE", W / 2, 655, TF_SB, 28, WH, int(255 * q), track=4, shadow=False)
    # duas colunas: cria / vende
    for side, (lab, tt, col) in enumerate((("CRIA", tcr, GD), ("VENDE", tv, GD))):
        cx = W / 2 + (-230 if side == 0 else 230); q = eo(prog(t, tt - .15, tt + .3))
        if q <= 0: continue
        txt(cv, "ADI" if side == 0 else "RUDOLF", cx, 820, TF_B, 70, WH, int(255 * q), track=4)
        if side == 0: shoe_art(cv, cx, 1010, .7, eio(prog(t, tt - .1, tt + .9)), GD, 3)
        else:
            stroke(cv, [LN((cx - 150, 1080), (cx - 60, 1000), (cx, 1040), (cx + 140, 930)), LN((cx + 90, 930), (cx + 140, 930), (cx + 140, 980))], eio(prog(t, tt - .1, tt + .7)), GD, 4, 255, 60)
        txt(cv, lab, cx, 1180, TF_B, 90, col, int(255 * q), track=6)
    if t > tcr: cv.drawLine(W / 2, 760, W / 2, 1200, P(WH, 50, stroke=2))

def s_owens(cv, t):
    a, b = L[5]; to = wt("Quatro", a + 2)
    background(cv, t)
    kicker(cv, "BERLIM  ·  JOGOS OLÍMPICOS DE 1936", 430, int(255 * eo(prog(t, a, a + .4))))
    k = eo(prog(t, wt("Jesse", a) - .1, wt("Jesse", a) + .3)); txt(cv, "JESSE OWENS", W / 2, 580, TF_B, 150, WH, int(255 * k), track=4)
    txt(cv, "CORRE COM SAPATOS DOS DASSLER", W / 2, 660, TF_SB, 30, GD, int(255 * eo(prog(t, wt("sapatos", a) - .1, wt("sapatos", a) + .3))), track=4, shadow=False)
    # pista
    pk = eio(prog(t, a + .2, a + 2.0))
    for j in range(5):
        y = 760 + j * 40; cv.drawLine(80, y, 80 + (W - 160) * pk, y, P(WH, 60, stroke=2))
    rx = 80 + (W - 160) * eio(prog(t, a + .4, to)); cv.drawCircle(rx, 820, 10, glow(GD, 255, 6))
    for j in range(4):
        q = eo(prog(t, to + j * .14, to + .35 + j * .14))
        if q > 0: medal_art(cv, W / 2 - 330 + j * 220, 1150 + (1 - q) * 40, .9, q)
    q = eo(prog(t, to, to + .3))
    txt(cv, f"{int(round(4 * eio(prog(t, to, to + .6))))} MEDALHAS DE OURO", W / 2, 1300, TF_B, 70, GD, int(255 * q), track=4)

def s_war(cv, t):
    a, b = L[6]; tm = wt("motivo", a + 2)
    background(cv, t, "#120C0C")
    k = eo(prog(t, a, a + .4)); txt(cv, "A GUERRA", W / 2, 480, TF_B, 150, WH, int(255 * k), track=6)
    txt(cv, "RACHA A FAMÍLIA", W / 2, 610, TF_B, 110, OR, int(255 * eo(prog(t, wt("racha", a) - .1, wt("racha", a) + .3))), track=4)
    # foto de família rasgando (moldura que se parte)
    pc = eio(prog(t, a + .2, a + 1.0)); sp = eio(prog(t, wt("racha", a), wt("racha", a) + .8))
    for side in (-1, 1):
        cv.save(); cv.translate(side * sp * 40, 0); cv.rotate(side * sp * 3)
        x0 = W / 2 - 300 if side < 0 else W / 2
        stroke(cv, [LN((x0 + (300 if side < 0 else 0), 700), (x0 + (0 if side < 0 else 300), 700), (x0 + (0 if side < 0 else 300), 1120), (x0 + (300 if side < 0 else 0), 1120))], pc, PAPER, 3, 220, 0)
        hx = W / 2 + side * 150
        cv.drawCircle(hx, 850, 50 * pc, P(PAPER, 200, stroke=3)); cv.drawArc(skia.Rect.MakeXYWH(hx - 100, 920, 200, 220), 180, 180, False, P(PAPER, int(200 * pc), stroke=3))
        cv.restore()
    if sp > 0:
        pa = path([(W / 2, 690), (W / 2 - 18, 790), (W / 2 + 14, 880), (W / 2 - 12, 990), (W / 2 + 10, 1130)], close=False)
        stroke(cv, [pa], sp, OR, 4, 255, 120)
    q = eo(prog(t, tm - .3, tm + .2))
    if q > 0:
        rrect(cv, W / 2 - 360, 1200, 720, 90, 8, P("#0B0D12", int(230 * q))); rrect(cv, W / 2 - 360, 1200, 720, 90, 8, P(MUT, int(120 * q), stroke=2))
        txt(cv, "MOTIVO EXATO:  INCERTO ATÉ HOJE", W / 2, 1258, TF_SB, 30, WH, int(255 * q), track=3, shadow=False)

def s_split(cv, t):
    a, b = L[7]; tp = wt("Puma", a + 1); ta = wt("Adidas", tp)
    background(cv, t)
    kk = eo(prog(t, a, a + .3)); txt(cv, "1948", W / 2, 470, TF_B, 200, WH, int(255 * kk), track=8)
    txt(cv, "ELES SE SEPARAM", W / 2, 560, TF_SB, 32, GD, int(255 * eo(prog(t, wt("separam", a) - .1, wt("separam", a) + .3))), track=6, shadow=False)
    split_line(cv, t, eio(prog(t, wt("separam", a), wt("separam", a) + .6)), OR)
    for side, (nm, co, tt, yrr) in enumerate((("RUDOLF", "PUMA", tp, "RUDA, 1948 → PUMA"), ("ADI", "ADIDAS", ta, "ADIDAS, 1949"))):
        cx = W / 4 if side == 0 else 3 * W / 4; q = eo(prog(t, tt - .5, tt))
        if q <= 0: continue
        txt(cv, nm, cx, 760, TF_B, 70, MUT, int(255 * q), track=4)
        cv.save(); cv.translate(cx, 920); s_ = cl(back(prog(t, tt - .2, tt + .2)), 0, 1.15); cv.scale(s_, s_)
        txt(cv, co, 0, 0, TF_B, 150, GD, 255, track=6); cv.restore()
        txt(cv, yrr, cx, 1000, TF_SB, 22, WH, int(200 * q), track=3, shadow=False)
        factory_art(cv, cx, 1180, .6, eio(prog(t, tt - .2, tt + .9)), GD, int(220 * q))

def s_river(cv, t):
    a, b = L[8]
    background(cv, t, "#0B1A2E", grid=True)
    txt(cv, "RIO AURACH", W / 2, 440, TF_B, 120, RIV, int(255 * eo(prog(t, a, a + .4))), track=6)
    txt(cv, "HERZOGENAURACH  ·  BAVIERA", W / 2, 500, TF_SB, 24, MUT, int(255 * eo(prog(t, a + .2, a + .6))), track=5, shadow=False)
    river(cv, t, W / 2, 560, 1230, eio(prog(t, a - .1, a + 1.0)))
    factory_art(cv, W / 4, 950, .7, eio(prog(t, a + .3, a + 1.3)), GD, smoke_t=t)
    factory_art(cv, 3 * W / 4, 950, .7, eio(prog(t, a + .5, a + 1.5)), GD, smoke_t=t + 1.3)
    q = eo(prog(t, a + 1.0, a + 1.4))
    txt(cv, "PUMA", W / 4, 1150, TF_B, 64, WH, int(255 * q), track=6); txt(cv, "ADIDAS", 3 * W / 4, 1150, TF_B, 64, WH, int(255 * q), track=6)
    txt(cv, "Fábricas em margens opostas do rio", W / 2, 1290, TF_MD, 24, MUT, int(255 * q), shadow=False)

def s_tension(cv, t):
    a, b = L[9]; u = prog(t, a, b + .3)
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#040508"))
    river(cv, t, W / 2, 300, 1400, 1.0, int(90 + 60 * eio(u)))
    hb = max(0, math.sin((t - a) * 2 * math.pi * 1.2)) ** 10
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, H * .7, [("#000000", 0), ("#3A0A00", int(140 * hb))]))
    reveal_txt(cv, "E AQUI", W / 2, 900, TF_B, 140, WH, prog(t, a, a + .5), track=6)
    reveal_txt(cv, "A HISTÓRIA VIRA", W / 2, 1040, TF_B, 130, OR, prog(t, a + .6, a + 1.5), track=4)

def s_town(cv, t):
    a, b = L[10]; tps = [wt("padarias", a + 2), wt("bares", a + 2), wt("escolas", a + 2)]
    background(cv, t)
    k = eo(prog(t, a, a + .4)); txt(cv, "A CIDADE SE DIVIDIU", W / 2, 470, TF_B, 110, WH, int(255 * k), track=4)
    river(cv, t, W / 2, 560, 1230, eio(prog(t, a, a + .8)), 200)
    q0 = eo(prog(t, a + .4, a + .8))
    txt(cv, "LADO PUMA", W / 4, 640, TF_SB, 26, GD, int(255 * q0), track=5, shadow=False)
    txt(cv, "LADO ADIDAS", 3 * W / 4, 640, TF_SB, 26, GD, int(255 * q0), track=5, shadow=False)
    for j, (lab, tt) in enumerate(zip(("PADARIAS", "BARES", "ESCOLAS"), tps)):
        q = back(prog(t, tt - .1, tt + .25)); y = 780 + j * 170
        if q <= 0: continue
        for cx in (W / 4, 3 * W / 4):
            cv.save(); cv.translate(cx, y); s_ = cl(q, 0, 1.15); cv.scale(s_, s_)
            rrect(cv, -190, -55, 380, 90, 10, P(WH, 16)); rrect(cv, -190, -55, 380, 90, 10, P(WH, 140, stroke=2))
            txt(cv, lab, 0, 18, TF_B, 62, WH, 255, track=5); cv.restore()
    txt(cv, "Relato da jornalista Barbara Smit, autora de livro sobre os Dassler (NPR, 2009)", W / 2, 1290, TF_MD, 21, MUT, int(255 * eo(prog(t, a + .8, a + 1.2))), shadow=False)

def s_necks(cv, t):
    a, b = L[11]; ts = wt("sapatos", a + 1)
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .4)); txt(cv, "“A CIDADE DOS", W / 2, 460, TF_B, 110, WH, int(255 * k), track=4)
    txt(cv, "PESCOÇOS TORTOS”", W / 2, 580, TF_B, 120, GD, int(255 * eo(prog(t, a + .3, a + .7))), track=4)
    # olhar descendo até os sapatos: duas cabeças inclinadas + sapatos
    tilt = eio(prog(t, a + .6, ts))
    for side in (-1, 1):
        cx = W / 2 + side * 220
        cv.save(); cv.translate(cx, 820); cv.rotate(side * -18 * tilt)
        cv.drawOval(skia.Rect.MakeXYWH(-60, -75, 120, 150), P("#05070B")); cv.drawOval(skia.Rect.MakeXYWH(-60, -75, 120, 150), P(GD, 120, stroke=3))
        cv.restore()
        body = skia.Path(); body.moveTo(cx - 120, 1130); body.cubicTo(cx - 120, 960, cx - 80, 910, cx, 905); body.cubicTo(cx + 80, 910, cx + 120, 960, cx + 120, 1130); body.close()
        cv.drawPath(body, P("#05070B")); cv.drawPath(body, P(GD, 90, stroke=2))
        shoe_art(cv, cx, 1190, .42, 1.0, GD if side < 0 else WH, 3, glow_a=0, flip=side > 0)
        # linha do olhar
        q = eo(prog(t, ts - .5, ts))
        if q > 0:
            cv.drawLine(cx - side * 10, 840, cx - side * 10 + (-side * 200) * q, 840 + 340 * q, P(OR, int(200 * q), stroke=2))
    txt(cv, "Antes de conversar, olhava-se o sapato do outro — relato de Barbara Smit", W / 2, 1290, TF_MD, 21, MUT, int(255 * eo(prog(t, a + .8, a + 1.2))), shadow=False)

def s_cemetery(cv, t):
    a, b = L[12]; t78 = wt("oito", a + 2); tm = wt("cemitério", t78)
    background(cv, t, "#0D0F16")
    # lápides nos extremos
    for side, (nm, yr, tt) in enumerate((("RUDOLF", "1898 — 1974", a), ("ADI", "1900 — 1978", t78 - 1.0))):
        cx = 190 if side == 0 else W - 190; q = eio(prog(t, tt, tt + .9))
        stone_art(cv, cx, 600, .95, q, WH if side == 0 else WH)
        q2 = eo(prog(t, tt + .4, tt + .8))
        txt(cv, nm, cx, 790, TF_B, 58, WH, int(255 * q2), track=4)
        txt(cv, yr, cx, 830, TF_SB, 22, GD, int(255 * q2), track=3, shadow=False)
    if t < tm - .3:
        k = eo(prog(t, a, a + .4)); txt(cv, "†", W / 2, 640, TF_B, 140, MUT, int(160 * k))
    redacted_where(cv, t, 1080, eo(prog(t, tm - 1.2, tm - .6)), reveal=prog(t, tm - .2, tm + 1.0))
    q = eo(prog(t, tm + 1.0, tm + 1.4))
    if q > 0:
        cv.drawLine(190, 900, 190 + (W - 380) * q, 900, P(OR, 220, stroke=3))
        for xx in (190, W - 190): cv.drawLine(xx, 885, xx, 915, P(OR, int(255 * q), stroke=3))

def s_2009(cv, t):
    a, b = L[13]; tf = wt("futebol", a + 1)
    background(cv, t)
    y = 560; x0, x1 = 120, W - 120; p = eio(prog(t, a, a + 1.4))
    cv.drawLine(x0, y, x0 + (x1 - x0) * p, y, P(WH, 200, stroke=3))
    for yr, fx, col in ((1948, 0, OR), (2009, 1, GD)):
        if p >= fx - .001:
            xx = x0 + (x1 - x0) * fx; cv.drawCircle(xx, y, 12, P(col)); cv.drawCircle(xx, y, 26, P(col, 120, stroke=2))
            txt(cv, str(yr), xx, y - 50, TF_B, 64, col, 255, track=2)
    n = int(round(61 * p)); txt(cv, f"{n} ANOS DEPOIS", W / 2, y + 120, TF_B, 90, WH, int(255 * eo(prog(t, a, a + .4))), track=4)
    # campo de futebol
    pf = eio(prog(t, a + .6, tf + .3)); fx0, fy0, fw, fh = W / 2 - 360, 800, 720, 420
    stroke(cv, [RR(fx0, fy0, fw, fh, 6), LN((W / 2, fy0), (W / 2, fy0 + fh)), CIR(W / 2, fy0 + fh / 2, 70), RR(fx0, fy0 + 120, 90, 180, 2), RR(fx0 + fw - 90, fy0 + 120, 90, 180, 2)], pf, GD, 3, 230, 40)
    if pf >= 1:
        r = random.Random(9)
        for j in range(10):
            col = GD if j % 2 else WH
            px = fx0 + 60 + (fw - 120) * ((r.random() + t * .07 * (1 if j % 3 else -1)) % 1); py = fy0 + 40 + (fh - 80) * r.random()
            cv.drawCircle(px, py, 12, P(col))
        bx = W / 2 + 200 * math.sin(t * 1.3); by = fy0 + fh / 2 + 120 * math.sin(t * 2.1)
        cv.drawCircle(bx, by, 9, glow(WH, 255, 3))
    q = eo(prog(t, tf - .2, tf + .3))
    txt(cv, "TIMES MISTURADOS", W / 2, 1290, TF_B, 64, GD, int(255 * q), track=5)

def s_end(cv, t):
    a, b = L[14]; tv = wt("Você", a + 1.5)
    background(cv, t)
    if t < tv - .1:
        k = eo(prog(t, a, a + .4)); txt(cv, "UMA BRIGA DE FAMÍLIA", W / 2, 760, TF_B, 110, WH, int(255 * k), track=4)
        txt(cv, "CRIOU DUAS GIGANTES.", W / 2, 900, TF_B, 110, GD, int(255 * eo(prog(t, wt("criou", a) - .1, wt("criou", a) + .3))), track=4)
        shoe_art(cv, W / 2 - 200, 1130, .5, eio(prog(t, a + .3, a + 1.3)), GD, 3)
        shoe_art(cv, W / 2 + 200, 1130, .5, eio(prog(t, a + .3, a + 1.3)), GD, 3, flip=True)
    else:
        for i_, (s, col) in enumerate((("VOCÊ ABRIRIA", WH), ("UM NEGÓCIO COM", WH), ("SEU IRMÃO?", GD))):
            q = eo(prog(t, tv + i_ * .18, tv + .4 + i_ * .18))
            txt(cv, s, W / 2, 760 + i_ * 160 + (1 - q) * 20, TF_B, 150, col, int(255 * q), track=4)
        kicker(cv, "CONTA NOS COMENTÁRIOS", 1250, int(255 * eo(prog(t, tv + 1.0, tv + 1.4))))
    kl = eio(prog(t, b + .2, b + .7))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG0, int(255 * kl)))
        cv.drawLine(W / 2 - 200 * kl, 1010, W / 2 + 200 * kl, 1010, P(GD, int(255 * kl), stroke=2))
        txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 980, TF_B, 120, WH, int(255 * kl), track=8)
        txt(cv, "HISTÓRIAS EXTRAORDINÁRIAS POR TRÁS DE GRANDES NEGÓCIOS", W / 2, 1060, TF_SB, 20, MUT, int(255 * kl), track=4, shadow=False)

FNS = [s_hook, s_teaser, s_1924, s_brothers, s_owens, s_war, s_split, s_river, s_tension, s_town, s_necks, s_cemetery, s_2009, s_end]
SCENES = []
for i_, fn in enumerate(FNS, start=1):
    s0 = 0.0 if i_ == 1 else L[i_][0] - .1
    e0 = TOTAL if i_ == len(FNS) else L[i_ + 1][0] - .1
    SCENES.append((fn, s0, e0))
XF = .3

CHUNKS = {
 1: [("Dois *irmãos*", 2), ("dividiram uma *fábrica*.", 3), ("E acabaram dividindo", 3), ("uma *cidade inteira*.", 3)],
 2: [("A *prova* mais forte", 4), ("dessa briga está", 3), ("num *lugar inesperado*.", 3)],
 3: [("Alemanha,", 1), ("*1924*.", 6)],
 4: [("*Adi* e *Rudolf Dassler*", 4), ("fazem sapatos", 2), ("na *lavanderia* da mãe.", 4), ("Adi *cria*.", 2), ("Rudolf *vende*.", 2)],
 5: [("Em *1936*,", 4), ("*Jesse Owens* corre em Berlim", 5), ("com sapatos dos Dassler.", 4), ("*4 ouros*.", 2)],
 6: [("Mas a *guerra*", 3), ("racha a família.", 3), ("E até hoje ninguém sabe", 5), ("o *motivo exato*.", 3)],
 7: [("Em *1948*,", 4), ("eles se *separam*.", 3), ("Rudolf funda", 2), ("a futura *Puma*.", 3), ("Adi, a *Adidas*.", 3)],
 8: [("Cada fábrica", 2), ("de um lado do *rio*.", 5)],
 9: [("E aqui a história *vira*.", 5)],
 10: [("Segundo a jornalista", 3), ("*Barbara Smit*,", 2), ("a cidade se *dividiu*:", 4), ("*padarias, bares, escolas*.", 3)],
 11: [("Antes de conversar,", 3), ("todo mundo olhava", 3), ("os *sapatos* do outro.", 4)],
 12: [("Rudolf morre em *1974*.", 6), ("Adi, em *1978*.", 5), ("*Mesmo cemitério*...", 2), ("*lados opostos*.", 2)],
 13: [("Só em *2009*,", 6), ("funcionários", 1), ("das duas marcas", 3), ("jogaram *futebol juntos*.", 3)],
 14: [("Uma briga de família", 4), ("criou *duas gigantes*.", 3), ("Você abriria um negócio", 4), ("com seu *irmão*?", 3)],
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
