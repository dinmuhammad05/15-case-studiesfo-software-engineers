"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

type Section = { id: string; title: string; words: number };

/** Bo'limlar (h2) va ularning hajmi (so'zlar), skroll progressi va joriy bo'lim. */
function useSections() {
  const [sections, setSections] = useState<Section[]>([]);
  const [state, setState] = useState({ pct: 0, current: 0 });

  useEffect(() => {
    const heads = Array.from(document.querySelectorAll<HTMLElement>(".lesson-prose h2"));
    setSections(
      heads.map((h) => {
        let words = 0;
        for (let el = h.nextElementSibling; el && el.tagName !== "H2"; el = el.nextElementSibling) {
          words += (el.textContent ?? "").split(/\s+/).filter(Boolean).length;
        }
        return { id: h.id, title: (h.textContent ?? "").replace(/^\d+\.\s*/, ""), words };
      }),
    );
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

const TICKERS: Record<string, string> = {
  chatgpt: "GPT",
  "url-shortener": "URL",
  redis: "RDS",
  twitter: "TWTR",
  reddit: "RDDT",
  slack: "SLCK",
  whatsapp: "WAPP",
  youtube: "YTB",
  spotify: "SPOT",
  "google-docs": "DOCS",
  airbnb: "ABNB",
  "uber-eta": "UBER",
  "amazon-s3": "S3",
  kafka: "KFKA",
  "stock-exchange": "BIRJA",
  bluesky: "BSKY",
  "meta-serverless": "FAAS",
};
const ticker = (slug: string) => TICKERS[slug] ?? slug.replace(/-/g, "").slice(0, 4).toUpperCase();
const fmt = (n: number) => n.toLocaleString("en-US").replace(/,/g, " ");
const scrollToId = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

/**
 * Birja skini: savdo terminali. Dars — instrument, uning "narxi" — o'qilgan
 * foiz. Bo'limlar — buyurtmalar kitobi: o'qilganlari — xarid (bid, yashil),
 * qolganlari — sotuv (ask, qizil), joriy bo'lim — spred. Hajm grafigi — har
 * bo'limdagi so'zlar soni.
 */
export function StockChrome({
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
  const { sections, pct, current } = useSections();
  const idx = lessons.findIndex((l) => l.slug === slug);
  const next = lessons.slice(idx + 1).find((l) => l.status === "tayyor");
  const total = sections.length;
  const words = sections.reduce((s, x) => s + x.words, 0);
  const price = (pct * 100).toFixed(2);
  const left = Math.max(0, Math.round(lesson.minutes * (1 - pct)));
  const at = Math.max(0, current - 1); // joriy bo'lim indeksi
  const done = pct >= 0.995;

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
      <header className="sticky top-0 z-30 border-b border-[var(--skin-border)] bg-[var(--bx-panel)]/95 backdrop-blur select-none">
        <div className="flex h-14 items-center gap-3 px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2" aria-label="Bosh sahifa">
            <CandleIcon />
            <span className="text-[17px] font-bold tracking-tight">darslik</span>
          </Link>
          <span className="rounded bg-[var(--skin-surface-2)] px-1.5 py-0.5 font-[family-name:var(--skin-mono)] text-[10px] text-[var(--skin-muted)]">
            TERMINAL
          </span>
          <nav className="hidden items-center gap-5 pl-4 text-[14px] text-[var(--skin-muted)] md:flex" aria-label="Bo'limlar">
            <span className="text-[var(--skin-text)]">Savdo</span>
            <span>Bozorlar</span>
            <span>Portfel</span>
          </nav>
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            className="ml-auto flex h-9 items-center gap-2 rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface)] px-3 text-[13px] text-[var(--skin-muted)] hover:text-[var(--skin-text)]"
          >
            <SearchIcon />
            <span className="hidden sm:inline">Tiker qidirish</span>
            <span className="sm:hidden">Darslar</span>
          </button>
          <span className="h-8 w-8 shrink-0 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
            <AuthorPhoto
              className="h-full w-full"
              fallback={<span className="flex h-full w-full items-center justify-center text-[12px]">D</span>}
            />
          </span>
        </div>

        {/* Tiker lentasi: har dars — bitta tiker */}
        <div className="overflow-hidden border-t border-[var(--skin-border)]" aria-hidden>
          <div className="bx-tape flex w-max">
            {[0, 1].map((copy) => (
              <div key={copy} className="flex">
                {lessons.map((l) => {
                  const ready = l.status === "tayyor";
                  return (
                    <span
                      key={l.slug}
                      className="flex h-8 items-center gap-2 border-r border-[var(--skin-border)] px-4 font-[family-name:var(--skin-mono)] text-[12px] whitespace-nowrap"
                    >
                      <span className={l.slug === slug ? "font-bold text-[var(--bx-amber)]" : "text-[var(--skin-text)]"}>
                        {ticker(l.slug)}
                      </span>
                      <span className="text-[var(--skin-muted)]">{ready ? l.minutes.toFixed(2) : "—"}</span>
                      <span className={ready ? "text-[var(--bx-up)]" : "text-[var(--skin-muted)]"}>
                        {ready ? "▲ tayyor" : "rejada"}
                      </span>
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] px-3 pt-4 pb-32 sm:px-5 xl:pb-16">
        {/* Instrument kartasi */}
        <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4 sm:p-6">
          <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 font-[family-name:var(--skin-mono)] text-[12px]">
            <span className="rounded bg-[var(--skin-surface-2)] px-2 py-0.5 font-bold text-[var(--bx-amber)]">
              {ticker(slug)}
            </span>
            <span className="text-[var(--skin-muted)]">DARSLIK · muallif: Dinmuhammad · bepul</span>
            <span className="flex items-center gap-1.5 text-[var(--bx-up)]">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--bx-up)]" aria-hidden />
              savdo ochiq
            </span>
          </div>
          <div className="[&_h1]:text-[28px] [&_h1]:leading-tight sm:[&_h1]:text-[34px] [&_header]:mb-5">{header}</div>

          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-[var(--skin-border)] bg-[var(--skin-border)] md:grid-cols-5">
            <Stat label="Oxirgi narx" value={price} tone={pct > 0 ? "up" : undefined} big />
            <Stat label="O‘zgarish" value={`${pct > 0 ? "+" : ""}${price}%`} tone={pct > 0 ? "up" : undefined} />
            <Stat label="Bo‘lim" value={`${current} / ${total || "—"}`} />
            <Stat label="Qolgan vaqt" value={`${left} daq`} tone={left === 0 ? "up" : "warn"} />
            <Stat label="Hajm (so‘z)" value={words ? fmt(words) : "—"} className="col-span-2 md:col-span-1" />
          </div>

          {/* Hajm grafigi: har bo'lim — bitta ustun */}
          <div className="mt-4">
            <div className="mb-1.5 flex justify-between font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">
              <span>Hajm · bo‘limlar bo‘yicha</span>
              <span>§1 — §{total || "—"}</span>
            </div>
            <VolumeBars sections={sections} at={current === 0 ? -1 : at} done={done} />
          </div>
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_330px]">
          <div className="min-w-0 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] px-4 pb-8 sm:px-8">
            {children}
          </div>

          <aside className="hidden xl:block">
            <div className="sticky top-[108px] space-y-4">
              <OrderBook sections={sections} at={at} current={current} done={done} />
              <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
                <div className="flex items-baseline justify-between">
                  <span className="font-[family-name:var(--skin-mono)] text-[26px] font-bold text-[var(--bx-up)]">{price}</span>
                  <span className="font-[family-name:var(--skin-mono)] text-[12px] text-[var(--skin-muted)]">{left} daq qoldi</span>
                </div>
                <button
                  type="button"
                  onClick={startReading}
                  className="mt-3 h-10 w-full rounded-md bg-[var(--bx-up)] text-[14px] font-semibold text-[var(--skin-accent-text)] hover:brightness-110"
                >
                  {done ? "Hammasi o‘qildi ✓" : pct > 0.02 ? "O‘qishni davom ettirish" : "O‘qishni boshlash"}
                </button>
                {next ? (
                  <div className="mt-3 border-t border-[var(--skin-border)] pt-3 text-[13px] text-[var(--skin-muted)]">
                    Keyingi instrument:{" "}
                    <Link href={`/darslar/${next.slug}/`} className="font-semibold text-[var(--skin-text)] hover:underline">
                      {ticker(next.slug)} · {next.title}
                    </Link>
                  </div>
                ) : null}
              </div>
            </div>
          </aside>
        </div>
      </main>

      {/* Mobil va o'rta ekran: pastki panel */}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--skin-border)] bg-[var(--bx-panel)] xl:hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 pr-28 sm:px-6">
          <div className="min-w-0 flex-1 font-[family-name:var(--skin-mono)]">
            <div className="flex items-baseline gap-2 truncate text-[14px]">
              <span className="font-bold text-[var(--bx-amber)]">{ticker(slug)}</span>
              <span className="font-semibold text-[var(--bx-up)]">{price}</span>
              <span className="text-[12px] text-[var(--skin-muted)]">
                §{current}/{total || "—"}
              </span>
            </div>
            <div className="mt-1.5 h-1.5 max-w-[260px] overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
              <div className="h-full bg-[var(--bx-up)]" style={{ width: `${pct * 100}%` }} />
            </div>
          </div>
          <button
            type="button"
            onClick={startReading}
            className="h-9 shrink-0 rounded-md bg-[var(--bx-up)] px-5 text-[14px] font-semibold text-[var(--skin-accent-text)]"
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Tikerlar ro'yxati */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/60" />
          <div className="absolute inset-x-2 top-16 max-h-[80vh] overflow-y-auto rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] shadow-2xl sm:inset-x-auto sm:left-1/2 sm:w-[600px] sm:-translate-x-1/2">
            <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-5 py-4">
              <div>
                <div className="text-[17px] font-semibold">Tikerlar ({lessons.length})</div>
                <div className="text-[13px] text-[var(--skin-muted)]">Har bir dars — alohida instrument</div>
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
                    <span
                      className={`w-14 shrink-0 font-[family-name:var(--skin-mono)] text-[13px] font-bold ${
                        active ? "text-[var(--bx-amber)]" : ready ? "text-[var(--skin-text)]" : "text-[var(--skin-muted)]"
                      }`}
                    >
                      {ticker(l.slug)}
                    </span>
                    <span className={`min-w-0 flex-1 truncate text-[14px] ${ready ? "" : "text-[var(--skin-muted)]"}`}>
                      {l.title}
                    </span>
                    <span
                      className={`shrink-0 font-[family-name:var(--skin-mono)] text-[12px] ${
                        ready ? "text-[var(--bx-up)]" : "text-[var(--skin-muted)]"
                      }`}
                    >
                      {ready ? `▲ ${l.minutes} daq` : "tez orada"}
                    </span>
                  </>
                );
                return (
                  <li key={l.slug}>
                    {ready ? (
                      <Link
                        href={`/darslar/${l.slug}/`}
                        onClick={() => setMenuOpen(false)}
                        className={`flex items-center gap-3 px-5 py-2.5 hover:bg-[var(--skin-surface-2)] ${
                          active ? "bg-[var(--skin-surface-2)]" : ""
                        }`}
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

function Stat({
  label,
  value,
  tone,
  big,
  className = "",
}: {
  label: string;
  value: string;
  tone?: "up" | "warn";
  big?: boolean;
  className?: string;
}) {
  return (
    <div className={`bg-[var(--skin-surface-2)] px-3 py-2.5 ${className}`}>
      <div className="truncate text-[12px] text-[var(--skin-muted)]">{label}</div>
      <div
        className={`mt-0.5 font-[family-name:var(--skin-mono)] font-semibold ${big ? "text-[20px]" : "text-[17px]"} ${
          tone === "up" ? "text-[var(--bx-up)]" : tone === "warn" ? "text-[var(--bx-amber)]" : ""
        }`}
      >
        {value}
      </div>
    </div>
  );
}

/** Hajm ustunlari: balandligi — bo'limdagi so'zlar; o'qilgani yashil, joriysi sariq. */
function VolumeBars({ sections, at, done }: { sections: Section[]; at: number; done: boolean }) {
  const max = Math.max(1, ...sections.map((s) => s.words));
  if (!sections.length) return <div className="h-16 rounded bg-[var(--skin-surface-2)]" aria-hidden />;
  return (
    <div className="flex h-16 items-end gap-[3px]" role="list" aria-label="Bo'limlar hajmi">
      {sections.map((s, i) => {
        const tone = done || i < at ? "bg-[var(--bx-up)]" : i === at ? "bg-[var(--bx-amber)]" : "bg-[#2a3342]";
        return (
          <button
            key={s.id || i}
            type="button"
            role="listitem"
            title={`§${i + 1} ${s.title} — ${fmt(s.words)} so‘z`}
            aria-label={`${i + 1}-bo'lim: ${s.title}`}
            onClick={() => scrollToId(s.id)}
            className={`min-w-0 flex-1 rounded-t-[2px] ${tone} hover:brightness-125`}
            style={{ height: `${Math.max(6, (s.words / max) * 100)}%` }}
          />
        );
      })}
    </div>
  );
}

/** Buyurtmalar kitobi: yuqorida — o'qilmagan bo'limlar (ask), pastda — o'qilganlar (bid). */
function OrderBook({ sections, at, current, done }: { sections: Section[]; at: number; current: number; done: boolean }) {
  const max = Math.max(1, ...sections.map((s) => s.words));
  const started = current > 0;
  const asks = sections
    .map((s, i) => ({ ...s, i }))
    .filter((s) => (started ? s.i > at : true) && !done)
    .slice(0, 6)
    .reverse();
  const bids = sections
    .map((s, i) => ({ ...s, i }))
    .filter((s) => (done ? true : started && s.i < at))
    .reverse()
    .slice(0, 6);
  const cur = started && !done ? sections[at] : undefined;

  return (
    <div className="overflow-hidden rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)]">
      <div className="flex items-center justify-between border-b border-[var(--skin-border)] px-3 py-2.5">
        <span className="text-[14px] font-semibold">Buyurtmalar kitobi</span>
        <span className="font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">bo‘limlar</span>
      </div>
      <div className="grid grid-cols-[52px_minmax(0,1fr)_56px] gap-2 px-3 py-1.5 font-[family-name:var(--skin-mono)] text-[10.5px] text-[var(--skin-muted)] uppercase">
        <span>Narx</span>
        <span>Bo‘lim</span>
        <span className="text-right">So‘z</span>
      </div>
      <div className="min-h-[24px]">
        {asks.map((s) => (
          <BookRow key={s.id || s.i} s={s} side="ask" max={max} />
        ))}
      </div>
      <div className="border-y border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2 font-[family-name:var(--skin-mono)] text-[12px]">
        {cur ? (
          <div className="flex items-center gap-2">
            <span className="font-bold text-[var(--bx-amber)]">§{String(at + 1).padStart(2, "0")}</span>
            <span className="truncate font-[family-name:var(--skin-font)] text-[var(--skin-text)]">{cur.title}</span>
          </div>
        ) : (
          <span className="text-[var(--skin-muted)]">{done ? "Hammasi bajarildi ✓" : "Spred: o‘qish hali boshlanmagan"}</span>
        )}
      </div>
      <div className="min-h-[24px] pb-1">
        {bids.map((s) => (
          <BookRow key={s.id || s.i} s={s} side="bid" max={max} />
        ))}
      </div>
    </div>
  );
}

/** Kitobning bitta qatori: narx — bo'lim raqami, hajm — so'zlar, fon — hajm chuqurligi. */
function BookRow({ s, side, max }: { s: Section & { i: number }; side: "ask" | "bid"; max: number }) {
  return (
    <button
      type="button"
      onClick={() => scrollToId(s.id)}
      className="relative grid w-full grid-cols-[52px_minmax(0,1fr)_56px] items-center gap-2 px-3 py-[5px] text-left font-[family-name:var(--skin-mono)] text-[12px] hover:bg-[var(--skin-surface-2)]"
      title={s.title}
    >
      <span
        aria-hidden
        className={`absolute inset-y-0 right-0 ${side === "ask" ? "bg-[var(--bx-down)]" : "bg-[var(--bx-up)]"} opacity-[0.12]`}
        style={{ width: `${(s.words / max) * 100}%` }}
      />
      <span className={side === "ask" ? "text-[var(--bx-down)]" : "text-[var(--bx-up)]"}>§{String(s.i + 1).padStart(2, "0")}</span>
      <span className="truncate font-[family-name:var(--skin-font)] text-[var(--skin-muted)]">{s.title}</span>
      <span className="text-right text-[var(--skin-text)]">{fmt(s.words)}</span>
    </button>
  );
}

/** Soddalashtirilgan belgi — ikki sham (candlestick). Biror birjaning logotipi emas. */
function CandleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" aria-hidden fill="none">
      <path d="M8 3v18" stroke="#f0495b" strokeWidth="1.5" />
      <rect x="5.5" y="7" width="5" height="9" rx="1" fill="#f0495b" />
      <path d="M16 2v18" stroke="#22c55e" strokeWidth="1.5" />
      <rect x="13.5" y="5" width="5" height="10" rx="1" fill="#22c55e" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
  );
}
