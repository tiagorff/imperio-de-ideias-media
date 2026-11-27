# Exemplo de módulo de cenas para o motor HyperFrames (primeiras cenas do EP05, recompostas na área segura).
# Copie para episodios/<data_tema>/producao/cenas_hf.py e troque as cenas pela história do dia.
# Regras de design aplicadas (ver operacao/skills/LEIA-ME.md): conteúdo entre y 300 e 1090, legenda em 1150;
# entradas variadas por papel (expo.out na chegada, power3.in na saída), títulos param depois de pousar,
# um destaque dourado por tela, laranja só na virada.

CHAPTERS = [(1, 2, "PRÓLOGO", "1851 — 1878"), (3, 5, "01  O BANQUEIRO", "1851 — 1853"), (6, 7, "02  O IMPÉRIO", "1854 — 1874"),
            (8, 11, "03  O PEDIDO", "1875"), (12, 14, "04  A QUEDA", "1875 — 1878")]

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

CSS = """
.line *{fill:none;stroke-linecap:round;stroke-linejoin:round}
.stamp{position:absolute;border:8px solid var(--orange);border-radius:10px;color:var(--orange);font-family:Bebas;font-size:118px;letter-spacing:6px;padding:0 26px}
"""

def facade_svg(id_, color="#D6B98C", w=720):
    ps = ['<polyline pathLength="1" points="-330,-150 0,-300 330,-150 -330,-150"/>', '<path pathLength="1" d="M-350,-125 L350,-125"/>',
          '<path pathLength="1" d="M-360,260 L360,260 M-380,290 L380,290"/>', '<circle pathLength="1" cx="0" cy="-205" r="34"/>']
    for k in range(6):
        x = -275 + k * 110
        ps.append(f'<rect pathLength="1" x="{x-26}" y="-110" width="52" height="360" rx="4"/>')
    return (f'<svg id="{id_}" class="line" viewBox="-400 -320 800 640" width="{w}" style="position:absolute;left:{504-w/2}px;top:650px;'
            f'overflow:visible;filter:drop-shadow(0 0 10px rgba(251,191,36,.35))" stroke="{color}" stroke-width="3">' + "".join(ps) + '</svg>')

def s_hook(c):
    # quadro 0 = capa: marca grande + título curto + elemento de tensão, já visíveis
    h = f'''<div class="bg" style="background:linear-gradient(180deg,#07090F,#14110A 50%,#07090F)"></div>
<div class="abs kicker" style="top:318px;font-size:24px;letter-spacing:4px">A ORIGEM QUE POUCOS CONHECEM</div>
<div id="h-brand" class="abs bebas gold shadow" style="top:360px;font-size:200px;line-height:.86">BANCO DO<br>BRASIL</div>
{facade_svg("h-fac", w=560)}
<div style="position:absolute;left:130px;top:880px;width:748px;rotate:-4deg">
  <div id="h-tag" style="background:#0B0D12;border:6px solid var(--gold);border-radius:10px;padding:26px 0 18px;text-align:center">
    <div class="bebas ink" style="font-size:88px">NASCEU DO BANCO</div><div class="bebas gold" style="font-size:88px">DE UM SÓ HOMEM</div>
  </div>
</div>'''
    j = f'''tl.fromTo("#h-fac *",{{strokeDashoffset:0.45,strokeDasharray:1}},{{strokeDashoffset:0,duration:1.4,stagger:.04,ease:"power2.inOut"}},0);
tl.fromTo("#h-tag",{{y:24,opacity:.85}},{{y:0,opacity:1,duration:.6,ease:"expo.out"}},0.05);'''
    return h, j

def doc_card(pre, top):
    return f'''<div id="{pre}-card" class="card" style="left:120px;top:{top}px;width:768px;height:430px;padding:30px 40px;rotate:-1.5deg">
  <div class="meta">BANCO MAUÁ &amp; CIA.  ·  RIO DE JANEIRO, 1875</div><hr>
  <div style="font-family:MontXB;font-size:28px">PEDIDO DE SOCORRO:</div>
  <div class="bebas" style="font-size:64px">3.000 CONTOS DE RÉIS</div>
  <div style="font-family:MontXB;font-size:28px;margin-top:18px">RESPOSTA / QUEM NEGOU:</div>
  <div style="position:relative;height:110px"><div class="bebas" style="font-size:100px;position:absolute;top:4px">BANCO DO BRASIL</div>
  <div id="{pre}-bar" class="redact" style="left:0;top:0;width:690px;height:104px"></div></div>
  <div class="meta" style="position:absolute;right:40px;bottom:22px;font-size:18px">CONFIDENCIAL ATÉ A VIRADA</div>
</div>'''

def s_teaser(c):
    a = c.a; tq = c.wt("quebrou", a); tn = c.wt("ninguém", tq)
    h = f'''<div class="bg" style="background:linear-gradient(180deg,#07090F,#141019 50%,#07090F)"></div>
<div id="t-1" class="abs bebas mut" style="top:330px;font-size:92px">ANOS DEPOIS,</div>
<div id="t-2" class="abs bebas ink shadow" style="top:425px;font-size:100px">ESSE HOMEM <span class="orange">QUEBROU</span></div>
{doc_card("t", 590)}
<div id="t-3" class="abs kicker" style="top:1040px;font-size:24px;letter-spacing:3px;color:var(--orange)">O “NÃO” VEIO DE ONDE NINGUÉM ESPERAVA</div>'''
    j = f'''tl.fromTo("#t-1",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},{a+.05:.3f});
tl.fromTo("#t-2",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},{tq-.25:.3f});
tl.fromTo("#t-card",{{y:90,opacity:0}},{{y:0,opacity:1,duration:.7,ease:"expo.out"}},{tq+.2:.3f});
tl.fromTo("#t-3",{{opacity:0}},{{opacity:1,duration:.25}},{tn-.3:.3f});'''
    return h, j

def s_maua(c):
    a = c.a; ti = c.wt("Irineu", a); tb = c.wt("Barão", ti)
    letters = "".join(f'<span class="lt">{ch}</span>' for ch in "BARÃO DE MAUÁ")
    h = f'''<div class="bg" style="background:linear-gradient(180deg,#07090F,#0B1A2E 50%,#07090F)"></div><div class="grid"></div>
<div class="abs kicker" style="top:340px">“O EMPRESÁRIO DO IMPÉRIO”</div>
<svg id="m-hat" class="line" viewBox="-260 -220 520 620" width="400" style="position:absolute;left:304px;top:390px;overflow:visible" stroke="#FBBF24" stroke-width="4">
 <polyline pathLength="1" points="-70,-40 -60,-190 60,-190 70,-40"/><path pathLength="1" d="M-140,-40 L140,-40"/>
 <ellipse pathLength="1" cx="0" cy="60" rx="80" ry="100"/><path pathLength="1" d="M-230,380 C-220,230 -120,190 -60,160 M230,380 C220,230 120,190 60,160 M0,210 L0,380"/></svg>
<div id="m-name" class="abs bebas ink" style="top:850px;font-size:64px">IRINEU EVANGELISTA DE SOUSA</div>
<div id="m-title" class="abs bebas gold shadow" style="top:920px;font-size:140px">{letters}</div>'''
    j = f'''tl.fromTo("#m-hat *",{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.6,stagger:.08,ease:"power2.inOut"}},{a:.3f});
tl.fromTo("#m-name",{{opacity:.25,color:"#9CA3AF"}},{{opacity:1,color:"#F9FAFB",duration:.3}},{ti-.1:.3f});
tl.fromTo("#m-title .lt",{{opacity:.3,filter:"blur(4px)"}},{{opacity:1,filter:"blur(0px)",duration:.12,stagger:.035}},{tb-.15:.3f});'''
    return h, j

def s_1851(c):
    a = c.a; tb = c.wt("Brasil", c.wt("chamado", a)) - .4
    h = f'''<div class="bg"></div>
<div id="y-num" class="abs bebas ink" style="top:330px;font-size:250px">1800</div>
<div class="abs kicker" style="top:575px">— RIO DE JANEIRO —</div>
<div style="position:absolute;left:140px;top:650px;width:728px;rotate:1.2deg"><div id="y-card" class="card" style="position:relative;height:300px;padding:28px 40px;text-align:center">
 <div class="meta" style="text-align:left">SOCIEDADE PRIVADA · 1851</div><hr>
 <div class="bebas" style="font-size:96px;white-space:nowrap">BANCO DO BRASIL</div><div class="meta" style="font-size:24px">O 2º BANCO COM ESSE NOME</div></div></div>
<div id="y-foot" class="abs bebas ink" style="top:985px;font-size:54px">VIRA O MAIOR DO RAMO NO <span class="gold">IMPÉRIO</span></div>'''
    j = f'''(function(){{const o={{v:1800}};const el=document.getElementById("y-num");
tl.to(o,{{v:1851,duration:1.4,ease:"power2.out",onUpdate:()=>{{el.textContent=Math.round(o.v)}}}},{a:.3f});
tl.to("#y-num",{{color:"#FBBF24",duration:.2}},{a+1.4:.3f});}})();
tl.fromTo("#y-card",{{y:70,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"expo.out"}},{tb-.2:.3f});
tl.fromTo("#y-foot",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},{tb+.5:.3f});'''
    return h, j

SCENES = [s_hook, s_teaser, s_maua, s_1851]
