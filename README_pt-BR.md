<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · **Português (Brasil)** · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Grave você lendo o seu pitch. Seu agente transforma isso em um vídeo demo pronto para o lançamento.

**Entra um talking head → sai uma demo de produto cortada, legendada, sonorizada e com lip-sync. De primeira.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#início-rápido)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#requisitos)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Início rápido](#início-rápido) · [O que você ganha](#o-que-você-ganha) · [Como funciona](#como-funciona) · [Vitrine](#vitrine) · [Por que funciona de primeira](#por-que-funciona-de-primeira) · [FAQ](#faq) · [Documentação](#documentação)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Uma gravação crua de talking head à esquerda vira uma demo de produto finalizada à direita: gameplay, bolha com o rosto e legendas embutidas" width="1100" />

</div>

---

Submissões de hackathon, vídeos de lançamento e demos para investidores querem a mesma coisa: **você explicando enquanto o produto fala por si.** Fazer isso na mão significa horas num editor: cortar os "é…", sincronizar as imagens com cada frase, legendar, caçar efeitos sonoros e, no fim, descobrir que seus lábios estão 300 ms fora de sincronia.

**Pitch Video é uma skill de agente que faz a edição inteira.** Entregue a gravação ao seu agente (e o roteiro e o app, se tiver). Ele transcreve você, corta o silêncio, acelera para 1.1× sem voz de esquilo, grava seu produto com um navegador roteirizado, corta cada take exatamente na palavra que você diz e adiciona legendas, uma bolha com seu rosto, uma animação explicativa, efeitos sonoros cinematográficos e uma trilha com ducking. Depois ele **mede o próprio resultado** (lip-sync, drift de áudio, loudness, clareza da voz) e se recusa a te entregar um arquivo quebrado.

Tudo roda localmente com ffmpeg, whisper.cpp e Playwright. Sem uploads, sem assinaturas, sem editor de timeline.

## Início rápido

### 1. Instale a skill

```bash
npx skills add codeswithroh/pitch-video
```

ou, direto para o Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

O instalador copia a skill para `~/.claude/skills/pitch-video` (e para `~/.agents/skills/pitch-video` para outros agentes) e monta a caixa de ferramentas compartilhada: um venv Python, o Playwright Chromium, o modelo Whisper `small.en` e um modelo de pontos faciais. Reinicie seu agente depois.

### 2. Grave você mesmo

Leia seu roteiro para a câmera. Na horizontal, rosto e ombros, em um cômodo silencioso. Respire entre as seções. Gaguejou? Tudo bem, é só reler a frase.

> Precisa de um roteiro? Peça ao seu agente: *"Escreva um roteiro de pitch video de 2 minutos para este repo usando a estrutura narrativa do pitch-video."*

### 3. Peça ao seu agente

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Seu agente planeja as cenas a partir do que você disse, grava seu app, renderiza, verifica e te entrega `out/demo.mp4`, além de um `demo_small.mp4` menor para upload.

## O que você ganha

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay com bolha de rosto e legenda" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Take de prova ampliado com legenda" /></td>
</tr>
</table>

| Recurso | O que faz |
| --- | --- |
| **Corte de pausas** | Remove o silêncio e mantém as respirações naturais, com pausas mais longas nas trocas de cena e nas que você escolher ("Until now." … *pausa*). |
| **Ritmo 1.1×** | Fala mais enxuta com o tom preservado. Imagem e voz são aceleradas juntas, então a sincronia continua exata. |
| **Cortes na palavra** | Cada cena e take é ancorado em *uma frase que você diz*, então a imagem muda exatamente na fala que a apresenta. |
| **Gravação roteirizada do produto** | Gera um script de gravação Playwright para o seu app: Chrome com interface, screencast CDP a 30 fps e um log de eventos com timestamps para guiar os cortes. |
| **Bolha de rosto** | Enquadramento automático a partir de pontos faciais, cantos arredondados e borda na cor de destaque. Some em takes de tela cheia e no card final. |
| **Legendas certinhas** | Tempos do Whisper por trecho, alinhados palavra por palavra ao seu roteiro: "Virev" vira **VRF** e o `**bold**` do roteiro vira palavras destacadas. |
| **Animações explicativas** | Diagramas HTML cujas etapas seguem a sua narração (`CUES.find(c => /sealed/.test(c.text))`). |
| **Som cinematográfico** | 23 SFX sintetizados (riser, boom, whoosh, lock, chime, glitch…), posicionados automaticamente em cortes e cards e abaixados sob cada palavra falada. Trilha de fundo opcional. |
| **Portão de verificação** | Medição de lip-sync, checagem de drift A/V, auditoria das amostras decodificadas, dB de voz sobre o fundo por fala, loudness EBU R128 e uma folha de contato. Só entrega com `PASS`. |

## Como funciona

<img src="docs/assets/pipeline.svg" alt="Pipeline: entram seu vídeo, seu roteiro e seu produto; a skill alinha, transcreve, corta pausas, grava, edita, sobrepõe, sonoriza e verifica; sai demo.mp4" width="100%" />

A edição inteira vive em um único arquivo legível, `project.json`. Cenas começam em frases, takes trocam em frases e os efeitos sonoros disparam em frases ou em eventos gravados do app:

```jsonc
{
  "speed": 1.1,
  "scenes": [
    { "title": "The hook", "start": "Every onchain game", "shots": [
      { "speaker": true },
      { "from": "If it lives", "rec": "main", "t": 9.8 } ]},
    { "title": "The problem", "start": "fog of war", "shots": [
      { "rec": "main", "t": 18.8, "card": "problem" },
      { "from": "Until now", "title": "UNTIL NOW." } ]},
    { "title": "How it works", "start": "Every position is sealed", "shots": [{ "anim": "diagram" }] }
  ],
  "sfx": [{ "sound": "denied", "phrase": "null", "edge": "end", "offset": -0.4 }]
}
```

Veja a [referência completa do project.json](docs/project-json.md) e o [passo a passo do pipeline](docs/pipeline.md).

## Vitrine

### Nightfall: o pitch de hackathon de um battle royale onchain

[![Folha de contato do vídeo demo do Nightfall](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Um take de talking head de 2:25 virou uma demo de 1:53 com 10 cenas, 18 takes, uma sequência de prova com gameplay ao vivo, um diagrama de arquitetura animado e mais de 40 efeitos sonoros. A verificação mediu **0 ms** de drift de voz em todas as janelas, **0 ms** de desvio de lip-sync e ≥14.6 dB de voz sobre o fundo em todas as falas.

**[Assista no YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [roteiro](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Cinco segundos da demo do Nightfall: arena escura, luz de tochas, legenda e bolha de rosto" width="720" />

Fez algo com o Pitch Video? [Abra uma issue](https://github.com/codeswithroh/pitch-video/issues) com o link e a gente adiciona aqui.

## Por que funciona de primeira

Esta skill foi extraída de uma edição real que levou muitas iterações sofridas. Cada falha virou uma regra que a skill agora aplica:

- **"Meus lábios não batem."** Arquivos do QuickTime e de celular costumam começar o áudio uns 150 ms depois do vídeo. A skill realinha explicitamente antes de qualquer coisa.
- **"A sincronia escorrega mais pra frente."** Os cortes caem na grade de quadros de 30 fps, pelo número do quadro *e* pelo número da amostra de áudio correspondente. Nada se acumula.
- **"Minha voz para antes da minha boca."** Um grafo combinado do ffmpeg descartava em silêncio 9 segundos de amostras de áudio (o loudnorm emite 192 kHz). Agora imagem e som são renderizados em passadas separadas, cada ramo é reamostrado para 48 kHz e o verificador decodifica o arquivo final para provar a contagem de amostras.
- **"As legendas parecem atrasadas."** Os timestamps do Whisper no arquivo inteiro atrasam. A transcrição por trechos coloca as legendas exatamente nos limites da fala.
- **"Os efeitos abafam minha voz."** Os efeitos abaixam −9 dB sob cada fala, impactos pesados passam por passa-baixa se encostarem na voz e o boom final vem *depois* da sua última palavra.
- **"A imagem fica borrada."** O gravador nativo do Playwright é VP8 de baixo bitrate. A skill usa um screencast CDP do Chrome com interface e GPU ligada.

A lista completa está em [docs/lessons.md](docs/lessons.md).

## Requisitos

- macOS ou Linux, com `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ e Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Cerca de 1 GB de disco para a caixa de ferramentas (Chromium, modelo Whisper, venv), compartilhada entre projetos.

## FAQ

<details>
<summary><strong>Quais agentes podem usar?</strong></summary>

Qualquer agente que carregue skills `SKILL.md` e consiga rodar comandos de shell: Claude Code, Codex, Cursor, Gemini CLI e outros via `npx skills add`. Os scripts são Python, Node e ffmpeg puros, então você também pode rodar o [pipeline na mão](docs/pipeline.md).

</details>

<details>
<summary><strong>Não tenho roteiro. Funciona mesmo assim?</strong></summary>

Sim. As legendas vêm direto do Whisper e seu agente as revisa. O roteiro só deixa jargões e nomes de produto exatos, e permite marcar ênfase com `**bold**`.

</details>

<details>
<summary><strong>Meu produto não é um web app.</strong></summary>

Use qualquer material: gravações de tela, capturas do simulador ou imagens. Coloque os quadros em `shots/<name>/` com um `stamps.json`, ou use takes `image`. O template de gravação web é uma conveniência, não um requisito.

</details>

<details>
<summary><strong>Posso usar minha própria música?</strong></summary>

Defina `"music": "path/to/track.mp3"`. Ela toca em loop, é normalizada em volume baixo e abaixada via side-chain sob a sua voz. Use `"none"` para silêncio.

</details>

<details>
<summary><strong>Vídeo vertical para TikTok, Reels ou Shorts?</strong></summary>

Ainda não: a saída é 1920×1080. O 9:16 é o primeiro item do [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Alguma coisa é enviada para fora?</strong></summary>

Não. Transcrição, renderização e análise rodam todas na sua máquina. Seu agente vê a transcrição e a timeline, e o provedor do modelo dele tem a própria política de dados.

</details>

## Documentação

- [Passo a passo do pipeline](docs/pipeline.md): cada etapa, suas entradas e saídas, e como rodar uma de novo.
- [Referência do project.json](docs/project-json.md): cenas, takes, cards, animações, efeitos sonoros, tema e música.
- [Lições](docs/lessons.md): as falhas que esta skill evita, e por quê.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): as instruções que seu agente segue.

## Contribuindo

Issues e PRs são bem-vindos, especialmente novos SFX, temas de legenda, saída vertical e vídeos para a vitrine. Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

[MIT](LICENSE). Os modelos Whisper e MediaPipe são baixados das fontes originais e mantêm suas próprias licenças.
