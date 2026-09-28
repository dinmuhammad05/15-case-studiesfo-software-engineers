"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
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

/**
 * Uber skini: qora yuqori panel, chapda "qayerdan — qayerga" rejalashtiruvchi,
 * o'ngda xarita. O'qish progressi — marshrut bo'ylab ketayotgan mashina va
 * "yetib kelish vaqti" (qolgan daqiqalar). Dars mavzusiga mos: ETA.
 */
export function UberChrome({
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
  const left = Math.max(0, Math.round(current.minutes * (1 - pct)));

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
      {/* Qora yuqori panel */}
      <header className="sticky top-0 z-30 bg-black text-white select-none">
        <div className="mx-auto flex h-16 max-w-[1280px] items-center gap-6 px-4 sm:px-6 lg:px-10">
          <Link href="/" className="shrink-0 text-[22px] font-bold tracking-tight" aria-label="Bosh sahifa">
            darslik
          </Link>
          <nav className="hidden items-center gap-1 text-[15px] font-medium md:flex" aria-label="Bo'limlar">
            <span className="rounded-full bg-white/15 px-3.5 py-1.5">Safar</span>
            <button
              type="button"
              onClick={() => setMenuOpen(true)}
              className="rounded-full px-3.5 py-1.5 hover:bg-white/10"
            >
              Darslar
            </button>
            <Link href="/darslar/" className="rounded-full px-3.5 py-1.5 hover:bg-white/10">
              Kurs rejasi
            </Link>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMenuOpen(true)}
              className="rounded-full bg-white px-4 py-2 text-[14px] font-medium text-black hover:bg-white/90"
            >
              Qayerga?
            </button>
            <span className="h-9 w-9 overflow-hidden rounded-full bg-[#333]">
              <AuthorPhoto
                className="h-full w-full"
                fallback={<span className="flex h-full w-full items-center justify-center text-[13px] font-bold">D</span>}
              />
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1280px] px-4 pb-32 sm:px-6 lg:px-10 lg:pb-16">
        {/* Rejalashtiruvchi + xarita */}
        <section className="grid gap-6 pt-8 lg:grid-cols-[minmax(0,460px)_minmax(0,1fr)] lg:gap-10 lg:pt-12">
          <div className="min-w-0">
            <div className="[&_h1]:text-[34px] [&_h1]:leading-[1.1] [&_h1]:tracking-[-0.03em] sm:[&_h1]:text-[44px] [&_header]:mb-6">
              {header}
            </div>
            <div className="relative rounded-lg bg-[var(--skin-surface-2)] p-2">
              <span aria-hidden className="absolute top-[34px] bottom-[34px] left-[25px] w-[2px] bg-black" />
              <div className="flex items-center gap-4 rounded-md px-3 py-3">
                <span aria-hidden className="relative z-[1] h-2.5 w-2.5 rounded-full bg-black ring-4 ring-[var(--skin-surface-2)]" />
                <span className="min-w-0">
                  <span className="block text-[12px] text-[var(--skin-muted)]">Qayerdan</span>
                  <span className="block truncate text-[15px] font-medium">1. Muammo: “7 daqiqa” ortida nima bor</span>
                </span>
              </div>
              <div className="mx-3 h-px bg-[var(--skin-border)]" />
              <div className="flex items-center gap-4 rounded-md px-3 py-3">
                <span aria-hidden className="relative z-[1] h-2.5 w-2.5 bg-black ring-4 ring-[var(--skin-surface-2)]" />
                <span className="min-w-0">
                  <span className="block text-[12px] text-[var(--skin-muted)]">Qayerga</span>
                  <span className="block truncate text-[15px] font-medium">Amaliyot: o‘z ETA dvigatelingiz</span>
                </span>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-[13px] font-medium">
              <span className="rounded-full bg-[var(--skin-surface-2)] px-3 py-1.5">{current.minutes} daqiqa</span>
              <span className="rounded-full bg-[var(--skin-surface-2)] px-3 py-1.5">{current.level}</span>
              <span className="rounded-full bg-[var(--skin-surface-2)] px-3 py-1.5">Bepul</span>
            </div>
            <button
              type="button"
              onClick={startReading}
              className="mt-5 h-12 w-full rounded-lg bg-black text-[16px] font-medium text-white hover:bg-[#222] sm:w-auto sm:px-8"
            >
              {pct > 0.02 ? "O‘qishni davom ettirish" : "O‘qishni boshlash"}
            </button>
          </div>

          <div className="relative h-56 overflow-hidden rounded-xl sm:h-80 lg:h-auto lg:min-h-[440px]">
            <RouteMap pct={pct} />
            <span className="absolute top-4 right-4 rounded-full bg-black px-4 py-2 text-[14px] font-medium text-white shadow-[var(--ub-shadow)]">
              {left} daq qoldi
            </span>
          </div>
        </section>

        {/* Dars va safar kartasi */}
        <div className="mt-12 grid gap-12 lg:grid-cols-[minmax(0,1fr)_340px] xl:gap-16">
          <div className="min-w-0">{children}</div>

          <aside className="hidden lg:block">
            <div className="sticky top-[88px] overflow-hidden rounded-xl bg-white shadow-[var(--ub-shadow)] ring-1 ring-[var(--skin-border)]">
              <div className="p-5">
                <div className="text-[13px] font-medium text-[var(--skin-muted)]">Safaringiz</div>
                <div className="mt-1 flex items-baseline gap-2">
                  <span className="text-[34px] leading-none font-bold tracking-tight">{left}</span>
                  <span className="text-[15px] font-medium">daqiqa qoldi</span>
                </div>
                <div className="mt-1 text-[13px] text-[var(--skin-muted)]">
                  {pct >= 0.995 ? "Yetib keldingiz" : `${Math.round(pct * 100)}% yo‘l bosildi`}
                </div>
                <MiniRoute pct={pct} />
                <div className="mt-4 space-y-1 text-[14px]">
                  <div className="flex justify-between">
                    <span className="text-[var(--skin-muted)]">Qayerdan</span>
                    <span className="font-medium">1-bo‘lim</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--skin-muted)]">Qayerga</span>
                    <span className="font-medium">Amaliyot</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 border-t border-[var(--skin-border)] px-5 py-4">
                <span className="h-11 w-11 shrink-0 overflow-hidden rounded-full bg-[#333]">
                  <AuthorPhoto
                    className="h-full w-full"
                    fallback={<span className="flex h-full w-full items-center justify-center font-bold text-white">D</span>}
                  />
                </span>
                <div className="min-w-0">
                  <div className="text-[15px] font-medium">Dinmuhammad</div>
                  <div className="text-[13px] text-[var(--skin-muted)]">Muallif · Full-stack dasturchi</div>
                </div>
              </div>
              <div className="border-t border-[var(--skin-border)] p-5">
                <button
                  type="button"
                  onClick={startReading}
                  className="h-12 w-full rounded-lg bg-black text-[15px] font-medium text-white hover:bg-[#222]"
                >
                  {pct > 0.02 ? "Davom ettirish" : "O‘qishni boshlash"}
                </button>
                {next ? (
                  <div className="mt-4 text-[14px]">
                    <span className="text-[var(--skin-muted)]">Keyingi safar: </span>
                    <Link href={`/darslar/${next.slug}/`} className="font-medium underline underline-offset-2">
                      {next.title}
                    </Link>
                  </div>
                ) : null}
              </div>
            </div>
          </aside>
        </div>
      </main>

      {/* Mobil: pastki panel */}
      <div className="fixed inset-x-0 bottom-0 z-30 rounded-t-2xl bg-white shadow-[0_-4px_16px_rgba(0,0,0,0.12)] lg:hidden">
        <div className="mx-auto mt-2 h-1 w-10 rounded-full bg-[#d6d6d6]" aria-hidden />
        <div className="flex items-center gap-3 px-4 pt-2 pb-3 pr-28 sm:px-6">
          <div className="min-w-0 flex-1">
            <div className="text-[16px] font-bold">{left} daqiqa qoldi</div>
            <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
              <div className="h-full bg-black" style={{ width: `${pct * 100}%` }} />
            </div>
          </div>
          <button
            type="button"
            onClick={startReading}
            className="h-11 shrink-0 rounded-lg bg-black px-5 text-[15px] font-medium text-white"
          >
            O‘qish
          </button>
        </div>
      </div>

      {/* Darslar ro'yxati — "safar variantlari" */}
      {menuOpen ? (
        <div className="fixed inset-0 z-40" role="dialog" aria-modal="true" aria-label="Darslar">
          <button type="button" aria-label="Yopish" onClick={() => setMenuOpen(false)} className="absolute inset-0 bg-black/50" />
          <div className="absolute inset-x-0 bottom-0 max-h-[85vh] overflow-y-auto rounded-t-2xl bg-white p-5 shadow-2xl sm:inset-x-auto sm:top-20 sm:right-6 sm:bottom-auto sm:w-[440px] sm:rounded-xl">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-[20px] font-bold tracking-tight">Qayerga boramiz?</span>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label="Yopish"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--skin-surface-2)] text-[18px]"
              >
                ×
              </button>
            </div>
            <div className="space-y-1.5">
              {lessons.map((l) => {
                const ready = l.status === "tayyor";
                const active = l.slug === slug;
                const row = (
                  <>
                    <span
                      className="flex h-11 w-11 shrink-0 items-center justify-center rounded-md text-[13px] font-bold text-white"
                      style={{ background: ready ? "#000" : "#c9c9c9" }}
                    >
                      {String(l.order).padStart(2, "0")}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-[15px] font-medium">{l.title}</span>
                      <span className="block text-[13px] text-[var(--skin-muted)]">{ready ? l.level : "Tez orada"}</span>
                    </span>
                    <span className="shrink-0 text-[15px] font-medium">{ready ? `${l.minutes} daq` : ""}</span>
                  </>
                );
                return ready ? (
                  <Link
                    key={l.slug}
                    href={`/darslar/${l.slug}/`}
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center gap-3 rounded-lg p-2.5 ${active ? "ring-2 ring-black" : "hover:bg-[var(--skin-surface-2)]"}`}
                  >
                    {row}
                  </Link>
                ) : (
                  <span key={l.slug} className="flex cursor-default items-center gap-3 rounded-lg p-2.5 opacity-50">
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

/* Xarita: ko'chalar to'ri, daryo, bog' va marshrut. Mashina o'qish progressi bo'yicha yuradi. */
const XS = [-10, 70, 150, 230, 310, 390, 470, 550, 630];
const YS = [-10, 70, 150, 230, 310, 390, 470];
const PARKS = new Set(["2,3", "5,4", "6,1"]);
// Xarita "slice" bilan kesiladi (keng va tor konteynerlar): marshrut markaziy
// xavfsiz hududda (x 110-510, y 130-270), shuning uchun har o'lchamda ko'rinadi.
const ROUTE = "M150 250 L150 230 L310 230 L310 150 L470 150";

function RouteMap({ pct }: { pct: number }) {
  const ref = useRef<SVGPathElement>(null);
  const [car, setCar] = useState({ x: 150, y: 250, a: -90 });
  useEffect(() => {
    const p = ref.current;
    if (!p) return;
    const L = p.getTotalLength();
    const at = Math.min(L - 0.5, Math.max(0, L * pct));
    const a = p.getPointAtLength(at);
    const b = p.getPointAtLength(Math.min(L, at + 1));
    setCar({ x: a.x, y: a.y, a: (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI });
  }, [pct]);

  return (
    <svg
      viewBox="0 0 620 400"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 h-full w-full"
      role="img"
      aria-label="Marshrut xaritasi: o'qish progressi"
    >
      <rect width="620" height="400" fill="var(--ub-map)" />
      {XS.slice(0, -1).flatMap((x, i) =>
        YS.slice(0, -1).map((y, j) => (
          <rect
            key={`${i},${j}`}
            x={x + 7}
            y={y + 7}
            width={XS[i + 1] - x - 14}
            height={YS[j + 1] - y - 14}
            rx="4"
            fill={PARKS.has(`${i},${j}`) ? "var(--ub-park)" : "var(--ub-block)"}
          />
        )),
      )}
      <path d="M-20 360 C 120 330, 260 420, 420 360 S 600 300, 660 330 L660 420 L-20 420 Z" fill="var(--ub-water)" />
      <path d="M300 352 L 300 378" stroke="#fff" strokeWidth="12" />
      <path ref={ref} d={ROUTE} fill="none" stroke="#000" strokeWidth="6" strokeLinejoin="round" strokeLinecap="round" />
      <path
        d={ROUTE}
        fill="none"
        stroke="#9a9a9a"
        strokeWidth="6"
        strokeLinejoin="round"
        strokeLinecap="round"
        pathLength={1}
        strokeDasharray={`${pct} 1`}
      />
      <circle cx="150" cy="250" r="9" fill="#000" />
      <circle cx="150" cy="250" r="3.5" fill="#fff" />
      <rect x="461" y="141" width="18" height="18" fill="#000" />
      <rect x="467" y="147" width="6" height="6" fill="#fff" />
      <g transform={`translate(${car.x} ${car.y}) rotate(${car.a})`}>
        <rect x="-12" y="-7" width="24" height="14" rx="4" fill="#000" stroke="#fff" strokeWidth="2" />
        <rect x="3" y="-4.5" width="5" height="9" rx="1.5" fill="#fff" opacity="0.85" />
      </g>
    </svg>
  );
}

function MiniRoute({ pct }: { pct: number }) {
  return (
    <div className="relative mt-5 h-6" aria-hidden>
      <div className="absolute top-1/2 right-2 left-2 h-[3px] -translate-y-1/2 bg-black" />
      <div className="absolute top-1/2 left-2 h-[3px] -translate-y-1/2 bg-[#b5b5b5]" style={{ width: `calc((100% - 16px) * ${pct})` }} />
      <span className="absolute top-1/2 left-0 h-3 w-3 -translate-y-1/2 rounded-full bg-black ring-2 ring-white" />
      <span className="absolute top-1/2 right-0 h-3 w-3 -translate-y-1/2 bg-black ring-2 ring-white" />
      <span
        className="absolute top-1/2 h-4 w-6 -translate-x-1/2 -translate-y-1/2 rounded-[4px] bg-black ring-2 ring-white"
        style={{ left: `calc(8px + (100% - 16px) * ${pct})` }}
      />
    </div>
  );
}
