"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

/** Skroll progressi va joriy bo'lim (h2) raqami. */
function useReading() {
  const [state, setState] = useState({ pct: 0, total: 0, current: 0 });
  useEffect(() => {
    const on = () => {
      const heads = Array.from(document.querySelectorAll<HTMLElement>(".lesson-prose h2"));
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(1, window.scrollY / max) : 0;
      const current = heads.filter((h) => h.getBoundingClientRect().top < 140).length;
      setState({ pct, total: heads.length, current: pct >= 0.995 ? heads.length : current });
    };
    on();
    window.addEventListener("scroll", on, { passive: true });
    window.addEventListener("resize", on);
    return () => {
      window.removeEventListener("scroll", on);
      window.removeEventListener("resize", on);
    };
  }, []);
  return state;
}

const topicName = (slug: string) => `darslar.${slug}`;

/**
 * Kafka skini: klaster boshqaruv paneli. Dars — topic, har h2 bo'lim — bitta
 * offset. O'quvchi — consumer: "committed offset" o'qilgan joy, "log-end-offset" —
 * dars oxiri, ular orasidagi farq — consumer lag (qolgan daqiqalar).
 */
export function KafkaChrome({
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
  const { pct, total, current: offset } = useReading();
  const idx = lessons.findIndex((l) => l.slug === slug);
  const next = lessons.slice(idx + 1).find((l) => l.status === "tayyor");
  const lag = Math.max(0, Math.round(current.minutes * (1 - pct)));
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

  return (
    <div className="min-h-screen lg:flex">
      {/* Chap panel */}
      <aside className="sticky top-0 hidden h-screen w-[248px] shrink-0 flex-col overflow-y-auto bg-[var(--kf-side)] text-[var(--kf-side-text)] select-none lg:flex">
        <Link href="/" className="flex items-center gap-2 px-5 pt-5 pb-4 text-white" aria-label="Bosh sahifa">
          <LogIcon />
          <span className="text-[17px] font-bold tracking-tight">darslik</span>
          <span className="ml-auto rounded bg-white/10 px-1.5 py-0.5 font-[family-name:var(--skin-mono)] text-[10px]">kafka-ui</span>
        </Link>
        <div className="mx-4 mb-4 rounded-md bg-[var(--kf-side-2)] px-3 py-2 text-[13px]">
          <div className="text-[11px] tracking-wide text-white/50 uppercase">Klaster</div>
          <div className="flex items-center gap-2 font-medium text-white">
            <span className="h-2 w-2 rounded-full bg-[var(--kf-green)]" aria-hidden />
            tizim-dizayni
          </div>
          <div className="text-[12px] text-white/50">3 broker · {readyCount} topic</div>
        </div>
        <nav className="px-2 text-[14px]" aria-label="Bo'limlar">
          {[
            ["Brokerlar", false],
            ["Topic'lar", true],
            ["Consumer'lar", false],
          ].map(([t, active]) => (
            <div
              key={String(t)}
              className={`rounded-md px-3 py-1.5 ${active ? "bg-white/10 font-medium text-white" : "text-white/60"}`}
            >
              {t}
            </div>
          ))}
        </nav>
        <div className="mt-4 px-5 pb-2 text-[11px] tracking-wide text-white/40 uppercase">Topic&apos;lar (darslar)</div>
        <ul className="flex-1 px-2 pb-6 font-[family-name:var(--skin-mono)] text-[12.5px]">
          {lessons.map((l) => {
            const ready = l.status === "tayyor";
            const active = l.slug === slug;
            const name = topicName(l.slug);
            return (
              <li key={l.slug}>
                {ready ? (
                  <Link
                    href={`/darslar/${l.slug}/`}
                    className={`block truncate rounded-md px-3 py-1 ${
                      active ? "bg-[var(--skin-accent)] text-white" : "hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    {name}
                  </Link>
                ) : (
                  <span className="block truncate px-3 py-1 text-white/25">{name}</span>
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
            <LogIcon dark />
            <span className="text-[16px] font-bold">darslik</span>
          </Link>
          <nav className="hidden min-w-0 items-center gap-2 text-[14px] text-[var(--skin-muted)] sm:flex" aria-label="Yo'l">
            <button type="button" onClick={() => setMenuOpen(true)} className="hover:text-[var(--skin-text)]">
              Topic&apos;lar
            </button>
            <span aria-hidden>/</span>
            <span className="truncate font-[family-name:var(--skin-mono)] text-[var(--skin-text)]">{topicName(slug)}</span>
          </nav>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="ml-auto rounded-md border border-[var(--skin-border)] px-3 py-1.5 text-[13px] font-medium hover:bg-[var(--skin-surface-2)]"
          >
            Barcha topic&apos;lar
          </button>
          <span className="h-8 w-8 overflow-hidden rounded-full bg-[#5f6672]">
            <AuthorPhoto
              className="h-full w-full"
              fallback={<span className="flex h-full w-full items-center justify-center text-[12px] text-white">D</span>}
            />
          </span>
        </header>

        <main className="mx-auto max-w-[1360px] px-3 pt-5 pb-32 sm:px-6 lg:pb-16">
          {/* Topic kartasi */}
          <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white p-5 sm:p-6">
            <div className="mb-3 flex flex-wrap items-center gap-2 font-[family-name:var(--skin-mono)] text-[12px]">
              <span className="rounded bg-[#dcfce7] px-2 py-0.5 font-medium text-[#166534]">ONLINE</span>
              <span className="text-[var(--skin-muted)]">{topicName(slug)} · muallif: Dinmuhammad · bepul</span>
            </div>
            <div className="[&_h1]:text-[28px] [&_h1]:leading-tight sm:[&_h1]:text-[34px] [&_header]:mb-5">{header}</div>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <Stat label="Partition'lar (bo'limlar)" value={total ? String(total) : "—"} />
              <Stat label="Replication factor" value="3" />
              <Stat label="Committed offset" value={`${offset} / ${total || "—"}`} />
              <Stat label="Consumer lag" value={`${lag} daq`} tone={lag === 0 ? "ok" : "warn"} />
            </div>
          </div>

          <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
            <div className="min-w-0 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white px-4 pb-8 sm:px-8">
              {children}
            </div>

            <aside className="hidden xl:block">
              <div className="sticky top-[76px] space-y-4">
                <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white p-5">
                  <div className="flex items-center justify-between">
                    <span className="text-[15px] font-semibold">Consumer group</span>
                    <span className="rounded bg-[var(--skin-surface-2)] px-2 py-0.5 font-[family-name:var(--skin-mono)] text-[12px]">
                      o&apos;quvchi
                    </span>
                  </div>
                  <div className="mt-3 flex items-baseline gap-2">
                    <span className={`text-[34px] leading-none font-bold ${lag === 0 ? "text-[var(--kf-green)]" : ""}`}>{lag}</span>
                    <span className="text-[14px] text-[var(--skin-muted)]">daqiqa lag</span>
                  </div>
                  <LogStrip total={total} offset={offset} className="mt-4" />
                  <div className="mt-2 flex justify-between font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">
                    <span>offset 0</span>
                    <span>LEO {total || "—"}</span>
                  </div>
                  <button
                    type="button"
                    onClick={startReading}
                    className="mt-4 h-10 w-full rounded-md bg-[var(--skin-accent)] text-[14px] font-semibold text-white hover:brightness-110"
                  >
                    {pct >= 0.995 ? "Hammasi o‘qildi ✓" : pct > 0.02 ? "Iste’molni davom ettirish" : "O‘qishni boshlash"}
                  </button>
                </div>
                <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-white p-5 font-[family-name:var(--skin-mono)] text-[12px] leading-relaxed text-[var(--skin-muted)]">
                  <div>$ kafka-consumer-groups --describe \</div>
                  <div className="pl-4">--group o&apos;quvchi</div>
                  <div className="mt-2 text-[var(--skin-text)]">
                    TOPIC {topicName(slug)}
                    <br />
                    CURRENT-OFFSET {offset} · LOG-END {total || "—"} · LAG {Math.max(0, total - offset)}
                  </div>
                  {next ? (
                    <div className="mt-3 border-t border-[var(--skin-border)] pt-3 font-[family-name:var(--skin-font)] text-[13px]">
                      <span>Keyingi topic: </span>
                      <Link href={`/darslar/${next.slug}/`} className="font-semibold text-[var(--skin-accent)] hover:underline">
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
            <div className="truncate text-[14px] font-semibold">Lag: {lag} daq · offset {offset}/{total || "—"}</div>
            <LogStrip total={total} offset={offset} className="mt-1.5 max-w-[260px]" small />
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

      {/* Topic'lar ro'yxati */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/50" />
          <div className="absolute inset-x-2 top-16 max-h-[80vh] overflow-y-auto rounded-[var(--skin-radius)] bg-white shadow-2xl sm:inset-x-auto sm:left-1/2 sm:w-[600px] sm:-translate-x-1/2">
            <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-5 py-4">
              <div>
                <div className="text-[17px] font-semibold">Topic&apos;lar ({lessons.length})</div>
                <div className="text-[13px] text-[var(--skin-muted)]">Har bir dars — alohida topic</div>
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
                      <span className={`block truncate font-[family-name:var(--skin-mono)] text-[13px] ${ready ? "text-[var(--skin-text)]" : "text-[#a0a6b0]"}`}>
                        {topicName(l.slug)}
                      </span>
                      <span className="block truncate text-[12px] text-[var(--skin-muted)]">{l.title}</span>
                    </span>
                    <span
                      className={`shrink-0 rounded px-2 py-0.5 font-[family-name:var(--skin-mono)] text-[11px] ${
                        ready ? "bg-[#dcfce7] text-[#166534]" : "bg-[var(--skin-surface-2)] text-[var(--skin-muted)]"
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
                        className={`flex items-center gap-3 px-5 py-2.5 hover:bg-[var(--skin-surface-2)] ${active ? "bg-[#fff1f2]" : ""}`}
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

function Stat({ label, value, tone }: { label: string; value: string; tone?: "ok" | "warn" }) {
  return (
    <div className="rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2.5">
      <div className="truncate text-[12px] text-[var(--skin-muted)]">{label}</div>
      <div
        className={`mt-0.5 font-[family-name:var(--skin-mono)] text-[18px] font-semibold ${
          tone === "ok" ? "text-[var(--kf-green)]" : tone === "warn" ? "text-[var(--kf-amber)]" : ""
        }`}
      >
        {value}
      </div>
    </div>
  );
}

/** Jurnal tasmasi: har katak — bitta offset (bo'lim); o'qilganlari to'ldirilgan. */
function LogStrip({ total, offset, className, small }: { total: number; offset: number; className?: string; small?: boolean }) {
  const n = total || 20;
  return (
    <div className={`flex gap-[3px] ${className ?? ""}`} aria-hidden>
      {Array.from({ length: n }).map((_, i) => (
        <span
          key={i}
          className={`flex-1 rounded-[2px] ${small ? "h-2" : "h-6"} ${
            i < offset ? "bg-[var(--skin-accent)]" : "bg-[var(--skin-surface-2)] ring-1 ring-[var(--skin-border)] ring-inset"
          }`}
        />
      ))}
    </div>
  );
}

/** Soddalashtirilgan belgi — "jurnal": ketma-ket kataklar. Rasmiy logotip emas. */
function LogIcon({ dark }: { dark?: boolean }) {
  const c = dark ? "#16181d" : "#ffffff";
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" aria-hidden fill="none">
      <rect x="2" y="8" width="4" height="8" rx="1" fill={c} opacity="0.35" />
      <rect x="7" y="8" width="4" height="8" rx="1" fill={c} opacity="0.6" />
      <rect x="12" y="8" width="4" height="8" rx="1" fill={c} />
      <rect x="17" y="8" width="5" height="8" rx="1" fill="#e11d48" />
    </svg>
  );
}
