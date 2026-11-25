# Império de Ideias — EP03 Havaianas — estilo PREMIUM (estética documental / editorial)
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


# ======================= EP03 — HAVAIANAS =======================
CHAPTERS = [(1, 2, "PRÓLOGO", "1962 — HOJE"), (3, 5, "01  O CHINELO DO POVO", "1962"), (6, 8, "02  A CRISE", "ANOS 80"),
            (9, 11, "03  A VIRADA", "ANOS 90"), (12, 14, "04  O ÍCONE", "HOJE")]
BLUE = "#2563EB"; SOLE_W = "#E5E7EB"

def sole_path():
    pa = skia.Path(); pa.moveTo(0, -240)
    pa.cubicTo(95, -240, 112, -150, 100, -60); pa.cubicTo(92, 10, 68, 40, 76, 110); pa.cubicTo(86, 200, 52, 240, 0, 240)
    pa.cubicTo(-52, 240, -86, 200, -76, 110); pa.cubicTo(-68, 40, -92, 10, -100, -60); pa.cubicTo(-112, -150, -95, -240, 0, -240); pa.close()
    return pa
SOLE = sole_path()
def inner_path():
    pa = skia.Path(SOLE); m = skia.Matrix(); m.setScale(.86, .9); pa.transform(m); return pa
INNER = inner_path()
STRAP = [LN((0, -150), (-92, -10)), LN((0, -150), (92, -10))]
def grains_paths():
    ps = []
    for j in range(7):
        for i in range(-2, 3):
            ps.append(LN((i * 26 - 5, -200 + j * 62 + (i % 2) * 20), (i * 26 + 5, -200 + j * 62 + (i % 2) * 20)))
    return ps
GRAINP = grains_paths()

def sandal(cv, x, y, s, p, line=GD, fill=None, strap=None, a=255, sx=1.0, rot=0, flag=0.0, glow_a=50, grains=True):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * sx, s)
    if fill is not None and p > .3:
        cv.drawPath(SOLE, P(fill, int(a * cl((p - .3) / .5))))
    stroke(cv, [SOLE, INNER], p, line, 3 / s, a, glow_a)
    if grains and p > .5: stroke(cv, GRAINP, cl((p - .5) * 2), line, 2 / s, int(a * .45), 0)
    q = cl((p - .4) / .6)
    if q > 0:
        if strap is not None:
            stroke(cv, STRAP, q, strap, 20 / s * s, a, 0)
            cv.drawCircle(0, -150, 14, P(strap, a))
        else:
            stroke(cv, STRAP, q, line, 4 / s, a, glow_a)
            cv.drawCircle(0, -150, 10, P(line, a, stroke=3 / s))
    if flag > 0:  # bandeirinha na tira (geométrica)
        cv.save(); cv.translate(-52, -84); cv.rotate(-56); k = flag
        cv.drawRect(skia.Rect.MakeXYWH(-34 * k, -22 * k, 68 * k, 44 * k), P("#16A34A", a))
        pa = path([(0, -18 * k), (28 * k, 0), (0, 18 * k), (-28 * k, 0)]); cv.drawPath(pa, P(GD, a))
        cv.drawCircle(0, 0, 10 * k, P("#1D4ED8", a)); cv.restore()
    cv.restore()

def zori(cv, x, y, s, p, a=255):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    ps = [SOLE] + [LN((-80 + abs(j - 7) * 3, -200 + j * 30), (80 - abs(j - 7) * 3, -200 + j * 30)) for j in range(15)]
    stroke(cv, ps, p, "#D6B98C", 3 / s, a, 30); stroke(cv, STRAP, cl((p - .5) * 2), "#D6B98C", 8 / s, a, 0)
    cv.restore()

def redacted_trick(cv, t, y, k, reveal=0.0):
    if k <= 0: return
    cv.save(); cv.translate(0, (1 - k) * 60)
    card(cv, W / 2, y, 860, 400, int(255 * cl(k)), rot=-1.5)
    al = int(255 * cl(k))
    txt(cv, "ARQUIVO HAVAIANAS  ·  BRASIL, ANOS 90", -390, -140, TF_SB, 21, "#6B6455", al, align="l", track=3, shadow=False)
    cv.drawLine(-390, -118, 390, -118, P("#B8AE98", al, stroke=2))
    txt(cv, "O TRUQUE QUE VIROU O JOGO:", -390, -62, TF_XB, 28, INK, al, align="l", track=1, shadow=False)
    if reveal > 0:
        txt(cv, "VIRAR A SOLA.", -390, 40, TF_B, 120, INK, al, align="l", shadow=False)
        k2 = eo(cl(reveal * 2 - 1))
        txt(cv, "IDEIA DOS SURFISTAS  ·  UMA COR SÓ", -390, 115, TF_B, 58, OR, int(al * k2), align="l", track=2, shadow=False)
    for j, (x0, w0, y0, h0) in enumerate(((-390, 620, -32, 95), (-390, 760, 68, 66))):
        r = cl(reveal * 1.6 - j * .5); ww = w0 * (1 - eio(r))
        if ww > 1:
            rrect(cv, x0 + w0 - ww, y0, ww, h0, 4, P("#0B0D12", al))
            if 0 < r < 1: cv.drawRect(skia.Rect.MakeXYWH(x0 + w0 - ww - 6, y0, 12, h0), glow(OR, 230, 10))
    txt(cv, "CONFIDENCIAL ATÉ A VIRADA" if reveal <= 0 else "REVELADO", 390, 175, TF_SB, 18, "#8A8272", al, align="r", track=4, shadow=False)
    cv.restore(); cv.restore()

def brand(cv, y, a=255, size=190, col=GD):
    txt(cv, "HAVAIANAS", W / 2, y, TF_B, size, col, a, track=10)

# ---------- cenas ----------
def s_hook(cv, t):
    a, b = L[1]; tp = wt("chinelo", a + 1.5)
    background(cv, t, "#14110A")
    brand(cv, 560, 255, 210)
    kicker(cv, "A MARCA DO SEU PÉ", 400, 255)
    sandal(cv, W / 2, 960, .78, eio(prog(t, 0, 1.4)) * .6 + .4, GD, glow_a=70)
    # carimbo de tensão (visível desde o 1º quadro)
    k = 1.0 if t < tp - .2 else 1.0
    cv.save(); cv.translate(W / 2, 1210); cv.rotate(-6); s_ = 1 + .25 * (1 - back(prog(t, tp - .25, tp + .15))) if t >= tp - .25 else 1; cv.scale(s_, s_)
    rrect(cv, -400, -70, 800, 130, 10, P("#0B0D12", 215)); rrect(cv, -400, -70, 800, 130, 10, P(OR, 255, stroke=6))
    txt(cv, "“CHINELO DE POBRE”", 0, 30, TF_B, 104, OR, int(255 * k), track=4); cv.restore()
    txt(cv, "JÁ FOI CHAMADA DE", W / 2, 680, TF_B, 84, WH, 255, track=5)

def s_teaser(cv, t):
    a, b = L[2]
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .4)); txt(cv, "A VIRADA VEIO", W / 2, 430, TF_B, 96, MUT, int(255 * k), track=4)
    txt(cv, "DE UM TRUQUE.", W / 2, 545, TF_B, 120, WH, int(255 * eo(prog(t, a + .6, a + 1.1))), track=3)
    redacted_trick(cv, t, 880, back(prog(t, a + .5, a + 1.1)))
    kicker(cv, "E NEM FOI IDEIA DA MARCA", 1210, int(255 * eo(prog(t, wt("nem", a) - .1, wt("nem", a) + .3))), OR)

def s_1962(cv, t):
    a, b = L[3]; tz = wt("zori", a + 2); tb = wt("borracha", a + 2)
    background(cv, t, "#0B1A2E", grid=True)
    kicker(cv, "SÃO PAULO ALPARGATAS  ·  BRASIL", 410, int(255 * eo(prog(t, a, a + .4))))
    p = eio(prog(t, a + .1, a + 1.6)); yr = int(round(1900 + 62 * p))
    txt(cv, str(yr), W / 2, 680, TF_B, 280, GD if p >= 1 else WH, int(255 * eo(prog(t, a, a + .3))), track=8)
    # zori (palha) -> borracha
    m = eio(prog(t, tz + .3, tz + 1.0))
    qz = eio(prog(t, tb - .4, tz + .4))
    if m < 1: zori(cv, W / 2 - 220 * m, 1030, .62, qz, int(255 * (1 - .6 * m)))
    if m > 0:
        sandal(cv, W / 2 + 220 * m, 1030, .62, eio(prog(t, tz + .3, tz + 1.4)), "#BFDBFE", glow_a=70)
        cv.drawLine(W / 2 - 60, 1030, W / 2 + 60 * m, 1030, P(GD, int(200 * m), stroke=3))
    q1 = eo(prog(t, tz - .2, tz + .2))
    txt(cv, "ZORI  ·  JAPÃO", W / 2 - 220 * max(m, .0001) if m > 0 else W / 2, 1265, TF_SB, 24, "#D6B98C", int(255 * q1), track=4, shadow=False)
    if m > .5: txt(cv, "BORRACHA  ·  BRASIL", W / 2 + 220, 1265, TF_SB, 24, "#BFDBFE", int(255 * eo((m - .5) * 2)), track=4, shadow=False)

def s_cheap(cv, t):
    a, b = L[4]; tz = wt("azul", a); tc = wt("Calçado", a)
    background(cv, t)
    k = eo(prog(t, a, a + .3)); txt(cv, "BARATA.", W / 2, 470, TF_B, 140, WH, int(255 * k), track=6)
    q = eo(prog(t, tz - .1, tz + .3))
    rich(cv, [("AZUL ", BLUE), ("E ", MUT), ("BRANCA.", WH)], W / 2, 600, TF_B, 120, int(255 * q), track=4)
    pf = eio(prog(t, a + .1, tz + .6))
    sandal(cv, W / 2 - 150, 960, .62, pf, "#93C5FD", fill=SOLE_W if q > 0 else None, strap=BLUE if q > 0 else None, a=255, rot=-8, glow_a=40)
    sandal(cv, W / 2 + 150, 960, .62, pf, "#93C5FD", fill=SOLE_W if q > 0 else None, strap=BLUE if q > 0 else None, a=255, rot=8, glow_a=40, sx=-1)
    q2 = eo(prog(t, tc - .1, tc + .3))
    if q2 > 0:
        rrect(cv, W / 2 - 360, 1190, 720, 84, 42, P(WH, int(20 * q2))); rrect(cv, W / 2 - 360, 1190, 720, 84, 42, P(GD, int(200 * q2), stroke=2))
        txt(cv, "CALÇADO DE TRABALHADOR", W / 2, 1245, TF_SB, 32, WH, int(255 * q2), track=4, shadow=False)

def s_inflation(cv, t):
    a, b = L[5]; tl = wt("lista", a); ta = wt("arroz", a + 2); tf = wt("feijão", a + 2)
    background(cv, t, "#0E1320")
    k = eo(prog(t, a, a + .4)); txt(cv, "ANOS 80", W / 2, 470, TF_B, 160, WH, int(255 * k), track=8)
    txt(cv, "INFLAÇÃO NAS ALTURAS NO BRASIL", W / 2, 540, TF_SB, 26, OR, int(255 * eo(prog(t, a + .3, a + .7))), track=4, shadow=False)
    kc = back(prog(t, tl - .2, tl + .4))
    if kc > 0:
        cv.save(); cv.translate(0, (1 - cl(kc)) * 80)
        card(cv, W / 2, 930, 760, 560, int(255 * cl(kc)), rot=1.2); al = int(255 * cl(kc))
        txt(cv, "LISTA DO GOVERNO  ·  CONTROLE DA INFLAÇÃO", -340, -220, TF_SB, 20, "#6B6455", al, align="l", track=2, shadow=False)
        cv.drawLine(-340, -198, 340, -198, P("#B8AE98", al, stroke=2))
        rows = [("ARROZ", tl), ("FEIJÃO", tl + .15), ("SANDÁLIAS HAVAIANAS", tl + .6)]
        for j, (nm, tt) in enumerate(rows):
            q = eo(prog(t, tt - .1, tt + .25)); yy = -110 + j * 120
            if q <= 0: continue
            col = INK if j < 2 else "#B45309"
            rrect(cv, -340, yy - 40, 48, 48, 6, P(INK, int(al * q), stroke=3))
            stroke(cv, [LN((-330, yy - 16), (-318, yy - 2), (-298, yy - 32))], q, "#B45309" if j == 2 else INK, 5, al, 0)
            txt(cv, nm, -270, yy, TF_B, 66 if j < 2 else 70, col, int(al * q), align="l", track=2, shadow=False)
            hl = eo(prog(t, (ta, tf, 99)[j] - .1, (ta, tf, 99)[j] + .2)) if j < 2 else 0
            if hl > 0: cv.drawLine(-270, yy + 12, -270 + tw(nm, TF_B, 66, 2) * hl, yy + 12, P("#B45309", al, stroke=5))
        if t > tf + .4:
            cv.drawLine(-340, 240, -340 + 680 * eo(prog(t, tf + .4, tf + 1)), 240, P("#B8AE98", al, stroke=2))
        cv.restore(); cv.restore()

def s_fakes(cv, t):
    a, b = L[6]; tl = wt("legítimas", a + 1)
    background(cv, t, "#120C0C")
    k = eo(prog(t, a, a + .3)); txt(cv, "IMITAÇÕES", W / 2, 470, TF_B, 150, WH, int(255 * k), track=6)
    r = random.Random(3)
    for j in range(7):
        q = eo(prog(t, a + .15 + j * .12, a + .5 + j * .12))
        if q <= 0: continue
        x = 170 + j * 125; y = 860 + (j % 2) * 120; jit = random.Random(int(t * 12) + j)
        sandal(cv, x + jit.uniform(-3, 3), y, .38, q, "#6B7280", a=int(200 * q), rot=r.uniform(-18, 18), glow_a=0, grains=False)
    qs = prog(t, tl - .25, tl + .15)
    if qs > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P("#000000", int(120 * eo(qs))))
        sandal(cv, W / 2, 930, .7, 1.0, GD, glow_a=90)
        cv.save(); cv.translate(W / 2, 1200); cv.rotate(-6); s_ = 1 + .6 * (1 - cl(back(qs))); cv.scale(s_, s_)
        rrect(cv, -330, -80, 660, 130, 10, P("#0B0D12", 220)); rrect(cv, -330, -80, 660, 130, 10, P(GD, 255, stroke=6))
        txt(cv, "AS LEGÍTIMAS", 0, 25, TF_B, 110, GD, int(255 * cl(qs * 3)), track=6); cv.restore()

def s_fall(cv, t):
    a, b = L[7]; tv = wt("vendas", a + 1)
    background(cv, t, "#120C0C")
    k = eo(prog(t, a, a + .4)); txt(cv, "A FAMA DE", W / 2, 450, TF_B, 96, MUT, int(255 * k), track=5)
    txt(cv, "“CHINELO DE POBRE”", W / 2, 570, TF_B, 120, OR, int(255 * eo(prog(t, a + .4, a + .8))), track=3)
    # seta de queda (qualitativa, sem números)
    p = eio(prog(t, tv - .3, tv + .9))
    pts = [(150, 760), (330, 800), (470, 780), (620, 900), (760, 960), (930, 1130)]
    pa = path(pts, close=False)
    for j in range(5): cv.drawLine(150, 760 + j * 100, 930, 760 + j * 100, P(LINE, 160, stroke=1))
    stroke(cv, [pa], p, OR, 8, 255, 120)
    if p >= 1:
        cv.save(); cv.translate(930, 1130); cv.rotate(math.degrees(math.atan2(170, 170)))
        cv.drawPath(path([(10, 0), (-30, -22), (-30, 22)]), P(OR)); cv.restore()
    txt(cv, "VENDAS EM QUEDA", W / 2, 1260, TF_B, 80, WH, int(255 * eo(prog(t, tv - .1, tv + .3))), track=5)

def s_tension(cv, t):
    a, b = L[8]
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#040508"))
    hb = max(0, math.sin((t - a) * 2 * math.pi * 1.2)) ** 10
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, H * .7, [("#000000", 0), ("#3A0A00", int(140 * hb))]))
    sandal(cv, W / 2, 940, .9, 1.0, "#1F2937", glow_a=0, grains=False)
    reveal_txt(cv, "E AQUI", W / 2, 880, TF_B, 140, WH, prog(t, a, a + .5), track=6)
    reveal_txt(cv, "A HISTÓRIA VIRA", W / 2, 1020, TF_B, 130, OR, prog(t, a + .6, a + 1.4), track=4)

def s_flip(cv, t):
    a, b = L[9]; ts = wt("surfistas", a); tv = wt("viravam", ts); tc = wt("cor", tv)
    background(cv, t, "#0B1A2E")
    kicker(cv, "ANOS 90  ·  PRAIAS DO BRASIL", 400, int(255 * eo(prog(t, a, a + .4))))
    # cartão do loop: revelado
    redacted_trick(cv, t, 700, 1.0, reveal=prog(t, tv - .1, tv + 1.1))
    # sola virando
    u = eio(prog(t, tv + .2, tv + 1.2)); sx = math.cos(math.pi * u)
    back_side = sx < 0
    fill = BLUE if back_side else SOLE_W
    sandal(cv, W / 2, 1100, .46, 1.0, "#93C5FD" if not back_side else "#BFDBFE", fill=fill, strap=BLUE if (u <= 0 or u >= 1) else None,
           sx=max(abs(sx), .03), glow_a=40)
    q = eo(prog(t, tc - .2, tc + .2))
    if q > 0: txt(cv, "UMA COR SÓ", W / 2, 1330, TF_B, 70, GD, int(255 * q), track=6)

def s_top(cv, t):
    a, b = L[10]; th = wt("Havaianas", a + 1)
    background(cv, t)
    k = eo(prog(t, a, a + .4)); txt(cv, "O TRUQUE VIRA PRODUTO", W / 2, 440, TF_B, 90, MUT, int(255 * k), track=4)
    q = back(prog(t, th - .2, th + .25))
    if q > 0:
        cv.save(); cv.translate(W / 2, 620); s_ = cl(q, 0, 1.15); cv.scale(s_, s_)
        txt(cv, "HAVAIANAS TOP", 0, 0, TF_B, 170, GD, 255, track=6); cv.restore()
        txt(cv, "TODA DE UMA COR", W / 2, 690, TF_SB, 30, WH, int(255 * cl(q)), track=6, shadow=False)
    cols = [BLUE, OR, GD, "#F9FAFB", "#374151", "#16A34A"]
    for j, c in enumerate(cols):
        qq = eo(prog(t, a + .4 + j * .15, a + .9 + j * .15))
        if qq <= 0: continue
        x = 160 + j * 152; y = 1010 + (1 - qq) * 60 + 18 * math.sin(t * 2 + j)
        sandal(cv, x, y, .36, 1.0, c, fill=c, strap=c, a=int(255 * qq), rot=-6 + j * 2.5, glow_a=0, grains=False)
        cv.drawPath(SOLE, P("#000000", 0))

def s_1998(cv, t):
    a, b = L[11]; tb = wt("bandeira", a + 1)
    background(cv, t, "#0A1A12")
    kk = eo(prog(t, a, a + .3)); txt(cv, "1998", W / 2, 520, TF_B, 220, WH, int(255 * kk), track=8)
    txt(cv, "COPA DO MUNDO  ·  FRANÇA", W / 2, 600, TF_SB, 30, GD, int(255 * eo(prog(t, wt("Copa", a) - .1, wt("Copa", a) + .3))), track=5, shadow=False)
    sandal(cv, W / 2, 980, .72, eio(prog(t, a + .2, a + 1.3)), "#86EFAC", fill="#F9FAFB" if t > tb - .6 else None, strap="#16A34A" if t > tb - .6 else None,
           flag=eo(prog(t, tb - .1, tb + .4)), glow_a=50)
    txt(cv, "A BANDEIRA VAI PARA A TIRA", W / 2, 1270, TF_B, 70, WH, int(255 * eo(prog(t, tb - .1, tb + .3))), track=4)

def s_today(cv, t):
    a, b = L[12]; tm = wt("duzentos", a)
    background(cv, t)
    y = 470; x0, x1 = 120, W - 120; p = eio(prog(t, a, a + 1.2))
    cv.drawLine(x0, y, x0 + (x1 - x0) * p, y, P(WH, 200, stroke=3))
    for lab, fx, col in (("1962", 0, MUT), ("1998", .55, OR), ("HOJE", 1, GD)):
        if p >= fx - .001:
            xx = x0 + (x1 - x0) * fx; cv.drawCircle(xx, y, 12, P(col)); cv.drawCircle(xx, y, 26, P(col, 120, stroke=2))
            txt(cv, lab, xx, y - 48, TF_B, 56, col, 255, track=2)
    q = eo(prog(t, tm - .3, tm + .1))
    n = int(round(200 * eio(prog(t, tm - .2, tm + 1.0))))
    txt(cv, "MAIS DE", W / 2, 680, TF_B, 80, WH, int(255 * q), track=6)
    txt(cv, f"{n}", W / 2, 960, TF_B, 330, GD, int(255 * q), track=6)
    txt(cv, "MILHÕES DE PARES POR ANO", W / 2, 1070, TF_B, 80, WH, int(255 * eo(prog(t, tm + .5, tm + .9))), track=4)
    txt(cv, "Fonte: dados da Alpargatas citados por Wikipedia, Highsnobiety (2020) e Ara (2026)", W / 2, 1270, TF_MD, 20, MUT, int(255 * eo(prog(t, tm + .6, tm + 1.0))), shadow=False)

def s_reflect(cv, t):
    a, b = L[13]; tm = wt("mudou", a + 1)
    background(cv, t, "#14110A")
    k = eo(prog(t, a, a + .4)); txt(cv, "A BORRACHA", W / 2, 470, TF_B, 140, WH, int(255 * k), track=6)
    txt(cv, "É A MESMA.", W / 2, 600, TF_B, 140, WH, int(255 * eo(prog(t, a + .4, a + .8))), track=6)
    u = eio(prog(t, tm - .4, tm + .6))
    sandal(cv, W / 2 - 170, 950, .52, 1.0, lerp_col(MUT, GD, u), fill=None, glow_a=int(80 * u), rot=-8)
    sandal(cv, W / 2 + 170, 950, .52, 1.0, lerp_col(MUT, GD, u), fill=None, glow_a=int(80 * u), rot=8, sx=-1)
    q = eo(prog(t, tm - .1, tm + .3))
    txt(cv, "O QUE MUDOU", W / 2, 1210, TF_B, 96, MUT, int(255 * q), track=5)
    txt(cv, "FOI O OLHAR.", W / 2, 1310, TF_B, 110, GD, int(255 * eo(prog(t, tm + .4, tm + .8))), track=5)

def lerp_col(c1, c2, u):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02X}" for x, y in zip(a, b))

def s_end(cv, t):
    a, b = L[14]; tv = a
    background(cv, t)
    for i_, (s, col) in enumerate((("QUE PRODUTO", WH), ("BARATO AINDA VAI", WH), ("VIRAR DESEJO?", GD))):
        q = eo(prog(t, tv + .3 + i_ * .25, tv + .7 + i_ * .25))
        txt(cv, s, W / 2, 720 + i_ * 160 + (1 - q) * 20, TF_B, 140, col, int(255 * q), track=4)
    sandal(cv, W / 2, 1150, .3, eio(prog(t, a + .4, a + 1.4)), GD, glow_a=40, grains=False)
    kicker(cv, "CONTA NOS COMENTÁRIOS", 1290, int(255 * eo(prog(t, tv + 1.4, tv + 1.8))))
    kl = eio(prog(t, b + .2, b + .7))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG0, int(255 * kl)))
        cv.drawLine(W / 2 - 200 * kl, 1010, W / 2 + 200 * kl, 1010, P(GD, int(255 * kl), stroke=2))
        txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 980, TF_B, 120, WH, int(255 * kl), track=8)
        txt(cv, "HISTÓRIAS EXTRAORDINÁRIAS POR TRÁS DE GRANDES NEGÓCIOS", W / 2, 1060, TF_SB, 20, MUT, int(255 * kl), track=4, shadow=False)

FNS = [s_hook, s_teaser, s_1962, s_cheap, s_inflation, s_fakes, s_fall, s_tension, s_flip, s_top, s_1998, s_today, s_reflect, s_end]
SCENES = []
for i_, fn in enumerate(FNS, start=1):
    s0 = 0.0 if i_ == 1 else L[i_][0] - .1
    e0 = TOTAL if i_ == len(FNS) else L[i_ + 1][0] - .1
    SCENES.append((fn, s0, e0))
XF = .3

CHUNKS = {
 1: [("A *Havaianas* do seu pé", 5), ("já foi chamada", 3), ("de *chinelo de pobre*.", 4)],
 2: [("E a *virada* veio", 4), ("de um *truque*", 3), ("que nem foi da marca.", 5)],
 3: [("*1962*.", 6), ("Nasce uma sandália", 3), ("de *borracha*", 2), ("inspirada no *zori* japonês.", 4)],
 4: [("*Barata*,", 1), ("*azul e branca*.", 3), ("Calçado de *trabalhador*.", 3)],
 5: [("Nos *anos 80*,", 3), ("entra numa *lista*", 3), ("do governo", 2), ("contra a *inflação*,", 3), ("com *arroz e feijão*.", 4)],
 6: [("Surgem *imitações*.", 2), ("E a marca avisa:", 4), ("*as legítimas*.", 2)],
 7: [("Mas, com a fama", 4), ("de *chinelo de pobre*,", 4), ("as *vendas caem*.", 3)],
 8: [("E aqui a história *vira*.", 5)],
 9: [("Nos *anos 90*,", 3), ("*surfistas* viravam", 2), ("a *sola ao contrário*,", 4), ("para ficar", 2), ("de *uma cor só*.", 4)],
 10: [("A empresa transforma", 3), ("o truque em produto:", 4), ("a *Havaianas Top*.", 3)],
 11: [("Em *98*,", 4), ("na *Copa*,", 2), ("a *bandeira do Brasil*", 4), ("vai para a tira.", 4)],
 12: [("Hoje, são mais de", 4), ("*200 milhões*", 2), ("de pares por ano.", 4)],
 13: [("A borracha", 2), ("é a *mesma*.", 3), ("O que mudou", 3), ("foi o *olhar*.", 3)],
 14: [("E você:", 2), ("que produto *barato*", 3), ("ainda vai virar *desejo*?", 4)],
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
