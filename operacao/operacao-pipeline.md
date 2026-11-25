# Império de Ideias — pipeline em produção (atualizado 25/11/2026)

- **Tarefa agendada:** roda todo dia às 13h47 (Brasília), só na nuvem, e agenda o vídeo do dia para 17h00.
- **Narração:** conector ElevenLabs, modelo eleven_v4, voz "Flavio Francisco" (voice_id x6uRgOliu4lpcrqMH3s1), 1 geração por roteiro. Áudio baixado direto de `elevenlabsusercontent.com`.
- **Tempos das palavras:** `creative_transcribe_audio` (eleven_scribe_v1) ligado ao nó de fala do mesmo flow (custo 0). Atenção: o Scribe devolve as tags de emoção como "palavras" (ex.: "[suspense," "mais" "devagar]") — filtrar tudo entre colchetes antes de montar words.json.
- **Render:** motor em `operacao/motor/` + episódio mais recente como base (ex.: `episodios/2026-11-25_havaianas/producao/ep03.py`). O workspace tem 2 núcleos: renderizar em 2 segmentos paralelos (~2 min para 53 s), concatenar e codificar com CRF 21 (~26 MB).
- **Hospedagem:** repositório público `tiagorff/imperio-de-ideias-media`. Pasta por episódio: `episodios/AAAA-MM-DD_tema/` com video.mp4, capa.jpg, legenda.txt, fontes.md, producao/.
- **Publicação (desde 25/11):** Buffer, organização "My organization" (6b05ff6bd2938b73c20d0480). Instagram channelId 6b0600718541f09ecb911d8e (Reel, shouldShareToFeed, isAiGenerated) e TikTok channelId 6b0600108541f09ecb911948 (isAiGenerated, title). Vídeo por link raw.githubusercontent.com; capa = quadro do vídeo via `thumbnailOffset` (ms). O Metricool não é mais usado.
