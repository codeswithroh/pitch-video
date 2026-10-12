<div align="center">

[English](README.md) · **简体中文** · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

# Pitch Video

### 对着镜头念一遍你的 pitch，agent 帮你剪成可直接发布的演示视频。

**输入口播素材 → 输出剪辑、字幕、配乐、口型同步全部到位的产品演示。一次成功。**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#快速开始)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#常见问题)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#环境要求)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[快速开始](#快速开始) · [你会得到什么](#你会得到什么) · [工作原理](#工作原理) · [作品展示](#作品展示) · [为什么一次就成](#为什么一次就成) · [常见问题](#常见问题) · [文档](#文档)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="左边是一段原始口播录像，右边是成片的产品演示：游戏画面、人脸气泡、烧录字幕" width="1100" />

</div>

---

黑客松提交、产品发布视频、投资人 demo，要的都是同一样东西：**你在讲，产品在演。** 手工做这种视频意味着在剪辑软件里耗上几个小时：剪掉"嗯""啊"，把画面对齐到每一句话，加字幕，找音效，最后才发现口型差了 300 毫秒。

**Pitch Video 是一个能包办整个剪辑的 agent skill。** 把录像（有脚本和应用的话也一起）交给你的 agent。它会转写你的语音、剪掉空白、在不变成"花栗鼠音"的前提下加速 1.1 倍、用脚本驱动的浏览器录制你的产品、把每个镜头精确卡在你说出的那个词上，再加上字幕、人脸气泡、动画讲解、电影感音效和自动闪避的背景音乐。然后它会**测量自己的输出**（口型同步、音频漂移、响度、人声清晰度），绝不把有问题的文件交给你。

一切都通过 ffmpeg、whisper.cpp 和 Playwright 在本地运行。不上传、不订阅、不用时间线编辑器。

## 快速开始

### 1. 安装 skill

```bash
npx skills add codeswithroh/pitch-video
```

或者直接为 Claude Code 安装：

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

安装脚本会把 skill 复制到 `~/.claude/skills/pitch-video`（以及供其他 agent 使用的 `~/.agents/skills/pitch-video`），并搭建共享工具箱：Python venv、Playwright Chromium、Whisper `small.en` 模型和一个人脸关键点模型。装完后重启你的 agent。

### 2. 录制自己

对着镜头念你的脚本。横屏，拍到脸和肩膀，找个安静的房间。段落之间停下来喘口气。念错了没关系，重读那一句就行。

> 还没有脚本？问你的 agent：*"按照 pitch-video 的故事结构，帮我为这个仓库写一份 2 分钟的 pitch 视频脚本。"*

### 3. 交给你的 agent

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

你的 agent 会根据你说的内容规划场景、录制你的应用、渲染、验证，然后交给你 `out/demo.mp4`，外加一个用于上传的更小的 `demo_small.mp4`。

## 你会得到什么

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="带人脸气泡和字幕的游戏画面" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="带字幕的放大证明镜头" /></td>
</tr>
</table>

| 功能 | 作用 |
| --- | --- |
| **停顿裁剪** | 剪掉空白，保留自然的换气；场景切换和你指定的停顿处会留更长的节拍（"Until now." … *停顿*）。 |
| **1.1× 节奏** | 表达更紧凑，音调不变。画面和人声一起加速，同步始终精确。 |
| **卡词剪辑** | 每个场景和镜头都锚定在*你说的某个短语*上，画面恰好在引出它的那句话出现时切换。 |
| **脚本化产品录屏** | 为你的应用生成 Playwright 录制脚本：有头 Chrome、30 fps CDP 截屏流，以及一份可供剪辑对齐的带时间戳事件日志。 |
| **人脸气泡** | 根据人脸关键点自动取景，圆角、带强调色描边。全屏镜头和片尾卡片上自动隐藏。 |
| **准确的字幕** | 分块 Whisper 计时，再逐词对齐到你的脚本，于是 "Virev" 会变成 **VRF**，脚本里的 `**bold**` 会变成高亮词。 |
| **讲解动画** | HTML 图示，每个节拍都与你的旁白对应（`CUES.find(c => /sealed/.test(c.text))`）。 |
| **电影感音效** | 23 种合成音效（上升音、轰鸣、呼啸、锁定、铃声、故障音……），自动放在切点和卡片上，并在每个字底下自动压低。可选背景音乐。 |
| **验证关卡** | 口型同步测量、音画漂移检查、解码采样审计、逐句人声与背景的 dB 差、EBU R128 响度和缩略图总览。只有 `PASS` 才交付。 |

## 工作原理

<img src="docs/assets/pipeline.svg" alt="流水线：输入你的视频、脚本和产品；skill 依次对齐、转写、裁剪、录制、剪辑、叠加、配乐并验证；输出 demo.mp4" width="100%" />

整个剪辑都在一个易读的文件 `project.json` 里。场景从某个短语开始，镜头在某个短语处切换，音效在短语或录制到的应用事件上触发：

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

完整说明见 [project.json 参考](docs/project-json.md) 和 [流水线详解](docs/pipeline.md)。

## 作品展示

### Nightfall：一个链上大逃杀游戏的黑客松 pitch

[![Nightfall 演示视频的缩略图总览](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

一段 2:25 的口播素材，变成了 1:53 的演示：10 个场景、18 个镜头、一段实机游戏证明、一张动画架构图和 40 多个音效。验证结果：所有窗口人声漂移 **0 ms**，口型同步偏差 **0 ms**，每一句人声高出背景 ≥14.6 dB。

**[在 YouTube 上观看](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [脚本](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Nightfall 演示的五秒片段：昏暗的竞技场、火把光、字幕、人脸气泡" width="720" />

用 Pitch Video 做了作品？[开个 issue](https://github.com/codeswithroh/pitch-video/issues) 附上链接，我们会把它加到这里。

## 为什么一次就成

这个 skill 提炼自一次真实的剪辑，那次剪辑经历了无数痛苦的返工。每一次失败都变成了 skill 现在强制执行的一条规则：

- **"口型对不上。"** QuickTime 和手机录的文件，音频常常比视频晚约 150 ms 开始。skill 会在一切开始之前先显式对齐。
- **"越往后越不同步。"** 剪辑点都落在 30 fps 的帧网格上，按帧号*和*对应的音频采样号同时对齐。误差不会累积。
- **"嘴还在动，声音没了。"** 一个合并的 ffmpeg 滤镜图曾悄无声息地丢掉了 9 秒的音频采样（loudnorm 输出 192 kHz）。现在画面和声音分两遍渲染，每条分支都重采样到 48 kHz，验证器会解码最终文件来证明采样数正确。
- **"字幕慢半拍。"** 整文件的 Whisper 时间戳会滞后。分块转写让字幕精确落在说话的边界上。
- **"音效盖过了人声。"** 音效在每句话下都会压低 −9 dB，重击音如果碰到人声会做低通处理，最后那声轰鸣会落在你说完最后一个词*之后*。
- **"画面糊。"** Playwright 自带的录屏是低码率 VP8。skill 改用开启 GPU 的有头 Chrome 的 CDP 截屏流。

完整列表见 [docs/lessons.md](docs/lessons.md)。

## 环境要求

- macOS 或 Linux，需要 `ffmpeg`、`whisper-cli`（whisper.cpp）、Node.js 18+ 和 Python 3.10+。
- macOS：`brew install ffmpeg whisper-cpp node python`
- 工具箱（Chromium、Whisper 模型、venv）约占 1 GB 磁盘，多个项目共享。

## 常见问题

<details>
<summary><strong>哪些 agent 能用？</strong></summary>

任何能加载 `SKILL.md` skill 并能执行 shell 命令的 agent：Claude Code、Codex、Cursor、Gemini CLI，以及其他通过 `npx skills add` 安装的 agent。脚本都是普通的 Python、Node 和 ffmpeg，所以你也可以[手动跑流水线](docs/pipeline.md)。

</details>

<details>
<summary><strong>我没有脚本，还能用吗？</strong></summary>

能。字幕直接来自 Whisper，由你的 agent 校对。脚本只是让术语和产品名更准确，并且能用 `**bold**` 标记重点。

</details>

<details>
<summary><strong>我的产品不是 Web 应用。</strong></summary>

任何素材都可以：录屏、模拟器录像或图片。把帧放进 `shots/<name>/` 并附上 `stamps.json`，或者使用 `image` 镜头。网页录制模板只是图个方便，不是必需的。

</details>

<details>
<summary><strong>能用我自己的音乐吗？</strong></summary>

设置 `"music": "path/to/track.mp3"`。它会循环播放、以较低音量标准化，并在你说话时侧链压低。用 `"none"` 表示无音乐。

</details>

<details>
<summary><strong>支持 TikTok、Reels 或 Shorts 的竖屏视频吗？</strong></summary>

暂时不支持：输出为 1920×1080。9:16 是[路线图](CHANGELOG.md#roadmap)上的头号事项。

</details>

<details>
<summary><strong>会上传任何东西吗？</strong></summary>

不会。转写、渲染和分析全部在你的机器上运行。你的 agent 能看到转写文本和时间线，而它背后的模型提供商有自己的数据政策。

</details>

## 文档

- [流水线详解](docs/pipeline.md)：每一步的输入输出，以及如何单独重跑某一步。
- [project.json 参考](docs/project-json.md)：场景、镜头、卡片、动画、音效、主题和音乐。
- [经验教训](docs/lessons.md)：这个 skill 帮你避开的各种失败模式，以及原因。
- [SKILL.md](.agents/skills/pitch-video/SKILL.md)：你的 agent 遵循的指令。

## 参与贡献

欢迎提 issue 和 PR，尤其是新音效、字幕主题、竖屏输出和展示视频。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)。Whisper 和 MediaPipe 模型从各自的上游下载，遵循其各自的许可证。
