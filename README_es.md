<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · **Español** · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Grábate leyendo tu pitch. Tu agente lo convierte en un video demo listo para el lanzamiento.

**Entra un talking head → sale una demo de producto cortada, subtitulada, sonorizada y con lip-sync. A la primera.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#inicio-rápido)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#requisitos)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Inicio rápido](#inicio-rápido) · [Qué obtienes](#qué-obtienes) · [Cómo funciona](#cómo-funciona) · [Showcase](#showcase) · [Por qué sale bien a la primera](#por-qué-sale-bien-a-la-primera) · [FAQ](#faq) · [Documentación](#documentación)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Una grabación cruda de talking head a la izquierda se convierte en una demo de producto terminada a la derecha: gameplay, burbuja con la cara y subtítulos incrustados" width="1100" />

</div>

---

Entregas de hackathon, videos de lanzamiento y demos para inversores piden lo mismo: **tú explicando mientras el producto habla por sí solo.** Hacerlo a mano son horas en un editor: recortar los "eh", sincronizar el metraje con cada frase, subtitular, buscar efectos de sonido… y luego descubrir que tus labios van 300 ms desfasados.

**Pitch Video es una skill de agente que hace toda la edición.** Pásale a tu agente la grabación (y el guion y la app, si los tienes). Te transcribe, elimina los silencios, te acelera a 1.1× sin efecto ardilla, graba tu producto con un navegador guionizado, corta cada plano justo en la palabra que dices y añade subtítulos, una burbuja con tu cara, una animación explicativa, efectos de sonido cinematográficos y una música de fondo con ducking. Después **mide su propio resultado** (lip-sync, deriva de audio, sonoridad, claridad de voz) y se niega a entregarte un archivo roto.

Todo corre en local con ffmpeg, whisper.cpp y Playwright. Sin subidas, sin suscripciones, sin editor de línea de tiempo.

## Inicio rápido

### 1. Instala la skill

```bash
npx skills add codeswithroh/pitch-video
```

o, directamente para Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

El instalador copia la skill a `~/.claude/skills/pitch-video` (y a `~/.agents/skills/pitch-video` para otros agentes) y monta la caja de herramientas compartida: un venv de Python, Playwright Chromium, el modelo Whisper `small.en` y un modelo de puntos faciales. Reinicia tu agente al terminar.

### 2. Grábate

Lee tu guion a cámara. En horizontal, cara y hombros, en una habitación silenciosa. Haz una pausa para respirar entre secciones. Si te trabas, no pasa nada: vuelve a leer la frase.

> ¿Necesitas un guion? Pídeselo a tu agente: *"Escríbeme un guion de pitch video de 2 minutos para este repo usando la estructura narrativa de pitch-video."*

### 3. Pídeselo a tu agente

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Tu agente planifica las escenas a partir de lo que dijiste, graba tu app, renderiza, verifica y te entrega `out/demo.mp4` más un `demo_small.mp4` más ligero para subir.

## Qué obtienes

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay con burbuja de cara y subtítulo" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Plano de prueba ampliado con subtítulo" /></td>
</tr>
</table>

| Función | Qué hace |
| --- | --- |
| **Recorte de pausas** | Elimina los silencios y conserva las respiraciones naturales, con pausas más largas en los cambios de escena y en las que tú marques ("Until now." … *pausa*). |
| **Ritmo 1.1×** | Una entrega más ágil sin cambiar el tono. Imagen y voz se aceleran juntas, así que la sincronía es exacta. |
| **Cortes a la palabra** | Cada escena y plano se ancla a *una frase que dices*, así que el metraje cambia justo en la línea que lo presenta. |
| **Grabación guionizada del producto** | Genera un script de grabación de Playwright para tu app: Chrome con interfaz, un screencast CDP a 30 fps y un registro de eventos con marcas de tiempo para cortar. |
| **Burbuja de cara** | Encuadre automático a partir de puntos faciales, esquinas redondeadas y borde de color de acento. Se oculta en planos a pantalla completa y en la tarjeta final. |
| **Subtítulos correctos** | Tiempos de Whisper por fragmento, alineados palabra a palabra con tu guion: "Virev" pasa a ser **VRF** y el `**bold**` del guion se convierte en palabras resaltadas. |
| **Animaciones explicativas** | Diagramas HTML cuyos pasos van sincronizados con tu narración (`CUES.find(c => /sealed/.test(c.text))`). |
| **Sonido cinematográfico** | 23 SFX sintetizados (riser, boom, whoosh, lock, chime, glitch…), colocados automáticamente en cortes y tarjetas y atenuados bajo cada palabra hablada. Música de fondo opcional. |
| **Control de verificación** | Medición de lip-sync, comprobación de deriva A/V, auditoría de muestras decodificadas, dB de voz sobre fondo por línea, sonoridad EBU R128 y una hoja de contactos. Solo se entrega con `PASS`. |

## Cómo funciona

<img src="docs/assets/pipeline.svg" alt="Pipeline: entran tu video, tu guion y tu producto; la skill alinea, transcribe, recorta, graba, corta, superpone, sonoriza y verifica; sale demo.mp4" width="100%" />

Toda la edición vive en un único archivo legible, `project.json`. Las escenas empiezan en frases, los planos cambian en frases y los efectos de sonido se disparan en frases o en eventos grabados de la app:

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

Consulta la [referencia completa de project.json](docs/project-json.md) y el [recorrido por el pipeline](docs/pipeline.md).

## Showcase

### Nightfall: el pitch de hackathon de un battle royale onchain

[![Hoja de contactos del video demo de Nightfall](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Una toma de talking head de 2:25 se convirtió en una demo de 1:53 con 10 escenas, 18 planos, una secuencia de prueba con gameplay real, un diagrama de arquitectura animado y más de 40 efectos de sonido. La verificación midió **0 ms** de deriva de voz en todas las ventanas, **0 ms** de desfase de lip-sync y ≥14.6 dB de voz sobre el fondo en cada línea.

**[Míralo en YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [guion](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Cinco segundos de la demo de Nightfall: arena oscura, luz de antorchas, subtítulo y burbuja de cara" width="720" />

¿Hiciste algo con Pitch Video? [Abre un issue](https://github.com/codeswithroh/pitch-video/issues) con el enlace y lo añadimos aquí.

## Por qué sale bien a la primera

Esta skill se extrajo de una edición real que costó muchas iteraciones dolorosas. Cada fallo se convirtió en una regla que la skill ahora impone:

- **"Mis labios no coinciden."** Los archivos de QuickTime y del móvil suelen arrancar el audio unos 150 ms después del video. La skill realinea explícitamente antes de cualquier otra cosa.
- **"La sincronía se desvía más adelante."** Los cortes caen en la rejilla de fotogramas de 30 fps, por número de fotograma *y* por el número de muestra de audio correspondiente. Nada se acumula.
- **"Mi voz se corta antes que mi boca."** Un único grafo combinado de ffmpeg perdía en silencio 9 segundos de muestras de audio (loudnorm emite a 192 kHz). Ahora imagen y sonido se renderizan en pasadas separadas, cada rama se remuestrea a 48 kHz y el verificador decodifica el archivo final para demostrar el número de muestras.
- **"Los subtítulos llegan tarde."** Las marcas de tiempo de Whisper sobre el archivo completo se retrasan. La transcripción por fragmentos coloca los subtítulos justo en los límites del habla.
- **"Los efectos me tapan."** Los efectos bajan −9 dB bajo cada línea hablada, los golpes fuertes pasan por un filtro paso bajo si tocan la voz y el boom final suena *después* de tu última palabra.
- **"El metraje se ve borroso."** El grabador integrado de Playwright es VP8 de bajo bitrate. La skill usa un screencast CDP desde Chrome con interfaz y GPU activada.

La lista completa está en [docs/lessons.md](docs/lessons.md).

## Requisitos

- macOS o Linux, con `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ y Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Alrededor de 1 GB de disco para la caja de herramientas (Chromium, modelo de Whisper, venv), compartida entre proyectos.

## FAQ

<details>
<summary><strong>¿Qué agentes pueden usarla?</strong></summary>

Cualquier agente que cargue skills `SKILL.md` y pueda ejecutar comandos de shell: Claude Code, Codex, Cursor, Gemini CLI y otros vía `npx skills add`. Los scripts son Python, Node y ffmpeg sin más, así que también puedes ejecutar el [pipeline a mano](docs/pipeline.md).

</details>

<details>
<summary><strong>No tengo guion. ¿Funciona igual?</strong></summary>

Sí. Los subtítulos salen directamente de Whisper y tu agente los revisa. El guion solo sirve para que la jerga y los nombres de producto queden exactos, y para marcar énfasis con `**bold**`.

</details>

<details>
<summary><strong>Mi producto no es una web app.</strong></summary>

Usa cualquier metraje: grabaciones de pantalla, capturas del simulador o imágenes. Coloca los fotogramas en `shots/<name>/` con un `stamps.json`, o usa planos `image`. La plantilla de grabación web es una comodidad, no un requisito.

</details>

<details>
<summary><strong>¿Puedo usar mi propia música?</strong></summary>

Define `"music": "path/to/track.mp3"`. Se reproduce en bucle, se normaliza a volumen bajo y se atenúa con side-chain bajo tu voz. Usa `"none"` para silencio.

</details>

<details>
<summary><strong>¿Video vertical para TikTok, Reels o Shorts?</strong></summary>

Todavía no: la salida es 1920×1080. El 9:16 es lo primero en el [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>¿Se sube algo?</strong></summary>

No. La transcripción, el render y el análisis se ejecutan en tu máquina. Tu agente ve la transcripción y la línea de tiempo, y su proveedor de modelo tiene su propia política de datos.

</details>

## Documentación

- [Recorrido por el pipeline](docs/pipeline.md): cada paso, sus entradas y salidas, y cómo volver a ejecutar uno.
- [Referencia de project.json](docs/project-json.md): escenas, planos, tarjetas, animaciones, efectos de sonido, tema y música.
- [Lecciones](docs/lessons.md): los fallos que esta skill evita y por qué.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): las instrucciones que sigue tu agente.

## Contribuir

Los issues y PR son bienvenidos, sobre todo nuevos SFX, temas de subtítulos, salida vertical y videos para el showcase. Consulta [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

[MIT](LICENSE). Los modelos de Whisper y MediaPipe se descargan de sus fuentes originales y mantienen sus propias licencias.
