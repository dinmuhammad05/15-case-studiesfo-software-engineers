#!/usr/bin/env node
/**
 * Yangi dars uchun skelet yaratadi:
 *   node scripts/yangi-dars.mjs kafka
 * Dars lib/lessons.ts ro'yxatida oldindan turgan bo'lishi kerak.
 */
import { mkdir, writeFile, readFile, access } from "node:fs/promises";
import { join } from "node:path";

const slug = process.argv[2];
if (!slug) {
  console.error("Foydalanish: node scripts/yangi-dars.mjs <slug>");
  process.exit(1);
}

const registry = await readFile("lib/lessons.ts", "utf8");
if (!registry.includes(`slug: "${slug}"`)) {
  console.error(`"${slug}" lib/lessons.ts ichida topilmadi. Avval ro'yxatga qo'shing.`);
  process.exit(1);
}

const pascal = slug
  .split("-")
  .map((p) => p[0].toUpperCase() + p.slice(1))
  .join("");

const dir = join("app", "darslar", slug);
try {
  await access(dir);
  console.error(`${dir} allaqachon mavjud.`);
  process.exit(1);
} catch {}
await mkdir(dir, { recursive: true });

await writeFile(
  join(dir, "theme.css"),
  `/* ${slug} skini uchun token qiymatlari (rasmiy brend materiali emas) */
[data-skin="${slug}"] {
  --skin-bg: #0b0d10;
  --skin-surface: #14171c;
  --skin-surface-2: #1c2027;
  --skin-border: #272c35;
  --skin-text: #e8ecf1;
  --skin-muted: #9aa4b2;
  --skin-accent: #f5a524;
  --skin-accent-text: #0b0d10;
  --skin-radius: 12px;
  --skin-font: ui-sans-serif, system-ui, sans-serif;
  --skin-mono: ui-monospace, "JetBrains Mono", Menlo, monospace;
}

/* Overscroll paytida sahifa foni skin rangida qolsin */
body:has([data-skin="${slug}"]) {
  background: #0b0d10;
}
`,
);

await writeFile(
  join(dir, "layout.tsx"),
  `import type { Metadata } from "next";
import { ${pascal}Shell } from "@/components/skins/${pascal}Shell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("${slug}")!;

export const metadata: Metadata = { title: lesson.title, description: lesson.summary };

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="${slug}" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <${pascal}Shell>{children}</${pascal}Shell>
    </div>
  );
}
`,
);

await writeFile(
  join(dir, "page.mdx"),
  `## 1. Muammo: aslida nimani qurmoqchimiz?

<StatGrid>
  <Stat value="—" label="Foydalanuvchi" />
  <Stat value="—" label="Yozish yuki" />
  <Stat value="—" label="O'qish yuki" />
  <Stat value="—" label="Kechikish maqsadi" />
</StatGrid>

## 2. v0: eng sodda ishlaydigan yechim

<Flow nodes={["Mijoz", "Server", "Baza"]} caption="Bitta server, bitta baza." />

## 3. Nima sindi

## 4. Evolyutsiya

<Step n="1" title="..." gain="..." cost="...">
  ...
</Step>

## 5. Bugungi arxitektura

<Arch layers={[{ name: "Mijoz", boxes: ["..."] }]} />

## 6. Trade-off'lar

<TradeOffs rows={[{ choice: "...", pro: "...", con: "..." }]} />

## 7. Intervyu savollari

<QA q="...">...</QA>

## 8. Amaliyot

<Task title="...">...</Task>
`,
);

const shellPath = join("components", "skins", `${pascal}Shell.tsx`);
try {
  await access(shellPath);
} catch {
  await writeFile(
    shellPath,
    `import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";

/** TODO: shu mahsulot interfeysidan ilhomlangan chrome (sidebar, panel, player...). */
export function ${pascal}Shell({ children }: { children: ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-3xl px-5 py-10">
      <LessonHeader slug="${slug}" />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="${slug}" />
      <SkinDisclaimer product="${pascal}" />
    </main>
  );
}
`,
  );
}

console.log(`Tayyor:
  ${dir}/page.mdx      — dars matni
  ${dir}/theme.css     — ranglar va shriftlar
  ${shellPath}  — UI chrome
lib/lessons.ts ichida status: "yozilmoqda" ga o'zgartiring.`);
