<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · **Deutsch** · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

# Pitch Video

### Nimm dich beim Vorlesen deines Pitches auf. Dein Agent macht daraus ein fertiges Launch-Demovideo.

**Talking Head rein → geschnittene, untertitelte, vertonte, lippensynchrone Produktdemo raus. Beim ersten Versuch.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#schnellstart)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#voraussetzungen)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Schnellstart](#schnellstart) · [Was du bekommst](#was-du-bekommst) · [So funktioniert's](#so-funktionierts) · [Showcase](#showcase) · [Warum es auf Anhieb klappt](#warum-es-auf-anhieb-klappt) · [FAQ](#faq) · [Dokumentation](#dokumentation)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Eine rohe Talking-Head-Aufnahme links wird rechts zu einer fertigen Produktdemo: Gameplay, Gesichtsblase und eingebrannte Untertitel" width="1100" />

</div>

---

Hackathon-Einreichungen, Launch-Videos und Investoren-Demos wollen alle dasselbe: **dich, wie du erklärst, während das Produkt für sich spricht.** Von Hand heißt das stundenlang im Schnittprogramm: Ähs rausschneiden, Footage auf jeden Satz legen, untertiteln, Soundeffekte suchen und am Ende feststellen, dass deine Lippen 300 ms daneben liegen.

**Pitch Video ist ein Agent-Skill, der den kompletten Schnitt übernimmt.** Gib deinem Agenten die Aufnahme (und dein Skript und deine App, falls vorhanden). Er transkribiert dich, schneidet Leerlauf raus, beschleunigt dich auf 1.1× ohne Mickymaus-Effekt, filmt dein Produkt mit einem geskripteten Browser, schneidet jede Einstellung exakt auf das Wort, das du sagst, und fügt Untertitel, eine Gesichtsblase, eine erklärende Animation, kinoreife Soundeffekte und eine geduckte Hintergrundmusik hinzu. Dann **misst er sein eigenes Ergebnis** (Lippensynchronität, Audio-Drift, Lautheit, Sprachverständlichkeit) und weigert sich, dir eine kaputte Datei zu geben.

Alles läuft lokal mit ffmpeg, whisper.cpp und Playwright. Keine Uploads, keine Abos, kein Timeline-Editor.

## Schnellstart

### 1. Skill installieren

```bash
npx skills add codeswithroh/pitch-video
```

oder direkt für Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

Der Installer kopiert den Skill nach `~/.claude/skills/pitch-video` (und nach `~/.agents/skills/pitch-video` für andere Agenten) und baut die gemeinsame Toolbox auf: ein Python-venv, Playwright Chromium, das Whisper-Modell `small.en` und ein Gesichts-Landmark-Modell. Starte deinen Agenten danach neu.

### 2. Nimm dich auf

Lies dein Skript in die Kamera. Querformat, Gesicht und Schultern, ruhiger Raum. Atme zwischen den Abschnitten kurz durch. Versprecher sind kein Problem: Lies die Zeile einfach noch mal.

> Kein Skript? Frag deinen Agenten: *„Schreib mir ein 2-minütiges Pitch-Video-Skript für dieses Repo nach der Story-Struktur von pitch-video.“*

### 3. Frag deinen Agenten

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Dein Agent plant die Szenen anhand dessen, was du gesagt hast, filmt deine App, rendert, prüft und übergibt dir `out/demo.mp4` plus ein kleineres `demo_small.mp4` für Uploads.

## Was du bekommst

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay mit Gesichtsblase und Untertitel" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Herangezoomte Beweis-Einstellung mit Untertitel" /></td>
</tr>
</table>

| Feature | Was es macht |
| --- | --- |
| **Pausen kürzen** | Schneidet Leerlauf raus und behält natürliche Atempausen, mit längeren Beats bei Szenenwechseln und an Stellen, die du festlegst ("Until now." … *Beat*). |
| **1.1×-Tempo** | Straffere Sprechweise bei gleicher Tonhöhe. Bild und Stimme werden gemeinsam beschleunigt, die Synchronität bleibt exakt. |
| **Wortgenaue Schnitte** | Jede Szene und Einstellung hängt an *einer Phrase, die du sagst*, sodass das Bild genau bei dem Satz wechselt, der es einführt. |
| **Geskriptete Produktaufnahmen** | Erzeugt ein Playwright-Drehskript für deine App: Chrome mit Fenster, ein 30-fps-CDP-Screencast und ein Event-Log mit Zeitstempeln zum Schneiden. |
| **Gesichtsblase** | Automatisch anhand von Gesichts-Landmarks gerahmt, abgerundet, mit Akzentrahmen. Ausgeblendet bei Vollbild-Einstellungen und auf der Endkarte. |
| **Untertitel, die stimmen** | Whisper-Timing pro Abschnitt, dann wortgenau an dein Skript angeglichen: aus "Virev" wird **VRF**, und `**bold**` im Skript wird zu hervorgehobenen Wörtern. |
| **Erklär-Animationen** | HTML-Diagramme, deren Schritte an deine Erzählung gekoppelt sind (`CUES.find(c => /sealed/.test(c.text))`). |
| **Kinoreifer Sound** | 23 synthetisierte SFX (Riser, Boom, Whoosh, Lock, Chime, Glitch…), automatisch auf Schnitte und Karten gesetzt und unter jedem gesprochenen Wort geduckt. Optionale Hintergrundmusik. |
| **Prüf-Gate** | Lippensync-Messung, A/V-Drift-Check, Audit der dekodierten Samples, Stimme-über-Hintergrund in dB pro Zeile, EBU-R128-Lautheit und ein Kontaktabzug. Ausgeliefert wird nur bei `PASS`. |

## So funktioniert's

<img src="docs/assets/pipeline.svg" alt="Pipeline: Dein Video, Skript und Produkt gehen rein; der Skill gleicht ab, transkribiert, kürzt, filmt, schneidet, überlagert, vertont und prüft; heraus kommt demo.mp4" width="100%" />

Der gesamte Schnitt steckt in einer lesbaren Datei, `project.json`. Szenen beginnen bei Phrasen, Einstellungen wechseln bei Phrasen, und Sound-Cues feuern bei Phrasen oder bei aufgezeichneten App-Events:

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

Siehe die vollständige [project.json-Referenz](docs/project-json.md) und den [Pipeline-Rundgang](docs/pipeline.md).

## Showcase

### Nightfall: ein Hackathon-Pitch für ein Onchain-Battle-Royale

[![Kontaktabzug des Nightfall-Demovideos](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Aus einem 2:25-Talking-Head-Take wurde eine 1:53-Demo mit 10 Szenen, 18 Einstellungen, einer Live-Gameplay-Beweissequenz, einem animierten Architekturdiagramm und über 40 Sound-Cues. Die Prüfung maß **0 ms** Stimm-Drift in jedem Fenster, **0 ms** Lippensync-Versatz und ≥14.6 dB Stimme über Hintergrund in jeder Zeile.

**[Auf YouTube ansehen](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [Skript](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Fünf Sekunden der Nightfall-Demo: dunkle Arena, Fackellicht, Untertitel, Gesichtsblase" width="720" />

Etwas mit Pitch Video gebaut? [Eröffne ein Issue](https://github.com/codeswithroh/pitch-video/issues) mit Link, und wir nehmen es hier auf.

## Warum es auf Anhieb klappt

Dieser Skill stammt aus einem echten Schnitt, der viele schmerzhafte Iterationen gebraucht hat. Jeder Fehler wurde zu einer Regel, die der Skill jetzt durchsetzt:

- **„Meine Lippen passen nicht.“** Bei QuickTime- und Handy-Dateien startet der Ton oft etwa 150 ms nach dem Bild. Der Skill gleicht das vor allem anderen explizit aus.
- **„Später im Video driftet die Synchronität.“** Schnitte landen auf dem 30-fps-Frame-Raster, nach Frame-Nummer *und* passender Audio-Sample-Nummer. Nichts summiert sich.
- **„Meine Stimme hört vor meinem Mund auf.“** Ein kombinierter ffmpeg-Graph hat stillschweigend 9 Sekunden Audio-Samples verschluckt (loudnorm gibt 192 kHz aus). Bild und Ton werden jetzt in getrennten Durchläufen gerendert, jeder Zweig wird auf 48 kHz resampelt, und der Prüfer dekodiert die fertige Datei, um die Sample-Anzahl nachzuweisen.
- **„Die Untertitel kommen zu spät.“** Whisper-Zeitstempel über die ganze Datei hinken hinterher. Transkription pro Abschnitt setzt Untertitel exakt auf die Sprachgrenzen.
- **„Die Effekte übertönen mich.“** Soundeffekte werden unter jeder gesprochenen Zeile um −9 dB geduckt, schwere Hits werden tiefpassgefiltert, wenn sie Sprache berühren, und der letzte Boom kommt *nach* deinem letzten Wort.
- **„Das Footage sieht verwaschen aus.“** Der eingebaute Recorder von Playwright liefert VP8 mit niedriger Bitrate. Der Skill nutzt einen CDP-Screencast aus Chrome mit Fenster und aktivierter GPU.

Die vollständige Liste steht in [docs/lessons.md](docs/lessons.md).

## Voraussetzungen

- macOS oder Linux, mit `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ und Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Etwa 1 GB Speicherplatz für die Toolbox (Chromium, Whisper-Modell, venv), geteilt zwischen Projekten.

## FAQ

<details>
<summary><strong>Welche Agenten können es nutzen?</strong></summary>

Jeder Agent, der `SKILL.md`-Skills lädt und Shell-Befehle ausführen kann: Claude Code, Codex, Cursor, Gemini CLI und andere über `npx skills add`. Die Skripte sind schlichtes Python, Node und ffmpeg, du kannst die [Pipeline also auch von Hand](docs/pipeline.md) laufen lassen.

</details>

<details>
<summary><strong>Ich habe kein Skript. Geht es trotzdem?</strong></summary>

Ja. Die Untertitel kommen direkt aus Whisper, und dein Agent liest sie Korrektur. Ein Skript sorgt nur dafür, dass Fachbegriffe und Produktnamen exakt stimmen, und erlaubt Betonungen mit `**bold**`.

</details>

<details>
<summary><strong>Mein Produkt ist keine Web-App.</strong></summary>

Nimm beliebiges Material: Bildschirmaufnahmen, Simulator-Mitschnitte oder Bilder. Leg die Frames mit einer `stamps.json` in `shots/<name>/`, oder nutze `image`-Einstellungen. Die Web-Drehvorlage ist eine Bequemlichkeit, keine Pflicht.

</details>

<details>
<summary><strong>Kann ich meine eigene Musik verwenden?</strong></summary>

Setze `"music": "path/to/track.mp3"`. Sie wird geloopt, leise normalisiert und per Sidechain unter deiner Stimme geduckt. Mit `"none"` gibt es Stille.

</details>

<details>
<summary><strong>Hochformat für TikTok, Reels oder Shorts?</strong></summary>

Noch nicht: Die Ausgabe ist 1920×1080. 9:16 steht ganz oben auf der [Roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Wird irgendetwas hochgeladen?</strong></summary>

Nein. Transkription, Rendering und Analyse laufen komplett auf deinem Rechner. Dein Agent sieht das Transkript und die Timeline, und sein Modellanbieter hat eigene Datenrichtlinien.

</details>

## Dokumentation

- [Pipeline-Rundgang](docs/pipeline.md): jeder Schritt, seine Ein- und Ausgaben und wie man ihn erneut ausführt.
- [project.json-Referenz](docs/project-json.md): Szenen, Einstellungen, Karten, Animationen, Sound-Cues, Theme und Musik.
- [Lektionen](docs/lessons.md): die Fehlerbilder, die dieser Skill verhindert, und warum.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): die Anweisungen, denen dein Agent folgt.

## Mitwirken

Issues und PRs sind willkommen, besonders neue SFX, Untertitel-Themes, Hochformat-Ausgabe und Showcase-Videos. Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz

[MIT](LICENSE). Die Whisper- und MediaPipe-Modelle werden aus ihren Originalquellen heruntergeladen und behalten ihre eigenen Lizenzen.
