# Império de Ideias — EP01 Kodak — versão PREMIUM (estética documental / editorial)
import sys, os, json, math, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ep01"))
import render as R
from render import (skia, np, W, H, FPS, C, P, rrect, lin, rad, glow, path, cl, lerp, eo, eio, back, prog, GRAINS)

FD = os.path.join(HERE, "..", "ep01", "fonts")
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

# ---------- cenas ----------
def s_hook(cv, t):
    a, b = L[1]; tq = wt("quase", a + 1.5)
    background(cv, t)
    g = cl((t - tq + .1) * 2) if t > tq - .1 else 0
    camera_art(cv, W / 2 - 30, 1130, 1.35 + .05 * eo(prog(t, 0, 6)), eio(prog(t, .1, 2.6)), OR if g > .5 else GD, 3, glitch=g * (.6 + .4 * math.sin(t * 40)), t=t)
    k1 = eo(prog(t, a, a + .5)); txt(cv, "ESSA EMPRESA INVENTOU", W / 2, 520 - (1 - k1) * 20, TF_B, 96, WH, int(255 * k1), track=3)
    if t < tq:
        k2 = eo(prog(t, a + .6, a + 1.1)); txt(cv, "A CÂMERA DIGITAL", W / 2, 660, TF_B, 140, GD, int(255 * k2), track=2)
        k3 = eo(prog(t, a + 1.4, a + 1.9)); kicker(cv, "KODAK  ·  1975", 740, int(255 * k3), MUT)
    else:
        k4 = back(prog(t, tq, tq + .35))
        cv.save(); cv.translate(W / 2, 650); s_ = .8 + .2 * cl(k4, 0, 1.15); cv.scale(s_, s_)
        txt(cv, "E QUASE ACABOU COM ELA", 0, 0, TF_B, 106, OR, int(255 * cl(k4)), track=2); cv.restore()
        cv.drawRect(skia.Rect.MakeXYWH(W / 2 - 330 * cl(k4), 690, 660 * cl(k4), 5), P(OR))

def redacted_card(cv, t, y, k, reveal=0.0, tb=0.0):
    if k <= 0: return
    cv.save(); cv.translate(0, (1 - k) * 60)
    card(cv, W / 2, y, 860, 470, int(255 * cl(k)), rot=-1.5)
    al = int(255 * cl(k))
    txt(cv, "SALA DE REUNIÃO  ·  ROCHESTER, NY  ·  1975", -390, -170, TF_SB, 22, "#6B6455", al, align="l", track=3, shadow=False)
    cv.drawLine(-390, -150, 390, -150, P("#B8AE98", al, stroke=2))
    txt(cv, "A RESPOSTA DOS EXECUTIVOS:", -390, -95, TF_XB, 30, INK, al, align="l", track=2, shadow=False)
    # citação revelada sob as tarjas
    if reveal > 0:
        txt(cv, "“BONITINHO...", -390, 20, TF_B, 110, INK, al, align="l", shadow=False)
        k2 = eo(prog(t, tb + .9, tb + 1.3))
        txt(cv, "MAS NÃO CONTE PRA NINGUÉM.”", -390, 120, TF_B, 74, OR, int(al * k2), align="l", shadow=False)
    for j, (x0, w0, y0, h0) in enumerate(((-390, 520, -50, 90), (-390, 700, 55, 80))):
        r = cl(reveal * 1.6 - j * .5)
        ww = w0 * (1 - eio(r))
        if ww > 1:
            rrect(cv, x0 + w0 - ww, y0, ww, h0, 4, P("#0B0D12", al))
            if 0 < r < 1: cv.drawRect(skia.Rect.MakeXYWH(x0 + w0 - ww - 6, y0, 12, h0), glow(OR, 230, 10))
    txt(cv, "RECONSTITUIÇÃO", 390, 205, TF_SB, 18, "#8A8272", al, align="r", track=4, shadow=False)
    cv.restore(); cv.restore()

def silhouettes(cv, t, a=255):
    for x, s_ in ((260, .95), (540, 1.05), (820, .95)):
        cv.save(); cv.translate(x, 1330); cv.scale(s_, s_)
        body = skia.Path(); body.moveTo(-150, 0); body.cubicTo(-150, -170, -110, -250, 0, -255); body.cubicTo(110, -250, 150, -170, 150, 0); body.close()
        cv.drawPath(body, P("#05070B", a)); cv.drawOval(skia.Rect.MakeXYWH(-72, -430, 144, 170), P("#05070B", a))
        rim = P(GD, int(a * .35), stroke=3); rim.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
        cv.drawArc(skia.Rect.MakeXYWH(-72, -430, 144, 170), 200, 120, False, rim)
        cv.restore()
    cv.drawRect(skia.Rect.MakeXYWH(0, 1300, W, 40), lin(0, 1300, 0, 1340, [("#2A1C10", a), ("#150E07", a)]))

def s_teaser(cv, t):
    a, b = L[2]
    background(cv, t, "#141019")
    silhouettes(cv, t, 160)
    k = eo(prog(t, a, a + .4)); txt(cv, "TUDO COMEÇOU COM", W / 2, 420, TF_B, 70, MUT, int(255 * k), track=4)
    txt(cv, "UMA FRASE.", W / 2, 540, TF_B, 150, WH, int(255 * eo(prog(t, a + .3, a + .8))), track=3)
    redacted_card(cv, t, 920, back(prog(t, a + .7, a + 1.3)))
    kicker(cv, "VOCÊ VAI OUVIR ELA DAQUI A POUCO", 1250, int(255 * eo(prog(t, a + 1.6, a + 2.0))))

def s_market(cv, t):
    a, b = L[3]
    background(cv, t)
    k = eo(prog(t, a, a + .4)); kicker(cv, "ANOS 70", 420, int(255 * k))
    p = eio(prog(t, a + .9, a + 2.6)); n = int(round(90 * p))
    txt(cv, f"{n}%", W / 2, 780, TF_B, 340, GD, int(255 * eo(prog(t, a + .8, a + 1.1))), track=4)
    txt(cv, "DO FILME FOTOGRÁFICO VENDIDO NOS EUA", W / 2, 870, TF_SB, 34, WH, int(255 * eo(prog(t, a + 1.2, a + 1.6))), track=2)
    txt(cv, "ERA KODAK", W / 2, 960, TF_B, 90, WH, int(255 * eo(prog(t, a + 1.6, a + 2.0))), track=4)
    # barra 90 / 10
    x0, y0, bw = 120, 1110, W - 240
    rrect(cv, x0, y0, bw, 46, 4, P(WH, 30))
    rrect(cv, x0, y0, bw * .9 * p, 46, 4, lin(x0, 0, x0 + bw, 0, ["#D99A12", GD]))
    ka = int(255 * eo(prog(t, a + 2.4, a + 2.8)))
    txt(cv, "KODAK", x0, y0 + 95, TF_SB, 24, GD, ka, align="l", track=4, shadow=False)
    txt(cv, "OUTROS", x0 + bw, y0 + 95, TF_SB, 24, MUT, ka, align="r", track=4, shadow=False)
    txt(cv, "Participação estimada em 1976, citada pela imprensa da época", W / 2, 1270, TF_MD, 22, MUT, ka, shadow=False)

def s_lab(cv, t):
    a, b = L[4]; tg = wt("gering", a + 1.0); tt = wt("torrad", tg)
    background(cv, t, "#0B1A2E", grid=True)
    # lower third
    k = eo(prog(t, a + .9, a + 1.4))
    if k > 0:
        x0 = 100; y0 = 470
        cv.drawRect(skia.Rect.MakeXYWH(x0, y0 - 70, 6 , 150 * k), P(GD))
        txt(cv, "STEVEN SASSON", x0 + 34 - (1 - k) * 30, y0, TF_B, 96, WH, int(255 * k), align="l", track=3)
        txt(cv, "ENGENHEIRO ELÉTRICO  ·  KODAK", x0 + 36, y0 + 58, TF_SB, 26, GD, int(255 * k), align="l", track=4, shadow=False)
    kk = eo(prog(t, a, a + .4)); txt(cv, "1975", W - 100, 470, TF_B, 140, WH, int(160 * kk), align="r", track=4)
    pc = eio(prog(t, tg - .3, tg + 1.6))
    camera_art(cv, W / 2 - 30, 1010, 1.3, pc, "#BFDBFE", 3, t=t, glow_a=70)
    specs = [("≈ 3,6 KG", -250, -340, -180, -150), ("16 PILHAS AA", 230, -340, 120, -150), ("SENSOR CCD", -330, 230, -200, 90), ("FITA CASSETE", 300, 230, 220, 130)]
    for i_, (lab, lx, ly, px, py) in enumerate(specs):
        q = eo(prog(t, tg + .8 + i_ * .25, tg + 1.2 + i_ * .25))
        if q <= 0: continue
        X, Y = W / 2 - 30, 1010
        cv.drawLine(X + px * 1.3, Y + py * 1.3, X + lx, Y + ly, P(GD, int(255 * q), stroke=2))
        cv.drawCircle(X + px * 1.3, Y + py * 1.3, 6, P(GD, int(255 * q)))
        txt(cv, lab, X + lx, Y + ly - 14, TF_SB, 26, WH, int(255 * q), track=3)
    q = eo(prog(t, tt - .1, tt + .4))
    if q > 0:
        y = 1290; x1, x2 = W / 2 - 30 - 260 * 1.3, W / 2 - 30 + 310 * 1.3
        cv.drawLine(x1, y, x1 + (x2 - x1) * q, y, P(GD, 255, stroke=2))
        for xx in (x1, x2): cv.drawLine(xx, y - 14, xx, y + 14, P(GD, int(255 * q), stroke=2))
        txt(cv, "TAMANHO DE UMA TORRADEIRA", W / 2, y - 24, TF_SB, 28, GD, int(255 * q), track=4)

def cassette_art(cv, x, y, s, p, t, color=WH):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    ps = [RR(-240, -140, 480, 280, 20), RR(-200, -105, 400, 130, 12), CIR(-110, -40, 42), CIR(110, -40, 42), LN((-120, 140), (-90, 80), (90, 80), (120, 140))]
    stroke(cv, ps, p, color, 3 / s, 255, 40)
    if p >= 1:
        for cx in (-110, 110):
            cv.save(); cv.translate(cx, -40); cv.rotate(t * 360)
            for k in range(6): cv.rotate(60); cv.drawLine(0, 14, 0, 30, P(color, 255, stroke=3 / s))
            cv.restore()
    cv.restore()

def s_tape(cv, t):
    a, b = L[5]
    background(cv, t)
    kicker(cv, "TEMPO PARA GRAVAR UMA FOTO", 420, int(255 * eo(prog(t, a, a + .4))))
    q = eio(prog(t, a + .3, b - .2)); sec = 23 * q
    txt(cv, f"00:{int(sec):02d}", W / 2, 720, TF_B, 280, GD if q >= 1 else WH, 255, track=6)
    cassette_art(cv, W / 2, 1040, 1.35, eio(prog(t, a - .1, a + 1.0)), t)
    rrect(cv, 140, 1260, W - 280, 6, 3, P(WH, 40)); rrect(cv, 140, 1260, (W - 280) * q, 6, 3, P(GD))

def s_works(cv, t):
    a, b = L[6]
    background(cv, t)
    # monitor minimalista
    mx, my, mw, mh = W / 2 - 330, 640, 660, 560
    stroke(cv, [RR(mx, my, mw, mh, 22), LN((W / 2 - 70, my + mh), (W / 2 - 100, my + mh + 110), (W / 2 + 100, my + mh + 110), (W / 2 + 70, my + mh))], eio(prog(t, a - .2, a + .5)), WH, 3, 255, 30)
    rev = eio(prog(t, a + .2, a + 1.6))
    if rev > 0: R.pixel_face(cv, skia.Rect.MakeXYWH(W / 2 - 230, my + 50, 460, 460), rev)
    txt(cv, "FUNCIONA.", W / 2, 470, TF_B, 140, WH, int(255 * eo(prog(t, a, a + .35))), track=4)
    k = back(prog(t, a + 1.2, a + 1.6))
    if k > 0:
        cv.save(); cv.translate(W / 2, 1300); s_ = cl(k, 0, 1.15); cv.scale(s_, s_)
        rrect(cv, -230, -48, 460, 74, 37, P(GD)); txt(cv, "SEM FILME", 0, 10, TF_B, 64, BG0, 255, track=6, shadow=False); cv.restore()
    txt(cv, "100 × 100 PIXELS  ·  PRETO E BRANCO  ·  DEZ/1975", W / 2, my - 30, TF_SB, 22, MUT, int(255 * eo(prog(t, a + 1.0, a + 1.4))), track=3, shadow=False)

def s_tension(cv, t):
    a, b = L[7]; u = prog(t, a, b + .3)
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#040508"))
    # mesa em perspectiva (linhas convergindo)
    vx, vy = W / 2, 760
    z = 1 + .25 * eio(u)
    cv.save(); cv.translate(vx, vy); cv.scale(z, z); cv.translate(-vx, -vy)
    door = .3 + .7 * eio(u)
    cv.drawRect(skia.Rect.MakeXYWH(vx - 70, vy - 210, 140, 260), P(GD, int(60 + 120 * door)))
    cv.drawRect(skia.Rect.MakeXYWH(vx - 70, vy - 210, 140, 260), glow(GD, int(120 * door), 40))
    for xb in (-700, -350, 0, 350, 700):
        cv.drawLine(vx + xb * .12, vy + 60, vx + xb * 1.6, H, P(GD, 70, stroke=2))
    for k in range(1, 9):
        yy = vy + 60 + (H - vy) * (k / 9) ** 1.8
        cv.drawLine(0, yy, W, yy, P(GD, 25, stroke=1))
    cv.restore()
    hb = max(0, math.sin((t - a) * 2 * math.pi * 1.2)) ** 10
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, H * .7, [("#000000", 0), ("#3A0A00", int(140 * hb))]))
    reveal_txt(cv, "AGORA VEM A PARTE", W / 2, 1120, TF_B, 110, WH, prog(t, a, a + .9), track=4)
    reveal_txt(cv, "QUE NINGUÉM ESPERAVA", W / 2, 1240, TF_B, 110, OR, prog(t, a + 1.1, a + 2.1), track=4)

def s_board(cv, t):
    a, b = L[8]; tb = wt("bonit", a + 1.0)
    background(cv, t, "#141019")
    silhouettes(cv, t, 200)
    k = eo(prog(t, a, a + .4)); kicker(cv, "A RESPOSTA", 420, int(255 * k))
    redacted_card(cv, t, 860, back(prog(t, a - .1, a + .5)), reveal=prog(t, tb - .15, tb + .5), tb=tb)
    q = eo(prog(t, tb + 1.0, tb + 1.4))
    txt(cv, "Segundo relato de Steven Sasson ao The New York Times (2008)", W / 2, 1180, TF_MD, 24, MUT, int(255 * q), shadow=False)

def s_motive(cv, t):
    a, b = L[9]
    background(cv, t)
    txt(cv, "O NEGÓCIO ERA", W / 2, 470, TF_B, 90, MUT, int(255 * eo(prog(t, a, a + .4))), track=4)
    txt(cv, "O FILME", W / 2, 600, TF_B, 160, GD, int(255 * eo(prog(t, a + .3, a + .7))), track=4)
    nodes = [("FILME", 820), ("PAPEL", 980), ("REVELAÇÃO", 1140)]
    hx, hy = 820, 980
    for i_, (lab, y) in enumerate(nodes):
        q = eo(prog(t, a + .5 + i_ * .25, a + .9 + i_ * .25))
        if q <= 0: continue
        rrect(cv, 90, y - 48, 330, 80, 40, P(WH, int(18 * q))); rrect(cv, 90, y - 48, 330, 80, 40, P(WH, int(160 * q), stroke=2))
        txt(cv, lab, 255, y + 8, TF_SB, 30, WH, int(255 * q), track=4, shadow=False)
        pa = skia.Path(); pa.moveTo(420, y - 8); pa.cubicTo(560, y - 8, 600, hy, hx - 120, hy)
        stroke(cv, [pa], q, GD, 2, 200)
        if q >= 1:
            m = skia.PathMeasure(pa, False, 1); ln = m.getLength()
            for j in range(3):
                d = ((t * .7 + j / 3 + i_ * .13) % 1) * ln; pos = m.getPosTan(d)
                if pos: cv.drawCircle(pos[0].x(), pos[0].y(), 7, glow(GD, 255, 4))
    q = eo(prog(t, a + .9, a + 1.3))
    cv.drawCircle(hx, hy, 120, P(GD, int(30 * q))); cv.drawCircle(hx, hy, 120, P(GD, int(255 * q), stroke=3))
    txt(cv, "KODAK", hx, hy + 22, TF_B, 70, WH, int(255 * q), track=4)

def s_patent(cv, t):
    a, b = L[10]; ts = wt("seguiu", a + 1.5)
    background(cv, t)
    k = back(prog(t, a - .1, a + .5)); out = eio(prog(t, ts - .2, ts + .5))
    cv.save(); cv.translate(-out * 140, out * 80); sc = 1 - .25 * out; cv.translate(W / 2, 960); cv.scale(sc, sc); cv.translate(-W / 2, -960)
    if k > 0:
        al = int(255 * cl(k) * (1 - .55 * out))
        card(cv, W / 2, 940 + (1 - cl(k)) * 80, 780, 860, al, rot=1.2); cv.scale(.88, .88)
        txt(cv, "UNITED STATES PATENT", -340, -330, TF_SB, 24, "#6B6455", al, align="l", track=4, shadow=False)
        txt(cv, "4,131,919", 340, -330, TF_B, 44, INK, al, align="r", track=2, shadow=False)
        cv.drawLine(-340, -305, 340, -305, P("#B8AE98", al, stroke=2))
        txt(cv, "ELECTRONIC STILL CAMERA", -340, -235, TF_B, 70, INK, al, align="l", track=2, shadow=False)
        txt(cv, "Inventores: Gareth A. Lloyd, Steven J. Sasson", -340, -185, TF_MD, 24, "#3A3F4A", al, align="l", shadow=False)
        txt(cv, "Titular: Eastman Kodak Company · Concedida em 26/12/1978", -340, -150, TF_MD, 22, "#3A3F4A", al, align="l", shadow=False)
        for j in range(8): cv.drawRect(skia.Rect.MakeXYWH(-340, -100 + j * 34, 680 - (j % 3) * 90, 10), P("#C9BFA6", al))
        cv.save(); cv.translate(-20, 260); camera_art(cv, 0, 0, .55, 1.0, "#3A3F4A", 2, t=t, glow_a=0); cv.restore()
        st = back(prog(t, a + .7, a + 1.0))
        if st > 0:
            cv.save(); cv.translate(200, 170); cv.rotate(-12); s_ = lerp(1.8, 1, cl(st)); cv.scale(s_, s_)
            rrect(cv, -150, -55, 300, 110, 10, P("#B45309", int(al * .9), stroke=8))
            txt(cv, "PATENTEADA", 0, 18, TF_B, 64, "#B45309", int(al * .9), track=3, shadow=False); cv.restore()
        cv.restore()
    cv.restore()
    q = eo(prog(t, wt("lucrou", a + .5), wt("lucrou", a + .5) + .4))
    if out <= 0: txt(cv, "PATENTEOU E LUCROU", W / 2, 440, TF_B, 100, GD, int(255 * q), track=4)
    if out > 0:
        film_art(cv, W / 2 + 230, 1000, 1.2, out, GD, 3)
        txt(cv, "...E SEGUIU APOSTANDO", W / 2, 440, TF_B, 96, WH, int(255 * out), track=4)
        txt(cv, "NO FILME", W / 2, 560, TF_B, 140, GD, int(255 * out), track=4)

def s_timeline(cv, t):
    a, b = L[11]; t12 = wt("2012", a + 1.0)
    background(cv, t)
    txt(cv, "O MUNDO NÃO ESPEROU", W / 2, 460, TF_B, 110, WH, int(255 * eo(prog(t, a, a + .4))), track=4)
    y = 900; x0, x1 = 110, W - 110
    p = eio(prog(t, a + .2, t12 + .1))
    cv.drawLine(x0, y, x0 + (x1 - x0) * p, y, P(WH, 200, stroke=3))
    marks = [(1975, "INVENÇÃO", GD), (1978, "PATENTE", GD), (2012, "RECUPERAÇÃO JUDICIAL", OR)]
    for yr, lab, col in marks:
        fx = (yr - 1975) / (2012 - 1975); xx = x0 + (x1 - x0) * fx
        if p < fx - .001: continue
        q = eo(cl((p - fx) * 8 + (1 if yr == 1975 else 0)))
        if yr == 2012: q = back(prog(t, t12, t12 + .4))
        cv.drawCircle(xx, y, 12 * cl(q, 0, 1.2), P(col)); cv.drawCircle(xx, y, 26 * cl(q), P(col, 120, stroke=2))
        up = yr != 1978
        txt(cv, str(yr), xx, y + (-50 if up else 80), TF_B, 64, col, int(255 * cl(q)), track=2)
        txt(cv, lab, min(max(xx, 200), W - 200), y + (-115 if up else 125), TF_SB, 22, WH, int(255 * cl(q)), track=3, shadow=False)
    # celulares surgindo ao longo da linha (a era digital)
    r = random.Random(4)
    for k in range(9):
        fx = .35 + .6 * k / 8; xx = x0 + (x1 - x0) * fx
        if p > fx: phone_art(cv, xx + r.uniform(-30, 30), 1180 + r.uniform(-40, 60), .7, eo(cl((p - fx) * 6)), EB, 160)
    q = eo(prog(t, t12 + .4, t12 + .9))
    if q > 0:
        txt(cv, "19 DE JANEIRO DE 2012", W / 2, 640, TF_SB, 30, OR, int(255 * q), track=4, shadow=False)
        txt(cv, "Pedido de Chapter 11 nos EUA", W / 2, 700, TF_MD, 24, MUT, int(255 * q), shadow=False)

def s_reflect(cv, t):
    a, b = L[12]; t2 = wt("difícil", a + 1.0)
    background(cv, t)
    k = eo(prog(t, a, a + .5))
    cv.drawCircle(300, 1000, 380, rad(300, 1000, 380, [(EB, int(60 * k)), (EB, 0)]))
    camera_art(cv, 300, 1010, .8, 1.0, EB, 3, t=t, glow_a=90)
    fade = 1 - .7 * eo(prog(t, t2, t2 + 1.2))
    film_art(cv, 800, 1010, 1.0, 1.0, MUT, 3, int(255 * fade), 0)
    txt(cv, "FUTURO", 300, 1300, TF_SB, 26, EB, int(255 * k), track=6, shadow=False)
    txt(cv, "PASSADO", 800, 1300, TF_SB, 26, MUT, int(255 * k * fade), track=6, shadow=False)
    txt(cv, "ELA VIU O FUTURO PRIMEIRO.", W / 2, 470, TF_B, 92, WH, int(255 * k), track=3)
    txt(cv, "O DIFÍCIL FOI LARGAR O PASSADO.", W / 2, 590, TF_B, 80, GD, int(255 * eo(prog(t, t2, t2 + .4))), track=3)

def s_end(cv, t):
    a, b = L[13]
    background(cv, t)
    k = eo(prog(t, a, a + .5))
    for i_, (s, col) in enumerate((("QUE GIGANTE", WH), ("DE HOJE ESTÁ", WH), ("COMETENDO O", WH), ("MESMO ERRO?", GD))):
        q = eo(prog(t, a + i_ * .18, a + .4 + i_ * .18))
        txt(cv, s, W / 2, 720 + i_ * 150 + (1 - q) * 20, TF_B, 160, col, int(255 * q), track=4)
    kicker(cv, "DEIXE SUA RESPOSTA NOS COMENTÁRIOS", 1330, int(255 * eo(prog(t, a + 1.4, a + 1.8))))
    kl = eio(prog(t, b + .1, b + .6))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG0, int(255 * kl)))
        cv.drawLine(W / 2 - 200 * kl, 1010, W / 2 + 200 * kl, 1010, P(GD, int(255 * kl), stroke=2))
        txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 980, TF_B, 120, WH, int(255 * kl), track=8)
        txt(cv, "HISTÓRIAS EXTRAORDINÁRIAS POR TRÁS DE GRANDES NEGÓCIOS", W / 2, 1060, TF_SB, 20, MUT, int(255 * kl), track=4, shadow=False)

SCENES = [(s_hook, 0.0, L[2][0] - .1), (s_teaser, L[2][0] - .1, L[3][0] - .1), (s_market, L[3][0] - .1, L[4][0] - .1),
          (s_lab, L[4][0] - .1, L[5][0] - .1), (s_tape, L[5][0] - .1, L[6][0] - .05), (s_works, L[6][0] - .05, L[7][0] - .05),
          (s_tension, L[7][0] - .05, L[8][0] - .1), (s_board, L[8][0] - .1, L[9][0] - .1), (s_motive, L[9][0] - .1, L[10][0] - .1),
          (s_patent, L[10][0] - .1, L[11][0] - .1), (s_timeline, L[11][0] - .1, L[12][0] - .1), (s_reflect, L[12][0] - .1, L[13][0] - .1),
          (s_end, L[13][0] - .1, TOTAL)]
XF = .3

# ---------- legendas ----------
CHUNKS = {
 1: [("Essa empresa inventou", 3), ("a *câmera digital*.", 3), ("E foi justamente", 3), ("a câmera digital", 3), ("que *quase acabou* com ela.", 5)],
 2: [("E tudo começou", 3), ("com *uma frase*,", 3), ("numa sala de reunião.", 4)],
 3: [("Anos 70:", 2), ("quase todo filme vendido", 4), ("nos EUA é *Kodak*.", 5)],
 4: [("Em *1975*,", 4), ("o jovem engenheiro", 3), ("*Steven Sasson*", 2), ("monta uma geringonça", 3), ("do tamanho de", 3), ("uma *torradeira*.", 2)],
 5: [("Cada foto leva", 3), ("*23 segundos* pra gravar...", 6), ("numa *fita cassete*.", 3)],
 6: [("Mas *funciona*:", 2), ("sem um único", 3), ("rolo de *filme*.", 3)],
 7: [("Agora vem a parte", 4), ("que *ninguém esperava*.", 3)],
 8: [("Ele mostra aos chefes.", 4), ("E, segundo Sasson,", 3), ("a resposta foi:", 3), ("“*Bonitinho*...", 1), ("mas *não conte*", 3), ("pra *ninguém*.”", 2)],
 9: [("O motivo?", 2), ("A Kodak vivia", 3), ("de vender *filme*.", 3)],
 10: [("A empresa *patenteou* a ideia,", 5), ("*lucrou* com ela...", 3), ("e seguiu apostando", 3), ("no *filme*.", 2)],
 11: [("Só que o mundo", 4), ("*não esperou*.", 2), ("Em *2012*,", 5), ("a Kodak pediu", 3), ("*recuperação judicial*.", 2)],
 12: [("Ela viu o *futuro*", 4), ("primeiro.", 1), ("O difícil foi", 3), ("largar o *passado*.", 3)],
 13: [("Que gigante de hoje", 4), ("está cometendo", 2), ("o mesmo *erro*?", 3)],
}
SPOKEN = {i: s for i, s in enumerate([
 "Essa empresa inventou a câmera digital E foi justamente a câmera digital que quase acabou com ela",
 "E tudo começou com uma frase numa sala de reunião",
 "Anos setenta quase todo filme vendido nos Estados Unidos é Kodak",
 "Em setenta e cinco o jovem engenheiro Steven Sasson monta uma geringonça do tamanho de uma torradeira",
 "Cada foto leva vinte e três segundos pra gravar numa fita cassete",
 "Mas funciona sem um único rolo de filme",
 "Agora vem a parte que ninguém esperava",
 "Ele mostra aos chefes E segundo Sasson a resposta foi Bonitinho mas não conte pra ninguém",
 "O motivo A Kodak vivia de vender filme",
 "A empresa patenteou a ideia lucrou com ela e seguiu apostando no filme",
 "Só que o mundo não esperou Em dois mil e doze a Kodak pediu recuperação judicial",
 "Ela viu o futuro primeiro O difícil foi largar o passado",
 "Que gigante de hoje está cometendo o mesmo erro",
], start=1)}
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
            rich(cv, parts, W / 2, 1450 + (1 - k) * 10, TF_SB, 58, int(255 * k))
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
