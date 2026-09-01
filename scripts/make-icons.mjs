#!/usr/bin/env node
/**
 * public/icon.svg dan PWA uchun PNG ikonkalar yasaydi.
 *
 * Ikonkalar repozitoriyga commit qilingan, shuning uchun bu skript odatda kerak emas —
 * faqat icon.svg o'zgarganda qayta yugurtiriladi. Playwright talab qiladi:
 *   npx --yes playwright@latest install chromium && node scripts/make-icons.mjs
 */
import { chromium } from "playwright";
import { readFile, writeFile } from "node:fs/promises";

const svg = await readFile("public/icon.svg", "utf8");
const browser = await chromium.launch({
  executablePath: process.env.PW_CHROMIUM ?? "/opt/pw-browsers/chromium",
});

for (const [size, name, pad] of [
  [192, "icon-192.png", 0],
  [512, "icon-512.png", 0],
  [512, "icon-maskable-512.png", 0.1], // maskable: chekkalarda bo'sh joy kerak
  [180, "apple-touch-icon.png", 0.06],
]) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  const inset = Math.round(size * pad);
  await page.setContent(
    `<body style="margin:0;background:#0b0d10;display:grid;place-items:center;width:${size}px;height:${size}px">
       <div style="width:${size - inset * 2}px;height:${size - inset * 2}px">${svg}</div>
     </body>`,
  );
  await writeFile(`public/${name}`, await page.screenshot({ omitBackground: false }));
  await page.close();
  console.log(`public/${name} (${size}px)`);
}
await browser.close();
