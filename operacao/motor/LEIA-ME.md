# Motor de vídeo (referência do EP01)

- `render_base.py`: utilitários de desenho (skia), grão, legendas. Espera as fontes em `../ep01/fonts/` relativo ao script que o importa (Anton, Bebas Neue, Montserrat SemiBold/Medium/ExtraBold — baixar de raw.githubusercontent.com/google/fonts e JulietaUla/Montserrat).
- `premium_ep01_kodak.py`: cenas do EP01 no estilo premium aprovado (blueprint, documentos, números, linha do tempo). Copie a estrutura e troque as cenas para a história do dia.
- `trilha_ep01.py`: trilha e efeitos sintetizados (sem música de terceiros), lê `timing.json` e `words.json`.
- Dependências: `pip install skia-python --break-system-packages`; ffmpeg; numpy/scipy.
- Saída: 1080x1920, 30 fps, H.264 (pix_fmt de entrada bgra), AAC, −14 LUFS.
