<div align="center">

[English](README.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · **Tiếng Việt** · [Türkçe](README_tr.md)

# Pitch Video

### Quay lại cảnh bạn đọc bài pitch. Agent của bạn biến nó thành video demo sẵn sàng ra mắt.

**Đưa vào video nói trước camera → nhận về bản demo sản phẩm đã cắt ghép, có phụ đề, âm thanh và khớp khẩu hình. Ngay lần đầu.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#bắt-đầu-nhanh)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#yêu-cầu)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Bắt đầu nhanh](#bắt-đầu-nhanh) · [Bạn nhận được gì](#bạn-nhận-được-gì) · [Cách hoạt động](#cách-hoạt-động) · [Showcase](#showcase) · [Vì sao thành công ngay lần đầu](#vì-sao-thành-công-ngay-lần-đầu) · [FAQ](#faq) · [Tài liệu](#tài-liệu)

<code>npx skills add codeswithroh/pitch-video</code>

<br /><br />

<img src="docs/assets/hero.jpg" alt="Một đoạn quay thô nói trước camera bên trái trở thành bản demo sản phẩm hoàn chỉnh bên phải: cảnh gameplay, bong bóng khuôn mặt, phụ đề in cứng" width="1100" />

</div>

---

Bài nộp hackathon, video ra mắt và demo gọi vốn đều cần cùng một thứ: **bạn giải thích, còn sản phẩm tự nói lên tất cả.** Làm thủ công nghĩa là hàng giờ trong phần mềm dựng phim: cắt những tiếng "ừm", khớp cảnh quay với từng câu, làm phụ đề, tìm hiệu ứng âm thanh, rồi phát hiện môi bạn lệch 300 ms.

**Pitch Video là một agent skill lo trọn khâu dựng phim.** Đưa bản ghi hình cho agent của bạn (kèm kịch bản và ứng dụng nếu có). Nó chép lời bạn nói, cắt khoảng lặng, tăng tốc 1.1× mà không bị giọng sóc chuột, quay sản phẩm bằng trình duyệt chạy theo script, cắt mỗi cảnh đúng vào từ bạn nói, rồi thêm phụ đề, bong bóng khuôn mặt, hoạt ảnh giải thích, hiệu ứng âm thanh điện ảnh và nhạc nền tự hạ âm lượng. Sau đó nó **tự đo kết quả của chính mình** (khớp khẩu hình, độ trôi âm thanh, độ lớn, độ rõ giọng) và từ chối giao cho bạn một file hỏng.

Mọi thứ chạy cục bộ với ffmpeg, whisper.cpp và Playwright. Không tải lên, không thuê bao, không timeline.

## Bắt đầu nhanh

### 1. Cài skill

```bash
npx skills add codeswithroh/pitch-video
```

hoặc cài thẳng cho Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

Trình cài đặt sao chép skill vào `~/.claude/skills/pitch-video` (và `~/.agents/skills/pitch-video` cho các agent khác) rồi dựng bộ công cụ dùng chung: một Python venv, Playwright Chromium, mô hình Whisper `small.en` và một mô hình điểm mốc khuôn mặt. Khởi động lại agent sau khi cài.

### 2. Quay chính bạn

Đọc kịch bản trước camera. Quay ngang, thấy mặt và vai, phòng yên tĩnh. Ngừng lấy hơi giữa các phần. Vấp cũng không sao, cứ đọc lại câu đó.

> Cần kịch bản? Hỏi agent của bạn: *"Viết cho tôi kịch bản pitch video 2 phút cho repo này theo cấu trúc câu chuyện của pitch-video."*

### 3. Nhờ agent của bạn

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Agent lên kế hoạch các cảnh từ những gì bạn nói, quay ứng dụng, render, kiểm tra và giao cho bạn `out/demo.mp4` cùng bản `demo_small.mp4` nhẹ hơn để tải lên.

## Bạn nhận được gì

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay với bong bóng khuôn mặt và phụ đề" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Cảnh bằng chứng phóng to có phụ đề" /></td>
</tr>
</table>

| Tính năng | Tác dụng |
| --- | --- |
| **Cắt khoảng lặng** | Cắt khoảng trống nhưng giữ nhịp thở tự nhiên, với nhịp nghỉ dài hơn ở chỗ chuyển cảnh và những chỗ bạn chọn ("Until now." … *ngừng*). |
| **Nhịp 1.1×** | Nói gọn hơn mà vẫn giữ cao độ. Hình và tiếng được tăng tốc cùng nhau nên đồng bộ luôn chính xác. |
| **Cắt hình theo từng từ** | Mỗi cảnh và shot được neo vào *một cụm từ bạn nói*, nên hình ảnh đổi đúng ở câu giới thiệu nó. |
| **Quay sản phẩm theo script** | Tạo script quay Playwright cho ứng dụng của bạn: Chrome có giao diện, screencast CDP 30 fps và nhật ký sự kiện có dấu thời gian để căn cắt. |
| **Bong bóng khuôn mặt** | Tự đóng khung theo điểm mốc khuôn mặt, bo góc, viền màu nhấn. Ẩn ở các shot toàn màn hình và thẻ kết. |
| **Phụ đề chuẩn** | Thời gian Whisper theo từng đoạn, rồi căn theo từng từ với kịch bản, nên "Virev" thành **VRF** và `**bold**` trong kịch bản thành từ được tô sáng. |
| **Hoạt ảnh giải thích** | Sơ đồ HTML có từng nhịp gắn với lời dẫn của bạn (`CUES.find(c => /sealed/.test(c.text))`). |
| **Âm thanh điện ảnh** | 23 SFX tổng hợp (riser, boom, whoosh, lock, chime, glitch…), tự đặt ở các điểm cắt và thẻ, và hạ xuống dưới mọi lời nói. Nhạc nền tùy chọn. |
| **Cổng kiểm định** | Đo khớp khẩu hình, kiểm tra trôi A/V, kiểm toán mẫu đã giải mã, dB giọng so với nền cho từng câu, độ lớn EBU R128 và contact sheet. Chỉ xuất khi `PASS`. |

## Cách hoạt động

<img src="docs/assets/pipeline.svg" alt="Pipeline: video, kịch bản và sản phẩm của bạn đi vào; skill căn chỉnh, chép lời, cắt, quay, dựng, chồng lớp, phối âm và kiểm định; demo.mp4 đi ra" width="100%" />

Toàn bộ bản dựng nằm trong một file dễ đọc, `project.json`. Cảnh bắt đầu theo cụm từ, shot chuyển theo cụm từ, và hiệu ứng âm thanh kích hoạt theo cụm từ hoặc theo sự kiện ứng dụng đã ghi lại:

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

Xem [tài liệu tham khảo project.json](docs/project-json.md) đầy đủ và [hướng dẫn pipeline](docs/pipeline.md).

## Showcase

### Nightfall: bài pitch hackathon cho một game battle royale onchain

[![Contact sheet của video demo Nightfall](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

Một đoạn quay nói trước camera dài 2:25 trở thành bản demo 1:53 với 10 cảnh, 18 shot, một chuỗi bằng chứng gameplay trực tiếp, một sơ đồ kiến trúc động và hơn 40 hiệu ứng âm thanh. Kết quả kiểm định: trôi giọng **0 ms** ở mọi đoạn, lệch khẩu hình **0 ms** và giọng cao hơn nền ≥14.6 dB ở mọi câu.

**[Xem trên YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [kịch bản](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Năm giây của demo Nightfall: đấu trường tối, ánh đuốc, phụ đề, bong bóng khuôn mặt" width="720" />

Bạn đã làm gì đó với Pitch Video? [Mở một issue](https://github.com/codeswithroh/pitch-video/issues) kèm đường dẫn và chúng tôi sẽ thêm vào đây.

## Vì sao thành công ngay lần đầu

Skill này được đúc kết từ một lần dựng thật, trải qua rất nhiều vòng sửa đau đầu. Mỗi lỗi đã trở thành một quy tắc mà skill giờ bắt buộc tuân theo:

- **"Môi tôi không khớp."** File QuickTime và điện thoại thường bắt đầu âm thanh chậm hơn video khoảng 150 ms. Skill căn chỉnh lại một cách tường minh trước mọi bước khác.
- **"Càng về sau càng lệch tiếng."** Điểm cắt rơi đúng lưới khung hình 30 fps, theo số khung hình *và* số mẫu âm thanh tương ứng. Không có sai số nào cộng dồn.
- **"Giọng tôi tắt trước khi miệng ngừng."** Một graph ffmpeg gộp chung từng âm thầm làm rơi 9 giây mẫu âm thanh (loudnorm xuất ra 192 kHz). Giờ hình và tiếng được render ở các lượt riêng, mọi nhánh đều được resample về 48 kHz, và bộ kiểm định giải mã file cuối để chứng minh số mẫu.
- **"Phụ đề cảm giác bị trễ."** Dấu thời gian Whisper trên cả file thường chậm. Chép lời theo từng đoạn giúp phụ đề rơi đúng ranh giới lời nói.
- **"Hiệu ứng át mất giọng tôi."** Hiệu ứng âm thanh hạ −9 dB dưới mọi câu nói, các cú đánh nặng được lọc thông thấp nếu chạm vào lời nói, và tiếng boom cuối vang lên *sau* từ cuối cùng của bạn.
- **"Hình bị mờ."** Bộ ghi tích hợp của Playwright là VP8 bitrate thấp. Skill dùng screencast CDP từ Chrome có giao diện, bật GPU.

Danh sách đầy đủ ở [docs/lessons.md](docs/lessons.md).

## Yêu cầu

- macOS hoặc Linux, có `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ và Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- Khoảng 1 GB dung lượng đĩa cho bộ công cụ (Chromium, mô hình Whisper, venv), dùng chung giữa các dự án.

## FAQ

<details>
<summary><strong>Những agent nào dùng được?</strong></summary>

Bất kỳ agent nào tải được skill `SKILL.md` và chạy được lệnh shell: Claude Code, Codex, Cursor, Gemini CLI và các agent khác qua `npx skills add`. Các script chỉ là Python, Node và ffmpeg thông thường, nên bạn cũng có thể [chạy pipeline thủ công](docs/pipeline.md).

</details>

<details>
<summary><strong>Tôi không có kịch bản. Vẫn dùng được chứ?</strong></summary>

Được. Phụ đề lấy thẳng từ Whisper và agent của bạn sẽ soát lại. Kịch bản chỉ giúp thuật ngữ và tên sản phẩm chính xác, và cho phép đánh dấu nhấn mạnh bằng `**bold**`.

</details>

<details>
<summary><strong>Sản phẩm của tôi không phải web app.</strong></summary>

Dùng cảnh quay nào cũng được: quay màn hình, ghi từ trình giả lập hay hình ảnh. Đặt các khung hình vào `shots/<name>/` kèm `stamps.json`, hoặc dùng shot `image`. Mẫu quay web chỉ để tiện, không bắt buộc.

</details>

<details>
<summary><strong>Tôi dùng nhạc riêng được không?</strong></summary>

Đặt `"music": "path/to/track.mp3"`. Nhạc được lặp lại, chuẩn hóa ở mức nhỏ và hạ side-chain dưới giọng bạn. Dùng `"none"` để không có nhạc.

</details>

<details>
<summary><strong>Video dọc cho TikTok, Reels hay Shorts?</strong></summary>

Chưa có: đầu ra là 1920×1080. 9:16 là mục ưu tiên hàng đầu trong [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Có gì bị tải lên không?</strong></summary>

Không. Chép lời, render và phân tích đều chạy trên máy của bạn. Agent của bạn thấy bản chép lời và timeline, còn nhà cung cấp mô hình của nó có chính sách dữ liệu riêng.

</details>

## Tài liệu

- [Hướng dẫn pipeline](docs/pipeline.md): từng bước, đầu vào và đầu ra, và cách chạy lại một bước.
- [Tham khảo project.json](docs/project-json.md): cảnh, shot, thẻ, hoạt ảnh, hiệu ứng âm thanh, giao diện và nhạc.
- [Bài học](docs/lessons.md): những lỗi mà skill này ngăn chặn, và lý do.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): hướng dẫn mà agent của bạn tuân theo.

## Đóng góp

Rất hoan nghênh issue và PR, đặc biệt là SFX mới, chủ đề phụ đề, đầu ra dọc và video showcase. Xem [CONTRIBUTING.md](CONTRIBUTING.md).

## Giấy phép

[MIT](LICENSE). Các mô hình Whisper và MediaPipe được tải từ nguồn gốc của chúng và giữ giấy phép riêng.
