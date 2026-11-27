# Império de Ideias — motor HyperFrames (HTML + GSAP -> MP4)
# Uso: python3 build_hf.py <pasta_producao> <modulo_cenas.py> [--ate SEGUNDOS]
# A pasta de produção precisa de timing.json e words.json (mesmo formato do motor skia).
# O módulo de cenas define: CHAPTERS, CHUNKS, SCENES (lista de funções cena(ctx) -> (html, js)) e opcionalmente CSS.
# Gera <producao>/hf/ (projeto HyperFrames). Render: cd hf && npx -y hyperframes@0.9.104 render --quality delivery -o video_mudo.mp4
import json, os, sys, re, shutil, importlib.util, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(sys.argv[1]); MOD = os.path.abspath(sys.argv[2])
ATE = float(sys.argv[sys.argv.index("--ate") + 1]) if "--ate" in sys.argv else None
TIM = json.load(open(os.path.join(PROD, "timing.json")))
WORDS = json.load(open(os.path.join(PROD, "words.json")))
L = {l["i"]: (l["start"], l["end"]) for l in TIM["lines"]}
TOTAL = TIM["total"] if ATE is None else ATE
SPOKEN = {l["i"]: l["text"] for l in TIM["lines"]}

def wt(word, after):
    for w in WORDS:
        if w[0] >= after - .05 and word.lower() in w[2].lower(): return w[0]
    return after

class Ctx:
    def __init__(s): s.L, s.wt, s.TOTAL, s.W, s.H = L, wt, TOTAL, 1080, 1920
    def clip(s, id_, a, b, inner, cls="", style="", track=2):
        """um elemento temporizado (data-start/duration em segundos)"""
        a = max(0.0, a); b = min(b, TOTAL)
        return (f'<div id="{id_}" class="clip {cls}" data-start="{a:.3f}" data-duration="{max(.04, b - a):.3f}" '
                f'data-track-index="{track}" style="{style}">{inner}</div>')

spec = importlib.util.spec_from_file_location("cenas", MOD); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
ctx = Ctx()

# ---------- cenas: cada uma ocupa [início da fala - .1, início da próxima fala - .1) ----------
scene_html, scene_js = [], []
n = len(M.SCENES)
for k, fn in enumerate(M.SCENES, start=1):
    a = 0.0 if k == 1 else L[k][0] - .1
    b = TOTAL if k == n else L[k + 1][0] - .1
    if a >= TOTAL: break
    ctx.a, ctx.b, ctx.i = a, min(b, TOTAL), k
    h, j = fn(ctx)
    scene_html.append(ctx.clip(f"s{k}", a, min(b, TOTAL), h, cls="scene", track=1))
    scene_js.append(f"// cena {k}\n" + j)

# ---------- legendas (blocos curtos, palavra-chave em dourado) ----------
def chunk_times(i, chunks):
    toks = SPOKEN[i].split(); assert sum(c for _, c in chunks) == len(toks), (i, sum(c for _, c in chunks), len(toks))
    a, b = L[i]; ws = [w for w in WORDS if a - .25 <= w[0] < b + .1]
    out, k = [], 0
    for disp, c in chunks:
        seg = ws[k:k + c] if len(ws) >= k + c else []
        out.append((seg[0][0] if seg else a, disp)); k += c
    res = []
    for m, (st, disp) in enumerate(out):
        en = out[m + 1][0] if m + 1 < len(out) else b + .15
        res.append((st, en, disp))
    return res
caps, cap_js, cid = [], [], 0
for i, chunks in M.CHUNKS.items():
    for st, en, disp in chunk_times(i, chunks):
        if st >= TOTAL: continue
        # *trecho* = destaque dourado; pontuação fica colada na palavra
        marked = re.sub(r"\*([^*]+)\*", lambda m: " ".join("\x01" + w + "\x02" for w in m.group(1).split()), disp)
        parts = []
        for tok in marked.split():
            t = H.escape(tok).replace("\x01", '<span class="k">').replace("\x02", "</span>")
            parts.append(f'<span class="w">{t}</span>')
        cid += 1
        caps.append(ctx.clip(f"c{cid}", st, min(en, TOTAL), " ".join(parts), cls="cap", track=9))
        cap_js.append(f'tl.fromTo("#c{cid} .w",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:.13,stagger:.06,ease:"power2.out"}},{st:.3f});')

# ---------- capítulos ----------
chap = []
for m, (a_, b_, name, yr) in enumerate(M.CHAPTERS):
    st = L[a_][0] - .15 if a_ > 1 else 0.0
    en = (L[b_ + 1][0] - .15) if b_ + 1 in L else TOTAL - 1.6
    if st >= TOTAL: continue
    chap.append(ctx.clip(f"ch{m}", st, min(en, TOTAL), f'<span class="cn">{H.escape(name)}</span><span class="cy">{H.escape(yr)}</span>', cls="chap", track=8))

STEPS = int(TOTAL * 15)
page = open(os.path.join(HERE, "base.html")).read()
page = (page.replace("{{TOTAL}}", f"{TOTAL:.3f}").replace("{{CSS}}", getattr(M, "CSS", ""))
        .replace("{{SCENES}}", "\n".join(scene_html)).replace("{{CAPTIONS}}", "\n".join(caps)).replace("{{CHAPTERS}}", "\n".join(chap))
        .replace("{{JS}}", "\n".join(scene_js) + "\n" + "\n".join(cap_js))
        .replace("{{PROG}}", f"{max(1, TOTAL - 1.6):.3f}").replace("{{STEPS}}", str(STEPS)).replace("{{GRAINX}}", str(STEPS * 865)).replace("{{GRAINY}}", str(STEPS * 611)))

OUT = os.path.join(PROD, "hf"); os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
for f in ("BebasNeue-Regular.ttf", "Montserrat-SemiBold.ttf", "Montserrat-Medium.ttf", "Montserrat-ExtraBold.ttf"):
    src = os.path.join(os.environ.get("FONTDIR", "/home/claude/fonts"), f)
    shutil.copy(src, os.path.join(OUT, "assets", "fonts", f))
shutil.copy(os.path.join(HERE, "grain.png"), os.path.join(OUT, "assets", "grain.png"))
open(os.path.join(OUT, "index.html"), "w").write(page)
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"assets": "assets"}}, open(os.path.join(OUT, "hyperframes.json"), "w"))
json.dump({"id": "imperio", "name": "imperio"}, open(os.path.join(OUT, "meta.json"), "w"))
print("ok", OUT, "duração", TOTAL, "cenas", len(scene_html), "legendas", cid)
