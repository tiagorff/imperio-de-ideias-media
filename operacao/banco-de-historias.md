# Império de Ideias — Banco de histórias e controle editorial

Atualizado em 26/11/2026. Notas de 0 a 10 com os pesos do briefing (gancho 25%, surpresa 20%, conflito 20%, visual 15%, relevância 10%, originalidade 10%). As notas são heurísticas de seleção, não previsões de alcance.

**Regra de confiança:** "Alta" = fatos centrais já checados em 2+ fontes. "A verificar" = história conhecida, mas os números, datas e citações ainda precisam de apuração antes do roteiro. Nenhuma história "A verificar" entra em produção sem passar para "Alta".

## Padrões aprovados pelo usuário (aplicar em todos os episódios)

- **Voz (aprovada em 23/11/2026):** conector ElevenLabs, modelo `eleven_v4`, voz **"Flavio Francisco - Narrative - Brazilian Portuguese"** (voice_id `x6uRgOliu4lpcrqMH3s1`). Substitui a voz "Andre" usada no EP01 via Higgsfield (desconectado). Vozes rejeitadas: Andre sem tag de sotaque (sotaque de Portugal) e Kokoro pm_alex (voz local).
- **Naturalidade:** gerar a narração inteira numa única requisição, e não frase por frase. Tags de emoção pontuais: `[misterioso]`, `[suspense, mais devagar]`, `[reflexivo]`, `[provocativo]`. Números por extenso.
- **Storytelling de retenção:** seguir as 7 batidas e o checklist de `claude/guia-de-roteiro-e-calendario.md` (gancho com o desfecho, loop aberto pago no clímax, re-gancho no meio, regra de três, consequência, frase-síntese + pergunta).
- **Ritmo:** pausas longas limitadas a ~0,3 s e aceleração leve (até 1,05×) para caber em 55–59 s.
- **Visual premium (pedido em 23/11):** nada de personagens cartoon. Estética de documentário/editorial: fundo quase preto, grão de filme, vinheta, títulos em Bebas Neue com espaçamento, textos de apoio em Montserrat, dourado como cor de destaque e laranja só para o ponto de virada. Elementos recorrentes: barra de progresso no topo, rótulo de capítulo + ano, ilustrações em traço técnico (estilo blueprint) que se desenham na tela, cartões de documento (papel) com tarjas que são reveladas, números grandes com contador, gráficos simples só com dados verificados, linha do tempo, rodapé com fonte. Legendas limpas, sem caixa, palavra-chave em dourado.
- **Marcas e logotipos:** não desenhamos nem recriamos logotipos; o nome da empresa entra em texto. Se o usuário enviar o arquivo oficial do logo, ele é inserido como foi enviado.
- **Publicação (desde 25/11):** via **Buffer** (organização "My organization"), Instagram @imperiodasideias (Reel, compartilhado no feed) e TikTok, todo dia às **17h00** (America/Sao_Paulo), `isAiGenerated: true`, vídeo por link do GitHub, capa = quadro do vídeo via `thumbnailOffset` (o Buffer gratuito não aceita capa personalizada; os 2 primeiros segundos funcionam como capa). Metricool não é mais usado. Detalhes em `claude/operacao-pipeline.md`.

## Banco (30 histórias)

| # | História | País / período | Cat. | Gancho central | Nota | Confiança | Status |
|---|---|---|---|---|---|---|---|
| 1 | Kodak inventa a câmera digital e quase é destruída por ela | EUA, 1975–2012 | C, F | A empresa que criou o futuro e não conseguiu largar o passado | 8,8 | Alta | PUBLICADO (EP01) |
| 2 | Samuel Klein: de mascate a fundador da Casas Bahia | Brasil, 1952– | A, B, I | Sobrevivente da guerra que começou vendendo de porta em porta | — | Ver nota | **BLOQUEADO** (decisão editorial 24/11: série "Caso Klein" da Agência Pública, 2021, com acusações de crimes sexuais contra meninas; um Reel celebrativo que omita isso seria enganoso — aguarda decisão do Tiago; posição no calendário: 06/12) |
| 3 | Barão de Mauá: o maior empresário do Império que perdeu tudo | Brasil, séc. XIX | G, I, C | Ferrovias, bancos e estaleiros — e a falência | 8,7 | A verificar | IDEIA (27/11) |
| 4 | Adidas x Puma: irmãos Dassler rompem e dividem uma cidade | Alemanha, 1924–2009 | E | Uma briga de família que criou duas gigantes | 8,9 | Alta | PUBLICADO (EP02, 24/11) |
| 5 | Nintendo começou vendendo cartas de baralho (hanafuda) | Japão, 1889– | D, B | 130 anos antes do videogame | 8,5 | Alta | AGENDADO 26/11 17h (EP04, Buffer IG + TikTok) |
| 6 | Elizabeth Magie e o jogo que virou o Monopoly | EUA, 1904–1935 | H | O jogo foi criado para criticar monopólios | 8,4 | A verificar | IDEIA (29/11) |
| 7 | Madam C. J. Walker, pioneira entre as milionárias self-made | EUA, 1905–1919 | A | Filha de ex-escravizados que criou um império de cosméticos | 8,4 | A verificar | IDEIA (01/12) |
| 8 | Silvio Santos: de camelô no Rio a dono de rede de TV | Brasil, 1940s– | A, I | A voz que vendia na rua | 8,7 | A verificar | IDEIA (03/12) |
| 9 | Blockbuster recusa comprar a Netflix | EUA, 2000 | J, C | A reunião em que riram da Netflix | 8,4 | A verificar | IDEIA (28/11) |
| 10 | Nokia: de fábrica de papel a rainha dos celulares — e a queda | Finlândia, 1865–2013 | D, C | Papel, borracha, cabos, celulares | 8,6 | A verificar | IDEIA (02/12) |
| 11 | Coca-Cola: Asa Candler compra a fórmula por uma pechincha | EUA, 1888–1891 | J, D | A compra mais barata da história do refrigerante | 8,3 | A verificar | IDEIA (13/12) |
| 12 | Havaianas: da sandália popular ao ícone da moda | Brasil, 1962–1990s | D, I | O "chinelo de pobre" que virou desejo graças a um truque dos surfistas | 8,6 | Alta | AGENDADO 25/11 17h (EP03, Buffer IG + TikTok) |
| 13 | Lamborghini x Ferrari: o fabricante de tratores que desafiou Enzo | Itália, 1963 | E | Rivalidade (separar anedota de fato) | 8,3 | A verificar | IDEIA (16/12) |
| 14 | LEGO: incêndios na oficina e a crise de 2003–2004 | Dinamarca, 1932–2004 | D, C | A empresa que quase quebrou duas vezes | 8,2 | A verificar | IDEIA (08/12) |
| 15 | Jacob Fugger, o banqueiro que financiava imperadores | Alemanha, séc. XVI | G, J | O homem que comprou uma eleição imperial | 8,0 | A verificar | IDEIA (18/12) |
| 16 | Companhia Holandesa das Índias Orientais e as primeiras ações | Holanda, 1602 | G, F | O nascimento da bolsa de valores | 8,1 | A verificar | IDEIA (09/12) |
| 17 | Varig: ascensão e queda da maior aérea brasileira | Brasil, 1927–2006 | C, I | O símbolo nacional que saiu do céu | 8,2 | A verificar | IDEIA (10/12) |
| 18 | Encol: a maior construtora do país que quebrou | Brasil, 1990s | C, I | Milhares de imóveis inacabados | 8,0 | A verificar | IDEIA (17/12) |
| 19 | Sakichi Toyoda: do tear automático à Toyota | Japão, 1890s–1930s | B, F | O tear que financiou os carros | 8,2 | A verificar | IDEIA (15/12) |
| 20 | Henry Ford fracassou antes de dar certo | EUA, 1899–1903 | A, C | Duas empresas antes da Ford Motor | 8,3 | A verificar | IDEIA (12/12) |
| 21 | Ingvar Kamprad: a IKEA começou com fósforos e canetas | Suécia, 1943– | B | Um adolescente vendendo pelo correio | 8,1 | A verificar | IDEIA (21/12) |
| 22 | Xerox PARC: a empresa que tinha a interface gráfica e não usou | EUA, 1973–1979 | J, F | A visita que mudou a computação pessoal | 8,3 | A verificar | IDEIA (04/12) |
| 23 | Yahoo e as chances de comprar o Google | EUA, 1998–2008 | J, C | Propostas recusadas dos dois lados | 8,2 | A verificar | IDEIA (22/12) |
| 24 | Ray Kroc e os irmãos McDonald | EUA, 1954–1961 | E, J | O vendedor de máquinas de milk-shake | 8,5 | A verificar | IDEIA (05/12) |
| 25 | Banco Medici: ascensão e colapso | Itália, séc. XV | G | O banco que financiou o Renascimento | 8,0 | A verificar | IDEIA (27/12) |
| 26 | Milton Hershey faliu antes do chocolate | EUA, 1880s–1900s | A, C | Falências em série antes do império | 8,1 | A verificar | IDEIA (25/12) |
| 27 | Garantia, Brahma e a origem do grupo de Lemann | Brasil, 1971–1999 | I, J | Um banco que comprou uma cervejaria | 8,0 | A verificar | IDEIA (20/12) |
| 28 | Theranos: a startup de US$ 9 bi que não funcionava | EUA, 2003–2018 | C | Uma promessa sem tecnologia | 8,0 | A verificar | IDEIA (07/12) |
| 29 | Sony Walkman: o produto que ninguém pediu | Japão, 1979 | F | Um gravador sem botão de gravar | 8,0 | A verificar | IDEIA (19/12) |
| 30 | Swatch salva a relojoaria suíça | Suíça, 1983 | D | O relógio de plástico contra o quartzo japonês | 7,9 | A verificar | IDEIA (29/12) |

Temas adicionais do calendário (fora do banco original): Fordlândia (30/11), Airbnb e o cereal (11/12), Natura (14/12), Bauducco (23/12), Coca-Cola e o Papai Noel (24/12), O Boticário (26/12), Tupperware e Brownie Wise (28/12), Embraer (30/12), Veuve Clicquot (31/12). Calendário completo em `claude/guia-de-roteiro-e-calendario.md`.

## Ficha do EP01 — Kodak

- **Status:** PUBLICADO em 23/11/2026 às 14:32 (horário de Brasília) via Metricool — https://www.instagram.com/reel/DgF7P9NCZOa/ (post Metricool id 439150309, uuid 830946646565208644). Capa: quadro aos 2,4 s. Histórico: v1 rejeitada (sotaque de Portugal, voz robótica, roteiro linear); v2 aprovada na narração/roteiro; v3 (voz local) rejeitada; publicada a versão premium (narração v2 + visual documental). Arquivos: repositório `tiagorff/imperio-de-ideias-media`, pasta `episodios/2026-11-23_kodak/`.
- **Roteiro (154 palavras, 58,8 s):** gancho com o desfecho → loop aberto ("tudo começou com uma frase") → contexto (≈90% do filme nos EUA) → protótipo de 1975 (torradeira, 23 s, fita cassete) → "funciona, sem filme" → "agora vem a parte que ninguém esperava" → revelação da frase (segundo Sasson) → motivo (filme) → patente e lucro → 2012, recuperação judicial → reflexão + pergunta.
- **Fatos centrais e fontes:**
  - Protótipo de Steven Sasson, dez/1975: ~3,6 kg, 100×100 pixels, P&B, 23 s para gravar na fita cassete — IEEE Spectrum; Wikipedia (Steven Sasson); NBC News/AP (2005); PetaPixel.
  - Patente US 4,131,919 "Electronic Still Camera": pedido em 20/05/1977, concedida em 26/12/1978; inventores Gareth A. Lloyd e Steven J. Sasson; titular Eastman Kodak Company — uspto.report, Google Patents, Wikipedia.
  - Reação dos executivos ("that's cute — but don't tell anyone about it"): **relato do próprio Sasson** ao NYT (2008), reproduzido pelo Bend Bulletin. O roteiro atribui a frase "segundo Sasson".
  - Kodak com ~90% do filme vendido nos EUA em 1976 — Digital Trends, FindLaw, Daily Maverick. (Narração diz "quase todo filme".)
  - Pedido de Chapter 11 (recuperação judicial) em 19/01/2012 — AP via phys.org, CBC, Al Jazeera.
  - Nuance registrada: a Kodak patenteou e lucrou com a invenção; a ideia de que "enterrou" a câmera é simplificada (Stratrix/Innosight). O roteiro evita dizer que ela escondeu a invenção.
- **Produção:** animação vetorial em código (skia), trilha e efeitos originais sintetizados (sem licenças de terceiros), legendas sincronizadas por transcrição automática (faster-whisper), mix a −14 LUFS.

## Ficha do EP02 — Adidas x Puma (irmãos Dassler)

- **Status:** AGENDADO para 24/11/2026 às 17h00 via Metricool (id 440597956, uuid 2189661377832963375, [planner](https://app.metricool.com/planner/calendar?blogId=8315012&openWithPostUuid=2189661377832963375)). Arquivos: `episodios/2026-11-24_adidas-puma/` (video.mp4, capa.jpg, legenda.txt, fontes.md, producao/).
- **Troca de tema:** substitui Samuel Klein (bloqueado por decisão editorial — ver banco, item 2).
- **Roteiro (162 palavras faladas, 59,7 s, 14 falas):** gancho com o desfecho ("dividiram uma fábrica… e uma cidade inteira") → loop aberto ("a prova mais forte está num lugar inesperado"; cartão com tarjas) → 1924, lavanderia da mãe → Adi cria / Rudolf vende → Owens em 1936, 4 ouros → a guerra racha a família, motivo incerto → 1948, Ruda/Puma e Adidas (1949) → rio Aurach → re-gancho "e aqui a história vira" → cidade dividida (segundo Barbara Smit) → "cidade dos pescoços tortos" → clímax: mortos em 1974/1978, mesmo cemitério, lados opostos (tarjas reveladas) → 2009, partida com times misturados → frase-síntese + pergunta.
- **Fontes:** NPR (21/09/2009), HISTORY (history.com), comunicado da PUMA (22/09/2009), Fortune (2013), Mental Floss. Relatos de Smit atribuídos na narração e no rodapé. Lista completa em `fontes.md` da pasta do episódio.
- **Notas técnicas:** narração acelerada 1,07× (acima do teto de 1,05×) para caber em 60 s — próximos roteiros devem ficar em ~145–150 palavras faladas. faster-whisper não consegue baixar o modelo (proxy bloqueia Hugging Face): tempos via ElevenLabs Scribe (`creative_transcribe_audio` ligado ao nó de fala do mesmo flow, custo 0). Música ~16 dB abaixo da voz, mix −14,1 LUFS, 28,8 MB.

## Ficha do EP03 — Havaianas: do "chinelo de pobre" ao ícone

- **Status:** AGENDADO para 25/11/2026 às 17h00 via Buffer — Instagram Reel (post 6b0713d9db153417ca0ff640) e TikTok (post 6b0713dbade17749debfff65), capa = quadro aos 1,5 s (`thumbnailOffset` 1500). Arquivos: `episodios/2026-11-25_havaianas/` (video.mp4, capa.jpg, legenda.txt, fontes.md, producao/ep03.py, trilha.py, timing.json, words.json, narracao.mp3). Commit e93f461.
- **Roteiro (153 palavras, 51,5 s de voz, vídeo 53,4 s, 14 falas, sem aceleração):** âncora "A Havaianas do seu pé já foi chamada de chinelo de pobre" (marca na 2ª palavra e na tela desde o 1º quadro) → loop aberto "a virada veio de um truque que nem foi da marca" (cartão com tarjas) → 1962, Alpargatas, zori japonês → barata, azul e branca, calçado de trabalhador → anos 80, lista do governo contra a inflação com arroz e feijão → imitações / "as legítimas" → fama de chinelo de pobre, vendas caem → re-gancho "e aqui a história vira" → clímax (57% do vídeo): surfistas viravam a sola para ter uma cor só (tarjas reveladas) → Havaianas Top → 1998, Copa, bandeira na tira → mais de 200 milhões de pares/ano → "A borracha é a mesma. O que mudou foi o olhar." + pergunta.
- **Fontes:** Wikipedia (Havaianas), página "Our story" da Havaianas, História do Mundo, Highsnobiety, Ara (2026), monografia de Rodrigues (BOCC/UFPB, 2006). Detalhes em `fontes.md`.
- **Decisões de integridade:** o ano de lançamento da Top não foi dito na narração (Rodrigues diz 1994; a página da marca cita "Top" já em 1969); a queda de vendas aparece sem números (nenhuma fonte os traz); "mais de 200 milhões" é o piso comum de Wikipedia (~200 mi), Highsnobiety (220 mi) e Ara (228,7 mi).
- **Notas técnicas:** tempos via Scribe — as tags de emoção vêm como "palavras" e precisam ser filtradas. Render em 2 segmentos paralelos (~2 min), CRF 21, 25,9 MB, −14,2 LUFS, música ~15 dB abaixo da voz.

## Ficha do EP04 — Nintendo: antes do Mario, baralho

- **Status:** AGENDADO para 26/11/2026 às 17h00 via Buffer — Instagram Reel (post 6b0865b5d3b9c1cd667cc442) e TikTok (post 6b0865bfdba28007e9f3695b), capa = quadro aos 1,5 s (`thumbnailOffset` 1500). Arquivos: `episodios/2026-11-26_nintendo/` (video.mp4, capa.jpg, legenda.txt, fontes.md, producao/ep04.py, scenes.py, trilha.py, timing.json, words.json, narracao.mp3). Commit da2b852.
- **Roteiro (159 palavras, 14 falas, voz 57,9 s acelerada 1,04× → vídeo 57,7 s):** âncora "Antes do Mario, a Nintendo vendia baralho. E errou feio tentando mudar." (Mario e Nintendo nas 5 primeiras palavras; NINTENDO + "VENDIA BARALHO" na tela desde o 1º quadro) → loop aberto "a salvação veio de quem ninguém esperava" (cartão com tarjas) → Kyoto 1889, Fusajiro Yamauchi, hanafuda → 1949, Hiroshi assume aos 22 → 1959, Disney nas cartas → táxi, arroz instantâneo → quase tudo fracassa; 1964, baralho despenca → re-gancho "e aqui a história vira" → clímax (53%): 1965, Gunpei Yokoi, o homem da manutenção (tarjas reveladas) → braço extensível nas horas vagas; o presidente manda fabricar → Ultra Hand, 1966; Nintendo vira fábrica de brinquedos → Game & Watch (1980), Donkey Kong (1981) estreia o futuro Mario → "A ideia que salvou a Nintendo nasceu no chão da fábrica." + pergunta.
- **Fontes:** Nintendo Company History (site oficial), Wikipedia (History of Nintendo; Gunpei Yokoi), Film Stories (2022), Vice (Matt Alt, 2020), Fortune (2019), Inc. (2025), the-shashi.com. Detalhes em `fontes.md`.
- **Decisões de integridade:** ficaram de fora os números de fonte única (ação de 900 para 60 ienes; vendas da Ultra Hand — Vice 1,4 mi × Wikipedia "centenas de milhares"; 600 mil baralhos Disney) e o "motel do amor" (sem prova documental). Disney em 1959 (site oficial + 2 fontes; Wikipedia diz 1958). Mario não é desenhado (personagem protegido), só citado em texto.
- **Notas técnicas:** tempos via Scribe ligado ao nó de fala (custo 0); o filtro de tags precisa descartar também "mais" de "[suspense, mais devagar]". Render em 4 segmentos paralelos (~1 min), CRF 21, 28,4 MB, −14,7 LUFS, música ~16 dB abaixo da voz.

## Notas operacionais

Ver `claude/operacao-pipeline.md` (pipeline 100% na nuvem: ElevenLabs → render no workspace → GitHub → Buffer). Tarefa agendada diária às 13h47 para publicar às 17h.
