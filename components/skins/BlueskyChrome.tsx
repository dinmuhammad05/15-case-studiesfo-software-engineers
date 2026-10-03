"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

type Section = { id: string; title: string };

/** Bo'limlar (h2), skroll progressi va o'qilgan bo'limlar soni. */
function useReading() {
  const [sections, setSections] = useState<Section[]>([]);
  const [state, setState] = useState({ pct: 0, current: 0 });
  useEffect(() => {
    const heads = Array.from(document.querySelectorAll<HTMLElement>(".lesson-prose h2"));
    setSections(heads.map((h) => ({ id: h.id, title: (h.textContent ?? "").replace(/^\d+\.\s*/, "") })));
    const on = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(1, window.scrollY / max) : 0;
      const current = heads.filter((h) => h.getBoundingClientRect().top < 140).length;
      setState({ pct, current: pct >= 0.995 ? heads.length : current });
    };
    on();
    window.addEventListener("scroll", on, { passive: true });
    window.addEventListener("resize", on);
    return () => {
      window.removeEventListener("scroll", on);
      window.removeEventListener("resize", on);
    };
  }, []);
  return { sections, ...state };
}

const feedName = (slug: string) => `darslar/${slug}`;
const scrollToId = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

const NAV: [string, (p: { className?: string }) => ReactNode, boolean][] = [
  ["Bosh sahifa", HomeIcon, false],
  ["Qidiruv", SearchIcon, false],
  ["Bildirishnomalar", BellIcon, false],
  ["Feed'lar", HashIcon, true],
  ["Profil", UserIcon, false],
];

/**
 * Bluesky skini: ochiq ijtimoiy tarmoq ilovasi. Dars — bitta post (muallif
 * handle'i — domen), bo'limlar — o'quvchining firehose'idagi hodisalar, darslar
 * — maxsus feed'lar. Progress — postdagi "like".
 */
export function BlueskyChrome({
  slug,
  header,
  children,
}: {
  slug: string;
  header: ReactNode;
  children: ReactNode;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const lesson = lessons.find((l) => l.slug === slug)!;
  const { sections, pct, current } = useReading();
  const idx = lessons.findIndex((l) => l.slug === slug);
  const next = lessons.slice(idx + 1).find((l) => l.status === "tayyor");
  const total = sections.length;
  const left = Math.max(0, Math.round(lesson.minutes * (1 - pct)));
  const done = pct >= 0.995;
  const liked = pct > 0.02;
  const readyCount = lessons.filter((l) => l.status === "tayyor").length;

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

  // Firehose: o'qilgan har bo'lim — bitta commit hodisasi (eng yangisi tepada)
  const events = sections
    .slice(0, current)
    .map((s, i) => ({ ...s, i, seq: 1_000_000 + (i + 1) * 37 }))
    .reverse()
    .slice(0, 6);

  return (
    <div className="mx-auto flex min-h-screen max-w-[1320px] justify-center">
      {/* Chap navigatsiya */}
      <aside className="sticky top-0 hidden h-screen w-[230px] shrink-0 flex-col px-4 py-5 select-none lg:flex">
        <Link href="/" className="mb-6 flex items-center gap-2 px-2" aria-label="Bosh sahifa">
          <SkyIcon />
          <span className="text-[18px] font-bold tracking-tight">darslik</span>
        </Link>
        <nav className="space-y-1" aria-label="Bo'limlar">
          {NAV.map(([label, Icon, active]) => (
            <button
              key={label}
              type="button"
              onClick={() => (label === "Feed'lar" ? setMenuOpen(true) : undefined)}
              className={`flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left text-[17px] hover:bg-[var(--skin-surface-2)] ${
                active ? "font-bold" : "text-[var(--skin-text)]"
              }`}
            >
              <Icon className="h-6 w-6" />
              {label}
            </button>
          ))}
        </nav>
        <button
          type="button"
          onClick={startReading}
          className="mt-6 h-11 rounded-full bg-[var(--skin-accent)] text-[15px] font-semibold text-white hover:brightness-110"
        >
          {done ? "O‘qildi ✓" : liked ? "Davom ettirish" : "O‘qishni boshlash"}
        </button>
        <div className="mt-auto flex items-center gap-2 px-1 text-[13px]">
          <span className="h-9 w-9 shrink-0 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
            <AuthorPhoto
              className="h-full w-full"
              fallback={<span className="flex h-full w-full items-center justify-center text-[13px]">D</span>}
            />
          </span>
          <span className="min-w-0">
            <span className="block truncate font-semibold">Dinmuhammad</span>
            <span className="block truncate text-[var(--skin-muted)]">@dinmuhammad.uz</span>
          </span>
        </div>
      </aside>

      {/* Markaziy ustun */}
      <div className="min-w-0 flex-1 border-x border-[var(--skin-border)] lg:max-w-[780px]">
        <header className="sticky top-0 z-30 border-b border-[var(--skin-border)] bg-white/95 backdrop-blur select-none">
          <div className="h-[3px] bg-transparent" aria-hidden>
            <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${pct * 100}%` }} />
          </div>
          <div className="flex h-12 items-center gap-3 px-4">
            <Link href="/" className="lg:hidden" aria-label="Bosh sahifa">
              <SkyIcon />
            </Link>
            <span className="text-[16px] font-bold">Post</span>
            <button
              type="button"
              onClick={() => setMenuOpen(true)}
              className="ml-auto rounded-full border border-[var(--skin-border)] px-3 py-1 text-[13px] font-medium hover:bg-[var(--skin-surface-2)]"
            >
              Feed&apos;lar
            </button>
          </div>
          <div className="flex text-[14px]">
            {["Following", "Discover", "Darslar"].map((t) => (
              <span
                key={t}
                className={`flex-1 py-2.5 text-center ${t === "Darslar" ? "font-semibold" : "text-[var(--skin-muted)]"}`}
              >
                <span className={t === "Darslar" ? "border-b-[3px] border-[var(--skin-accent)] pb-2" : ""}>{t}</span>
              </span>
            ))}
          </div>
        </header>

        <main className="pb-28 lg:pb-12">
          {/* Post sarlavhasi */}
          <div className="border-b border-[var(--skin-border)] px-4 pt-4 pb-3 sm:px-6">
            <div className="flex items-center gap-3">
              <span className="h-12 w-12 shrink-0 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
                <AuthorPhoto
                  className="h-full w-full"
                  fallback={<span className="flex h-full w-full items-center justify-center">D</span>}
                />
              </span>
              <div className="min-w-0 flex-1 leading-tight">
                <div className="truncate text-[16px] font-bold">Dinmuhammad</div>
                <div className="truncate text-[14px] text-[var(--skin-muted)]">@dinmuhammad.uz · bepul darslik</div>
              </div>
              <span className="shrink-0 rounded-full bg-[var(--bs-soft)] px-3 py-1 text-[13px] font-semibold text-[var(--skin-accent)]">
                + Obuna
              </span>
            </div>
            <div className="mt-4 [&_h1]:text-[28px] [&_h1]:leading-tight sm:[&_h1]:text-[34px] [&_header]:mb-4">{header}</div>
            <div className="flex items-center justify-between border-t border-[var(--skin-border)] pt-3 text-[14px] text-[var(--skin-muted)]">
              <span className="flex items-center gap-1.5" title="Bo'limlar">
                <ReplyIcon className="h-5 w-5" />
                {current}/{total || "—"}
              </span>
              <span className="flex items-center gap-1.5" title="Qolgan vaqt">
                <RepostIcon className="h-5 w-5" />
                {left} daq
              </span>
              <span
                className={`flex items-center gap-1.5 ${liked ? "text-[var(--bs-like)]" : ""}`}
                title="O'qilgan qism"
              >
                <HeartIcon className="h-5 w-5" filled={liked} />
                {Math.round(pct * 100)}%
              </span>
              <button type="button" onClick={() => setMenuOpen(true)} className="flex items-center gap-1.5 hover:text-[var(--skin-accent)]">
                <HashIcon className="h-5 w-5" />
                <span className="hidden sm:inline">Feed&apos;lar</span>
              </button>
            </div>
          </div>

          <div className="px-4 pb-8 sm:px-6">{children}</div>
        </main>
      </div>

      {/* O'ng ustun */}
      <aside className="sticky top-0 hidden h-screen w-[300px] shrink-0 flex-col gap-4 overflow-y-auto px-4 py-4 xl:flex">
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          className="flex h-10 items-center gap-2 rounded-lg bg-[var(--skin-surface-2)] px-3 text-[14px] text-[var(--skin-muted)]"
        >
          <SearchIcon className="h-4 w-4" />
          Darslarni qidirish
        </button>

        <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)]">
          <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-4 py-3">
            <span className="text-[15px] font-bold">Firehose</span>
            <span className="flex items-center gap-1.5 text-[12px] text-[var(--bs-green)]">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--bs-green)]" aria-hidden />
              jonli
            </span>
          </div>
          <ul className="divide-y divide-[var(--skin-border)] font-[family-name:var(--skin-mono)] text-[11.5px]">
            {events.length ? (
              events.map((e) => (
                <li key={e.id || e.i}>
                  <button
                    type="button"
                    onClick={() => scrollToId(e.id)}
                    className="block w-full px-4 py-2 text-left hover:bg-[var(--skin-surface-2)]"
                  >
                    <span className="text-[var(--skin-muted)]">#{e.seq} </span>
                    <span className="text-[var(--skin-accent)]">#commit</span>
                    <span className="mt-0.5 block truncate font-[family-name:var(--skin-font)] text-[13px] text-[var(--skin-text)]">
                      §{e.i + 1} · {e.title}
                    </span>
                  </button>
                </li>
              ))
            ) : (
              <li className="px-4 py-3 font-[family-name:var(--skin-font)] text-[13px] text-[var(--skin-muted)]">
                Hali hodisa yo‘q — o‘qishni boshlang, har bo‘lim bitta commit.
              </li>
            )}
          </ul>
        </div>

        <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)]">
          <div className="border-b border-[var(--skin-border)] px-4 py-3 text-[15px] font-bold">
            Feed&apos;lar <span className="font-normal text-[var(--skin-muted)]">· {readyCount} tayyor</span>
          </div>
          <ul className="max-h-[40vh] overflow-y-auto py-1 text-[14px]">
            {lessons.map((l) => {
              const ready = l.status === "tayyor";
              const active = l.slug === slug;
              const row = (
                <>
                  <span
                    className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-[12px] font-bold text-white ${
                      ready ? "" : "opacity-40"
                    }`}
                    style={{ background: l.accent }}
                  >
                    #
                  </span>
                  <span className={`min-w-0 flex-1 truncate ${active ? "font-semibold" : ready ? "" : "text-[var(--skin-muted)]"}`}>
                    {l.title}
                  </span>
                </>
              );
              return (
                <li key={l.slug}>
                  {ready ? (
                    <Link
                      href={`/darslar/${l.slug}/`}
                      className={`flex items-center gap-2.5 px-4 py-1.5 hover:bg-[var(--skin-surface-2)] ${active ? "bg-[var(--bs-soft)]" : ""}`}
                    >
                      {row}
                    </Link>
                  ) : (
                    <span className="flex items-center gap-2.5 px-4 py-1.5">{row}</span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>

        {next ? (
          <div className="px-1 text-[13px] text-[var(--skin-muted)]">
            Keyingi feed:{" "}
            <Link href={`/darslar/${next.slug}/`} className="font-semibold text-[var(--skin-accent)] hover:underline">
              {next.title}
            </Link>
          </div>
        ) : null}
      </aside>

      {/* Mobil: pastki panel */}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--skin-border)] bg-white lg:hidden">
        <div className="h-[2px] bg-[var(--skin-surface-2)]" aria-hidden>
          <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${pct * 100}%` }} />
        </div>
        <div className="flex items-center gap-3 px-4 py-2.5 pr-28 sm:px-6">
          <span className={`flex items-center gap-1.5 text-[14px] font-semibold ${liked ? "text-[var(--bs-like)]" : "text-[var(--skin-muted)]"}`}>
            <HeartIcon className="h-5 w-5" filled={liked} />
            {Math.round(pct * 100)}%
          </span>
          <span className="min-w-0 flex-1 truncate text-[13px] text-[var(--skin-muted)]">
            §{current}/{total || "—"} · {left} daq qoldi
          </span>
          <button
            type="button"
            onClick={startReading}
            className="h-9 shrink-0 rounded-full bg-[var(--skin-accent)] px-5 text-[14px] font-semibold text-white"
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Feed'lar ro'yxati */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/40" />
          <div className="absolute inset-x-2 top-14 max-h-[80vh] overflow-y-auto rounded-2xl bg-white shadow-2xl sm:inset-x-auto sm:left-1/2 sm:w-[560px] sm:-translate-x-1/2">
            <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-5 py-4">
              <div>
                <div className="text-[17px] font-bold">Feed&apos;lar ({lessons.length})</div>
                <div className="text-[13px] text-[var(--skin-muted)]">Har bir dars — alohida maxsus feed</div>
              </div>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label="Yopish"
                className="flex h-8 w-8 items-center justify-center rounded-full text-[20px] text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
              >
                ×
              </button>
            </div>
            <ul className="divide-y divide-[var(--skin-border)]">
              {lessons.map((l) => {
                const ready = l.status === "tayyor";
                const active = l.slug === slug;
                const row = (
                  <>
                    <span
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-[14px] font-bold text-white ${ready ? "" : "opacity-40"}`}
                      style={{ background: l.accent }}
                    >
                      #
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className={`block truncate text-[15px] font-semibold ${ready ? "" : "text-[var(--skin-muted)]"}`}>{l.title}</span>
                      <span className="block truncate font-[family-name:var(--skin-mono)] text-[12px] text-[var(--skin-muted)]">
                        {feedName(l.slug)}
                      </span>
                    </span>
                    <span
                      className={`shrink-0 rounded-full px-2.5 py-0.5 text-[12px] font-medium ${
                        ready ? "bg-[var(--bs-soft)] text-[var(--skin-accent)]" : "bg-[var(--skin-surface-2)] text-[var(--skin-muted)]"
                      }`}
                    >
                      {ready ? `${l.minutes} daq` : "tez orada"}
                    </span>
                  </>
                );
                return (
                  <li key={l.slug}>
                    {ready ? (
                      <Link
                        href={`/darslar/${l.slug}/`}
                        onClick={() => setMenuOpen(false)}
                        className={`flex items-center gap-3 px-5 py-2.5 hover:bg-[var(--skin-surface-2)] ${active ? "bg-[var(--bs-soft)]" : ""}`}
                      >
                        {row}
                      </Link>
                    ) : (
                      <span className="flex items-center gap-3 px-5 py-2.5">{row}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
}

/* ---------------------------------------------------------------- belgilar
   Soddalashtirilgan belgilar; Bluesky logotipi emas. */
function SkyIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-7 w-7" aria-hidden fill="none">
      <circle cx="12" cy="12" r="10" fill="#0a7aff" />
      <path d="M6.5 14.5c1.5-3 3.5-4.5 5.5-4.5s4 1.5 5.5 4.5" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="8" r="1.3" fill="#fff" />
    </svg>
  );
}

function Svg({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  );
}
function HomeIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <path d="M3 10.5 12 3l9 7.5V21h-6v-6H9v6H3z" />
    </Svg>
  );
}
function SearchIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </Svg>
  );
}
function BellIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <path d="M6 9a6 6 0 1 1 12 0c0 6 2 7 2 7H4s2-1 2-7" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </Svg>
  );
}
function HashIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <path d="M5 9h14M5 15h14M10 3 8 21M16 3l-2 18" />
    </Svg>
  );
}
function UserIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" />
    </Svg>
  );
}
function ReplyIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <path d="M21 12a8 8 0 0 1-11.5 7.2L4 21l1.8-5.5A8 8 0 1 1 21 12z" />
    </Svg>
  );
}
function RepostIcon({ className }: { className?: string }) {
  return (
    <Svg className={className}>
      <path d="M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4M21 13v2a3 3 0 0 1-3 3H3" />
    </Svg>
  );
}
function HeartIcon({ className, filled }: { className?: string; filled?: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
      <path d="M12 20s-7-4.4-9-9a4.8 4.8 0 0 1 9-3 4.8 4.8 0 0 1 9 3c-2 4.6-9 9-9 9z" />
    </svg>
  );
}
