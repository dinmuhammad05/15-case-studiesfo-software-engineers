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

/** Galereyadagi kichik "xonalar": darsning asosiy mavzulari rangli plitkalar sifatida. */
const TILE_COLORS = [
  "linear-gradient(135deg, #ffd6de 0%, #ffb3c2 100%)",
  "linear-gradient(135deg, #fde8d7 0%, #f8c9a0 100%)",
  "linear-gradient(135deg, #dcefe9 0%, #a9d8c8 100%)",
  "linear-gradient(135deg, #e3e6fb 0%, #b9c0f2 100%)",
];

/**
 * Airbnb skini: yuqorida qidiruv "pill"i, e'lon sarlavhasi va foto-galereya,
 * pastda ikki ustun — chapda dars, o'ngda yopishqoq "bron" kartasi (o'qish progressi).
 */
export function AirbnbChrome({
  slug,
  header,
  children,
}: {
  slug: string;
  header: ReactNode;
  children: ReactNode;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const current = lessons.find((l) => l.slug === slug)!;
  const pct = useScrollProgress();
  const idx = lessons.findIndex((l) => l.slug === slug);
  const next = lessons.slice(idx + 1).find((l) => l.status === "tayyor");
  const readMin = Math.round(current.minutes * pct);

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
      <header className="sticky top-0 z-30 border-b border-[var(--ab-hairline)] bg-white select-none">
        <div className="mx-auto flex h-[72px] max-w-[1280px] items-center gap-4 px-4 sm:px-6 lg:px-10">
          <Link href="/" className="flex shrink-0 items-center gap-2 text-[var(--ab-rausch)]" aria-label="Bosh sahifa">
            <MarkIcon />
            <span className="hidden text-[20px] font-bold tracking-tight md:inline">darslik</span>
          </Link>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="mx-auto flex h-12 min-w-0 items-center rounded-full border border-[var(--skin-border)] text-left text-[14px] shadow-[0_1px_2px_rgba(0,0,0,0.08),0_4px_12px_rgba(0,0,0,0.05)] transition-shadow hover:shadow-[var(--ab-shadow)]"
            aria-label="Darslar ro'yxatini ochish"
          >
            <span className="truncate px-5 font-medium">Istalgan dars</span>
            <span className="hidden h-6 w-px bg-[var(--skin-border)] sm:block" />
            <span className="hidden px-5 font-medium whitespace-nowrap sm:block">{current.minutes} daqiqa</span>
            <span className="hidden h-6 w-px bg-[var(--skin-border)] sm:block" />
            <span className="hidden px-5 whitespace-nowrap text-[var(--skin-muted)] sm:block">Tizim dizayni</span>
            <span
              className="mr-2 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white"
              style={{ background: "var(--ab-rausch)" }}
            >
              <IconSearch />
            </span>
          </button>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="flex shrink-0 items-center gap-3 rounded-full border border-[var(--skin-border)] py-1.5 pr-1.5 pl-3 hover:shadow-[var(--ab-shadow)]"
            aria-label="Menyu"
          >
            <IconMenu />
            <span className="h-8 w-8 overflow-hidden rounded-full bg-[#717171]">
              <AuthorPhoto
                className="h-full w-full"
                fallback={<span className="flex h-full w-full items-center justify-center text-[12px] font-bold text-white">D</span>}
              />
            </span>
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-[1280px] px-4 pb-28 sm:px-6 lg:px-10 lg:pb-16">
        {/* Sarlavha va harakatlar */}
        <div className="pt-6 [&_header]:mb-4">
          {header}
          <div className="-mt-1 mb-5 flex flex-wrap items-center justify-between gap-3 text-[14px]">
            <div className="flex items-center gap-2 text-[var(--skin-text)]">
              <IconStar />
              <span className="font-semibold">Yangi</span>
              <span aria-hidden>·</span>
              <span className="underline underline-offset-2">{current.topics.length} ta mavzu</span>
              <span aria-hidden className="hidden sm:inline">·</span>
              <span className="hidden sm:inline">Tizim dizayni, o‘zbek tilida</span>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setSaved((v) => !v)}
                aria-pressed={saved}
                className="flex items-center gap-2 rounded-lg px-3 py-2 font-semibold underline underline-offset-2 hover:bg-[var(--skin-surface-2)]"
              >
                <IconHeart filled={saved} />
                Saqlash
              </button>
            </div>
          </div>
        </div>

        {/* Foto-galereya: katta rasm + 4 ta mavzu plitkasi */}
        <div className="grid h-[260px] grid-cols-1 gap-2 overflow-hidden rounded-xl sm:h-[340px] md:grid-cols-4 md:grid-rows-2 lg:h-[420px]">
          <div className="relative md:col-span-2 md:row-span-2">
            <AuthorPhoto
              variant="portrait"
              position="50% 20%"
              className="h-full w-full"
              alt="Dars muallifi"
              fallback={<div className="h-full w-full" style={{ background: TILE_COLORS[0] }} />}
            />
          </div>
          {current.topics.slice(0, 4).map((t, i) => (
            <div
              key={t}
              className="hidden flex-col justify-end p-4 md:flex"
              style={{ background: TILE_COLORS[i % TILE_COLORS.length] }}
            >
              <span className="text-[11px] font-semibold tracking-wide text-black/50 uppercase">Mavzu {i + 1}</span>
              <span className="text-[17px] leading-tight font-semibold text-[#222]">{t}</span>
            </div>
          ))}
        </div>

        {/* Ikki ustun: dars va bron kartasi */}
        <div className="mt-10 grid gap-12 lg:grid-cols-[minmax(0,1fr)_360px] xl:gap-20">
          <div className="min-w-0">
            {/* "Mezbon" qatori */}
            <div className="mb-8 flex items-center gap-4 border-b border-[var(--ab-hairline)] pb-8">
              <span className="relative h-14 w-14 shrink-0">
                <span className="block h-full w-full overflow-hidden rounded-full">
                  <AuthorPhoto
                    className="h-full w-full"
                    fallback={<span className="flex h-full w-full items-center justify-center rounded-full bg-[#222] text-white">D</span>}
                  />
                </span>
                <span
                  className="absolute -right-1 -bottom-1 flex h-6 w-6 items-center justify-center rounded-full text-white ring-2 ring-white"
                  style={{ background: "var(--ab-grad)" }}
                  aria-hidden
                >
                  <IconBadge />
                </span>
              </span>
              <div>
                <div className="text-[17px] font-semibold">Muallif: Dinmuhammad</div>
                <div className="text-[14px] text-[var(--skin-muted)]">Full-stack dasturchi · {current.minutes} daqiqalik dars</div>
              </div>
            </div>
            {children}
          </div>

          {/* Yopishqoq bron kartasi */}
          <aside className="hidden lg:block">
            <div className="sticky top-[104px] rounded-xl border border-[var(--skin-border)] p-6 shadow-[var(--ab-shadow)]">
              <div className="flex items-baseline gap-1">
                <span className="text-[22px] font-semibold">{readMin}</span>
                <span className="text-[var(--skin-muted)]">/ {current.minutes} daqiqa o‘qildi</span>
              </div>
              <div className="mt-5 overflow-hidden rounded-lg border border-[#b0b0b0]">
                <div className="grid grid-cols-2">
                  <div className="border-r border-[#b0b0b0] px-3 py-2.5">
                    <div className="text-[10px] font-bold tracking-wide uppercase">Boshlash</div>
                    <div className="text-[14px] text-[var(--skin-muted)]">1-bo‘lim</div>
                  </div>
                  <div className="px-3 py-2.5">
                    <div className="text-[10px] font-bold tracking-wide uppercase">Tugatish</div>
                    <div className="text-[14px] text-[var(--skin-muted)]">Amaliyot</div>
                  </div>
                </div>
                <div className="border-t border-[#b0b0b0] px-3 py-2.5">
                  <div className="text-[10px] font-bold tracking-wide uppercase">Daraja</div>
                  <div className="text-[14px] text-[var(--skin-muted)]">{current.level}</div>
                </div>
              </div>
              <button
                type="button"
                onClick={startReading}
                className="mt-4 h-12 w-full rounded-lg text-[16px] font-semibold text-white"
                style={{ background: "var(--ab-grad)" }}
              >
                {pct > 0.02 ? "O‘qishni davom ettirish" : "O‘qishni boshlash"}
              </button>
              <div className="mt-5">
                <div className="h-1.5 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
                  <div className="h-full rounded-full" style={{ width: `${pct * 100}%`, background: "var(--ab-grad)" }} />
                </div>
                <div className="mt-2 flex justify-between text-[13px] text-[var(--skin-muted)]">
                  <span>{Math.round(pct * 100)}% o‘qildi</span>
                  <span>{Math.max(0, current.minutes - readMin)} daqiqa qoldi</span>
                </div>
              </div>
              {next ? (
                <div className="mt-5 border-t border-[var(--ab-hairline)] pt-4 text-[14px]">
                  <span className="text-[var(--skin-muted)]">Keyingi dars: </span>
                  <Link href={`/darslar/${next.slug}/`} className="font-semibold underline underline-offset-2">
                    {next.title}
                  </Link>
                </div>
              ) : null}
            </div>
          </aside>
        </div>
      </main>

      {/* Mobil: pastki "bron" paneli */}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--ab-hairline)] bg-white lg:hidden">
        <div className="h-1 bg-[var(--skin-surface-2)]">
          <div className="h-full" style={{ width: `${pct * 100}%`, background: "var(--ab-grad)" }} />
        </div>
        <div className="flex items-center gap-3 px-4 py-3 pr-28 sm:px-6">
          <div className="min-w-0 flex-1">
            <div className="text-[15px] font-semibold">
              {readMin} / {current.minutes} daq
            </div>
            <div className="text-[13px] text-[var(--skin-muted)]">{Math.round(pct * 100)}% o‘qildi</div>
          </div>
          <button
            type="button"
            onClick={startReading}
            className="h-11 shrink-0 rounded-lg px-5 text-[15px] font-semibold text-white"
            style={{ background: "var(--ab-grad)" }}
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Darslar ro'yxati — "e'lonlar" */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/40" />
          <div className="absolute inset-x-0 top-0 max-h-[85vh] overflow-y-auto rounded-b-3xl bg-white p-5 shadow-2xl sm:inset-x-auto sm:top-20 sm:right-6 sm:w-[420px] sm:rounded-2xl">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-[16px] font-semibold">Darslar</span>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label="Yopish"
                className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-[var(--skin-surface-2)]"
              >
                ×
              </button>
            </div>
            <div className="space-y-1">
              {lessons.map((l) => {
                const ready = l.status === "tayyor";
                const active = l.slug === slug;
                const row = (
                  <>
                    <span
                      className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg text-[13px] font-bold text-white"
                      style={{ background: ready ? l.accent : "#c4c4c4" }}
                    >
                      {String(l.order).padStart(2, "0")}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className={`block truncate text-[15px] ${active ? "font-semibold" : ""}`}>{l.title}</span>
                      <span className="block text-[13px] text-[var(--skin-muted)]">
                        {ready ? `${l.minutes} daqiqa · ${l.level}` : "Tez orada"}
                      </span>
                    </span>
                  </>
                );
                return ready ? (
                  <Link
                    key={l.slug}
                    href={`/darslar/${l.slug}/`}
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center gap-3 rounded-xl p-2 hover:bg-[var(--skin-surface-2)] ${active ? "bg-[var(--skin-surface-2)]" : ""}`}
                  >
                    {row}
                  </Link>
                ) : (
                  <span key={l.slug} className="flex cursor-default items-center gap-3 rounded-xl p-2 opacity-50">
                    {row}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

/** Soddalashtirilgan belgi — rasmiy logotip emas. */
function MarkIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-8 w-8" aria-hidden fill="none">
      <path
        d="M16 4 5 15v12a1 1 0 0 0 1 1h7v-8h6v8h7a1 1 0 0 0 1-1V15z"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <path d="M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM16.5 16.5 21 21" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
function IconMenu() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}
function IconStar() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="currentColor" aria-hidden>
      <path d="M12 2.5l2.9 6.2 6.6.7-5 4.5 1.4 6.6L12 17.2l-5.9 3.3 1.4-6.6-5-4.5 6.6-.7z" />
    </svg>
  );
}
function IconBadge() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" aria-hidden>
      <path d="m7 12.5 3.2 3L17 8.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function IconHeart({ filled }: { filled: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden fill={filled ? "#ff385c" : "none"}>
      <path
        d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"
        stroke={filled ? "#ff385c" : "currentColor"}
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}
