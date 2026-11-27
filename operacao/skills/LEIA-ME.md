# Skills de design do Império de Ideias (instaladas em 27/11/2026)

Aprovadas pelo Tiago em 27/11: **HyperFrames**, **Impeccable** e **Taste Skill**. As três são gratuitas e não usam chaves nem contas.
Ficaram de fora: Remotion (licença paga para empresas com mais de 3 funcionários), video-use (exige chave da ElevenLabs e serve para filmagem bruta) e Whisper (os modelos são baixados de um servidor bloqueado na nuvem; usamos o Scribe da ElevenLabs).

| Pasta | Origem (commit em `VERSOES.txt`) | Licença | Para que usamos |
|---|---|---|---|
| `hyperframes/`, `hyperframes-cli/`, `hyperframes-registry/`, `style-sampling/` | github.com/heygen-com/hyperframes | Apache 2.0 | Montar as cenas em HTML/CSS + GSAP e renderizar em MP4 (CLI `npx -y hyperframes@0.9.104`) |
| `impeccable/` | github.com/pbakaus/impeccable | Apache 2.0 | Direção de design: tipografia, hierarquia, contraste e crítica (ler `reference/craft-floor.md` e `reference/typeset.md`) |
| `taste-skill/` | github.com/Leonxlnx/taste-skill (sem a pasta `assets/`, de 38 MB) | MIT | Evitar a "cara de IA": uma ideia por tela, ritmo, contenção (ler `SKILL.md`, seção House rules) |

## Como a rotina diária usa (resumo obrigatório)

1. **Motor:** `operacao/motor-hf/` (HyperFrames) é o motor principal desde 28/11. O motor skia (`operacao/motor/` e o episódio anterior) é o **plano B**: se o HyperFrames falhar duas vezes ou o render passar de 15 min, renderize com o skia, como no EP05.
2. **Ler antes de escrever as cenas:** `hyperframes/SKILL.md` (contrato), `hyperframes/references/types/vertical.md`, `hyperframes/references/motion.md`, `hyperframes/references/captions.md`, `impeccable/reference/craft-floor.md` e a seção "House rules" de `taste-skill/SKILL.md`. A marca manda: as skills refinam o estilo premium aprovado, **não o substituem** (sem cartoon, fundo quase preto, Bebas Neue + Montserrat, dourado de destaque, laranja só na virada).
3. **Sem telemetria:** não rode `hyperframes events` (a rotina é desassistida). Exporte `DO_NOT_TRACK=1`. Não use os recursos pagos (Studio Pro, cloud render, HeyGen TTS/música): voz = ElevenLabs; trilha = `trilha.py` sintetizada; mixagem = ffmpeg.

## Regras de design extraídas das skills (aplicar em todo episódio)

**Área segura (Reels, TikTok e Shorts, 1080x1920):** todo texto importante fica entre **y 288–1248** e **x 120–888**. O trilho de botões fica à direita, e a legenda do post e o @ ficam embaixo. Abaixo de 1248 e acima de 288, só textura, a barra de progresso e o rótulo de capítulo. As legendas vão na base da faixa segura (top ≈ 1140) e não mais em 1450, que fica escondido pela interface do Instagram.

**Primeiro quadro = capa e gancho:** a marca grande, um título curto e o elemento de tensão já visíveis no quadro 0. Nunca preto, nunca só o logo do perfil.

**Movimento (`motion.md`):**
- A chegada usa um ease longo (`expo.out`/`power4.out`, 0,3–0,6 s). Movimento de câmera e mudança de cor usam `power2.inOut`. A saída acelera (`power3.in`) e é 40–50% mais curta que a entrada.
- Título que pousou **fica parado**: nada de zoom lento contínuo (o "creeping scale" de 4% por cena do motor skia está proibido). O movimento passa para o próximo elemento.
- Varie as entradas (blur-in palavra a palavra, letra a letra para nomes, cinza→tinta) e não use fade+subida em tudo. Escalonamento: palavras a 60–120 ms, itens a 40–80 ms.
- Leitura: um texto fica ≥ 0,5 s + 0,3 s por palavra; a última frase do filme fica ≥ 2 s.
- Transições com causa (3–5 tipos por filme: objeto vira o mundo, inundação de cor, whip, blur swap, dip cut); no máximo 1/3 de cortes secos entre batidas.

**Tipografia (Impeccable/Taste):** nada abaixo de 28 px; título com 4–9% da altura da tela (77–173 px), em 1 ou 2 linhas; **um** destaque em dourado por tela, com significado; contraste AA (4,5:1 no texto). O cinza `#9CA3AF` sobre papel reprova: use tinta escura.

**Verificação:** `npx -y hyperframes@0.9.104 check --json` sem nenhum erro (ponderar os avisos de safe zone, contraste e leitura); depois `snapshot --at <tempos>` e olhe o `contact-sheet.jpg` antes de renderizar.
