// Step 5: render an HTML animation (explainer/diagram) to anims/<name>.mp4 at exactly the shot length.
// usage: node render_anim.mjs <name>      (reads anims/<name>.html; the shot is the plan entry with anim:<name>)
// The page must define window.seek(t) that draws the frame at t seconds (deterministic, no CSS transitions).
// Before load it receives window.CUES = [{t, end, text}] — the narration lines inside the shot, in shot-relative
// seconds — so beats can be keyed to words: e.g. const lock = CUES.find(c => /sealed/i.test(c.text)).t
import fs from "node:fs";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
const TB = process.env.PITCH_VIDEO_HOME || `${process.env.HOME}/.cache/pitch-video`;
const { chromium } = createRequire(`${TB}/package.json`)("playwright");
// Canvas: 1920x1080, or 1080x960 (the top half of a 9:16 frame) when project.json has "layout": "split".
const SPLIT = fs.existsSync("project.json") && JSON.parse(fs.readFileSync("project.json", "utf8")).layout === "split";
const CW = SPLIT ? 1080 : 1920, CH = SPLIT ? 960 : 1080;

const name = process.argv[2];
const t = JSON.parse(fs.readFileSync("timeline.json", "utf8"));
const shot = t.plan.find((x) => x.anim === name);
if (!shot) throw new Error(`no shot with anim: "${name}" in timeline.json`);
const dur = shot.end - shot.start;
const cues = t.caps
  .filter((c) => c.end > shot.start && c.start < shot.end)
  .map((c) => ({ t: +(c.start - shot.start).toFixed(3), end: +(c.end - shot.start).toFixed(3), text: c.html.replace(/<[^>]+>/g, "") }));

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: CW, height: CH } });
await p.addInitScript((c) => (window.CUES = c), cues);
await p.goto("file://" + process.cwd() + `/anims/${name}.html`);
await p.waitForTimeout(1200);
await p.evaluate(() => document.fonts.ready);
const ff = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", "30", "-i", "-",
  "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", `anims/${name}.mp4`], { stdio: ["pipe", "inherit", "inherit"] });
const N = Math.round(dur * 30);
for (let i = 0; i < N; i++) {
  await p.evaluate((x) => window.seek(x), i / 30);
  const png = await p.screenshot({ type: "png" });
  if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await b.close();
console.log(`anims/${name}.mp4  ${N} frames (${dur.toFixed(2)}s), cues:`, cues.map((c) => `${c.t}s ${c.text}`).join(" | "));
