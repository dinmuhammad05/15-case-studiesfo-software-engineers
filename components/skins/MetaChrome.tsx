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

const fnName = (slug: string) => `darslar.${slug.replace(/-/g, "_")}`;
const scrollToId = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

/**
 * Meta Serverless skini: ichki funksiyalar konsoli. Dars — funksiya; har h2
 * bo'lim — navbatdagi chaqiruv (bajarildi / bajarilmoqda / navbatda); o'qish
 * progressi — ishchilar bandligi; darslar — konsoldagi funksiyalar ro'yxati.
 */
export function MetaChrome({
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
  const running = done ? -1 : Math.max(0, current - 1);
  const executed = done ? total : Math.max(0, current - 1);
  const queued = Math.max(0, total - executed - (done ? 0 : current > 0 ? 1 : 0));
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

  // Navbat oynasi: joriy chaqiruv atrofidagi bo'limlar
  const from = Math.max(0, Math.min(Math.max(0, current - 3), Math.max(0, total - 8)));
  const windowRows = sections.slice(from, from + 8).map((s, k) => ({ ...s, i: from + k }));

  return (
    <div className="min-h-screen lg:flex">
      {/* Chap panel */}
      <aside className="sticky top-0 hidden h-screen w-[240px] shrink-0 flex-col overflow-y-auto bg-[var(--xf-nav)] text-white/80 select-none lg:flex">
        <Link href="/" className="flex items-center gap-2 px-5 pt-5 pb-4 text-white" aria-label="Bosh sahifa">
          <LambdaIcon />
          <span className="text-[17px] font-bold tracking-tight">darslik</span>
          <span className="ml-auto rounded bg-white/10 px-1.5 py-0.5 font-[family-name:var(--skin-mono)] text-[10px]">faas</span>
        </Link>
        <div className="mx-4 mb-4 rounded-md bg-[var(--xf-nav-2)] px-3 py-2 text-[13px]">
          <div className="text-[11px] tracking-wide text-white/50 uppercase">Ishchilar hovuzi</div>
          <div className="flex items-center gap-2 font-medium text-white">
            <span className="h-2 w-2 rounded-full bg-[var(--xf-ok)]" aria-hidden />
            tizim-dizayni
          </div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/10" aria-hidden>
            <div className="h-full bg-[var(--xf-ok)]" style={{ width: `${Math.round(pct * 100)}%` }} />
          </div>
          <div className="mt-1 text-[12px] text-white/50">bandlik {Math.round(pct * 100)}%</div>
        </div>
        <div className="px-5 pb-2 text-[11px] tracking-wide text-white/40 uppercase">Funksiyalar ({readyCount})</div>
        <ul className="flex-1 px-2 pb-6 font-[family-name:var(--skin-mono)] text-[12px]">
          {lessons.map((l) => {
            const ready = l.status === "tayyor";
            const active = l.slug === slug;
            return (
              <li key={l.slug}>
                {ready ? (
                  <Link
                    href={`/darslar/${l.slug}/`}
                    className={`flex items-center gap-2 rounded-md px-3 py-1 ${
                      active ? "bg-[var(--skin-accent)] text-white" : "hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${active ? "bg-white" : "bg-[var(--xf-ok)]"}`} aria-hidden />
                    <span className="truncate">{fnName(l.slug)}</span>
                  </Link>
                ) : (
                  <span className="flex items-center gap-2 px-3 py-1 text-white/25">
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-white/20" aria-hidden />
                    <span className="truncate">{fnName(l.slug)}</span>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </aside>

      <div className="min-w-0 flex-1">
        {/* Yuqori panel */}
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[var(--skin-border)] bg-white/95 px-4 backdrop-blur select-none sm:px-6">
          <Link href="/" className="flex items-center gap-2 lg:hidden" aria-label="Bosh sahifa">
            <LambdaIcon dark />
            <span className="text-[16px] font-bold">darslik</span>
          </Link>
          <nav className="hidden min-w-0 items-center gap-2 text-[14px] text-[var(--skin-muted)] sm:flex" aria-label="Yo'l">
            <span>faas</span>
            <span aria-hidden>/</span>
            <button type="button" onClick={() => setMenuOpen(true)} className="hover:text-[var(--skin-text)]">
              funksiyalar
            </button>
            <span aria-hidden>/</span>
            <span className="truncate font-[family-name:var(--skin-mono)] text-[var(--skin-text)]">{fnName(slug)}</span>
          </nav>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="ml-auto rounded-md border border-[var(--skin-border)] px-3 py-1.5 text-[13px] font-medium hover:bg-[var(--skin-surface-2)]"
          >
            Barcha funksiyalar
          </button>
          <span className="h-8 w-8 shrink-0 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
            <AuthorPhoto
              className="h-full w-full"
              fallback={<span className="flex h-full w-full items-center justify-center text-[12px]">D</span>}
            />
          </span>
        </header>

        <main className="mx-auto max-w-[1360px] px-3 pt-5 pb-32 sm:px-6 lg:pb-16">
          {/* Funksiya kartasi */}
          <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white p-5 sm:p-6">
            <div className="mb-3 flex flex-wrap items-center gap-2 font-[family-name:var(--skin-mono)] text-[12px]">
              <span className="rounded bg-[#e3f5e7] px-2 py-0.5 font-medium text-[#1e7a36]">DEPLOYED</span>
              <span className="text-[var(--skin-muted)]">{fnName(slug)} · runtime: o‘zbek tili · muallif: Dinmuhammad · bepul</span>
            </div>
            <div className="[&_h1]:text-[28px] [&_h1]:leading-tight sm:[&_h1]:text-[34px] [&_header]:mb-5">{header}</div>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <Stat label="Bajarilgan chaqiruvlar" value={`${executed} / ${total || "—"}`} tone={done ? "ok" : undefined} />
              <Stat label="Navbatda" value={total ? String(queued) : "—"} />
              <Stat label="Muddatgacha" value={`${left} daq`} tone={left === 0 ? "ok" : "warn"} />
              <Stat label="Ishchilar bandligi" value={`${Math.round(pct * 100)}%`} tone="run" />
            </div>
          </div>

          <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_330px]">
            <div className="min-w-0 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white px-4 pb-8 sm:px-8">
              {children}
            </div>

            <aside className="hidden xl:block">
              <div className="sticky top-[76px] space-y-4">
                <div className="overflow-hidden rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white">
                  <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-4 py-3">
                    <span className="text-[15px] font-semibold">Chaqiruvlar navbati</span>
                    <span className="font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">EDF</span>
                  </div>
                  <ul className="divide-y divide-[var(--skin-border)]">
                    {windowRows.map((s) => {
                      const state = done || s.i < executed ? "ok" : s.i === running && current > 0 ? "run" : "wait";
                      return (
                        <li key={s.id || s.i}>
                          <button
                            type="button"
                            onClick={() => scrollToId(s.id)}
                            className={`flex w-full items-center gap-2.5 px-4 py-2 text-left hover:bg-[var(--skin-surface-2)] ${
                              state === "run" ? "bg-[var(--xf-soft)]" : ""
                            }`}
                          >
                            <span
                              className={`w-[82px] shrink-0 rounded px-1.5 py-0.5 text-center font-[family-name:var(--skin-mono)] text-[10.5px] font-medium ${
                                state === "ok"
                                  ? "bg-[#e3f5e7] text-[#1e7a36]"
                                  : state === "run"
                                    ? "bg-[var(--skin-accent)] text-white"
                                    : "bg-[var(--skin-surface-2)] text-[var(--skin-muted)]"
                              }`}
                            >
                              {state === "ok" ? "bajarildi" : state === "run" ? "ishlamoqda" : "navbatda"}
                            </span>
                            <span className="min-w-0 flex-1 truncate text-[13px]">
                              <span className="font-[family-name:var(--skin-mono)] text-[var(--skin-muted)]">#{s.i + 1} </span>
                              {s.title}
                            </span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
                <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white p-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-[14px] font-semibold">Kvota</span>
                    <span className="font-[family-name:var(--skin-mono)] text-[12px] text-[var(--skin-muted)]">{left} daq qoldi</span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--skin-surface-2)]" aria-hidden>
                    <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${pct * 100}%` }} />
                  </div>
                  <button
                    type="button"
                    onClick={startReading}
                    className="mt-3 h-10 w-full rounded-md bg-[var(--skin-accent)] text-[14px] font-semibold text-white hover:brightness-110"
                  >
                    {done ? "Hammasi bajarildi ✓" : pct > 0.02 ? "Bajarishni davom ettirish" : "Ishga tushirish"}
                  </button>
                  {next ? (
                    <div className="mt-3 border-t border-[var(--skin-border)] pt-3 text-[13px] text-[var(--skin-muted)]">
                      Keyingi funksiya:{" "}
                      <Link href={`/darslar/${next.slug}/`} className="font-semibold text-[var(--skin-accent)] hover:underline">
                        {next.title}
                      </Link>
                    </div>
                  ) : (
                    <div className="mt-3 border-t border-[var(--skin-border)] pt-3 text-[13px] text-[var(--skin-muted)]">
                      Bu — darslikning oxirgi funksiyasi. Barcha darslar:{" "}
                      <Link href="/" className="font-semibold text-[var(--skin-accent)] hover:underline">
                        bosh sahifa
                      </Link>
                    </div>
                  )}
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
            <div className="truncate text-[14px] font-semibold">
              Bajarildi {executed}/{total || "—"} · {left} daq
            </div>
            <div className="mt-1.5 h-1.5 max-w-[260px] overflow-hidden rounded-full bg-[var(--skin-surface-2)]" aria-hidden>
              <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${pct * 100}%` }} />
            </div>
          </div>
          <button
            type="button"
            onClick={startReading}
            className="h-9 shrink-0 rounded-md bg-[var(--skin-accent)] px-5 text-[14px] font-semibold text-white"
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Funksiyalar ro'yxati */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/50" />
          <div className="absolute inset-x-2 top-16 max-h-[80vh] overflow-y-auto rounded-[var(--skin-radius)] bg-white shadow-2xl sm:inset-x-auto sm:left-1/2 sm:w-[600px] sm:-translate-x-1/2">
            <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-5 py-4">
              <div>
                <div className="text-[17px] font-semibold">Funksiyalar ({lessons.length})</div>
                <div className="text-[13px] text-[var(--skin-muted)]">Har bir dars — alohida funksiya</div>
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
            <ul className="divide-y divide-[var(--skin-border)]">
              {lessons.map((l) => {
                const ready = l.status === "tayyor";
                const active = l.slug === slug;
                const row = (
                  <>
                    <span className="min-w-0 flex-1">
                      <span className={`block truncate font-[family-name:var(--skin-mono)] text-[13px] ${ready ? "" : "text-[#a0a6b0]"}`}>
                        {fnName(l.slug)}
                      </span>
                      <span className="block truncate text-[12px] text-[var(--skin-muted)]">{l.title}</span>
                    </span>
                    <span
                      className={`shrink-0 rounded px-2 py-0.5 font-[family-name:var(--skin-mono)] text-[11px] ${
                        ready ? "bg-[#e3f5e7] text-[#1e7a36]" : "bg-[var(--skin-surface-2)] text-[var(--skin-muted)]"
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
                        className={`flex items-center gap-3 px-5 py-2.5 hover:bg-[var(--skin-surface-2)] ${active ? "bg-[var(--xf-soft)]" : ""}`}
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

function Stat({ label, value, tone }: { label: string; value: string; tone?: "ok" | "warn" | "run" }) {
  return (
    <div className="rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2.5">
      <div className="truncate text-[12px] text-[var(--skin-muted)]">{label}</div>
      <div
        className={`mt-0.5 font-[family-name:var(--skin-mono)] text-[18px] font-semibold ${
          tone === "ok" ? "text-[var(--xf-ok)]" : tone === "warn" ? "text-[var(--xf-warn)]" : tone === "run" ? "text-[var(--xf-run)]" : ""
        }`}
      >
        {value}
      </div>
    </div>
  );
}

/** Soddalashtirilgan belgi — lambda (funksiya). Biror kompaniya logotipi emas. */
function LambdaIcon({ dark }: { dark?: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" aria-hidden fill="none">
      <rect x="1" y="1" width="22" height="22" rx="6" fill={dark ? "#0064e0" : "#ffffff"} opacity={dark ? 1 : 0.12} />
      <path d="M7 19 11.5 9 9.5 5H7M11.5 9 16 19h2" stroke={dark ? "#ffffff" : "#5aa2ff"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
