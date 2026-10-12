<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · **Français** · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Filmez-vous en lisant votre pitch. Votre agent en fait une vidéo de démo prête pour le lancement.

**Un face caméra en entrée → une démo produit montée, sous-titrée, sonorisée et synchronisée aux lèvres en sortie. Du premier coup.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#démarrage-rapide)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#prérequis)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Démarrage rapide](#démarrage-rapide) · [Ce que vous obtenez](#ce-que-vous-obtenez) · [Comment ça marche](#comment-ça-marche) · [Vitrine](#vitrine) · [Pourquoi ça marche du premier coup](#pourquoi-ça-marche-du-premier-coup) · [FAQ](#faq) · [Documentation](#documentation)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Un enregistrement brut en face caméra à gauche devient une démo produit finie à droite : séquences de jeu, bulle avec le visage, sous-titres incrustés" width="1100" />

</div>

---

Rendus de hackathon, vidéos de lancement, démos pour investisseurs : tous veulent la même chose, **vous qui expliquez pendant que le produit parle de lui-même.** À la main, c'est des heures dans un logiciel de montage : couper les « euh », caler les images sur chaque phrase, sous-titrer, chercher des effets sonores… puis découvrir que vos lèvres sont décalées de 300 ms.

**Pitch Video est une skill d'agent qui fait tout le montage.** Donnez l'enregistrement à votre agent (avec votre script et votre app si vous les avez). Il vous transcrit, supprime les blancs, vous accélère à 1.1× sans effet voix de souris, filme votre produit avec un navigateur scripté, cale chaque plan sur le mot exact que vous prononcez, puis ajoute sous-titres, bulle avec votre visage, animation explicative, effets sonores cinématographiques et musique de fond avec ducking. Ensuite, il **mesure son propre rendu** (synchro labiale, dérive audio, loudness, clarté de la voix) et refuse de vous livrer un fichier cassé.

Tout tourne en local avec ffmpeg, whisper.cpp et Playwright. Pas d'upload, pas d'abonnement, pas de timeline.

## Démarrage rapide

### 1. Installez la skill

```bash
npx skills add codeswithroh/pitch-video
```

ou, directement pour Claude Code :

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

L'installateur copie la skill dans `~/.claude/skills/pitch-video` (et dans `~/.agents/skills/pitch-video` pour les autres agents) et prépare la boîte à outils partagée : un venv Python, Playwright Chromium, le modèle Whisper `small.en` et un modèle de points du visage. Redémarrez ensuite votre agent.

### 2. Filmez-vous

Lisez votre script face caméra. Format paysage, visage et épaules, pièce calme. Marquez une respiration entre les sections. Vous butez sur un mot ? Pas grave, relisez la phrase.

> Besoin d'un script ? Demandez à votre agent : *« Écris-moi un script de pitch video de 2 minutes pour ce repo en suivant la structure narrative de pitch-video. »*

### 3. Demandez à votre agent

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Votre agent planifie les scènes à partir de ce que vous avez dit, filme votre app, fait le rendu, vérifie, puis vous remet `out/demo.mp4` ainsi qu'un `demo_small.mp4` plus léger pour les uploads.

## Ce que vous obtenez

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Séquence de jeu avec bulle de visage et sous-titre" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Plan de preuve zoomé avec sous-titre" /></td>
</tr>
</table>

| Fonctionnalité | Ce qu'elle fait |
| --- | --- |
| **Coupe des silences** | Supprime les blancs en gardant les respirations naturelles, avec des temps plus longs aux changements de scène et aux pauses que vous choisissez ("Until now." … *temps*). |
| **Rythme 1.1×** | Un débit plus serré, sans changer la hauteur de la voix. Image et voix sont accélérées ensemble, la synchro reste exacte. |
| **Coupes au mot près** | Chaque scène et chaque plan est ancré à *une phrase que vous dites* : l'image change pile sur la réplique qui l'introduit. |
| **Captation produit scriptée** | Génère un script de tournage Playwright pour votre app : Chrome en mode fenêtré, screencast CDP à 30 fps et journal d'événements horodaté pour caler le montage. |
| **Bulle de visage** | Cadrage automatique à partir des points du visage, coins arrondis, bordure de couleur d'accent. Masquée sur les plans plein écran et le carton de fin. |
| **Des sous-titres justes** | Timing Whisper par segment, puis alignement mot à mot sur votre script : "Virev" devient **VRF** et le `**bold**` du script devient des mots surlignés. |
| **Animations explicatives** | Des schémas HTML dont les étapes suivent votre narration (`CUES.find(c => /sealed/.test(c.text))`). |
| **Son cinématographique** | 23 SFX synthétisés (riser, boom, whoosh, lock, chime, glitch…), placés automatiquement sur les coupes et les cartons, et atténués sous chaque mot prononcé. Musique de fond en option. |
| **Contrôle de vérification** | Mesure de la synchro labiale, contrôle de dérive A/V, audit des échantillons décodés, dB voix/fond par réplique, loudness EBU R128 et planche contact. Livré uniquement sur `PASS`. |

## Comment ça marche

<img src="docs/assets/pipeline.svg" alt="Pipeline : votre vidéo, votre script et votre produit entrent ; la skill aligne, transcrit, coupe, filme, monte, superpose, sonorise et vérifie ; demo.mp4 sort" width="100%" />

Tout le montage tient dans un seul fichier lisible, `project.json`. Les scènes démarrent sur des phrases, les plans changent sur des phrases, et les effets sonores se déclenchent sur des phrases ou sur des événements enregistrés de l'app :

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

Voir la [référence complète de project.json](docs/project-json.md) et le [tour du pipeline](docs/pipeline.md).

## Vitrine

### Nightfall : le pitch de hackathon d'un battle royale onchain

[![Planche contact de la vidéo de démo Nightfall](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Une prise face caméra de 2:25 est devenue une démo de 1:53 avec 10 scènes, 18 plans, une séquence de preuve en jeu réel, un schéma d'architecture animé et plus de 40 effets sonores. La vérification a mesuré **0 ms** de dérive de la voix sur toutes les fenêtres, **0 ms** de décalage labial et ≥14.6 dB de voix au-dessus du fond sur chaque réplique.

**[Regarder sur YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [script](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Cinq secondes de la démo Nightfall : arène sombre, lueur des torches, sous-titre, bulle de visage" width="720" />

Vous avez fait quelque chose avec Pitch Video ? [Ouvrez une issue](https://github.com/codeswithroh/pitch-video/issues) avec le lien et on l'ajoute ici.

## Pourquoi ça marche du premier coup

Cette skill est tirée d'un vrai montage qui a demandé de nombreuses itérations douloureuses. Chaque échec est devenu une règle que la skill applique désormais :

- **« Mes lèvres ne correspondent pas. »** Les fichiers QuickTime et de téléphone démarrent souvent l'audio environ 150 ms après la vidéo. La skill réaligne explicitement avant toute chose.
- **« La synchro dérive plus loin dans la vidéo. »** Les coupes tombent sur la grille d'images à 30 fps, par numéro d'image *et* par numéro d'échantillon audio correspondant. Rien ne s'accumule.
- **« Ma voix s'arrête avant ma bouche. »** Un graphe ffmpeg combiné perdait en silence 9 secondes d'échantillons audio (loudnorm sort du 192 kHz). Désormais, image et son sont rendus en passes séparées, chaque branche est rééchantillonnée à 48 kHz et le vérificateur décode le fichier final pour prouver le nombre d'échantillons.
- **« Les sous-titres arrivent en retard. »** Les timestamps Whisper calculés sur tout le fichier traînent. La transcription par segments pose les sous-titres pile sur les limites de la parole.
- **« Les effets me couvrent. »** Les effets baissent de −9 dB sous chaque réplique, les gros impacts passent dans un passe-bas s'ils touchent la voix, et le boom final tombe *après* votre dernier mot.
- **« L'image est floue. »** L'enregistreur intégré de Playwright fait du VP8 à faible débit. La skill utilise un screencast CDP depuis un Chrome fenêtré avec GPU activé.

La liste complète est dans [docs/lessons.md](docs/lessons.md).

## Prérequis

- macOS ou Linux, avec `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ et Python 3.10+.
- macOS : `brew install ffmpeg whisper-cpp node python`
- Environ 1 Go d'espace disque pour la boîte à outils (Chromium, modèle Whisper, venv), partagée entre projets.

## FAQ

<details>
<summary><strong>Quels agents peuvent l'utiliser ?</strong></summary>

Tout agent qui charge des skills `SKILL.md` et peut exécuter des commandes shell : Claude Code, Codex, Cursor, Gemini CLI et d'autres via `npx skills add`. Les scripts sont du Python, du Node et du ffmpeg tout simples, vous pouvez donc aussi lancer le [pipeline à la main](docs/pipeline.md).

</details>

<details>
<summary><strong>Je n'ai pas de script. Ça marche quand même ?</strong></summary>

Oui. Les sous-titres viennent directement de Whisper et votre agent les relit. Un script rend simplement le jargon et les noms de produit exacts, et permet de marquer l'emphase avec `**bold**`.

</details>

<details>
<summary><strong>Mon produit n'est pas une web app.</strong></summary>

Utilisez n'importe quelle source : enregistrements d'écran, captures de simulateur ou images. Déposez les images dans `shots/<name>/` avec un `stamps.json`, ou utilisez des plans `image`. Le modèle de captation web est une facilité, pas une obligation.

</details>

<details>
<summary><strong>Je peux utiliser ma propre musique ?</strong></summary>

Définissez `"music": "path/to/track.mp3"`. Elle est jouée en boucle, normalisée à bas volume et atténuée en side-chain sous votre voix. Utilisez `"none"` pour le silence.

</details>

<details>
<summary><strong>De la vidéo verticale pour TikTok, Reels ou Shorts ?</strong></summary>

Pas encore : la sortie est en 1920×1080. Le 9:16 est en tête de la [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Est-ce que quelque chose est uploadé ?</strong></summary>

Non. Transcription, rendu et analyse tournent tous sur votre machine. Votre agent voit la transcription et la timeline, et son fournisseur de modèle a sa propre politique de données.

</details>

## Documentation

- [Tour du pipeline](docs/pipeline.md) : chaque étape, ses entrées et sorties, et comment en relancer une.
- [Référence de project.json](docs/project-json.md) : scènes, plans, cartons, animations, effets sonores, thème et musique.
- [Leçons](docs/lessons.md) : les défaillances que cette skill évite, et pourquoi.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md) : les instructions que suit votre agent.

## Contribuer

Les issues et les PR sont les bienvenues, en particulier de nouveaux SFX, thèmes de sous-titres, la sortie verticale et des vidéos pour la vitrine. Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

[MIT](LICENSE). Les modèles Whisper et MediaPipe sont téléchargés depuis leurs sources d'origine et conservent leurs propres licences.
