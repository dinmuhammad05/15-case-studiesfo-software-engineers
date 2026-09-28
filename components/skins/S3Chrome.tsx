"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

function useScrollProgress() {
  const [pct, setPct] = useState(0);
  useEffect(() => {
    const on = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setPct(max > 0 ? Math.min(1, window.scrollY / max) : 0);
    };
    on();
    window.addEventListener("scroll", on, { passive: true });
    window.addEventListener("resize", on);
    return () => {
      window.removeEventListener("scroll", on);
      window.removeEventListener("resize", on);
    };
  }, []);
  return pct;
}

const PARTS = 10;
const bucketName = (order: number, slug: string) => `${String(order).padStart(2, "0")}-${slug}`;

/**
 * Amazon S3 skini: bulut konsoli — to'q yuqori panel, "non bo'laklari" yo'li,
 * chapda bucket'lar (darslar), markazda ob'ekt sahifasi. O'qish progressi —
 * multipart upload: dars 10 qismga bo'lingan va o'qilgan sari qismlar "yuklanadi".
 */
export function S3Chrome({
  slug,
  header,
  children,
}: {
  slug: string;
  header: ReactNode;
  children: ReactNode;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const current = lessons.find((l) => l.slug === slug)!;
  const pct = useScrollProgress();
  const idx = lessons.findIndex((l) => l.slug === slug);
  const next = lessons.slice(idx + 1).find((l) => l.status === "tayyor");
  const done = Math.min(PARTS, Math.floor(pct * PARTS + 0.0001));
  const left = Math.max(0, Math.round(current.minutes * (1 - pct)));
  const self = bucketName(current.order, current.slug);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const startReading = () =>
    document.querySelector(".lesson-prose")?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <div className="min-h-screen">
      {/* Yuqori panel */}
      <header className="sticky top-0 z-30 select-none">
        <div className="flex h-12 items-center gap-3 bg-[var(--s3-nav)] px-3 text-white sm:px-4">
          <Link href="/" className="flex shrink-0 flex-col leading-none" aria-label="Bosh sahifa">
            <span className="text-[17px] font-bold tracking-tight">darslik</span>
            <span aria-hidden className="mt-0.5 h-[3px] w-9 rounded-full bg-[var(--s3-orange)]" />
          </Link>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="hidden items-center gap-1.5 rounded px-2 py-1 text-[14px] font-bold hover:bg-white/10 sm:flex"
          >
            <IconGrid /> Darslar
          </button>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="flex h-8 min-w-0 flex-1 items-center gap-2 rounded-lg border border-[#7d8998] bg-[var(--s3-nav-2)] px-3 text-left text-[14px] text-[#aab7b8] hover:border-white/70 md:max-w-[520px]"
            aria-label="Darslarni qidirish"
          >
            <IconSearch />
            <span className="truncate">Darslar, mavzular qidirish</span>
            <span className="ml-auto hidden rounded border border-[#7d8998] px-1.5 text-[11px] sm:block">[Alt+S]</span>
          </button>
          <span className="ml-auto hidden items-center gap-1 text-[14px] font-bold md:flex">
            uz-central-1 <IconCaret />
          </span>
          <span className="flex items-center gap-2 text-[14px] font-bold">
            <span className="h-7 w-7 overflow-hidden rounded-full bg-[#5f6b7a]">
              <AuthorPhoto
                className="h-full w-full"
                fallback={<span className="flex h-full w-full items-center justify-center text-[12px]">D</span>}
              />
            </span>
            <span className="hidden lg:inline">Dinmuhammad</span>
          </span>
        </div>
        <div className="flex h-9 items-center gap-2 overflow-hidden border-b border-[var(--skin-border)] bg-white px-4 text-[13px] whitespace-nowrap sm:px-6">
          <Link href="/" className="text-[var(--skin-accent)] hover:underline">
            Tizim dizayni
          </Link>
          <Sep />
          <button type="button" onClick={() => setMenuOpen(true)} className="text-[var(--skin-accent)] hover:underline">
            Darslar
          </button>
          <Sep />
          <span className="truncate text-[var(--skin-muted)]">{self}</span>
        </div>
      </header>

      <div className="flex">
        {/* Chap navigatsiya: bucket'lar */}
        <aside className="sticky top-[84px] hidden h-[calc(100vh-84px)] w-[248px] shrink-0 overflow-y-auto border-r border-[var(--skin-border)] bg-white py-5 lg:block">
          <div className="px-6 pb-3 text-[18px] font-bold">Amazon S3</div>
          <div className="px-6 pb-2 text-[12px] font-bold tracking-wide text-[var(--skin-muted)] uppercase">
            Bucket&apos;lar (darslar)
          </div>
          <ul className="space-y-0.5 text-[14px]">
            {lessons.map((l) => {
              const ready = l.status === "tayyor";
              const active = l.slug === slug;
              const name = bucketName(l.order, l.slug);
              return (
                <li key={l.slug}>
                  {ready ? (
                    <Link
                      href={`/darslar/${l.slug}/`}
                      className={`block truncate border-l-4 py-1 pr-4 pl-5 ${
                        active
                          ? "border-[var(--s3-orange)] font-bold text-[var(--skin-accent)]"
                          : "border-transparent hover:text-[var(--skin-accent)]"
                      }`}
                    >
                      {name}
                    </Link>
                  ) : (
                    <span className="block truncate border-l-4 border-transparent py-1 pr-4 pl-5 text-[#9ba7b6]">{name}</span>
                  )}
                </li>
              );
            })}
          </ul>
        </aside>

        <main className="mx-auto min-w-0 max-w-[1400px] flex-1 px-3 pt-5 pb-32 sm:px-6 lg:pb-16">
          {/* Ob'ekt sahifasi sarlavhasi */}
          <div className="rounded-[var(--skin-radius)] bg-white p-5 shadow-[var(--s3-shadow)] sm:p-6">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-[12px]">
              <span className="rounded-full border border-[var(--s3-green)] px-2 py-0.5 font-bold text-[var(--s3-green)]">
                ● Mavjud
              </span>
              <span className="text-[var(--skin-muted)]">Saqlash sinfi: Standard · Bepul</span>
            </div>
            <div className="[&_h1]:text-[28px] [&_h1]:leading-tight sm:[&_h1]:text-[34px] [&_header]:mb-5">{header}</div>
            <div className="grid gap-x-8 gap-y-3 border-t border-[var(--skin-border)] pt-4 text-[14px] sm:grid-cols-2 xl:grid-cols-4">
              <Field label="Muallif (egasi)" value="Dinmuhammad" />
              <Field label="Kalit" value={`darslar/${self}.mdx`} mono />
              <Field label="Hajmi" value={`~${current.minutes} daqiqa o‘qish`} />
              <Field label="S3 URI" value={`s3://tizim-dizayni/darslar/${self}`} mono />
            </div>
            <nav className="-mb-5 mt-5 flex gap-1 overflow-x-auto border-t border-[var(--skin-border)] text-[14px] font-bold sm:-mb-6" aria-label="Tablar">
              {[
                ["Dars", ""],
                ["Intervyu", "#17-intervyu-savollari"],
                ["Amaliyot", "#18-amaliyot"],
                ["Manbalar", "#21-manbalar"],
              ].map(([t, href], i) => (
                <a
                  key={t}
                  href={href || undefined}
                  onClick={href ? undefined : startReading}
                  className={`shrink-0 cursor-pointer border-b-4 px-3 pt-3 pb-2.5 ${
                    i === 0 ? "border-[var(--skin-accent)] text-[var(--skin-accent)]" : "border-transparent text-[var(--skin-muted)] hover:text-[var(--skin-text)]"
                  }`}
                >
                  {t}
                </a>
              ))}
            </nav>
          </div>

          <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
            <div className="min-w-0 rounded-[var(--skin-radius)] bg-white px-4 pb-8 shadow-[var(--s3-shadow)] sm:px-8">
              {children}
            </div>

            {/* Yuklash holati: o'qish progressi multipart upload sifatida */}
            <aside className="hidden xl:block">
              <div className="sticky top-[104px] space-y-4">
                <div className="rounded-[var(--skin-radius)] bg-white p-5 shadow-[var(--s3-shadow)]">
                  <div className="text-[16px] font-bold">Yuklash holati</div>
                  <div className="mt-0.5 text-[13px] text-[var(--skin-muted)]">Multipart upload · {PARTS} qism</div>
                  <Parts done={done} className="mt-4 grid grid-cols-5 gap-1.5" />
                  <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
                    <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${pct * 100}%` }} />
                  </div>
                  <div className="mt-2 flex justify-between text-[13px] text-[var(--skin-muted)]">
                    <span>
                      {done}/{PARTS} qism · {Math.round(pct * 100)}%
                    </span>
                    <span>~{left} daq qoldi</span>
                  </div>
                  <button
                    type="button"
                    onClick={startReading}
                    className="mt-4 h-9 w-full rounded-full bg-[var(--s3-orange)] text-[14px] font-bold text-[var(--skin-text)] hover:bg-[var(--s3-orange-dark)]"
                  >
                    {pct >= 0.995 ? "Yakunlandi ✓" : pct > 0.02 ? "Yuklashni davom ettirish" : "Yuklashni boshlash"}
                  </button>
                </div>
                <div className="rounded-[var(--skin-radius)] bg-white p-5 text-[14px] shadow-[var(--s3-shadow)]">
                  <div className="text-[12px] font-bold tracking-wide text-[var(--skin-muted)] uppercase">Nazorat summasi</div>
                  <div className="mt-1 font-[family-name:var(--skin-mono)] text-[12px] break-all">crc32c: {checksum(done)}</div>
                  {next ? (
                    <div className="mt-4 border-t border-[var(--skin-border)] pt-3">
                      <span className="text-[var(--skin-muted)]">Keyingi bucket: </span>
                      <Link href={`/darslar/${next.slug}/`} className="font-bold text-[var(--skin-accent)] hover:underline">
                        {next.title}
                      </Link>
                    </div>
                  ) : null}
                </div>
              </div>
            </aside>
          </div>
        </main>
      </div>

      {/* Mobil va o'rta ekran: pastki panel */}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--skin-border)] bg-white xl:hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 pr-28 sm:px-6">
          <div className="min-w-0 flex-1">
            <div className="truncate text-[14px] font-bold">
              {done}/{PARTS} qism · {Math.round(pct * 100)}%
            </div>
            <Parts done={done} className="mt-1.5 grid max-w-[260px] grid-cols-10 gap-1" small />
          </div>
          <button
            type="button"
            onClick={startReading}
            className="h-9 shrink-0 rounded-full bg-[var(--s3-orange)] px-5 text-[14px] font-bold text-[var(--skin-text)]"
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Darslar — bucket'lar jadvali */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-[#000716]/50" />
          <div className="absolute inset-x-2 top-14 max-h-[80vh] overflow-y-auto rounded-[var(--skin-radius)] bg-white shadow-2xl sm:inset-x-auto sm:left-1/2 sm:w-[640px] sm:-translate-x-1/2">
            <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-5 py-4">
              <div>
                <div className="text-[18px] font-bold">Bucket&apos;lar ({lessons.length})</div>
                <div className="text-[13px] text-[var(--skin-muted)]">Har bir dars — alohida bucket</div>
              </div>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label="Yopish"
                className="flex h-8 w-8 items-center justify-center rounded text-[20px] text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
              >
                ×
              </button>
            </div>
            <table className="w-full text-left text-[14px]">
              <thead className="text-[13px] text-[var(--skin-muted)]">
                <tr className="border-b border-[var(--skin-border)]">
                  <th className="px-5 py-2 font-bold">Nomi</th>
                  <th className="hidden px-3 py-2 font-bold sm:table-cell">Mintaqa</th>
                  <th className="px-5 py-2 text-right font-bold">Holat</th>
                </tr>
              </thead>
              <tbody>
                {lessons.map((l) => {
                  const ready = l.status === "tayyor";
                  const active = l.slug === slug;
                  const name = bucketName(l.order, l.slug);
                  return (
                    <tr key={l.slug} className={`border-b border-[var(--skin-border)] ${active ? "bg-[#f2f8fd]" : ""}`}>
                      <td className="px-5 py-2.5">
                        {ready ? (
                          <Link
                            href={`/darslar/${l.slug}/`}
                            onClick={() => setMenuOpen(false)}
                            className="font-bold text-[var(--skin-accent)] hover:underline"
                          >
                            {name}
                          </Link>
                        ) : (
                          <span className="text-[#9ba7b6]">{name}</span>
                        )}
                        <div className="truncate text-[12px] text-[var(--skin-muted)]">{l.title}</div>
                      </td>
                      <td className="hidden px-3 py-2.5 text-[var(--skin-muted)] sm:table-cell">uz-central-1</td>
                      <td className="px-5 py-2.5 text-right whitespace-nowrap">
                        {ready ? (
                          <span className="text-[var(--s3-green)]">● {l.minutes} daq</span>
                        ) : (
                          <span className="text-[var(--skin-muted)]">○ Tez orada</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function Parts({ done, className, small }: { done: number; className: string; small?: boolean }) {
  return (
    <div className={className} aria-hidden>
      {Array.from({ length: PARTS }).map((_, i) => (
        <span
          key={i}
          className={`flex items-center justify-center rounded ${small ? "h-2" : "h-8 text-[11px] font-bold"} ${
            i < done ? "bg-[var(--s3-green)] text-white" : "bg-[var(--skin-surface-2)] text-[var(--skin-muted)] ring-1 ring-[var(--skin-border)] ring-inset"
          }`}
        >
          {small ? null : i < done ? "✓" : i + 1}
        </span>
      ))}
    </div>
  );
}

/** Soxta, lekin deterministik "nazorat summasi": qancha qism yuklangan bo'lsa, shunga qarab o'zgaradi. */
function checksum(done: number) {
  let h = 0x811c9dc5 ^ (done * 2654435761);
  for (let i = 0; i < 4; i++) h = Math.imul(h ^ (h >>> 15), 0x2c1b3c6d) >>> 0;
  return h.toString(16).padStart(8, "0") + "==";
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="min-w-0">
      <div className="text-[13px] font-bold text-[var(--skin-muted)]">{label}</div>
      <div className={`truncate ${mono ? "font-[family-name:var(--skin-mono)] text-[13px]" : ""}`}>{value}</div>
    </div>
  );
}

function Sep() {
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3 shrink-0 text-[var(--skin-muted)]" aria-hidden fill="none">
      <path d="m6 3 5 5-5 5" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}
function IconGrid() {
  return (
    <svg viewBox="0 0 16 16" className="h-4 w-4" aria-hidden fill="currentColor">
      <rect x="1" y="1" width="4" height="4" />
      <rect x="6" y="1" width="4" height="4" />
      <rect x="11" y="1" width="4" height="4" />
      <rect x="1" y="6" width="4" height="4" />
      <rect x="6" y="6" width="4" height="4" />
      <rect x="11" y="6" width="4" height="4" />
      <rect x="1" y="11" width="4" height="4" />
      <rect x="6" y="11" width="4" height="4" />
      <rect x="11" y="11" width="4" height="4" />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg viewBox="0 0 16 16" className="h-4 w-4 shrink-0" aria-hidden fill="none">
      <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="2" />
      <path d="m11 11 4 4" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}
function IconCaret() {
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3" aria-hidden fill="currentColor">
      <path d="M3 5h10L8 11z" />
    </svg>
  );
}
