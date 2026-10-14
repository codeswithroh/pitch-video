// Step 7: render every overlay as a transparent canvas-sized PNG into ov/ (1920x1080, or 1080x960 in split layout).
// Captions, scene chips, title statements, custom cards (cards/<name>.html), end card, PiP frame + mask.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const TB = process.env.PITCH_VIDEO_HOME || `${process.env.HOME}/.cache/pitch-video`;
const { chromium } = createRequire(`${TB}/package.json`)("playwright");
// Canvas: 1920x1080, or 1080x960 (the top half of a 9:16 frame) when project.json has "layout": "split".
const SPLIT = fs.existsSync("project.json") && JSON.parse(fs.readFileSync("project.json", "utf8")).layout === "split";
const CW = SPLIT ? 1080 : 1920, CH = SPLIT ? 960 : 1080;
const SKILL = path.dirname(path.dirname(new URL(import.meta.url).pathname));

const t = JSON.parse(fs.readFileSync("timeline.json", "utf8"));
const P = JSON.parse(fs.readFileSync("project.json", "utf8"));
const theme = { accent: "#ffe040", head: "Inter", body: "Inter", ...(P.theme || {}) };
const PIP = { size: 380, margin: 48 };
fs.rmSync("ov", { recursive: true, force: true });
fs.mkdirSync("ov");

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: CW, height: CH } });
await p.goto("file://" + path.join(SKILL, "templates/overlay.html"));
// Weight lists must exist for each family or Google returns 400; override with theme.google_fonts for unusual fonts.
const fams = theme.google_fonts || [...new Set([theme.head, theme.body])].map((f) => `family=${f.replace(/ /g, "+")}:wght@400;700`).join("&");
await p.evaluate(
  ([href, th, extra, split]) => {
    document.getElementById("fonts").href = `https://fonts.googleapis.com/css2?${href}&display=swap`;
    const r = document.documentElement.style;
    r.setProperty("--accent", th.accent);
    r.setProperty("--head", `"${th.head}"`);
    r.setProperty("--body", `"${th.body}"`);
    document.getElementById("extra").textContent = extra;
    if (split) document.documentElement.classList.add("split");
  },
  [fams, theme, fs.existsSync("cards/cards.css") ? fs.readFileSync("cards/cards.css", "utf8") : "", SPLIT],
);
await p.waitForTimeout(1500);
await p.evaluate(() => document.fonts.ready);
const shot = async (file, html) => {
  await p.evaluate((h) => window.render(h), html);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: `ov/${file}`, omitBackground: true });
};

// The face bubble is visible on every shot except full-frame speaker, end card, or pip:false.
const pipOn = (s) => t.plan.some((x) => s >= x.start - 0.05 && s < x.end && !(x.speaker || x.end_card || x.pip === false));
if (!SPLIT) for (const [i, c] of t.caps.entries()) await shot(`cap${String(i).padStart(3, "0")}.png`, `<div class="cap ${pipOn(c.start) ? "pip" : ""}">${c.html}</div>`);
for (const s of t.scenes) if (s.chip) await shot(`chip${s.n}.png`, `<div class="chip"><span class="n">${s.n}</span>${s.title}</div>`);
for (const [i, x] of t.plan.entries()) {
  if (x.title) await shot(`title${i}.png`, `<div class="big"><h1>${x.title}</h1>${x.subtitle ? `<p>${x.subtitle}</p>` : ""}</div>`);
  if (x.card) await shot(`card_${x.card}.png`, fs.readFileSync(`cards/${x.card}.html`, "utf8"));
}
const e = P.end || {};
await shot("end.png", `<div class="end"><h1>${e.title || P.title || ""}</h1>${e.tagline ? `<div class="tag">${e.tagline}</div>` : ""}
  <div class="links">${(e.links || []).map((l) => `<span>${l}</span>`).join("")}</div>${e.by ? `<div class="by">${e.by}</div>` : ""}
  ${P.credit === false ? "" : `<div class="credit">Edited by an agent · github.com/codeswithroh/pitch-video</div>`}</div>`);
const px = CW - PIP.margin - PIP.size, py = CH - PIP.margin - PIP.size;
await shot("pipframe.png", `<div class="pipframe" style="left:${px - 5}px;top:${py - 5}px;width:${PIP.size + 10}px;height:${PIP.size + 10}px"></div>`);
await p.setViewportSize({ width: PIP.size, height: PIP.size });
await p.evaluate(() => (document.body.style.background = "#000"));
await shot("pipmask.png", `<div style="position:absolute;inset:0;background:#fff;border-radius:24px"></div>`);
await b.close();
fs.writeFileSync("ov/pip.json", JSON.stringify({ ...PIP, x: px, y: py }));
console.log("overlays:", fs.readdirSync("ov").length);
