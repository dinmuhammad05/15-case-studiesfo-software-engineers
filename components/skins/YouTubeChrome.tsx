"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";
import { AuthorPhoto } from "@/components/AuthorPhoto";

const pad = (n: number) => String(n).padStart(2, "0");

/** Soniyalarni YouTube uslubida: 3:05:00 yoki 12:07 */
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

/**
 * YouTube skini: tomosha sahifasi. Pleyerning qizil chizig'i — o'qish progressi,
 * vaqt hisoblagichi — darsning "davomiyligi" bo'yicha. O'ngda "Keyingi" ro'yxati.
 */
export function YouTubeChrome({ slug, children }: { slug: string; children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const current = lessons.find((l) => l.slug === slug);
  const pct = useScrollProgress();
  const total = (current?.minutes ?? 60) * 60;

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

  const upNext = lessons.filter((l) => l.slug !== slug);

  return (
    <div className="min-h-screen">
      {/* Yuqori panel */}
      <header className="sticky top-0 z-30 select-none bg-[var(--skin-bg)]">
        <div className="flex h-14 items-center gap-2 px-2 sm:px-4">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Darslar ro'yxatini ochish"
            className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-[var(--yt-chip)]"
          >
            <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
          <Link href="/" className="flex items-center gap-1 pr-2" title="Bosh sahifa">
            <Logo />
            <span className="text-[19px] font-bold tracking-tight">darslik</span>
            <sup className="-mt-3 text-[10px] text-[var(--skin-muted)]">UZ</sup>
          </Link>

          <div aria-hidden className="mx-auto hidden w-full max-w-[640px] items-center gap-3 md:flex">
            <div className="flex h-10 min-w-0 flex-1 items-center rounded-full border border-[#cccccc] bg-white pl-4">
              <span className="min-w-0 flex-1 truncate text-[15px] text-[var(--skin-muted)]">
                Tizim dizayni darslari
              </span>
              <span className="flex h-full w-16 items-center justify-center rounded-r-full border-l border-[#d3d3d3] bg-[#f8f8f8]">
                <IconSearch />
              </span>
            </div>
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[var(--yt-chip)]">
              <IconMic />
            </span>
          </div>

          <span aria-hidden className="ml-auto h-8 w-8 shrink-0 overflow-hidden rounded-full md:ml-0">
            <AuthorPhoto
              className="h-full w-full"
              fallback={
                <span className="flex h-full w-full items-center justify-center bg-[#7b1fa2] text-[13px] font-medium text-white">
                  D
                </span>
              }
            />
          </span>
        </div>
        <ReadingProgress />
      </header>

      <div className="mx-auto flex max-w-[1750px] justify-center gap-6 px-3 pt-4 pb-16 sm:px-6">
        {/* Asosiy ustun — kengligi pleyer ekranga sig'adigan qilib cheklangan */}
        <div
          className="min-w-0 flex-1"
          style={{ maxWidth: "max(640px, calc((100vh - 280px) * 16 / 9))" }}
        >
          {/* Pleyer */}
          <div className="relative aspect-video w-full overflow-hidden rounded-xl bg-black select-none">
            <div
              aria-hidden
              className="absolute inset-0 opacity-60"
              style={{
                background: `radial-gradient(ellipse at 30% 40%, ${current?.accent ?? "#ff0000"}55, transparent 60%), radial-gradient(ellipse at 80% 70%, #3ea6ff22, transparent 55%)`,
              }}
            />
            {/* Taqdimotchi — muallif portreti (fayl bo'lmasa hech narsa ko'rinmaydi) */}
            <div
              aria-hidden
              className="absolute inset-y-0 right-0 w-[42%] [mask-image:linear-gradient(to_left,black_55%,transparent)]"
            >
              <AuthorPhoto className="h-full w-full opacity-90" position="50% 20%" alt="" fallback={null} />
            </div>
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 px-6 pb-10 text-center sm:items-start sm:pr-[40%] sm:pb-0 sm:pl-[7%] sm:text-left">
              <span className="hidden font-[family-name:var(--skin-mono)] text-sm tracking-widest text-white/60 uppercase sm:block">
                Dars {pad(current?.order ?? 8)} · tizim dizayni
              </span>
              <span className="max-w-3xl text-2xl font-bold text-white sm:text-4xl lg:text-5xl">
                {current?.title}
              </span>
              <button
                type="button"
                onClick={startReading}
                aria-label="O'qishni boshlash"
                className="mt-2 hidden h-12 w-[68px] items-center justify-center rounded-2xl bg-[var(--yt-red)] transition-transform hover:scale-105 sm:flex"
              >
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="#fff" aria-hidden>
                  <path d="M8 5v14l11-7z" />
                </svg>
              </button>
            </div>

            {/* Boshqaruv paneli */}
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent px-3 pt-8 pb-2">
              <div className="relative h-1 w-full rounded bg-white/25">
                <div className="h-full rounded bg-[var(--yt-red)]" style={{ width: `${pct * 100}%` }} />
                <span
                  className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--yt-red)]"
                  style={{ left: `${pct * 100}%` }}
                />
              </div>
              <div className="mt-2 flex items-center gap-3 text-[13px] text-white">
                <button type="button" onClick={startReading} aria-label="O'qishni boshlash" className="p-1">
                  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="#fff" aria-hidden>
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </button>
                <IconVolume />
                <span className="font-[family-name:var(--skin-mono)] tabular-nums">
                  {fmt(pct * total)} / {fmt(total)}
                </span>
                <span className="ml-auto flex items-center gap-3" aria-hidden>
                  <span className="rounded border border-white/80 px-1 text-[10px] font-bold">CC</span>
                  <span className="relative">
                    <IconGear />
                    <span className="absolute -top-1 -right-2 rounded bg-[var(--yt-red)] px-0.5 text-[8px] font-bold">
                      HD
                    </span>
                  </span>
                  <IconFull />
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4">{children}</div>
        </div>

        {/* O'ng: Keyingi */}
        <aside className="hidden w-[400px] shrink-0 xl:block">
          <div className="mb-3 flex gap-2 overflow-hidden" aria-hidden>
            {["Hammasi", "Tizim dizayni", "darslik", "Tayyor"].map((c, i) => (
              <span
                key={c}
                className={`shrink-0 rounded-lg px-3 py-1.5 text-[14px] font-medium ${
                  i === 0 ? "bg-[var(--skin-text)] text-[var(--skin-bg)]" : "bg-[var(--yt-chip)]"
                }`}
              >
                {c}
              </span>
            ))}
          </div>
          <div className="space-y-2">
            {upNext.map((l) => (
              <UpNextCard key={l.slug} lesson={l} />
            ))}
          </div>
        </aside>
      </div>

      {/* Panel (barcha o'lchamlarda) */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[260px] max-w-[85vw] flex-col bg-[var(--skin-bg)] shadow-2xl">
            <div className="flex h-14 shrink-0 items-center gap-2 px-4">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="-ml-2 flex h-10 w-10 items-center justify-center rounded-full hover:bg-[var(--yt-chip)]"
              >
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden>
                  <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </button>
              <Logo />
              <span className="text-[19px] font-bold tracking-tight">darslik</span>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-6">
              <div className="px-3 pt-2 pb-1 text-[16px] font-medium">Darslar</div>
              {lessons.map((l) =>
                l.status === "tayyor" ? (
                  <Link
                    key={l.slug}
                    href={`/darslar/${l.slug}/`}
                    onClick={() => setDrawerOpen(false)}
                    className={`flex items-center gap-4 rounded-lg px-3 py-2 text-[14px] hover:bg-[var(--yt-chip)] ${
                      l.slug === slug ? "bg-[var(--yt-chip)] font-medium" : ""
                    }`}
                  >
                    <span className="w-5 text-center text-[var(--skin-muted)]">{pad(l.order)}</span>
                    <span className="min-w-0 truncate">{l.title}</span>
                  </Link>
                ) : (
                  <span
                    key={l.slug}
                    className="flex cursor-default items-center gap-4 rounded-lg px-3 py-2 text-[14px] opacity-40"
                  >
                    <span className="w-5 text-center">{pad(l.order)}</span>
                    <span className="min-w-0 truncate">{l.title}</span>
                  </span>
                ),
              )}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}

/** Kanal qatori — sarlavha ostida. Obuna tugmasi faqat bezak holati. */
export function YouTubeChannelRow() {
  const [subscribed, setSubscribed] = useState(false);
  return (
    <div className="mb-6 flex flex-wrap items-center gap-3 select-none">
      <span className="h-10 w-10 shrink-0 overflow-hidden rounded-full">
        <AuthorPhoto
          className="h-full w-full"
          fallback={
            <span className="flex h-full w-full items-center justify-center bg-[var(--yt-red)] text-sm font-bold text-white">
              DL
            </span>
          }
        />
      </span>
      <div className="mr-2">
        <div className="text-[16px] font-medium">darslik</div>
        <div className="text-[12px] text-[var(--skin-muted)]">tizim dizayni · o‘zbek tilida</div>
      </div>
      <button
        type="button"
        onClick={() => setSubscribed((v) => !v)}
        className={`rounded-full px-4 py-2 text-[14px] font-medium ${
          subscribed ? "bg-[var(--yt-chip)] text-[var(--skin-text)]" : "bg-[var(--skin-text)] text-[var(--skin-bg)]"
        }`}
      >
        {subscribed ? "Obuna bo‘lingan" : "Obuna bo‘lish"}
      </button>
    </div>
  );
}

function UpNextCard({ lesson }: { lesson: (typeof lessons)[number] }) {
  const ready = lesson.status === "tayyor";
  const body = (
    <>
      <span
        className="relative flex aspect-video w-[168px] shrink-0 items-center justify-center overflow-hidden rounded-lg"
        style={{ background: `linear-gradient(135deg, ${lesson.accent}, #111 85%)` }}
      >
        <span className="text-3xl font-black text-white/90">{pad(lesson.order)}</span>
        <span className="absolute right-1 bottom-1 rounded bg-black/80 px-1 text-[12px] font-medium text-white">
          {ready ? fmt(lesson.minutes * 60) : "tez orada"}
        </span>
      </span>
      <span className="min-w-0 flex-1">
        <span className="line-clamp-2 text-[14px] leading-5 font-medium">{lesson.title}</span>
        <span className="mt-1 block text-[12px] text-[var(--skin-muted)]">darslik</span>
        <span className="block text-[12px] text-[var(--skin-muted)]">
          {ready ? `${lesson.level} · tayyor` : "rejada"}
        </span>
      </span>
    </>
  );
  return ready ? (
    <Link href={`/darslar/${lesson.slug}/`} className="flex gap-2 rounded-lg hover:bg-[var(--skin-surface-2)]">
      {body}
    </Link>
  ) : (
    <span className="flex cursor-default gap-2 opacity-45">{body}</span>
  );
}

/* Rasmiy logotip emas — soddalashtirilgan belgi va ikonkalar */
function Logo() {
  return (
    <svg viewBox="0 0 30 21" className="h-5 w-[29px]" aria-hidden>
      <rect width="30" height="21" rx="6" fill="#ff0000" />
      <path d="M12 6v9l8-4.5z" fill="#fff" />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16 16l4.5 4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function IconMic() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function IconVolume() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path d="M4 9v6h4l5 4V5L8 9H4z" fill="#fff" />
      <path d="M16 8.5a5 5 0 0 1 0 7" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function IconGear() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="3" stroke="#fff" strokeWidth="1.8" />
      <path
        d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"
        stroke="#fff"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
function IconFull() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
