<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · **한국어** · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

# Pitch Video

### 피치를 읽는 모습만 녹화하세요. 에이전트가 출시용 데모 영상으로 만들어 줍니다.

**토킹헤드 영상을 넣으면 → 컷 편집, 자막, 효과음, 립싱크까지 끝난 제품 데모가 나옵니다. 한 번에.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#빠른-시작)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#요구-사항)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[빠른 시작](#빠른-시작) · [주요 기능](#주요-기능) · [작동 방식](#작동-방식) · [쇼케이스](#쇼케이스) · [한 번에 되는 이유](#한-번에-되는-이유) · [FAQ](#faq) · [문서](#문서)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="왼쪽의 날것 그대로인 토킹헤드 녹화가 오른쪽의 완성된 제품 데모로 바뀝니다: 게임 화면, 얼굴 버블, 번인 자막" width="1100" />

</div>

---

해커톤 제출물, 출시 영상, 투자자 데모가 원하는 건 모두 같습니다: **당신이 설명하고, 제품이 보여주는 것.** 이걸 직접 만들려면 편집기에서 몇 시간을 써야 합니다. "음…"을 잘라내고, 화면을 문장마다 맞추고, 자막을 달고, 효과음을 찾고, 그러다 입 모양이 300 ms 어긋난 걸 뒤늦게 발견하죠.

**Pitch Video는 편집 전체를 맡아 하는 에이전트 스킬입니다.** 녹화 파일(있다면 대본과 앱도)을 에이전트에게 건네세요. 음성을 받아 적고, 빈 구간을 잘라내고, 다람쥐 목소리 없이 1.1배 빠르게 만들고, 스크립트로 제어하는 브라우저로 제품을 촬영하고, 모든 샷을 당신이 말하는 바로 그 단어에 맞춰 자릅니다. 여기에 자막, 얼굴 버블, 애니메이션 설명, 시네마틱 효과음, 더킹된 배경 음악까지 더하죠. 그리고 **자기 결과물을 직접 측정합니다**(립싱크, 오디오 드리프트, 라우드니스, 목소리 명료도). 망가진 파일은 절대 넘기지 않습니다.

모든 작업은 ffmpeg, whisper.cpp, Playwright로 로컬에서 실행됩니다. 업로드도, 구독도, 타임라인 편집기도 없습니다.

## 빠른 시작

### 1. 스킬 설치

```bash
npx skills add codeswithroh/pitch-video
```

Claude Code에 바로 설치하려면:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

설치 프로그램은 스킬을 `~/.claude/skills/pitch-video`(다른 에이전트용으로는 `~/.agents/skills/pitch-video`)에 복사하고 공유 툴박스를 구성합니다: Python venv, Playwright Chromium, Whisper `small.en` 모델, 얼굴 랜드마크 모델. 설치 후 에이전트를 재시작하세요.

### 2. 직접 녹화하기

카메라를 보며 대본을 읽으세요. 가로 화면, 얼굴과 어깨가 나오게, 조용한 방에서. 섹션 사이에는 한 번 숨을 고르세요. 말이 꼬여도 괜찮습니다. 그 줄만 다시 읽으면 됩니다.

> 대본이 없나요? 에이전트에게 물어보세요: *"pitch-video 스토리 구조로 이 저장소에 맞는 2분짜리 피치 영상 대본을 써 줘."*

### 3. 에이전트에게 요청하기

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

에이전트가 당신이 말한 내용으로 장면을 구성하고, 앱을 촬영하고, 렌더링과 검증을 거쳐 `out/demo.mp4`와 업로드용 소용량 `demo_small.mp4`를 넘겨줍니다.

## 주요 기능

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="얼굴 버블과 자막이 있는 게임 화면" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="자막이 있는 확대된 증거 샷" /></td>
</tr>
</table>

| 기능 | 하는 일 |
| --- | --- |
| **공백 트리밍** | 빈 구간은 자르고 자연스러운 호흡은 남기며, 장면 전환과 당신이 지정한 멈춤에는 더 긴 여백을 둡니다("Until now." … *멈춤*). |
| **1.1× 속도** | 음높이는 그대로 두고 전달은 더 탄탄하게. 화면과 목소리를 함께 빠르게 하므로 싱크가 정확히 유지됩니다. |
| **단어 단위 컷** | 모든 장면과 샷이 *당신이 말하는 구절*에 고정되어, 그 화면을 소개하는 문장에서 정확히 바뀝니다. |
| **스크립트 기반 제품 촬영** | 앱용 Playwright 촬영 스크립트를 생성합니다: 헤드 모드 Chrome, 30 fps CDP 스크린캐스트, 컷 기준이 되는 타임스탬프 이벤트 로그. |
| **얼굴 버블** | 얼굴 랜드마크로 자동 프레이밍, 둥근 모서리에 포인트 컬러 테두리. 전체 화면 샷과 엔드 카드에서는 숨겨집니다. |
| **정확한 자막** | 청크별 Whisper 타이밍을 대본에 단어 단위로 맞춰서, "Virev"는 **VRF**가 되고 대본의 `**bold**`는 강조된 단어가 됩니다. |
| **설명 애니메이션** | 내레이션에 맞춰 단계가 진행되는 HTML 다이어그램(`CUES.find(c => /sealed/.test(c.text))`). |
| **시네마틱 사운드** | 합성한 23가지 SFX(라이저, 붐, 우시, 잠금, 차임, 글리치…)를 컷과 카드에 자동 배치하고, 말하는 모든 구간 아래로 더킹합니다. 배경 음악은 선택 사항. |
| **검증 게이트** | 립싱크 측정, A/V 드리프트 검사, 디코딩 샘플 감사, 줄별 목소리 대 배경 dB, EBU R128 라우드니스, 콘택트 시트. `PASS`일 때만 내보냅니다. |

## 작동 방식

<img src="docs/assets/pipeline.svg" alt="파이프라인: 영상, 대본, 제품이 들어가면 스킬이 정렬, 전사, 트리밍, 촬영, 컷, 오버레이, 사운드, 검증을 거쳐 demo.mp4를 내놓습니다" width="100%" />

편집 전체가 읽기 쉬운 파일 하나, `project.json`에 담깁니다. 장면은 구절에서 시작하고, 샷은 구절에서 바뀌며, 효과음은 구절이나 기록된 앱 이벤트에서 울립니다:

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

전체 [project.json 레퍼런스](docs/project-json.md)와 [파이프라인 안내](docs/pipeline.md)를 참고하세요.

## 쇼케이스

### Nightfall: 온체인 배틀로얄 게임의 해커톤 피치

[![Nightfall 데모 영상의 콘택트 시트](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

2분 25초짜리 토킹헤드 촬영본이 10개 장면, 18개 샷, 실제 게임플레이 증명 시퀀스, 애니메이션 아키텍처 다이어그램, 40개 이상의 효과음을 갖춘 1분 53초 데모가 되었습니다. 검증 결과 모든 구간에서 목소리 드리프트 **0 ms**, 립싱크 오차 **0 ms**, 모든 줄에서 목소리가 배경보다 ≥14.6 dB 컸습니다.

**[YouTube에서 보기](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [대본](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Nightfall 데모의 5초 장면: 어두운 아레나, 횃불, 자막, 얼굴 버블" width="720" />

Pitch Video로 뭔가 만드셨나요? 링크와 함께 [이슈를 열어 주시면](https://github.com/codeswithroh/pitch-video/issues) 여기에 추가하겠습니다.

## 한 번에 되는 이유

이 스킬은 수없이 고생하며 반복한 실제 편집에서 뽑아낸 것입니다. 모든 실패가 지금 스킬이 강제하는 규칙이 되었습니다:

- **"입 모양이 안 맞아요."** QuickTime과 휴대폰 파일은 오디오가 영상보다 약 150 ms 늦게 시작하는 경우가 많습니다. 스킬은 무엇보다 먼저 명시적으로 다시 맞춥니다.
- **"뒤로 갈수록 싱크가 밀려요."** 컷은 30 fps 프레임 격자 위에, 프레임 번호*와* 그에 맞는 오디오 샘플 번호 모두로 놓입니다. 오차가 쌓이지 않습니다.
- **"입보다 목소리가 먼저 끝나요."** 하나로 합친 ffmpeg 그래프가 오디오 샘플 9초 분량을 조용히 날려 버린 적이 있습니다(loudnorm은 192 kHz를 출력). 이제 영상과 소리는 따로 렌더링하고, 모든 분기를 48 kHz로 리샘플링하며, 검증기가 최종 파일을 디코딩해 샘플 수를 증명합니다.
- **"자막이 늦게 느껴져요."** 파일 전체 Whisper 타임스탬프는 뒤처집니다. 청크별 전사로 자막이 발화 경계에 정확히 떨어집니다.
- **"효과음에 목소리가 묻혀요."** 효과음은 말하는 모든 줄 아래로 −9 dB 더킹되고, 묵직한 타격음이 목소리에 닿으면 로우패스를 걸며, 마지막 붐은 마지막 단어 *다음에* 터집니다.
- **"화면이 흐릿해요."** Playwright 기본 레코더는 저비트레이트 VP8입니다. 스킬은 GPU를 켠 헤드 모드 Chrome의 CDP 스크린캐스트를 사용합니다.

전체 목록은 [docs/lessons.md](docs/lessons.md)에 있습니다.

## 요구 사항

- macOS 또는 Linux, 그리고 `ffmpeg`, `whisper-cli`(whisper.cpp), Node.js 18+, Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- 툴박스(Chromium, Whisper 모델, venv)에 약 1 GB의 디스크가 필요하며, 프로젝트끼리 공유합니다.

## FAQ

<details>
<summary><strong>어떤 에이전트에서 쓸 수 있나요?</strong></summary>

`SKILL.md` 스킬을 불러오고 셸 명령을 실행할 수 있는 에이전트라면 무엇이든: Claude Code, Codex, Cursor, Gemini CLI, 그리고 `npx skills add`로 설치하는 그 밖의 에이전트. 스크립트는 평범한 Python, Node, ffmpeg라서 [파이프라인을 직접](docs/pipeline.md) 돌릴 수도 있습니다.

</details>

<details>
<summary><strong>대본이 없어도 되나요?</strong></summary>

네. 자막은 Whisper에서 바로 만들어지고 에이전트가 교정합니다. 대본이 있으면 전문 용어와 제품 이름이 정확해지고, `**bold**`로 강조를 표시할 수 있습니다.

</details>

<details>
<summary><strong>제 제품은 웹 앱이 아니에요.</strong></summary>

어떤 영상이든 됩니다: 화면 녹화, 시뮬레이터 캡처, 이미지. 프레임을 `stamps.json`과 함께 `shots/<name>/`에 넣거나 `image` 샷을 쓰세요. 웹 촬영 템플릿은 편의 기능일 뿐 필수가 아닙니다.

</details>

<details>
<summary><strong>제 음악을 쓸 수 있나요?</strong></summary>

`"music": "path/to/track.mp3"`를 설정하세요. 반복 재생되고, 낮은 음량으로 정규화되며, 목소리 아래로 사이드체인 더킹됩니다. 무음으로 하려면 `"none"`을 쓰세요.

</details>

<details>
<summary><strong>TikTok, Reels, Shorts용 세로 영상은요?</strong></summary>

아직입니다: 출력은 1920×1080입니다. 9:16은 [로드맵](CHANGELOG.md#roadmap)의 최우선 항목입니다.

</details>

<details>
<summary><strong>업로드되는 게 있나요?</strong></summary>

없습니다. 전사, 렌더링, 분석 모두 당신의 컴퓨터에서 실행됩니다. 에이전트는 전사 내용과 타임라인을 보며, 그 모델 제공자에게는 자체 데이터 정책이 있습니다.

</details>

## 문서

- [파이프라인 안내](docs/pipeline.md): 각 단계의 입력과 출력, 그리고 단계별 재실행 방법.
- [project.json 레퍼런스](docs/project-json.md): 장면, 샷, 카드, 애니메이션, 효과음, 테마, 음악.
- [교훈](docs/lessons.md): 이 스킬이 막아 주는 실패 유형과 그 이유.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): 에이전트가 따르는 지침.

## 기여하기

이슈와 PR 환영합니다. 특히 새 SFX, 자막 테마, 세로 출력, 쇼케이스 영상을 기다립니다. [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

[MIT](LICENSE). Whisper와 MediaPipe 모델은 각각의 업스트림에서 내려받으며 각자의 라이선스를 따릅니다.
