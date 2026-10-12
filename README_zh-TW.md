<div align="center">

[English](README.md) · [简体中文](README_zh.md) · **繁體中文** · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

# Pitch Video

### 對著鏡頭念一遍你的 pitch，agent 幫你剪成可直接發布的展示影片。

**輸入口播素材 → 輸出剪輯、字幕、配樂、嘴型同步全部到位的產品展示。一次成功。**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#快速開始)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#常見問題)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#環境需求)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[快速開始](#快速開始) · [你會得到什麼](#你會得到什麼) · [運作原理](#運作原理) · [作品展示](#作品展示) · [為什麼一次就成](#為什麼一次就成) · [常見問題](#常見問題) · [文件](#文件)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="左邊是一段原始口播錄影，右邊是完成的產品展示：遊戲畫面、人臉泡泡、燒錄字幕" width="1100" />

</div>

---

黑客松提交、產品發表影片、投資人 demo，要的都是同一件事：**你在講，產品在演。** 手工做這種影片代表要在剪輯軟體裡耗上好幾個小時：剪掉「嗯」「呃」、把畫面對齊每一句話、上字幕、找音效，最後才發現嘴型差了 300 毫秒。

**Pitch Video 是一個能包辦整個剪輯的 agent skill。** 把錄影（有腳本和應用程式的話也一起）交給你的 agent。它會轉錄你的語音、剪掉空白、在不變成「花栗鼠聲」的前提下加速 1.1 倍、用腳本驅動的瀏覽器錄下你的產品、把每個鏡頭精準卡在你說出的那個詞上，再加上字幕、人臉泡泡、動畫解說、電影感音效和自動閃避的背景音樂。接著它會**量測自己的輸出**（嘴型同步、音訊漂移、響度、人聲清晰度），絕不把壞掉的檔案交給你。

一切都透過 ffmpeg、whisper.cpp 和 Playwright 在本機執行。不上傳、不訂閱、不用時間軸編輯器。

## 快速開始

### 1. 安裝 skill

```bash
npx skills add codeswithroh/pitch-video
```

或者直接為 Claude Code 安裝：

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

安裝程式會把 skill 複製到 `~/.claude/skills/pitch-video`（以及給其他 agent 用的 `~/.agents/skills/pitch-video`），並建立共用工具箱：Python venv、Playwright Chromium、Whisper `small.en` 模型和一個人臉特徵點模型。裝好後重新啟動你的 agent。

### 2. 錄下自己

對著鏡頭念你的腳本。橫向拍攝，拍到臉和肩膀，找個安靜的房間。段落之間停下來換口氣。念錯沒關係，重念那一句就好。

> 還沒有腳本？問你的 agent：*「依照 pitch-video 的故事結構，幫我替這個 repo 寫一份 2 分鐘的 pitch 影片腳本。」*

### 3. 交給你的 agent

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

你的 agent 會根據你說的內容規劃場景、錄製你的應用程式、算圖、驗證，然後交給你 `out/demo.mp4`，外加一個用來上傳的較小檔案 `demo_small.mp4`。

## 你會得到什麼

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="帶有人臉泡泡和字幕的遊戲畫面" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="帶有字幕的放大佐證鏡頭" /></td>
</tr>
</table>

| 功能 | 作用 |
| --- | --- |
| **停頓修剪** | 剪掉空白、保留自然換氣；場景切換和你指定的停頓處會留較長的節拍（"Until now." … *停頓*）。 |
| **1.1× 節奏** | 表達更緊湊，音調不變。畫面與人聲一起加速，同步始終精準。 |
| **卡詞剪輯** | 每個場景和鏡頭都錨定在*你說的某個片語*上，畫面恰好在引出它的那句話出現時切換。 |
| **腳本化產品錄影** | 為你的應用程式產生 Playwright 拍攝腳本：有頭 Chrome、30 fps CDP 螢幕串流，以及一份可供剪輯對齊的時間戳事件記錄。 |
| **人臉泡泡** | 依人臉特徵點自動取景，圓角、帶強調色外框。全畫面鏡頭與片尾卡上自動隱藏。 |
| **正確的字幕** | 分段 Whisper 計時，再逐字對齊到你的腳本，所以 "Virev" 會變成 **VRF**，腳本裡的 `**bold**` 會變成醒目標示的字。 |
| **解說動畫** | HTML 圖解，每個節拍都對應到你的旁白（`CUES.find(c => /sealed/.test(c.text))`）。 |
| **電影感音效** | 23 種合成音效（上升音、轟鳴、呼嘯、上鎖、鈴聲、故障音……），自動放在切點與卡片上，並在每句話底下自動壓低。可選背景音樂。 |
| **驗證關卡** | 嘴型同步量測、影音漂移檢查、解碼取樣稽核、逐句人聲對背景 dB 差、EBU R128 響度和縮圖總覽。只有 `PASS` 才交付。 |

## 運作原理

<img src="docs/assets/pipeline.svg" alt="流程：輸入你的影片、腳本和產品；skill 依序對齊、轉錄、修剪、拍攝、剪輯、疊加、配樂與驗證；輸出 demo.mp4" width="100%" />

整個剪輯都在一個好讀的檔案 `project.json` 裡。場景從某個片語開始，鏡頭在某個片語處切換，音效在片語或錄到的應用程式事件上觸發：

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

完整說明請見 [project.json 參考](docs/project-json.md) 和 [流程詳解](docs/pipeline.md)。

## 作品展示

### Nightfall：一款鏈上大逃殺遊戲的黑客松 pitch

[![Nightfall 展示影片的縮圖總覽](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

一段 2:25 的口播素材，變成 1:53 的展示影片：10 個場景、18 個鏡頭、一段實機遊戲佐證、一張動畫架構圖和 40 多個音效。驗證結果：所有區段人聲漂移 **0 ms**、嘴型同步偏差 **0 ms**，每一句人聲都高出背景 ≥14.6 dB。

**[在 YouTube 上觀看](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [腳本](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Nightfall 展示的五秒片段：昏暗的競技場、火炬光、字幕、人臉泡泡" width="720" />

用 Pitch Video 做了作品？[開個 issue](https://github.com/codeswithroh/pitch-video/issues) 附上連結，我們會把它加到這裡。

## 為什麼一次就成

這個 skill 萃取自一次真實的剪輯，那次經歷了無數痛苦的返工。每一次失敗都成了 skill 現在強制執行的規則：

- **「嘴型對不上。」** QuickTime 和手機錄的檔案，音訊常比影像晚約 150 ms 開始。skill 會在一切開始前先明確對齊。
- **「越後面越不同步。」** 剪輯點都落在 30 fps 的影格網格上，同時依影格編號*和*對應的音訊取樣編號對齊。誤差不會累積。
- **「嘴還在動，聲音卻沒了。」** 一個合併的 ffmpeg 濾鏡圖曾無聲無息地丟掉 9 秒的音訊取樣（loudnorm 輸出 192 kHz）。現在畫面和聲音分兩次算圖，每條分支都重新取樣到 48 kHz，驗證器會解碼最終檔案來證明取樣數正確。
- **「字幕慢半拍。」** 整檔 Whisper 時間戳會落後。分段轉錄讓字幕精準落在說話的邊界上。
- **「音效蓋過人聲。」** 音效在每句話底下都會壓低 −9 dB，重擊音若碰到人聲會做低通處理，最後那聲轟鳴會落在你說完最後一個字*之後*。
- **「畫面糊糊的。」** Playwright 內建的錄影是低位元率 VP8。skill 改用開啟 GPU 的有頭 Chrome 的 CDP 螢幕串流。

完整清單請見 [docs/lessons.md](docs/lessons.md)。

## 環境需求

- macOS 或 Linux，需要 `ffmpeg`、`whisper-cli`（whisper.cpp）、Node.js 18+ 和 Python 3.10+。
- macOS：`brew install ffmpeg whisper-cpp node python`
- 工具箱（Chromium、Whisper 模型、venv）約佔 1 GB 磁碟空間，各專案共用。

## 常見問題

<details>
<summary><strong>哪些 agent 能用？</strong></summary>

任何能載入 `SKILL.md` skill 並執行 shell 指令的 agent：Claude Code、Codex、Cursor、Gemini CLI，以及其他透過 `npx skills add` 安裝的 agent。腳本都是一般的 Python、Node 和 ffmpeg，所以你也可以[手動執行流程](docs/pipeline.md)。

</details>

<details>
<summary><strong>我沒有腳本，還能用嗎？</strong></summary>

可以。字幕直接來自 Whisper，由你的 agent 校對。腳本只是讓術語和產品名稱更精準，並能用 `**bold**` 標示重點。

</details>

<details>
<summary><strong>我的產品不是 Web 應用程式。</strong></summary>

任何素材都行：螢幕錄影、模擬器錄影或圖片。把影格放進 `shots/<name>/` 並附上 `stamps.json`，或使用 `image` 鏡頭。網頁拍攝範本只是為了方便，不是必要條件。

</details>

<details>
<summary><strong>可以用我自己的音樂嗎？</strong></summary>

設定 `"music": "path/to/track.mp3"`。它會循環播放、以較低音量正規化，並在你說話時以側鏈壓低。用 `"none"` 表示不要音樂。

</details>

<details>
<summary><strong>支援 TikTok、Reels 或 Shorts 的直式影片嗎？</strong></summary>

還沒有：輸出為 1920×1080。9:16 是[路線圖](CHANGELOG.md#roadmap)上的第一優先項目。

</details>

<details>
<summary><strong>會上傳任何東西嗎？</strong></summary>

不會。轉錄、算圖和分析全都在你的電腦上執行。你的 agent 看得到逐字稿和時間軸，而它背後的模型供應商有自己的資料政策。

</details>

## 文件

- [流程詳解](docs/pipeline.md)：每個步驟的輸入與輸出，以及如何單獨重跑某一步。
- [project.json 參考](docs/project-json.md)：場景、鏡頭、卡片、動畫、音效、主題和音樂。
- [經驗教訓](docs/lessons.md)：這個 skill 幫你避開的失敗模式，以及原因。
- [SKILL.md](.agents/skills/pitch-video/SKILL.md)：你的 agent 遵循的指示。

## 參與貢獻

歡迎提出 issue 和 PR，特別是新音效、字幕主題、直式輸出和展示影片。詳見 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 授權

[MIT](LICENSE)。Whisper 和 MediaPipe 模型從各自的上游下載，並保留各自的授權條款。
