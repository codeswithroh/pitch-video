<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · **Bahasa Indonesia** · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Rekam dirimu membacakan pitch. Agent-mu mengubahnya jadi video demo yang siap rilis.

**Masuk video talking head → keluar demo produk yang sudah dipotong, diberi teks, diberi musik, dan lip-sync. Langsung jadi.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#mulai-cepat)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#persyaratan)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Mulai cepat](#mulai-cepat) · [Yang kamu dapatkan](#yang-kamu-dapatkan) · [Cara kerjanya](#cara-kerjanya) · [Showcase](#showcase) · [Kenapa langsung berhasil](#kenapa-langsung-berhasil) · [FAQ](#faq) · [Dokumentasi](#dokumentasi)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Rekaman talking head mentah di kiri berubah menjadi demo produk jadi di kanan: cuplikan gameplay, gelembung wajah, teks yang tertanam" width="1100" />

</div>

---

Submisi hackathon, video peluncuran, dan demo untuk investor semuanya butuh hal yang sama: **kamu menjelaskan, sementara produknya yang berbicara.** Membuatnya secara manual berarti berjam-jam di editor: memotong "eee", menyelaraskan cuplikan dengan tiap kalimat, membuat teks, mencari efek suara, lalu baru sadar bibirmu meleset 300 ms.

**Pitch Video adalah skill agent yang mengerjakan seluruh proses edit.** Serahkan rekamannya ke agent-mu (beserta naskah dan aplikasimu, kalau ada). Ia mentranskripsi suaramu, memangkas jeda kosong, mempercepatmu 1.1× tanpa suara cempreng, merekam produkmu dengan browser yang di-script, memotong setiap shot tepat di kata yang kamu ucapkan, lalu menambahkan teks, gelembung wajah, animasi penjelasan, efek suara sinematik, dan musik latar yang otomatis mengecil. Setelah itu ia **mengukur hasilnya sendiri** (lip sync, drift audio, loudness, kejernihan suara) dan menolak menyerahkan file yang rusak.

Semuanya berjalan lokal dengan ffmpeg, whisper.cpp, dan Playwright. Tanpa unggahan, tanpa langganan, tanpa editor timeline.

## Mulai cepat

### 1. Pasang skill-nya

```bash
npx skills add codeswithroh/pitch-video
```

atau langsung untuk Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

Installer menyalin skill ke `~/.claude/skills/pitch-video` (dan `~/.agents/skills/pitch-video` untuk agent lain) lalu menyiapkan toolbox bersama: venv Python, Playwright Chromium, model Whisper `small.en`, dan model titik wajah. Setelah itu, restart agent-mu.

### 2. Rekam dirimu

Bacakan naskahmu ke kamera. Posisi landscape, wajah dan bahu terlihat, di ruangan yang tenang. Ambil napas sejenak di antara bagian. Salah ucap tidak masalah, cukup ulangi kalimatnya.

> Belum punya naskah? Minta ke agent-mu: *"Tuliskan naskah pitch video 2 menit untuk repo ini dengan struktur cerita pitch-video."*

### 3. Minta ke agent-mu

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Agent-mu merencanakan adegan dari apa yang kamu ucapkan, merekam aplikasimu, me-render, memverifikasi, lalu menyerahkan `out/demo.mp4` plus `demo_small.mp4` yang lebih kecil untuk diunggah.

## Yang kamu dapatkan

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay dengan gelembung wajah dan teks" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Shot bukti yang di-zoom dengan teks" /></td>
</tr>
</table>

| Fitur | Fungsinya |
| --- | --- |
| **Pemangkasan jeda** | Memotong jeda kosong sambil mempertahankan tarikan napas alami, dengan ketukan lebih panjang di pergantian adegan dan jeda yang kamu pilih ("Until now." … *jeda*). |
| **Tempo 1.1×** | Penyampaian lebih padat tanpa mengubah nada. Gambar dan suara dipercepat bersamaan, jadi sinkronisasinya tetap presisi. |
| **Visual yang dipotong per kata** | Setiap adegan dan shot ditambatkan ke *frasa yang kamu ucapkan*, jadi cuplikannya berganti tepat di kalimat yang memperkenalkannya. |
| **Rekaman produk ber-script** | Membuat script rekaman Playwright untuk aplikasimu: Chrome headed, screencast CDP 30 fps, dan log event bertimestamp untuk acuan potongan. |
| **Gelembung wajah** | Dibingkai otomatis dari titik wajah, sudut membulat, bingkai warna aksen. Disembunyikan di shot layar penuh dan kartu penutup. |
| **Teks yang akurat** | Timing Whisper per potongan, lalu diselaraskan kata demi kata dengan naskahmu, jadi "Virev" menjadi **VRF** dan `**bold**` di naskah menjadi kata yang disorot. |
| **Animasi penjelasan** | Diagram HTML yang tiap langkahnya mengikuti narasimu (`CUES.find(c => /sealed/.test(c.text))`). |
| **Suara sinematik** | 23 SFX hasil sintesis (riser, boom, whoosh, lock, chime, glitch…), otomatis ditempatkan di potongan dan kartu, dan dikecilkan di bawah setiap kata yang diucapkan. Musik latar opsional. |
| **Gerbang verifikasi** | Pengukuran lip-sync, cek drift A/V, audit sampel yang di-decode, dB suara terhadap latar per kalimat, loudness EBU R128, dan contact sheet. Hanya dikirim jika `PASS`. |

## Cara kerjanya

<img src="docs/assets/pipeline.svg" alt="Pipeline: video, naskah, dan produkmu masuk; skill menyelaraskan, mentranskripsi, memangkas, merekam, memotong, menimpa, memberi suara, dan memverifikasi; keluar demo.mp4" width="100%" />

Seluruh proses edit ada di satu file yang mudah dibaca, `project.json`. Adegan dimulai pada frasa, shot berganti pada frasa, dan efek suara terpicu pada frasa atau event aplikasi yang terekam:

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

Lihat [referensi lengkap project.json](docs/project-json.md) dan [panduan pipeline](docs/pipeline.md).

## Showcase

### Nightfall: pitch hackathon untuk game battle royale onchain

[![Contact sheet video demo Nightfall](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Satu take talking head berdurasi 2:25 berubah menjadi demo 1:53 dengan 10 adegan, 18 shot, urutan bukti gameplay langsung, diagram arsitektur animasi, dan lebih dari 40 efek suara. Verifikasi mengukur drift suara **0 ms** di semua jendela, offset lip-sync **0 ms**, dan suara ≥14.6 dB di atas latar pada setiap kalimat.

**[Tonton di YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [naskah](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Lima detik demo Nightfall: arena gelap, cahaya obor, teks, gelembung wajah" width="720" />

Sudah membuat sesuatu dengan Pitch Video? [Buka issue](https://github.com/codeswithroh/pitch-video/issues) dengan tautannya dan kami akan menambahkannya di sini.

## Kenapa langsung berhasil

Skill ini diekstrak dari proses edit sungguhan yang butuh banyak iterasi menyakitkan. Setiap kegagalan menjadi aturan yang kini ditegakkan skill ini:

- **"Bibirku tidak pas."** File QuickTime dan ponsel sering memulai audio sekitar 150 ms setelah video. Skill ini menyelaraskan ulang secara eksplisit sebelum melakukan apa pun.
- **"Sinkronnya bergeser di bagian akhir."** Potongan jatuh di grid frame 30 fps, berdasarkan nomor frame *dan* nomor sampel audio yang sesuai. Tidak ada yang menumpuk.
- **"Suaraku berhenti sebelum mulutku."** Satu graph ffmpeg gabungan diam-diam membuang 9 detik sampel audio (loudnorm mengeluarkan 192 kHz). Sekarang gambar dan suara di-render di pass terpisah, setiap cabang di-resample ke 48 kHz, dan verifier men-decode file akhir untuk membuktikan jumlah sampelnya.
- **"Teksnya terasa telat."** Timestamp Whisper untuk seluruh file cenderung tertinggal. Transkripsi per potongan menaruh teks tepat di batas ucapan.
- **"Efeknya menenggelamkan suaraku."** Efek suara turun −9 dB di bawah setiap kalimat yang diucapkan, hentakan berat diberi low-pass jika menyentuh ucapan, dan boom terakhir muncul *setelah* kata terakhirmu.
- **"Rekamannya buram."** Perekam bawaan Playwright adalah VP8 dengan bitrate rendah. Skill ini memakai screencast CDP dari Chrome headed dengan GPU aktif.

Daftar lengkapnya ada di [docs/lessons.md](docs/lessons.md).

## Persyaratan

- macOS atau Linux, dengan `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+, dan Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Sekitar 1 GB ruang disk untuk toolbox (Chromium, model Whisper, venv), dipakai bersama antarproyek.

## FAQ

<details>
<summary><strong>Agent apa saja yang bisa memakainya?</strong></summary>

Agent apa pun yang bisa memuat skill `SKILL.md` dan menjalankan perintah shell: Claude Code, Codex, Cursor, Gemini CLI, dan lainnya lewat `npx skills add`. Script-nya cuma Python, Node, dan ffmpeg biasa, jadi kamu juga bisa menjalankan [pipeline-nya secara manual](docs/pipeline.md).

</details>

<details>
<summary><strong>Aku tidak punya naskah. Masih bisa?</strong></summary>

Bisa. Teks langsung diambil dari Whisper dan agent-mu memeriksanya. Naskah hanya membuat istilah teknis dan nama produk jadi tepat, serta memungkinkanmu menandai penekanan dengan `**bold**`.

</details>

<details>
<summary><strong>Produkku bukan web app.</strong></summary>

Pakai cuplikan apa saja: rekaman layar, tangkapan simulator, atau gambar. Taruh frame-nya di `shots/<name>/` dengan `stamps.json`, atau gunakan shot `image`. Template rekaman web hanya untuk kemudahan, bukan keharusan.

</details>

<details>
<summary><strong>Bisa pakai musikku sendiri?</strong></summary>

Atur `"music": "path/to/track.mp3"`. Musiknya diputar berulang, dinormalisasi dengan volume rendah, dan dikecilkan lewat side-chain di bawah suaramu. Gunakan `"none"` untuk hening.

</details>

<details>
<summary><strong>Video vertikal untuk TikTok, Reels, atau Shorts?</strong></summary>

Belum: output-nya 1920×1080. 9:16 adalah prioritas utama di [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Apakah ada yang diunggah?</strong></summary>

Tidak. Transkripsi, rendering, dan analisis semuanya berjalan di mesinmu. Agent-mu melihat transkrip dan timeline, dan penyedia modelnya punya kebijakan data sendiri.

</details>

## Dokumentasi

- [Panduan pipeline](docs/pipeline.md): setiap langkah, input dan output-nya, serta cara menjalankan ulang satu langkah.
- [Referensi project.json](docs/project-json.md): adegan, shot, kartu, animasi, efek suara, tema, dan musik.
- [Pelajaran](docs/lessons.md): mode kegagalan yang dicegah skill ini, dan alasannya.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): instruksi yang diikuti agent-mu.

## Berkontribusi

Issue dan PR sangat diterima, terutama SFX baru, tema teks, output vertikal, dan video showcase. Lihat [CONTRIBUTING.md](CONTRIBUTING.md).

## Lisensi

[MIT](LICENSE). Model Whisper dan MediaPipe diunduh dari sumber aslinya dan tetap memakai lisensinya masing-masing.
