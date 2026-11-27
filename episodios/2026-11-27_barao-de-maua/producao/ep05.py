# Império de Ideias — EP05 Barão de Mauá — estilo PREMIUM (estética documental / editorial)
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



def lerp_col(c1, c2, u):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02X}" for x, y in zip(a, b))

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

def xmark(cv, x, y, sz, q, col=OR):
    if q <= 0: return
    stroke(cv, [LN((x - sz, y - sz), (x + sz, y + sz)), LN((x + sz, y - sz), (x - sz, y + sz))], q, col, 10, 255, 120)



# ======================= EP05 — BARÃO DE MAUÁ =======================
CHAPTERS = [(1, 2, "PRÓLOGO", "1851 — 1878"), (3, 5, "01  O BANQUEIRO", "1851 — 1853"), (6, 7, "02  O IMPÉRIO", "1854 — 1874"),
            (8, 11, "03  O PEDIDO", "1875"), (12, 14, "04  A QUEDA", "1875 — 1878")]
SRC = {1: "FONTE: AGÊNCIA SENADO (2023)", 2: "FONTES: CAPITAL ABERTO · REVISTA CLIO/UFPE (2024)", 3: "FONTE: REVISTA PESQUISA FAPESP (2005)",
       4: "FONTE: AGÊNCIA SENADO (2023)", 5: "FONTES: AGÊNCIA SENADO · REVISTA CLIO/UFPE", 6: "FONTES: REVISTA PESQUISA FAPESP · DIÁRIO DO RIO",
       7: "FONTES: CAPITAL ABERTO · TODA MATÉRIA", 9: "FONTES: CAPITAL ABERTO · REVISTA CLIO/UFPE", 10: "FONTES: CAPITAL ABERTO · REVISTA CLIO/UFPE",
       11: "FONTES: CAPITAL ABERTO · REVISTA CLIO/UFPE", 12: "FONTES: REVISTA CLIO/UFPE · CAPITAL ABERTO"}

def footer(cv, t, i):
    if i not in SRC: return
    a, b = L[i]; k = eo(prog(t, a + .2, a + .6))
    txt(cv, SRC[i], W / 2, 336, TF_SB, 19, MUT, int(170 * k), track=3, shadow=False)

# ---------- ilustrações em traço técnico ----------
def facade_paths():
    ps = [path([(-330, -150), (0, -300), (330, -150)]), LN((-350, -150), (350, -150)), LN((-350, -125), (350, -125)),
          LN((-360, 260), (360, 260)), LN((-380, 290), (380, 290))]
    for k in range(6):
        x = -275 + k * 110
        ps += [RR(x - 26, -110, 52, 360, 4), LN((x - 36, -110), (x + 36, -110)), LN((x - 36, 250), (x + 36, 250))]
    ps.append(CIR(0, -205, 34))
    return ps
FACADE = facade_paths()
def facade(cv, x, y, s, p, color=GD, a=255, glow_a=50):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, FACADE, p, color, 3 / s, a, glow_a); cv.restore()

def hat_paths():
    ps = [path([(-70, -40), (-60, -190), (60, -190), (70, -40)]), LN((-140, -40), (140, -40)), LN((-66, -70), (66, -70))]
    head = skia.Path(); head.addOval(skia.Rect.MakeXYWH(-80, -40, 160, 200)); ps.append(head)
    col = skia.Path(); col.moveTo(-60, 150); col.lineTo(0, 210); col.lineTo(60, 150); ps.append(col)
    sh = skia.Path(); sh.moveTo(-230, 380); sh.cubicTo(-220, 230, -120, 190, -60, 160); ps.append(sh)
    sh2 = skia.Path(); sh2.moveTo(230, 380); sh2.cubicTo(220, 230, 120, 190, 60, 160); ps.append(sh2)
    ps += [LN((0, 210), (0, 380)), path([(-22, 215), (22, 215), (0, 245)])]
    return ps
HAT = hat_paths()
def gentleman(cv, x, y, s, p, color=GD, a=255, glow_a=50):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, HAT, p, color, 3 / s, a, glow_a); cv.restore()

def loco_paths():
    ps = [RR(-200, -60, 260, 110, 10), RR(60, -130, 130, 180, 8), RR(80, -110, 90, 60, 6), path([(-170, -60), (-180, -150), (-120, -150), (-130, -60)]),
          LN((-200, 50), (-250, 90)), CIR(-140, 85, 38), CIR(-40, 85, 38), CIR(120, 75, 48), CIR(120, 75, 16), LN((-140, 85), (120, 75)), LN((-230, -10), (-200, -10))]
    return ps
LOCO = loco_paths()
def loco(cv, x, y, s, p, color=GD, a=255, glow_a=50, t=0.0, smoke=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s); stroke(cv, LOCO, p, color, 3 / s, a, glow_a)
    if smoke > 0:
        for k in range(5):
            ph = ((t * .8 + k / 5) % 1)
            cv.drawCircle(-150 - ph * 140, -170 - ph * 160, 18 + ph * 40, P(MUT, int(90 * (1 - ph) * smoke), stroke=3 / s))
    cv.restore()

def ship_paths():
    hull = path([(-200, 0), (200, 0), (150, 80), (-160, 80)])
    return [hull, LN((-20, 0), (-20, -230)), path([(-14, -220), (120, -40), (-14, -40)]), path([(-26, -200), (-150, -40), (-26, -40)]),
            LN((-240, 110), (-180, 100), (-120, 110), (-60, 100), (0, 110), (60, 100), (120, 110), (180, 100), (240, 110))]
SHIP = ship_paths()
def lamp_paths():
    return [LN((0, 240), (0, -40)), LN((-50, 240), (50, 240)), path([(-50, -40), (50, -40), (30, -150), (-30, -150)]), path([(-40, -150), (0, -190), (40, -150)]),
            LN((-60, -60), (60, -60))]
LAMP = lamp_paths()
def cable_paths():
    w = skia.Path(); w.moveTo(-260, 80); w.cubicTo(-120, -160, 120, -160, 260, 80)
    return [CIR(-260, 80, 26), CIR(260, 80, 26), w]
CABLE = cable_paths()

def doc_card(cv, t, y, k, reveal=0.0, stamp=0.0):
    """o pedido de socorro de 1875 (peça do loop aberto)."""
    if k <= 0: return
    cv.save(); cv.translate(0, (1 - k) * 60)
    card(cv, W / 2, y, 880, 470, int(255 * cl(k)), rot=-1.5)
    al = int(255 * cl(k))
    txt(cv, "BANCO MAUÁ & CIA.  ·  RIO DE JANEIRO, 1875", -400, -170, TF_SB, 21, "#6B6455", al, align="l", track=3, shadow=False)
    cv.drawLine(-400, -148, 400, -148, P("#B8AE98", al, stroke=2))
    txt(cv, "PEDIDO DE SOCORRO:", -400, -96, TF_XB, 28, INK, al, align="l", track=1, shadow=False)
    txt(cv, "3.000 CONTOS DE RÉIS", -400, -40, TF_B, 64, INK, al, align="l", track=2, shadow=False)
    txt(cv, "RESPOSTA / QUEM NEGOU:", -400, 30, TF_XB, 28, INK, al, align="l", track=1, shadow=False)
    if reveal > 0:
        txt(cv, "BANCO DO BRASIL", -400, 140, TF_B, 112, INK, al, align="l", shadow=False)
    for j, (x0, w0, y0, h0) in enumerate(((-400, 760, 52, 104),)):
        r = cl(reveal * 1.4); ww = w0 * (1 - eio(r))
        if ww > 1:
            rrect(cv, x0 + w0 - ww, y0, ww, h0, 4, P("#0B0D12", al))
            if 0 < r < 1: cv.drawRect(skia.Rect.MakeXYWH(x0 + w0 - ww - 6, y0, 12, h0), glow(OR, 230, 10))
    txt(cv, "CONFIDENCIAL ATÉ A VIRADA" if reveal <= 0 else "REVELADO", 400, 210, TF_SB, 18, "#8A8272", al, align="r", track=4, shadow=False)
    if stamp > 0:
        s_ = 1 + 1.2 * (1 - eo(cl(stamp * 2.5))); sa = int(255 * cl(stamp * 3))
        cv.save(); cv.translate(230, -60); cv.rotate(-12); cv.scale(s_, s_)
        rrect(cv, -170, -70, 340, 130, 10, P(OR, sa, stroke=8))
        txt(cv, "NEGADO", 0, 38, TF_B, 118, OR, sa, track=6, shadow=False); cv.restore()
    cv.restore(); cv.restore()

def brand(cv, y, a=255, size=200, col=GD):
    txt(cv, "BANCO DO BRASIL", W / 2, y, TF_B, size, col, a, track=3)

# ---------- cenas ----------
def s_hook(cv, t):
    a, b = L[1]; tn = wt("nasceu", a)
    background(cv, t, "#14110A")
    kicker(cv, "A ORIGEM QUE POUCOS CONHECEM", 400, 255)
    brand(cv, 590, 255, 160)
    p = eio(prog(t, 0, 1.4)) * .45 + .55
    facade(cv, W / 2, 930, .9, p, "#D6B98C", glow_a=50)
    cv.save(); cv.translate(W / 2, 1225); cv.rotate(-4)
    rrect(cv, -440, -120, 880, 210, 10, P("#0B0D12", 225)); rrect(cv, -440, -120, 880, 210, 10, P(GD, 255, stroke=6))
    txt(cv, "NASCEU DO BANCO", 0, -24, TF_B, 96, WH, 255, track=5)
    txt(cv, "DE UM SÓ HOMEM", 0, 70, TF_B, 96, GD, 255, track=5); cv.restore()
    footer(cv, t, 1)

def s_teaser(cv, t):
    a, b = L[2]; tq = wt("quebrou", a); tn = wt("ninguém", tq)
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .4)); txt(cv, "ANOS DEPOIS,", W / 2, 420, TF_B, 96, MUT, int(255 * k), track=4)
    txt(cv, "ESSE HOMEM QUEBROU", W / 2, 535, TF_B, 112, WH, int(255 * eo(prog(t, tq - .3, tq + .2))), track=3)
    doc_card(cv, t, 900, back(prog(t, tq + .2, tq + .8)))
    kicker(cv, "O “NÃO” VEIO DE ONDE NINGUÉM ESPERAVA", 1250, int(255 * eo(prog(t, tn - .3, tn + .2))), OR)
    footer(cv, t, 2)

def s_maua(cv, t):
    a, b = L[3]; ti = wt("Irineu", a); tb = wt("Barão", ti)
    background(cv, t, "#0B1A2E", grid=True)
    kicker(cv, "“O EMPRESÁRIO DO IMPÉRIO”", 400, int(255 * eo(prog(t, a, a + .4))))
    gentleman(cv, W / 2, 760, .95, eio(prog(t, a, a + 2.2)), GD, glow_a=60)
    txt(cv, "IRINEU EVANGELISTA DE SOUSA", W / 2, 1140, TF_B, 74, WH, int(255 * eo(prog(t, ti - .1, ti + .3))), track=3)
    q = back(prog(t, tb - .2, tb + .3))
    if q > 0:
        cv.save(); cv.translate(W / 2, 1290); s_ = cl(q, 0, 1.12); cv.scale(s_, s_)
        txt(cv, "BARÃO DE MAUÁ", 0, 0, TF_B, 150, GD, 255, track=6); cv.restore()
    footer(cv, t, 3)

def s_1851(cv, t):
    a, b = L[4]; tc = wt("cria", a); tb = wt("Brasil", wt("chamado", tc)) - .4
    background(cv, t)
    p = eio(prog(t, a, a + 1.6)); yr = int(round(1800 + 51 * p))
    txt(cv, str(yr), W / 2, 600, TF_B, 260, GD if p >= 1 else WH, int(255 * eo(prog(t, a, a + .3))), track=8)
    kicker(cv, "RIO DE JANEIRO", 680, int(255 * eo(prog(t, a + .4, a + .8))))
    q = back(prog(t, tb - .3, tb + .3))
    if q > 0:
        cv.save(); cv.translate(0, (1 - cl(q)) * 50)
        card(cv, W / 2, 960, 820, 330, int(255 * cl(q)), rot=1.2)
        txt(cv, "SOCIEDADE PRIVADA  ·  1851", -370, -100, TF_SB, 21, "#6B6455", 255, align="l", track=3, shadow=False)
        cv.drawLine(-370, -78, 370, -78, P("#B8AE98", 255, stroke=2))
        txt(cv, "BANCO DO BRASIL", 0, 40, TF_B, 130, INK, 255, track=4, shadow=False)
        txt(cv, "O 2º BANCO COM ESSE NOME", 0, 112, TF_SB, 26, "#6B6455", 255, track=3, shadow=False)
        cv.restore(); cv.restore()
    txt(cv, "VIRA O MAIOR DO RAMO NO IMPÉRIO", W / 2, 1250, TF_B, 62, WH, int(255 * eo(prog(t, tb + .5, tb + .9))), track=3)
    footer(cv, t, 4)

def s_1853(cv, t):
    a, b = L[5]; tg = wt("governo", a); tf = wt("funde", tg); tn = wt("nasce", tf)
    background(cv, t, "#0E1320")
    k = eo(prog(t, a, a + .3)); txt(cv, "1853", W / 2, 520, TF_B, 220, WH, int(255 * k), track=8)
    kicker(cv, "O GOVERNO DECIDE A FUSÃO", 600, int(255 * eo(prog(t, tg - .1, tg + .3))))
    m = eio(prog(t, tf, tn - .05))  # caixas convergem
    for j, (lab, yr, sx) in enumerate((("BANCO DO BRASIL", "DE MAUÁ · 1851", -1), ("BANCO COMERCIAL", "DO RIO · 1838", 1))):
        x = W / 2 + sx * 250 * (1 - m); al = int(255 * eo(prog(t, a + .2 + j * .3, a + .6 + j * .3)) * (1 - eio(prog(t, tn - .1, tn + .2))))
        if al <= 2: continue
        rrect(cv, x - 220, 780, 440, 190, 12, P("#0B0D12", int(al * .85))); rrect(cv, x - 220, 780, 440, 190, 12, P(GD if j == 0 else MUT, al, stroke=4))
        txt(cv, lab, x, 880, TF_B, 64, WH, al, track=3); txt(cv, yr, x, 930, TF_SB, 22, GD if j == 0 else MUT, al, track=3, shadow=False)
    q = back(prog(t, tn - .1, tn + .4))
    if q > 0:
        cv.save(); cv.translate(W / 2, 880); s_ = cl(q, 0, 1.1); cv.scale(s_, s_)
        rrect(cv, -420, -120, 840, 240, 14, P("#0B0D12", 230)); rrect(cv, -420, -120, 840, 240, 14, P(GD, 255, stroke=6))
        txt(cv, "BANCO DO BRASIL", 0, 20, TF_B, 140, GD, 255, track=5)
        txt(cv, "O DE HOJE  ·  DESDE A LEI DE 1853", 0, 80, TF_SB, 24, WH, 255, track=4, shadow=False); cv.restore()
    footer(cv, t, 5)

def s_rail(cv, t):
    a, b = L[6]; tp = wt("primeira", a); tk = wt("Catorze", tp)
    background(cv, t, "#0B1A2E", grid=True)
    k = eo(prog(t, a, a + .3)); txt(cv, "1854", W / 2, 520, TF_B, 220, WH, int(255 * k), track=8)
    txt(cv, "A PRIMEIRA FERROVIA DO PAÍS", W / 2, 640, TF_B, 80, GD, int(255 * eo(prog(t, tp - .1, tp + .3))), track=3)
    y = 1010; x0, x1 = 110, W - 110; pr_ = eio(prog(t, a + .3, b))
    cv.drawLine(x0, y + 70, x1, y + 70, P(MUT, 160, stroke=3)); cv.drawLine(x0, y + 90, x1, y + 90, P(MUT, 160, stroke=3))
    for xx in range(x0, x1, 40): cv.drawLine(xx, y + 64, xx + 14, y + 96, P(LINE, 220, stroke=4))
    cv.drawLine(x0, y + 70, x0 + (x1 - x0) * pr_, y + 70, P(GD, 255, stroke=4))
    lx = x0 + 150 + (x1 - x0 - 300) * pr_
    loco(cv, lx, y - 20, .55, eio(prog(t, a, a + 1.4)), GD, t=t, smoke=cl((t - a - 1.2) * 2))
    txt(cv, "PORTO DE MAUÁ", x0, y + 150, TF_SB, 24, MUT, int(255 * k), align="l", track=3, shadow=False)
    txt(cv, "FRAGOSO", x1, y + 150, TF_SB, 24, MUT, int(255 * k), align="r", track=3, shadow=False)
    qk = eo(prog(t, tk - .2, tk + .1)); km = 14.5 * eio(prog(t, tk - .2, tk + .9))
    if qk > 0:
        txt(cv, f"{km:.1f} KM".replace(".", ","), W / 2, 1290, TF_B, 150, GD, int(255 * qk), track=6)
    footer(cv, t, 6)

def s_empire(cv, t):
    a, b = L[7]; te = wt("Estaleiro", a); tg = wt("gás", te); tc = wt("cabo", tg)
    background(cv, t, "#14110A")
    k = eo(prog(t, a, a + .3)); txt(cv, "MAUÁ NÃO PARA", W / 2, 440, TF_B, 110, WH, int(255 * k), track=5)
    items = [(SHIP, "ESTALEIRO", "PONTA DA AREIA · NITERÓI", W / 2 - 270, 700, .62, te), (LAMP, "GÁS NO RIO", "ILUMINAÇÃO", W / 2 + 270, 700, .7, tg)]
    for ps, lab, sub, x, y, s, tt in items:
        q = eio(prog(t, tt - .2, tt + .9))
        if q <= 0: continue
        icon(cv, ps, x, y, s, q, GD)
        txt(cv, lab, x, y + 230, TF_B, 64, WH, int(255 * eo(q)), track=3)
        txt(cv, sub, x, y + 270, TF_SB, 20, MUT, int(255 * eo(q)), track=3, shadow=False)
    q = eio(prog(t, tc - .2, tc + 1.2))
    if q > 0:
        icon(cv, CABLE, W / 2, 1150, 1.0, q, EB, glow_a=60)
        txt(cv, "BRASIL", W / 2 - 260, 1310, TF_B, 48, WH, int(255 * eo(q)), track=3)
        txt(cv, "EUROPA", W / 2 + 260, 1310, TF_B, 48, WH, int(255 * eo(q)), track=3)
        txt(cv, "CABO SUBMARINO · 1874", W / 2, 1185, TF_B, 54, EB, int(255 * eo(prog(t, tc + .2, tc + .6))), track=3)
    footer(cv, t, 7)

def s_tension(cv, t):
    a, b = L[8]
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#040508"))
    hb = max(0, math.sin((t - a) * 2 * math.pi * 1.2)) ** 10
    cv.drawRect(skia.Rect.MakeWH(W, H), rad(W / 2, H / 2, H * .7, [("#000000", 0), ("#3A0A00", int(140 * hb))]))
    facade(cv, W / 2, 960, 1.05, 1.0, "#1F2937", glow_a=0)
    reveal_txt(cv, "MAS AQUI", W / 2, 880, TF_B, 140, WH, prog(t, a, a + .5), track=6)
    reveal_txt(cv, "A HISTÓRIA VIRA", W / 2, 1020, TF_B, 130, OR, prog(t, a + .5, a + 1.2), track=4)

def s_1875(cv, t):
    a, b = L[9]; tu = wt("Uruguai", a); tb = wt("banco", tu)
    background(cv, t, "#120C0C")
    k = eo(prog(t, a, a + .3)); txt(cv, "1875", W / 2, 520, TF_B, 220, WH, int(255 * k), track=8)
    qu = eo(prog(t, tu - .3, tu + .2))
    # Montevidéu -> Rio (onda de choque)
    mx, my, rx, ry = W / 2 - 250, 1150, W / 2 + 230, 820
    if qu > 0:
        cv.drawCircle(mx, my, 14, P(OR, int(255 * qu)))
        for j in range(3):
            ph = ((t - tu) * .9 + j / 3) % 1
            if t > tu: cv.drawCircle(mx, my, 20 + ph * 120, P(OR, int(200 * (1 - ph) * qu), stroke=3))
        txt(cv, "MONTEVIDÉU", mx, my + 80, TF_B, 58, OR, int(255 * qu), track=3)
        txt(cv, "CRISE NO URUGUAI", mx, my + 125, TF_SB, 22, MUT, int(255 * qu), track=3, shadow=False)
    qa = eio(prog(t, tu + .1, tb + .2))
    if qa > 0:
        pa = skia.Path(); pa.moveTo(mx + 30, my - 30); pa.cubicTo(mx + 120, my - 250, rx - 200, ry + 40, rx - 70, ry + 10)
        stroke(cv, [pa], qa, OR, 7, 255, 120)
    qb = back(prog(t, tb - .25, tb + .25))
    if qb > 0:
        cv.save(); cv.translate(rx, ry); s_ = cl(qb, 0, 1.1); cv.scale(s_, s_)
        j = random.Random(int(t * 24)); sh = 6 * cl((t - tb) * 2) * (1 - cl((t - tb - .8) * 2))
        cv.translate(j.uniform(-sh, sh), j.uniform(-sh, sh))
        rrect(cv, -190, -90, 380, 180, 12, P("#0B0D12", 230)); rrect(cv, -190, -90, 380, 180, 12, P(GD, 255, stroke=5))
        txt(cv, "BANCO MAUÁ", 0, 10, TF_B, 80, GD, 255, track=3); txt(cv, "& CIA.", 0, 60, TF_SB, 24, WH, 255, track=4, shadow=False)
        cv.restore()
    footer(cv, t, 9)

def s_loan(cv, t):
    a, b = L[10]; ts = wt("socorro", a); tt = wt("três", ts)
    background(cv, t, "#141019")
    k = eo(prog(t, a, a + .3)); txt(cv, "MAUÁ PEDE", W / 2, 420, TF_B, 100, MUT, int(255 * k), track=5)
    txt(cv, "SOCORRO", W / 2, 545, TF_B, 140, WH, int(255 * eo(prog(t, ts - .1, ts + .3))), track=6)
    doc_card(cv, t, 880, 1.0)
    qn = eo(prog(t, tt - .2, tt + .1)); n = int(round(3000 * eio(prog(t, tt - .2, tt + .9))))
    if qn > 0:
        txt(cv, f"{n:,}".replace(",", "."), W / 2, 1250, TF_B, 150, GD, int(255 * qn), track=6)
        txt(cv, "CONTOS DE RÉIS · EMPRÉSTIMO", W / 2, 1310, TF_SB, 24, WH, int(255 * qn), track=4, shadow=False)
    footer(cv, t, 10)

def s_reveal(cv, t):
    a, b = L[11]; tq = wt("nega", a); tb = wt("Banco", tq); to = wt("nasceu", tb)
    background(cv, t, "#14110A")
    k = eo(prog(t, a, a + .3)); txt(cv, "QUEM NEGA?", W / 2, 470, TF_B, 140, WH, int(255 * k), track=6)
    doc_card(cv, t, 830, 1.0, reveal=prog(t, tb - .25, tb + .6), stamp=prog(t, tb + .4, tb + 1.0))
    q = eo(prog(t, to - .5, to - .1))
    txt(cv, "O BANCO QUE NASCEU", W / 2, 1200, TF_B, 84, WH, int(255 * q), track=4)
    txt(cv, "DO BANCO DELE", W / 2, 1300, TF_B, 104, OR, int(255 * eo(prog(t, to + .1, to + .5))), track=5)
    footer(cv, t, 11)

def s_fall(cv, t):
    a, b = L[12]; tm = wt("moratória", a); tf = wt("falência", tm)
    background(cv, t, "#120C0C")
    y = 560; x0, x1 = 130, W - 130; p = eio(prog(t, a, a + .8))
    cv.drawLine(x0, y, x0 + (x1 - x0) * p, y, P(WH, 200, stroke=3))
    for lab, sub, fx, col, tt in (("1851", "BANCO", 0, GD, a), ("1854", "FERROVIA", .3, GD, a), ("1875", "MORATÓRIA", .7, OR, tm), ("1878", "FALÊNCIA", 1, OR, tf)):
        if p >= fx - .001 and t >= tt - .15:
            xx = x0 + (x1 - x0) * fx; cv.drawCircle(xx, y, 12, P(col)); cv.drawCircle(xx, y, 26, P(col, 120, stroke=2))
            txt(cv, lab, xx, y - 50, TF_B, 54, col, 255, track=2)
            txt(cv, sub, xx, y + 62, TF_SB, 19, MUT, 255, track=2, shadow=False)
    pts = [(150, 760), (330, 720), (480, 690), (620, 700), (720, 860), (820, 1010), (930, 1130)]
    pg = eio(prog(t, a + .2, tf + .4))
    for j in range(4): cv.drawLine(150, 760 + j * 120, 930, 760 + j * 120, P(LINE, 160, stroke=1))
    stroke(cv, [path(pts, close=False)], pg, OR, 8, 255, 120)
    q1 = back(prog(t, tm - .2, tm + .3))
    if q1 > 0:
        cv.save(); cv.translate(W / 2, 1230); s_ = cl(q1, 0, 1.1); cv.scale(s_, s_)
        txt(cv, "MORATÓRIA" if t < tf - .2 else "FALÊNCIA", 0, 0, TF_B, 150, OR, 255, track=8); cv.restore()
    footer(cv, t, 12)

def s_reflect(cv, t):
    a, b = L[13]; tn = wt("nem", a)
    background(cv, t, "#14110A")
    k = eo(prog(t, a, a + .4)); txt(cv, "QUEM CONSTRÓI", W / 2, 470, TF_B, 120, WH, int(255 * k), track=5)
    txt(cv, "O SISTEMA", W / 2, 600, TF_B, 140, GD, int(255 * eo(prog(t, a + .4, a + .8))), track=6)
    u = eio(prog(t, tn - .4, tn + .6))
    facade(cv, W / 2, 920, .6, 1.0, lerp_col(GD, "#4B5563", u), glow_a=int(60 * (1 - u)))
    q = eo(prog(t, tn - .1, tn + .3))
    txt(cv, "NEM SEMPRE É", W / 2, 1180, TF_B, 96, MUT, int(255 * q), track=5)
    txt(cv, "SALVO POR ELE.", W / 2, 1290, TF_B, 110, GD, int(255 * eo(prog(t, tn + .4, tn + .8))), track=5)

def s_end(cv, t):
    a, b = L[14]
    background(cv, t)
    for i_, (s, col) in enumerate((("MAUÁ FOI", WH), ("VÍTIMA", GD), ("OU ARRISCOU", WH), ("DEMAIS?", GD))):
        q = eo(prog(t, a - .1 + i_ * .35, a + .3 + i_ * .35))
        txt(cv, s, W / 2, 620 + i_ * 150 + (1 - q) * 20, TF_B, 140, col, int(255 * q), track=4)
    kicker(cv, "CONTA NOS COMENTÁRIOS", 1290, int(255 * eo(prog(t, a + 1.4, a + 1.8))))
    kl = eio(prog(t, b + .2, b + .7))
    if kl > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(BG0, int(255 * kl)))
        cv.drawLine(W / 2 - 200 * kl, 1010, W / 2 + 200 * kl, 1010, P(GD, int(255 * kl), stroke=2))
        txt(cv, "IMPÉRIO DE IDEIAS", W / 2, 980, TF_B, 120, WH, int(255 * kl), track=8)
        txt(cv, "HISTÓRIAS EXTRAORDINÁRIAS POR TRÁS DE GRANDES NEGÓCIOS", W / 2, 1060, TF_SB, 20, MUT, int(255 * kl), track=4, shadow=False)

FNS = [s_hook, s_teaser, s_maua, s_1851, s_1853, s_rail, s_empire, s_tension, s_1875, s_loan, s_reveal, s_fall, s_reflect, s_end]
SCENES = []
for i_, fn in enumerate(FNS, start=1):
    s0 = 0.0 if i_ == 1 else L[i_][0] - .1
    e0 = TOTAL if i_ == len(FNS) else L[i_ + 1][0] - .1
    SCENES.append((fn, s0, e0))
XF = .3

CHUNKS = {
 1: [("O *Banco do Brasil* nasceu,", 5), ("em parte,", 2), ("do banco de *um só homem*.", 6)],
 2: [("Anos depois,", 2), ("esse homem *quebrou*.", 3), ("E o *“não”* que o derrubou", 6), ("veio de onde *ninguém esperava*.", 5)],
 3: [("Ele era *Irineu Evangelista de Sousa*,", 6), ("o *Barão de Mauá*.", 4)],
 4: [("Em *1851*,", 7), ("cria um banco chamado", 4), ("*Banco do Brasil*.", 3)],
 5: [("Dois anos depois,", 3), ("o *governo* o funde a outro:", 6), ("nasce o *Banco do Brasil* atual.", 6)],
 6: [("Em *1854*,", 4), ("Mauá inaugura", 2), ("a *primeira ferrovia* do país.", 5), ("*14,5 km*.", 4)],
 7: [("*Estaleiro*,", 1), ("*gás* no Rio,", 3), ("e o *cabo submarino*", 4), ("que liga o Brasil à *Europa*.", 6)],
 8: [("Mas aqui a história *vira*.", 5)],
 9: [("Em *1875*,", 4), ("a crise no *Uruguai*", 4), ("atinge o banco dele.", 4)],
 10: [("Mauá pede *socorro*:", 3), ("*3.000 contos de réis*", 5), ("emprestados.", 1)],
 11: [("Quem *nega*?", 2), ("O *Banco do Brasil*.", 4), ("O banco que nasceu", 4), ("do *banco dele*.", 3)],
 12: [("Vem a *moratória*.", 3), ("Em *1878*,", 4), ("a *falência*.", 2)],
 13: [("Quem constrói o *sistema*", 4), ("nem sempre é", 3), ("*salvo* por ele.", 3)],
 14: [("Mauá foi *vítima*,", 3), ("ou *arriscou demais*?", 3)],
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
