# Trilha original + efeitos sintetizados (sem material de terceiros)
import numpy as np, json, wave, os
SR = 48000
BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "timing.json")))
L = {l["i"]: (l["start"], l["end"]) for l in TIM["lines"]}
TOT = TIM["total"]
N = int(TOT * SR)
rng = np.random.default_rng(1)
t = np.arange(N) / SR

def env_ar(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    # vectorised one-pole via lfilter-like recurrence using scipy if available
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
        return y
def hp(x, fc): return x - lp(x, fc)
def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i]
def note(f): return 440 * 2 ** ((f - 69) / 12)
def saw(f, d, det=0.0):
    tt = np.arange(int(d * SR)) / SR
    s = 0
    for dd in (-det, 0, det):
        ph = (tt * f * (1 + dd)) % 1; s = s + (2 * ph - 1)
    return s / 3
def sine(f, d):
    tt = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * tt)

mus = np.zeros(N)
BPM = 96; beat = 60 / BPM
# chord progression (MIDI roots) per section
prog_a = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
prog_b = [[50, 53, 57], [57, 60, 64], [52, 56, 59], [57, 60, 64]]  # Dm Am E Am (tense)
prog_c = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [52, 56, 59, 64]]

def pads(t0, t1, prog, lvl, cutoff):
    bar = beat * 4; k = 0; x = t0
    while x < t1:
        d = min(bar, t1 - x) + 0.4
        ch = prog[k % len(prog)]
        sig = sum(saw(note(m), d, 0.004) for m in ch) / len(ch)
        sig = lp(sig, cutoff) * env_ar(len(sig), 0.35, 0.45) * lvl
        add(mus, sig, x); x += bar; k += 1

def drone(t0, t1, root, lvl):
    d = t1 - t0
    s = (sine(note(root - 12), d) * .7 + sine(note(root - 24), d) * .5) * env_ar(int(d * SR), 0.8, 1.0) * lvl
    add(mus, s, t0)

def pulse(t0, t1, prog, lvl, cutoff=1800, div=2):
    step = beat / div; x = t0; k = 0
    while x < t1:
        ch = prog[int((x - t0) / (beat * 4)) % len(prog)]
        m = ch[0] + (12 if k % 4 == 2 else 0)
        s = lp(saw(note(m - 12), 0.18, 0.002), cutoff) * np.exp(-np.arange(int(0.18 * SR)) / SR * 18) * lvl
        add(mus, s, x); x += step; k += 1

def tick(t0, t1, lvl):
    x = t0
    while x < t1:
        n = int(0.03 * SR); s = hp(rng.standard_normal(n), 6000) * np.exp(-np.arange(n) / SR * 160) * lvl
        add(mus, s, x); x += beat / 2

def kick(at, lvl=1.0, f0=110, dec=6):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    f = 45 + (f0 - 45) * np.exp(-tt * 18); ph = 2 * np.pi * np.cumsum(f) / SR
    add(mus, np.sin(ph) * np.exp(-tt * dec) * lvl, at)

def boom(at, lvl=1.0):
    kick(at, lvl * 1.2, 90, 2.2)
    n = int(2.0 * SR); s = lp(rng.standard_normal(n), 300) * np.exp(-np.arange(n) / SR * 2.5) * lvl * .8
    add(mus, s, at)

def riser(t0, t1, lvl):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n); out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        fc = 300 + 5000 * (i / n) ** 2; out[i:i + seg] = lp(nz[i:i + seg], fc)
    add(mus, out * (tt / tt[-1]) ** 2 * lvl, t0)

def whoosh(at, lvl=.5, d=.5):
    n = int(d * SR); tt = np.linspace(0, 1, n); nz = rng.standard_normal(n); out = np.zeros(n); seg = 1024
    for i in range(0, n, seg):
        fc = 400 + 4000 * np.sin(np.pi * i / n); out[i:i + seg] = hp(lp(nz[i:i + seg], fc), 200)
    add(mus, out * np.sin(np.pi * tt) ** 2 * lvl, at - d * .55)

def blip(at, f, lvl=.18):
    s = np.sign(sine(f, .06)) * env_ar(int(.06 * SR), .002, .03) * lvl; add(mus, lp(s, 4000), at)

def coin_sfx(at, lvl=.16):
    s = (sine(2637, .25) + .6 * sine(3951, .25)) * np.exp(-np.arange(int(.25 * SR)) / SR * 14) * lvl
    add(mus, s, at); add(mus, s * .7, at + .07)

def stamp(at): kick(at, 1.1, 160, 14); add(mus, lp(rng.standard_normal(int(.12 * SR)), 1500) * np.exp(-np.arange(int(.12 * SR)) / SR * 40) * .6, at)

def tape(t0, t1, lvl=.05):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    s = lp(rng.standard_normal(n), 900) * (1 + .5 * np.sin(2 * np.pi * 7 * tt)) * lvl * env_ar(n, .2, .3)
    add(mus, s, t0)

def shimmer(at, lvl=.12):
    for k, m in enumerate([81, 84, 88, 93]):
        s = sine(note(m), 2.0) * np.exp(-np.arange(int(2 * SR)) / SR * 2.2) * lvl; add(mus, s, at + k * .08)

# ---- arrangement EP03 (Havaianas) ----
import json as _j
W2=_j.load(open(os.path.join(BASE,"words.json")))
def wt(word, after):
    for w in W2:
        if w[0] >= after - .05 and word.lower() in w[2].lower(): return w[0]
    return after
tp = wt("chinelo", 1.5); tv = wt("viravam", L[9][0]); tl = wt("legítimas", L[6][0] + 1)
boom(0.05, 1.0)
drone(0.0, L[3][0], 45, .18)
riser(0.8, tp, .18); stamp(tp)
drone(L[2][0], L[3][0], 40, .14); tick(L[2][0], L[3][0], .05)
pads(L[3][0] - .1, L[6][0] - .1, prog_a, .10, 1400)
drone(L[3][0] - .1, L[6][0] - .1, 45, .10)
pulse(L[4][0], L[6][0] - .1, prog_a, .10, 1600)
tick(L[4][0], L[6][0] - .1, .05)
stamp(wt("lista", L[5][0]) + .6)
boom(L[6][0] - .05, .5)
pads(L[6][0] - .05, L[8][0] - .1, prog_b, .09, 1000)
drone(L[6][0] - .05, L[8][0] - .1, 38, .12)
pulse(L[6][0], L[8][0] - .1, prog_b, .09, 1200, div=2)
stamp(tl)
drone(L[8][0] - .1, L[9][0], 33, .16)
x = L[8][0]
while x < L[9][0] - .2:
    kick(x, .55, 70, 9); kick(x + .22, .35, 70, 9); x += 60 / 72
riser(L[8][0], tv - .05, .16); boom(tv, .9); shimmer(tv + .3, .08)
pads(L[9][0] - .05, L[12][0] - .1, prog_c, .10, 2200)
pulse(L[10][0], L[12][0] - .1, prog_c, .10, 2800, div=4)
tick(L[10][0], L[12][0] - .1, .05)
tm = wt("duzentos", L[12][0])
for k in range(6): coin_sfx(tm + k * .16, .10)
pads(L[12][0] - .1, L[13][0] - .1, prog_c, .10, 2600)
pads(L[13][0] - .1, TOT, prog_a, .08, 1200)
drone(L[13][0] - .1, TOT, 45, .10)
shimmer(L[14][1] + .1)
for x in [L[i][0] - .12 for i in range(2, 15)]: whoosh(x, .35)

mus = mus / (np.max(np.abs(mus)) + 1e-9) * .8
out = (np.clip(mus, -1, 1) * 32767).astype(np.int16)
with wave.open(os.path.join(BASE, "music.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("music ok", len(out) / SR)
