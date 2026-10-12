<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · **日本語** · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

# Pitch Video

### ピッチを読み上げて録画するだけ。あとはエージェントがローンチ用のデモ動画に仕上げます。

**トーキングヘッド動画を入れれば、カット・字幕・効果音・リップシンクまで済んだプロダクトデモが出てくる。しかも一発で。**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#クイックスタート)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#動作環境)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[クイックスタート](#クイックスタート) · [できること](#できること) · [仕組み](#仕組み) · [ショーケース](#ショーケース) · [一発でうまくいく理由](#一発でうまくいく理由) · [FAQ](#faq) · [ドキュメント](#ドキュメント)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="左側の素のトーキングヘッド録画が、右側の完成したプロダクトデモに変わる：ゲーム画面、顔のバブル、焼き込み字幕" width="1100" />

</div>

---

ハッカソンの提出動画、ローンチ動画、投資家向けデモ。どれも求めているものは同じです：**あなたが説明し、プロダクトが語る。** これを手作業で作ると、編集ソフトで何時間もかかります。「えー」「あの」をカットし、映像を一文ずつ合わせ、字幕を付け、効果音を探し、最後に口の動きが 300 ms ずれていることに気づく。

**Pitch Video は、編集をまるごと引き受けるエージェントスキルです。** 録画（あれば台本とアプリも）をエージェントに渡すだけ。音声を文字起こしし、無音部分を詰め、声が高くならないまま 1.1 倍速にし、スクリプト化したブラウザでプロダクトを撮影し、すべてのショットをあなたが話す言葉ぴったりにカット。さらに字幕、顔のバブル、アニメーション解説、シネマティックな効果音、ダッキングされた BGM を加えます。そして**自分の出力を測定し**（リップシンク、音声ドリフト、ラウドネス、声の明瞭さ）、壊れたファイルは絶対に渡しません。

すべて ffmpeg、whisper.cpp、Playwright でローカル実行。アップロードなし、サブスクなし、タイムライン編集なし。

## クイックスタート

### 1. スキルをインストール

```bash
npx skills add codeswithroh/pitch-video
```

Claude Code に直接入れる場合：

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

インストーラーはスキルを `~/.claude/skills/pitch-video`（他のエージェント向けには `~/.agents/skills/pitch-video`）にコピーし、共有ツールボックスを構築します：Python venv、Playwright Chromium、Whisper `small.en` モデル、顔ランドマークモデル。終わったらエージェントを再起動してください。

### 2. 自分を録画する

カメラに向かって台本を読みます。横向き、顔と肩が入る構図、静かな部屋で。セクションの間ではひと呼吸置きましょう。噛んでも大丈夫、その行を読み直せば OK です。

> 台本がない？エージェントに頼みましょう：*「pitch-video のストーリー構成で、このリポジトリ用の 2 分間のピッチ動画の台本を書いて」*

### 3. エージェントに頼む

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

エージェントが話した内容からシーンを組み立て、アプリを撮影し、レンダリングと検証を行い、`out/demo.mp4` とアップロード用の軽量版 `demo_small.mp4` を渡してくれます。

## できること

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="顔のバブルと字幕付きのゲーム画面" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="字幕付きのズームした証拠ショット" /></td>
</tr>
</table>

| 機能 | 内容 |
| --- | --- |
| **間のトリミング** | 無音を詰めつつ自然な息継ぎは残し、シーン転換や指定した「溜め」では長めの間を取ります（"Until now." … *間*）。 |
| **1.1× のテンポ** | ピッチを保ったまま引き締まった話し方に。映像と声を一緒に速めるので、同期は完璧なまま。 |
| **言葉ぴったりのカット** | すべてのシーンとショットが*あなたが話すフレーズ*に紐づき、それを紹介する一言のタイミングで映像が切り替わります。 |
| **スクリプト化したプロダクト撮影** | アプリ用の Playwright 撮影スクリプトを生成：ヘッドあり Chrome、30 fps の CDP スクリーンキャスト、カット合わせ用のタイムスタンプ付きイベントログ。 |
| **顔のバブル** | 顔ランドマークから自動でフレーミング、角丸でアクセントカラーの枠付き。全画面ショットやエンドカードでは非表示。 |
| **正確な字幕** | チャンクごとの Whisper タイミングを台本に単語単位で合わせるので、"Virev" は **VRF** に、台本の `**bold**` はハイライトされた単語になります。 |
| **解説アニメーション** | ナレーションに合わせてビートが進む HTML 図解（`CUES.find(c => /sealed/.test(c.text))`）。 |
| **シネマティックな効果音** | 合成した 23 種の SFX（ライザー、ブーム、ウーシュ、ロック、チャイム、グリッチ…）をカットやカードに自動配置し、話している間は必ずダッキング。BGM もオプションで。 |
| **検証ゲート** | リップシンク測定、A/V ドリフトチェック、デコード後のサンプル監査、行ごとの声と背景の dB 差、EBU R128 ラウドネス、コンタクトシート。`PASS` のときだけ出荷します。 |

## 仕組み

<img src="docs/assets/pipeline.svg" alt="パイプライン：動画・台本・プロダクトを入力し、スキルが整列、文字起こし、トリミング、撮影、カット、オーバーレイ、効果音付け、検証を行い、demo.mp4 を出力" width="100%" />

編集のすべては、読みやすい 1 つのファイル `project.json` にまとまっています。シーンはフレーズで始まり、ショットはフレーズで切り替わり、効果音はフレーズや記録されたアプリのイベントで鳴ります：

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

詳しくは [project.json リファレンス](docs/project-json.md) と [パイプライン解説](docs/pipeline.md) を参照してください。

## ショーケース

### Nightfall：オンチェーンのバトルロイヤルゲームのハッカソンピッチ

[![Nightfall デモ動画のコンタクトシート](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

2:25 のトーキングヘッド素材が、10 シーン・18 ショット、実際のゲームプレイによる証明シーケンス、アニメーションのアーキテクチャ図、40 以上の効果音を備えた 1:53 のデモになりました。検証結果は、全区間で声のドリフト **0 ms**、リップシンクのずれ **0 ms**、すべての行で声が背景を ≥14.6 dB 上回りました。

**[YouTube で観る](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [台本](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Nightfall デモの 5 秒間：暗いアリーナ、たいまつの光、字幕、顔のバブル" width="720" />

Pitch Video で何か作りましたか？リンクを添えて [issue を立てて](https://github.com/codeswithroh/pitch-video/issues) もらえれば、ここに追加します。

## 一発でうまくいく理由

このスキルは、何度も苦しい手直しを重ねた実際の編集から抽出されました。すべての失敗が、今スキルが強制するルールになっています：

- **「口の動きが合わない」** QuickTime やスマホのファイルは、音声が映像より約 150 ms 遅れて始まることがよくあります。スキルは何よりも先に明示的に揃えます。
- **「後半になるほど同期がずれる」** カットは 30 fps のフレームグリッド上に、フレーム番号*と*対応する音声サンプル番号の両方で置かれます。誤差は蓄積しません。
- **「口より先に声が止まる」** ひとつにまとめた ffmpeg グラフが、音声サンプルを 9 秒分こっそり落としていました（loudnorm は 192 kHz を出力する）。今は映像と音声を別パスでレンダリングし、すべての分岐を 48 kHz にリサンプリングし、検証ツールが最終ファイルをデコードしてサンプル数を証明します。
- **「字幕が遅れて見える」** ファイル全体での Whisper タイムスタンプは遅れがち。チャンクごとの文字起こしで、字幕が発話の境界ぴったりに乗ります。
- **「効果音に声がかき消される」** 効果音は話している行の下で必ず −9 dB ダッキング、重い打撃音は声にかぶるならローパス、最後のブームは最後の一言の*後に*鳴ります。
- **「映像がぼやける」** Playwright 標準のレコーダーは低ビットレートの VP8。スキルは GPU 有効・ヘッドありの Chrome から CDP スクリーンキャストを使います。

全リストは [docs/lessons.md](docs/lessons.md) にあります。

## 動作環境

- macOS または Linux。`ffmpeg`、`whisper-cli`（whisper.cpp）、Node.js 18+、Python 3.10+ が必要です。
- macOS：`brew install ffmpeg whisper-cpp node python`
- ツールボックス（Chromium、Whisper モデル、venv）に約 1 GB のディスクを使い、プロジェクト間で共有されます。

## FAQ

<details>
<summary><strong>どのエージェントで使えますか？</strong></summary>

`SKILL.md` スキルを読み込めてシェルコマンドを実行できるエージェントなら何でも：Claude Code、Codex、Cursor、Gemini CLI、そのほか `npx skills add` で入れられるもの。スクリプトは素の Python、Node、ffmpeg なので、[パイプラインを手動で](docs/pipeline.md)動かすこともできます。

</details>

<details>
<summary><strong>台本がなくても使えますか？</strong></summary>

使えます。字幕は Whisper からそのまま作られ、エージェントが校正します。台本があれば専門用語やプロダクト名が正確になり、`**bold**` で強調箇所を指定できます。

</details>

<details>
<summary><strong>プロダクトが Web アプリではありません。</strong></summary>

どんな素材でも OK：画面収録、シミュレーターのキャプチャ、画像。フレームを `stamps.json` と一緒に `shots/<name>/` に置くか、`image` ショットを使ってください。Web 撮影テンプレートはあくまで便利機能で、必須ではありません。

</details>

<details>
<summary><strong>自分の音楽を使えますか？</strong></summary>

`"music": "path/to/track.mp3"` を設定してください。ループ再生され、小さめの音量に正規化され、声の下でサイドチェインでダッキングされます。無音にするなら `"none"`。

</details>

<details>
<summary><strong>TikTok、Reels、Shorts 向けの縦型動画は？</strong></summary>

まだです：出力は 1920×1080。9:16 は[ロードマップ](CHANGELOG.md#roadmap)の最優先項目です。

</details>

<details>
<summary><strong>何かアップロードされますか？</strong></summary>

いいえ。文字起こし、レンダリング、分析はすべてあなたのマシン上で動きます。エージェントは文字起こしとタイムラインを見ますが、そのモデルプロバイダーには独自のデータポリシーがあります。

</details>

## ドキュメント

- [パイプライン解説](docs/pipeline.md)：各ステップの入出力と、個別に再実行する方法。
- [project.json リファレンス](docs/project-json.md)：シーン、ショット、カード、アニメーション、効果音、テーマ、音楽。
- [教訓](docs/lessons.md)：このスキルが防ぐ失敗パターンとその理由。
- [SKILL.md](.agents/skills/pitch-video/SKILL.md)：エージェントが従う指示書。

## コントリビュート

issue や PR は大歓迎です。特に新しい SFX、字幕テーマ、縦型出力、ショーケース動画を待っています。[CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

[MIT](LICENSE)。Whisper と MediaPipe のモデルはそれぞれのアップストリームからダウンロードされ、各自のライセンスに従います。
