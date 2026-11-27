# Motor HyperFrames (principal desde 28/11/2026)

Testado em 27/11 na nuvem: Node 22, Chromium do sistema, ffmpeg 6.1. Render "looks" ≈ 3,5 s de máquina por segundo de vídeo, ou seja, ~3,5 min para 57 s.

## Arquivos
- `base.html`: moldura fixa (tokens de cor, fontes locais, grão animado, vinheta, barra de progresso, capítulos, faixa e estilo das legendas na área segura).
- `build_hf.py`: gera `<producao>/hf/index.html` a partir de `timing.json`, `words.json` e do módulo de cenas do dia. As legendas saem dos CHUNKS (`*trecho*` = dourado).
- `exemplo_ep05.py`: exemplo real com 4 cenas do EP05 (capa com marca, cartão com tarja, nome letra a letra, contador de ano). Copie a estrutura.
- `grain.png`: textura do grão.

## Passo a passo do dia
```bash
export DO_NOT_TRACK=1
P=episodios/AAAA-MM-DD_tema/producao
cp operacao/motor-hf/exemplo_ep05.py $P/cenas_hf.py      # reescreva CHAPTERS, CHUNKS, CSS e SCENES (uma função por fala)
python3 operacao/motor-hf/build_hf.py $P $P/cenas_hf.py   # FONTDIR=/home/claude/fonts por padrão
cd $P/hf
npx -y hyperframes@0.9.104 check --json                  # zero erros
npx -y hyperframes@0.9.104 snapshot --at 0,1.5,10,20,30,40,50   # olhar .hyperframes/artifacts/snapshots/*/contact-sheet.jpg
npx -y hyperframes@0.9.104 render --quality looks -o ../video_mudo.mp4
cd ..; python3 trilha.py   # music.wav
# mixagem e codificação final (igual ao EP05):
ffmpeg -y -i narracao.mp3 -i music.wav -filter_complex "[0:a]aresample=48000,apad[v];[1:a]aresample=48000,volume=0.16[m];[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:<TOTAL>,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map "[a]" -c:a pcm_s16le mix.wav
ffmpeg -y -i video_mudo.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart -shortest ../video.mp4
```
Não versione `hf/.hyperframes/`, `hf/assets/fonts` nem `video_mudo.mp4` (há um .gitignore).

## Contrato (resumo de `operacao/skills/hyperframes/SKILL.md`)
- Todo elemento temporizado: `class="clip"`, `data-start`, `data-duration` (s) e um `id`. Use `ctx.clip(...)`.
- Uma timeline pausada (`tl`); nada de `Math.random()` sem semente, `Date.now()`, timers ou `repeat:-1`.
- Não anime `display`/`visibility` de um `.clip`: anime um filho. Não ponha `transform` CSS num elemento que o GSAP transforma: use `rotate:` numa div externa, como no exemplo.
- Traço técnico que se desenha: SVG com `pathLength="1"` e tween `strokeDasharray:1, strokeDashoffset 1→0`.
- Contadores: tween de um objeto `{v}` com `onUpdate` que só troca o texto.
- `ctx.wt("palavra", depois_de)` dá o tempo de uma palavra falada; `ctx.L[i]` dá (início, fim) da fala i.
