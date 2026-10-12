<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · **Türkçe**

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Pitch'ini okurken kendini kaydet. Agent'ın onu lansmana hazır bir demo videosuna dönüştürsün.

**Konuşan kafa videosu girer → kurgulanmış, altyazılı, sesli, dudak senkronlu ürün demosu çıkar. İlk denemede.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#hızlı-başlangıç)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#sss)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#gereksinimler)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Hızlı başlangıç](#hızlı-başlangıç) · [Neler elde edersin](#neler-elde-edersin) · [Nasıl çalışır](#nasıl-çalışır) · [Vitrin](#vitrin) · [Neden ilk denemede çalışır](#neden-ilk-denemede-çalışır) · [SSS](#sss) · [Dokümantasyon](#dokümantasyon)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Soldaki ham konuşan kafa kaydı sağda bitmiş bir ürün demosuna dönüşüyor: oyun görüntüleri, yüz balonu, gömülü altyazılar" width="1100" />

</div>

---

Hackathon başvuruları, lansman videoları ve yatırımcı demoları hep aynı şeyi ister: **sen anlatırken ürünün kendini göstermesi.** Bunu elle yapmak, bir editörde saatler demek: "ııı"ları kesmek, görüntüleri her cümleye denk getirmek, altyazı eklemek, ses efekti aramak ve sonunda dudaklarının 300 ms kaydığını fark etmek.

**Pitch Video, kurgunun tamamını üstlenen bir agent skill'idir.** Kaydı agent'ına ver (varsa senaryonu ve uygulamanı da). Seni metne döker, ölü boşlukları kırpar, sincap sesine çevirmeden 1.1× hızlandırır, ürününü script'li bir tarayıcıyla çeker, her çekimi tam söylediğin kelimede keser; ardından altyazı, yüz balonu, animasyonlu açıklama, sinematik ses efektleri ve otomatik kısılan bir fon müziği ekler. Sonra **kendi çıktısını ölçer** (dudak senkronu, ses kayması, ses yüksekliği, ses netliği) ve bozuk bir dosyayı sana vermeyi reddeder.

Her şey ffmpeg, whisper.cpp ve Playwright ile yerelde çalışır. Yükleme yok, abonelik yok, zaman çizelgesi editörü yok.

## Hızlı başlangıç

### 1. Skill'i kur

```bash
npx skills add codeswithroh/pitch-video
```

ya da doğrudan Claude Code için:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

Yükleyici skill'i `~/.claude/skills/pitch-video` dizinine (diğer agent'lar için de `~/.agents/skills/pitch-video` dizinine) kopyalar ve ortak araç kutusunu kurar: bir Python venv, Playwright Chromium, Whisper `small.en` modeli ve bir yüz işaret noktası modeli. Ardından agent'ını yeniden başlat.

### 2. Kendini kaydet

Senaryonu kameraya oku. Yatay, yüz ve omuzlar kadrajda, sessiz bir oda. Bölümler arasında bir nefes al. Takılırsan sorun değil, o satırı yeniden oku.

> Senaryo mu lazım? Agent'ına sor: *"pitch-video hikâye yapısını kullanarak bu repo için 2 dakikalık bir pitch video senaryosu yaz."*

### 3. Agent'ından iste

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Agent'ın söylediklerinden sahneleri planlar, uygulamanı çeker, render alır, doğrular ve sana `out/demo.mp4` ile birlikte yüklemeler için daha küçük bir `demo_small.mp4` teslim eder.

## Neler elde edersin

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Yüz balonu ve altyazılı oyun görüntüsü" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Altyazılı, yakınlaştırılmış kanıt çekimi" /></td>
</tr>
</table>

| Özellik | Ne yapar |
| --- | --- |
| **Duraklama kırpma** | Ölü boşlukları keser, doğal nefesleri korur; sahne geçişlerinde ve senin seçtiğin duraklarda daha uzun vuruşlar bırakır ("Until now." … *es*). |
| **1.1× tempo** | Ses tonu korunarak daha sıkı bir anlatım. Görüntü ve ses birlikte hızlandırılır, senkron tam olarak kalır. |
| **Kelimeye kesilen görseller** | Her sahne ve çekim *söylediğin bir ifadeye* bağlanır; görüntü tam da onu tanıtan cümlede değişir. |
| **Script'li ürün çekimi** | Uygulaman için bir Playwright çekim script'i üretir: pencereli Chrome, 30 fps CDP ekran yayını ve kesimlerin hizalanacağı zaman damgalı bir olay günlüğü. |
| **Yüz balonu** | Yüz işaret noktalarından otomatik kadrajlanır, köşeleri yuvarlak, vurgu renginde çerçeveli. Tam ekran çekimlerde ve kapanış kartında gizlenir. |
| **Doğru altyazılar** | Parça başına Whisper zamanlaması, ardından senaryona kelime kelime hizalama; böylece "Virev" **VRF** olur ve senaryodaki `**bold**` vurgulanmış kelimelere dönüşür. |
| **Açıklayıcı animasyonlar** | Adımları anlatımına bağlı HTML diyagramlar (`CUES.find(c => /sealed/.test(c.text))`). |
| **Sinematik ses** | 23 sentezlenmiş SFX (riser, boom, whoosh, lock, chime, glitch…); kesimlere ve kartlara otomatik yerleştirilir, söylenen her kelimenin altında kısılır. İsteğe bağlı fon müziği. |
| **Doğrulama kapısı** | Dudak senkronu ölçümü, A/V kayma kontrolü, çözülmüş örnek denetimi, satır başına ses/arka plan dB farkı, EBU R128 ses yüksekliği ve bir kontak sayfası. Yalnızca `PASS` olursa teslim edilir. |

## Nasıl çalışır

<img src="docs/assets/pipeline.svg" alt="İşlem hattı: videon, senaryon ve ürünün girer; skill hizalar, metne döker, kırpar, çeker, keser, bindirir, seslendirir ve doğrular; demo.mp4 çıkar" width="100%" />

Tüm kurgu tek ve okunaklı bir dosyada yaşar: `project.json`. Sahneler ifadelerle başlar, çekimler ifadelerle değişir ve ses efektleri ifadelerde ya da kaydedilmiş uygulama olaylarında tetiklenir:

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

Tam [project.json referansına](docs/project-json.md) ve [işlem hattı rehberine](docs/pipeline.md) göz at.

## Vitrin

### Nightfall: zincir üstü bir battle royale için hackathon pitch'i

[![Nightfall demo videosunun kontak sayfası](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

2:25'lik bir konuşan kafa çekimi; 10 sahne, 18 çekim, canlı oynanış kanıt sekansı, animasyonlu bir mimari diyagram ve 40'tan fazla ses efektiyle 1:53'lük bir demoya dönüştü. Doğrulama, tüm pencerelerde **0 ms** ses kayması, **0 ms** dudak senkronu sapması ve her satırda arka planın ≥14.6 dB üzerinde ses ölçtü.

**[YouTube'da izle](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [senaryo](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Nightfall demosundan beş saniye: karanlık arena, meşale ışığı, altyazı, yüz balonu" width="720" />

Pitch Video ile bir şey mi yaptın? Bağlantısıyla birlikte [bir issue aç](https://github.com/codeswithroh/pitch-video/issues), buraya ekleyelim.

## Neden ilk denemede çalışır

Bu skill, pek çok sancılı tekrardan geçen gerçek bir kurgudan çıkarıldı. Her başarısızlık, skill'in artık uyguladığı bir kurala dönüştü:

- **"Dudaklarım uymuyor."** QuickTime ve telefon dosyalarında ses çoğu zaman videodan yaklaşık 150 ms sonra başlar. Skill her şeyden önce bunu açıkça yeniden hizalar.
- **"Videonun ilerisinde senkron kayıyor."** Kesimler 30 fps kare ızgarasına, kare numarasına *ve* buna karşılık gelen ses örneği numarasına göre oturur. Hiçbir şey birikmez.
- **"Sesim ağzımdan önce kesiliyor."** Birleşik bir ffmpeg grafiği sessiz sedasız 9 saniyelik ses örneğini düşürüyordu (loudnorm 192 kHz çıktı verir). Artık görüntü ve ses ayrı geçişlerde render edilir, her dal 48 kHz'e yeniden örneklenir ve doğrulayıcı örnek sayısını kanıtlamak için son dosyayı çözer.
- **"Altyazılar geç kalıyor gibi."** Tüm dosya üzerindeki Whisper zaman damgaları geride kalır. Parça parça metne dökme, altyazıları konuşmanın tam sınırlarına oturtur.
- **"Efektler sesimi bastırıyor."** Ses efektleri her konuşulan satırın altında −9 dB kısılır, ağır vuruşlar konuşmaya değiyorsa alçak geçiren filtreden geçer ve son boom senin son kelimenden *sonra* gelir.
- **"Görüntü bulanık."** Playwright'ın yerleşik kaydedicisi düşük bit hızlı VP8'dir. Skill, GPU'su açık pencereli Chrome'dan CDP ekran yayını kullanır.

Tam liste [docs/lessons.md](docs/lessons.md) içinde.

## Gereksinimler

- macOS veya Linux; `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ ve Python 3.10+ ile.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Araç kutusu (Chromium, Whisper modeli, venv) için yaklaşık 1 GB disk; projeler arasında paylaşılır.

## SSS

<details>
<summary><strong>Hangi agent'lar kullanabilir?</strong></summary>

`SKILL.md` skill'lerini yükleyebilen ve kabuk komutu çalıştırabilen her agent: Claude Code, Codex, Cursor, Gemini CLI ve `npx skills add` üzerinden diğerleri. Script'ler düz Python, Node ve ffmpeg olduğundan [işlem hattını elle de](docs/pipeline.md) çalıştırabilirsin.

</details>

<details>
<summary><strong>Senaryom yok. Yine de çalışır mı?</strong></summary>

Evet. Altyazılar doğrudan Whisper'dan gelir ve agent'ın onları düzeltir. Senaryo yalnızca jargonun ve ürün adlarının doğru çıkmasını sağlar, `**bold**` ile vurgu işaretlemene de izin verir.

</details>

<details>
<summary><strong>Ürünüm bir web uygulaması değil.</strong></summary>

Herhangi bir görüntü kullan: ekran kayıtları, simülatör kayıtları ya da görseller. Kareleri bir `stamps.json` ile `shots/<name>/` içine koy ya da `image` çekimleri kullan. Web çekim şablonu bir kolaylıktır, zorunluluk değil.

</details>

<details>
<summary><strong>Kendi müziğimi kullanabilir miyim?</strong></summary>

`"music": "path/to/track.mp3"` ayarla. Döngüye alınır, düşük seviyede normalize edilir ve sesinin altında side-chain ile kısılır. Sessizlik için `"none"` kullan.

</details>

<details>
<summary><strong>TikTok, Reels veya Shorts için dikey video?</strong></summary>

Henüz değil: çıktı 1920×1080. 9:16, [yol haritasındaki](CHANGELOG.md#roadmap) ilk madde.

</details>

<details>
<summary><strong>Bir şey yükleniyor mu?</strong></summary>

Hayır. Metne dökme, render ve analiz tamamen senin makinende çalışır. Agent'ın transkripti ve zaman çizelgesini görür; onun model sağlayıcısının da kendi veri politikası vardır.

</details>

## Dokümantasyon

- [İşlem hattı rehberi](docs/pipeline.md): her adım, girdileri ve çıktıları, ve bir adımın nasıl yeniden çalıştırılacağı.
- [project.json referansı](docs/project-json.md): sahneler, çekimler, kartlar, animasyonlar, ses efektleri, tema ve müzik.
- [Dersler](docs/lessons.md): bu skill'in önlediği hata türleri ve nedenleri.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): agent'ının izlediği talimatlar.

## Katkıda bulunma

Issue ve PR'lara açığız; özellikle yeni SFX'ler, altyazı temaları, dikey çıktı ve vitrin videoları. Bkz. [CONTRIBUTING.md](CONTRIBUTING.md).

## Lisans

[MIT](LICENSE). Whisper ve MediaPipe modelleri kendi kaynaklarından indirilir ve kendi lisanslarını korur.
