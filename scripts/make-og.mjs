#!/usr/bin/env node
/**
 * Ijtimoiy tarmoqlarda ulashish uchun preview rasmlar (1200x630) yasaydi:
 *   public/og.png            — bosh sahifa uchun
 *   public/og-<slug>.png     — har bir tayyor dars uchun
 *
 * Rasmlar repozitoriyga commit qilinadi, shuning uchun bu skript faqat
 * dizayn yoki darslar ro'yxati o'zgarganda kerak. Playwright talab qiladi:
 *   npx --yes playwright@latest install chromium && node scripts/make-og.mjs
 */
import { chromium } from "playwright";
import { writeFile, readFile } from "node:fs/promises";

const lessonsSrc = await readFile("lib/lessons.ts", "utf8");
const ready = [...lessonsSrc.matchAll(/order:\s*(\d+),\s*\n\s*slug:\s*"([^"]+)",\s*\n\s*title:\s*"([^"]+)",[\s\S]*?accent:\s*"([^"]+)",\s*\n\s*status:\s*"([^"]+)"/g)]
  .map((m) => ({ order: +m[1], slug: m[2], title: m[3], accent: m[4], status: m[5] }))
  .filter((l) => l.status === "tayyor");

const MARK = `<svg viewBox="0 0 512 512" width="96" height="96">
  <g stroke="ACCENT" stroke-width="26" fill="none" stroke-linecap="round">
    <circle cx="256" cy="150" r="46"/><circle cx="150" cy="340" r="46"/><circle cx="362" cy="340" r="46"/>
    <path d="M232 190 L174 300 M280 190 L338 300 M196 340 L316 340"/>
  </g></svg>`;

const template = ({ accent, eyebrow, title, subtitle, footer }) => `
<body style="margin:0;width:1200px;height:630px;background:#0b0d10;color:#e8ecf1;
  font-family:ui-sans-serif,system-ui,'Segoe UI',Roboto,sans-serif;position:relative;overflow:hidden">
  <div style="position:absolute;inset:0;background:
    radial-gradient(900px 420px at 88% -10%, ${accent}26, transparent 60%),
    radial-gradient(700px 380px at -10% 110%, ${accent}1a, transparent 60%)"></div>
  <div style="position:absolute;left:0;top:0;width:100%;height:8px;background:${accent}"></div>
  <div style="position:relative;padding:70px 76px;height:100%;box-sizing:border-box;
    display:flex;flex-direction:column;justify-content:space-between">
    <div style="display:flex;align-items:center;gap:22px">
      ${MARK.replace(/ACCENT/g, accent)}
      <div style="font-size:26px;color:#9aa4b2;font-weight:500">${eyebrow}</div>
    </div>
    <div>
      <div style="font-size:${title.length > 34 ? 62 : 76}px;font-weight:800;line-height:1.08;
        letter-spacing:-0.03em;max-width:1000px">${title}</div>
      <div style="margin-top:22px;font-size:29px;color:#9aa4b2;max-width:900px;line-height:1.4">${subtitle}</div>
    </div>
    <div style="display:flex;align-items:center;gap:14px;font-size:23px;color:#8b949e;
      font-family:ui-monospace,Menlo,monospace">
      <span style="color:${accent}">${footer.left}</span>
      <span style="opacity:.4">·</span>
      <span>${footer.right}</span>
    </div>
  </div>
</body>`;

const browser = await chromium.launch({
  executablePath: process.env.PW_CHROMIUM ?? "/opt/pw-browsers/chromium",
});

async function shot(name, html) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await page.setContent(html);
  await writeFile(`public/${name}`, await page.screenshot());
  await page.close();
  console.log(`public/${name}`);
}

await shot(
  "og.png",
  template({
    accent: "#f5a524",
    eyebrow: "System Design darsligi",
    title: "17 ta case study,<br/>noldan arxitekturagacha",
    subtitle:
      "ChatGPT, Redis, Kafka, S3 va boshqalar — hisob-kitob, intervyu savollari va amaliyot bilan",
    footer: { left: "o‘zbek tilida", right: "github.com/dinmuhammad05" },
  }),
);

for (const l of ready) {
  await shot(
    `og-${l.slug}.png`,
    template({
      accent: l.accent === "#000000" ? "#e8ecf1" : l.accent,
      eyebrow: `System Design darsligi · dars ${String(l.order).padStart(2, "0")}`,
      title: l.title,
      subtitle: "Noldan bugungi arxitekturagacha: hisob-kitob, tuzoqlar va intervyu savollari",
      footer: { left: "o‘zbek tilida", right: "github.com/dinmuhammad05" },
    }),
  );
}

await browser.close();
