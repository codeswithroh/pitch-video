// Films the product footage. Copy to <workdir>/film.mjs, then write one scripted, deterministic "shot" per
// thing the narration shows. Run:  node film.mjs            → shots/<name>/*.jpg + stamps.json, shots/events.json
//
// Why this way (learned the hard way):
//  - Playwright's recordVideo is low-bitrate VP8 — unusable at 1080p. A CDP screencast of JPEG frames with
//    per-frame timestamps is crisp and lets build_bg.py time-fit any slice of a recording to any shot length.
//  - Headed Chrome (headless:false) keeps the GPU on: WebGL/canvas apps render at full speed and quality.
//  - ev() logs the recording-clock time of every interesting moment (click, kill, modal opens). Shots in
//    project.json reference those times ("rec": "main", "t": 12.4, "to": 18.0) and SFX cues can too.
//  - Pre-seed localStorage (skip tutorials/cookie banners, fixed username), use test wallets/accounts you own,
//    and hide dev overlays. Film each beat 2-3x longer than the line it covers; the edit trims.
import fs from "node:fs";
import { createRequire } from "node:module";
const TB = process.env.PITCH_VIDEO_HOME || `${process.env.HOME}/.cache/pitch-video`;
const { chromium } = createRequire(`${TB}/package.json`)("playwright");

const URL = process.env.APP_URL || "http://localhost:5173/";
// Film at the canvas size: 1920x1080, or 1080x960 for "layout": "split" (sites render their tablet layout,
// which fills the top half without letterboxing).
const SPLIT = fs.existsSync("project.json") && JSON.parse(fs.readFileSync("project.json", "utf8")).layout === "split";
const VW = SPLIT ? 1080 : 1920, VH = SPLIT ? 960 : 1080;
const OUT = "shots";
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const T0 = Date.now();
const events = fs.existsSync(`${OUT}/events.json`) ? JSON.parse(fs.readFileSync(`${OUT}/events.json`, "utf8")) : [];
const ev = (shot, what, extra = {}) => {
  const e = { t: +((Date.now() - T0) / 1000).toFixed(3), shot, what, ...extra };
  events.push(e);
  console.log(e.t.toFixed(2), shot, what, JSON.stringify(extra));
  fs.writeFileSync(`${OUT}/events.json`, JSON.stringify(events, null, 1));
};

const browser = await chromium.launch({
  headless: false,
  args: [`--window-size=${VW},${VH + 100}`, "--force-device-scale-factor=1", "--autoplay-policy=no-user-gesture-required"],
});

/** Continuous screencast of `page` into shots/<name>/ (≈30 fps JPEG) with timestamps on the ev() clock. */
async function recorder(ctx, page, name) {
  const dir = `${OUT}/${name}`;
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const cdp = await ctx.newCDPSession(page);
  const stamps = [];
  let n = 0;
  cdp.on("Page.screencastFrame", async (f) => {
    const i = n++;
    fs.writeFile(`${dir}/${String(i).padStart(6, "0")}.jpg`, Buffer.from(f.data, "base64"), () => {});
    stamps.push([i, f.metadata.timestamp]);
    cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
  });
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 88, maxWidth: VW, maxHeight: VH, everyNthFrame: 2 });
  const startedAt = (Date.now() - T0) / 1000;
  ev(name, "rec-start");
  return {
    async stop() {
      await cdp.send("Page.stopScreencast").catch(() => {});
      await sleep(500);
      fs.writeFileSync(`${dir}/stamps.json`, JSON.stringify({ startedAt, stamps }));
      ev(name, "rec-stop", { frames: stamps.length });
    },
  };
}

async function newPage(seed = {}) {
  const ctx = await browser.newContext({ viewport: { width: VW, height: VH } });
  await ctx.addInitScript((s) => { for (const [k, v] of Object.entries(s)) localStorage.setItem(k, v); }, seed);
  const page = await ctx.newPage();
  page.on("pageerror", (e) => console.log("pageerror", e.message));
  return { ctx, page };
}

// ───────────────────────── shots: edit below ─────────────────────────
{
  const { ctx, page } = await newPage({ /* "app-onboarded": "1" */ });
  await page.goto(URL);
  await page.waitForLoadState("networkidle");
  const rec = await recorder(ctx, page, "main");
  await sleep(2500);
  ev("main", "landing");
  // await page.getByRole("button", { name: "Get started" }).click(); ev("main", "clicked get started");
  // await page.keyboard.press("KeyW"); ...
  await sleep(4000);
  await rec.stop();
  await ctx.close();
}

await browser.close();
