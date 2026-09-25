"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

const pad = (n: number) => String(n).padStart(2, "0");

function fmt(sec: number) {
  const s = Math.max(0, Math.floor(sec));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  return h > 0 ? `${h}:${pad(m)}:${pad(r)}` : `${m}:${pad(r)}`;
}

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

/** Darsning kichik "muqovasi": rasm bo'lmasa — rangli kvadrat va raqam. */
function Cover({ lesson, className = "" }: { lesson: (typeof lessons)[number]; className?: string }) {
  return (
    <span
      aria-hidden
      className={`flex shrink-0 items-center justify-center rounded font-black text-white ${className}`}
      style={{ background: `linear-gradient(135deg, ${lesson.accent}, #121212 130%)` }}
    >
      {pad(lesson.order)}
    </span>
  );
}

/**
 * Spotify desktop skini: chapda kutubxona (darslar = pleylistlar), o'rtada
 * pleylist sahifasi, pastda doimiy pleyer paneli — uning chizig'i o'qish progressi.
 */
export function SpotifyChrome({
  slug,
  header,
  children,
}: {
  slug: string;
  header: ReactNode;
  children: ReactNode;
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [liked, setLiked] = useState(false);
  const current = lessons.find((l) => l.slug === slug)!;
  const pct = useScrollProgress();
  const total = current.minutes * 60;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setDrawerOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  const startReading = () =>
    document.querySelector(".lesson-prose")?.scrollIntoView({ behavior: "smooth", block: "start" });

  const library = (onNavigate?: () => void) =>
    lessons.map((l) => {
      const ready = l.status === "tayyor";
      const active = l.slug === slug;
      const row = (
        <>
          <Cover lesson={l} className="h-12 w-12 text-sm" />
          <span className="min-w-0 flex-1">
            <span
              className={`block truncate text-[15px] ${active ? "text-[var(--sp-green)]" : "text-white"}`}
            >
              {l.title}
            </span>
            <span className="block truncate text-[13px] text-[var(--skin-muted)]">
              {ready ? `Pleylist · darslik · ${l.minutes} daq` : "Tez orada"}
            </span>
          </span>
          {active ? (
            <span aria-hidden className="text-[var(--sp-green)]">
              <IconSpeaker />
            </span>
          ) : null}
        </>
      );
      return ready ? (
        <Link
          key={l.slug}
          href={`/darslar/${l.slug}/`}
          onClick={onNavigate}
          title={l.title}
          className={`flex items-center gap-3 rounded-md p-2 hover:bg-[var(--sp-hover)] ${
            active ? "bg-[var(--sp-hover)]" : ""
          }`}
        >
          {row}
        </Link>
      ) : (
        <span key={l.slug} className="flex cursor-default items-center gap-3 rounded-md p-2 opacity-45">
          {row}
        </span>
      );
    });

  return (
    <div className="flex min-h-screen gap-2 p-2 pb-[88px]">
      {/* Chap: kutubxona */}
      <aside className="sticky top-2 hidden h-[calc(100vh-104px)] w-[300px] shrink-0 flex-col rounded-lg bg-[var(--skin-bg)] lg:flex xl:w-[340px]">
        <div className="flex items-center gap-3 px-5 pt-4 pb-2">
          <Link href="/" title="Bosh sahifa" className="text-[var(--skin-muted)] hover:text-white">
            <IconLibrary />
          </Link>
          <span className="font-bold text-white">Kutubxonangiz</span>
        </div>
        <div className="flex gap-2 px-4 py-2" aria-hidden>
          {["Pleylistlar", "Tizim dizayni"].map((c) => (
            <span key={c} className="rounded-full bg-[var(--skin-surface-2)] px-3 py-1.5 text-[13px] text-white">
              {c}
            </span>
          ))}
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">{library()}</div>
      </aside>

      {/* O'rta: pleylist sahifasi */}
      <main className="min-w-0 flex-1 overflow-clip rounded-lg bg-[var(--skin-bg)]">
        <div
          className="relative"
          style={{ background: `linear-gradient(180deg, ${current.accent}cc 0%, ${current.accent}55 55%, #121212 100%)` }}
        >
          {/* Yuqori panel */}
          <div className="sticky top-0 z-20 flex items-center gap-2 px-4 py-3 select-none sm:px-6">
            <button
              type="button"
              onClick={() => setDrawerOpen(true)}
              aria-label="Kutubxonani ochish"
              className="flex h-8 w-8 items-center justify-center rounded-full bg-black/60 lg:hidden"
            >
              <IconLibrary />
            </button>
            <Link
              href="/"
              aria-label="Bosh sahifa"
              className="hidden h-8 w-8 items-center justify-center rounded-full bg-black/60 lg:flex"
            >
              <IconChevron />
            </Link>
            <div
              aria-hidden
              className="mx-auto hidden h-10 w-full max-w-[420px] items-center gap-3 rounded-full bg-[var(--skin-surface-2)] px-4 text-[14px] text-[var(--skin-muted)] md:flex"
            >
              <IconSearch />
              Nimani tinglamoqchisiz?
            </div>
            <span aria-hidden className="ml-auto h-8 w-8 shrink-0 overflow-hidden rounded-full bg-black/60 p-1 md:ml-0">
              <AuthorPhoto
                className="h-full w-full rounded-full"
                fallback={
                  <span className="flex h-full w-full items-center justify-center rounded-full bg-[#e8115b] text-[12px] font-bold">
                    D
                  </span>
                }
              />
            </span>
          </div>

          {/* Pleylist sarlavhasi: muqova + dars sarlavhasi */}
          <div className="flex flex-col gap-6 px-4 pt-4 pb-6 sm:flex-row sm:items-end sm:px-6">
            <div className="h-48 w-48 shrink-0 overflow-hidden rounded-md shadow-[0_8px_40px_rgba(0,0,0,0.6)] xl:h-56 xl:w-56">
              <AuthorPhoto
                variant="portrait"
                position="50% 18%"
                className="h-full w-full"
                alt="Pleylist muqovasi"
                fallback={<Cover lesson={current} className="h-full w-full text-6xl" />}
              />
            </div>
            <div className="min-w-0 flex-1 [&_header]:mb-0">
              <div className="mb-1 text-[13px] font-medium text-white">Pleylist</div>
              {header}
            </div>
          </div>
        </div>

        {/* Harakatlar qatori */}
        <div className="flex items-center gap-6 bg-gradient-to-b from-black/20 to-transparent px-4 py-5 select-none sm:px-6">
          <button
            type="button"
            onClick={startReading}
            aria-label="O'qishni boshlash"
            className="flex h-14 w-14 items-center justify-center rounded-full bg-[var(--sp-green)] text-black shadow-lg transition-transform hover:scale-105"
          >
            <IconPlay className="h-6 w-6" />
          </button>
          <button
            type="button"
            onClick={() => setLiked((v) => !v)}
            aria-label="Yoqtirganlarga qo'shish"
            aria-pressed={liked}
            className={liked ? "text-[var(--sp-green)]" : "text-[var(--skin-muted)] hover:text-white"}
          >
            <IconHeart filled={liked} />
          </button>
          <span aria-hidden className="text-[var(--skin-muted)]">
            <IconDownload />
          </span>
          <span aria-hidden className="text-[var(--skin-muted)]">
            <IconDots />
          </span>
        </div>

        <div className="mx-auto max-w-[980px] px-4 pb-10 sm:px-6">{children}</div>
      </main>

      {/* Pastki pleyer paneli */}
      <footer className="fixed inset-x-0 bottom-0 z-30 flex h-[80px] items-center gap-4 bg-[var(--sp-black)] px-4 select-none">
        <div className="flex min-w-0 flex-1 items-center gap-3 lg:w-[30%] lg:flex-none">
          <span className="h-14 w-14 shrink-0 overflow-hidden rounded">
            <AuthorPhoto
              className="h-full w-full"
              alt=""
              fallback={<Cover lesson={current} className="h-full w-full text-lg" />}
            />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-[14px] text-white">{current.title}</span>
            <span className="block truncate text-[12px] text-[var(--skin-muted)]">
              darslik · Dars {pad(current.order)}
            </span>
          </span>
        </div>

        <div className="hidden min-w-0 flex-1 flex-col items-center gap-1 md:flex">
          <div className="flex items-center gap-5 text-[var(--skin-muted)]" aria-hidden>
            <IconShuffle />
            <IconPrev />
            <button
              type="button"
              onClick={startReading}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black"
              tabIndex={-1}
            >
              <IconPlay className="h-4 w-4" />
            </button>
            <IconNext />
            <IconRepeat />
          </div>
          <div className="flex w-full max-w-[640px] items-center gap-2 text-[11px] text-[var(--skin-muted)] tabular-nums">
            <span className="w-12 text-right">{fmt(pct * total)}</span>
            <div className="group relative h-1 flex-1 rounded-full bg-[#4d4d4d]">
              <div
                className="h-full rounded-full bg-white group-hover:bg-[var(--sp-green)]"
                style={{ width: `${pct * 100}%` }}
              />
            </div>
            <span className="w-12">{fmt(total)}</span>
          </div>
        </div>

        <div className="hidden w-[30%] items-center justify-end gap-3 pr-24 text-[var(--skin-muted)] lg:flex" aria-hidden>
          <IconDevice />
          <IconSpeaker />
          <span className="h-1 w-24 rounded-full bg-[#4d4d4d]">
            <span className="block h-full w-2/3 rounded-full bg-white" />
          </span>
        </div>

        {/* Mobil: faqat play tugmasi */}
        <button
          type="button"
          onClick={startReading}
          aria-label="O'qishni boshlash"
          className="mr-20 flex h-9 w-9 items-center justify-center text-white md:hidden"
        >
          <IconPlay className="h-6 w-6" />
        </button>
        {/* Mobil: yuqori chiziq — progress */}
        <span aria-hidden className="absolute inset-x-0 top-0 h-0.5 bg-[#4d4d4d] md:hidden">
          <span className="block h-full bg-white" style={{ width: `${pct * 100}%` }} />
        </span>
      </footer>

      {/* Mobil: kutubxona paneli */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[320px] max-w-[88vw] flex-col bg-[var(--skin-bg)] shadow-2xl">
            <div className="flex items-center gap-3 px-5 pt-5 pb-3">
              <IconLibrary />
              <span className="font-bold">Kutubxonangiz</span>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="ml-auto flex h-8 w-8 items-center justify-center rounded-full hover:bg-[var(--sp-hover)]"
              >
                ×
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-24">
              {library(() => setDrawerOpen(false))}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}

/* Ikonkalar — soddalashtirilgan, rasmiy emas */
const I = (d: string, cls = "h-5 w-5") =>
  function Icon() {
    return (
      <svg viewBox="0 0 24 24" className={cls} fill="none" aria-hidden>
        <path d={d} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  };
const IconLibrary = I("M4 4v16M9 4v16M14 5l5 14");
const IconChevron = I("M15 6l-6 6 6 6", "h-4 w-4");
const IconSearch = I("M11 17.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM16 16l4 4");
const IconDownload = I("M12 4v11M7 11l5 5 5-5M5 20h14", "h-7 w-7");
const IconDots = I("M5 12h.01M12 12h.01M19 12h.01", "h-7 w-7");
const IconShuffle = I("M4 7h3l10 10h3M4 17h3l3-3M14 10l3-3h3M18 5l2 2-2 2M18 15l2 2-2 2", "h-4 w-4");
const IconPrev = I("M6 5v14M18 6l-9 6 9 6z", "h-4 w-4");
const IconNext = I("M18 5v14M6 6l9 6-9 6z", "h-4 w-4");
const IconRepeat = I("M4 12V9a3 3 0 0 1 3-3h11l-3-3M20 12v3a3 3 0 0 1-3 3H6l3 3", "h-4 w-4");
const IconDevice = I("M4 5h16v10H4zM9 19h6", "h-4 w-4");
const IconSpeaker = I("M4 10v4h4l5 4V6L8 10H4zM16 9a4 4 0 0 1 0 6", "h-4 w-4");
function IconPlay({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M8 5v14l11-7z" />
    </svg>
  );
}
function IconHeart({ filled }: { filled: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="h-7 w-7" fill={filled ? "currentColor" : "none"} aria-hidden>
      <path
        d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
    </svg>
  );
}
