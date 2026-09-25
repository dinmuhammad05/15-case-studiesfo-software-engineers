"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { AuthorPhoto } from "@/components/AuthorPhoto";

const MENUS = ["Fayl", "Tahrirlash", "Ko‘rinish", "Qo‘shish", "Format", "Asboblar", "Kengaytmalar", "Yordam"];

/** Hujjatdagi boshqa "hamkorlar" — dars mavzusi: bir vaqtda tahrirlash. */
const PEERS = [
  { name: "Ali", color: "#188038" },
  { name: "Vali", color: "#a142f4" },
];

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
 * Google Docs skini: yuqorida menyu va asboblar paneli, chapda hujjat tablari
 * (darslar), o'rtada oq "qog'oz" sahifa. Pastki chap burchakda — so'zlar soni.
 */
export function GoogleDocsChrome({
  slug,
  header,
  children,
}: {
  slug: string;
  header: ReactNode;
  children: ReactNode;
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [starred, setStarred] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [words, setWords] = useState<number | null>(null);
  const current = lessons.find((l) => l.slug === slug)!;
  const pct = useScrollProgress();

  useEffect(() => {
    const text = document.querySelector(".lesson-prose")?.textContent ?? "";
    setWords(text.split(/\s+/).filter(Boolean).length);
  }, []);
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
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2200);
    return () => clearTimeout(t);
  }, [toast]);

  const share = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setToast("Havola nusxalandi");
    } catch {
      setToast("Havolani manzil satridan nusxalang");
    }
  };

  const tabs = (onNavigate?: () => void) =>
    lessons.map((l) => {
      const ready = l.status === "tayyor";
      const active = l.slug === slug;
      const row = (
        <>
          <span className={active ? "text-[var(--gd-blue)]" : "text-[var(--skin-muted)]"}>
            <IconTab />
          </span>
          <span className="min-w-0 flex-1 truncate">{l.title}</span>
          {!ready ? <span className="text-[11px] text-[var(--skin-muted)]">tez orada</span> : null}
        </>
      );
      const cls = `flex items-center gap-2.5 rounded-full px-3 py-1.5 text-[13.5px] ${
        active ? "bg-[#d3e3fd] font-medium text-[#041e49]" : ""
      }`;
      return ready ? (
        <Link
          key={l.slug}
          href={`/darslar/${l.slug}/`}
          onClick={onNavigate}
          title={l.title}
          className={`${cls} ${active ? "" : "hover:bg-[var(--gd-hover)]"}`}
        >
          {row}
        </Link>
      ) : (
        <span key={l.slug} className={`${cls} cursor-default opacity-50`}>
          {row}
        </span>
      );
    });

  return (
    <div className="min-h-screen">
      {/* Yuqori panel: sarlavha, menyular, hamkorlar, "Ulashish" */}
      <header className="sticky top-0 z-30 bg-[var(--gd-canvas)] select-none">
        <div className="flex items-center gap-2 px-2 pt-2 pb-1 sm:px-3">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Hujjat tablarini ochish"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-[var(--skin-muted)] hover:bg-[var(--gd-hover)] lg:hidden"
          >
            <IconMenu />
          </button>
          <Link href="/" aria-label="Bosh sahifa" title="Bosh sahifa" className="shrink-0 p-1">
            <DocIcon />
          </Link>
          <div className="min-w-0 flex-1">
            <div className="flex min-w-0 items-center gap-1.5">
              <span className="truncate rounded border border-transparent px-1.5 text-[17px] leading-7 hover:border-[var(--skin-border)]">
                {current.title}
              </span>
              <button
                type="button"
                onClick={() => setStarred((v) => !v)}
                aria-label="Yulduzcha qo'yish"
                aria-pressed={starred}
                className={`hidden rounded-full p-1 hover:bg-[var(--gd-hover)] sm:block ${
                  starred ? "text-[#f4b400]" : "text-[var(--skin-muted)]"
                }`}
              >
                <IconStar filled={starred} />
              </button>
              <span
                aria-hidden
                className="hidden items-center gap-1 text-[12px] text-[var(--skin-muted)] md:flex"
                title="Barcha o'zgarishlar saqlandi"
              >
                <IconCloud />
                Saqlandi
              </span>
            </div>
            <nav aria-hidden className="hidden gap-0.5 text-[14px] md:flex">
              {MENUS.map((m) => (
                <span key={m} className="rounded px-1.5 py-0.5 hover:bg-[var(--gd-hover)]">
                  {m}
                </span>
              ))}
            </nav>
          </div>

          <span aria-hidden className="hidden rounded-full p-2 text-[var(--skin-muted)] hover:bg-[var(--gd-hover)] lg:block">
            <IconHistory />
          </span>
          <span aria-hidden className="hidden rounded-full p-2 text-[var(--skin-muted)] hover:bg-[var(--gd-hover)] lg:block">
            <IconComment />
          </span>
          <span className="hidden items-center sm:flex" aria-label="Hujjatdagi hamkorlar">
            {PEERS.map((p, i) => (
              <span
                key={p.name}
                title={p.name}
                className="-ml-1.5 flex h-8 w-8 items-center justify-center rounded-full border-2 border-[var(--gd-canvas)] text-[13px] font-medium text-white first:ml-0"
                style={{ background: p.color, zIndex: 3 - i }}
              >
                {p.name[0]}
              </span>
            ))}
          </span>
          <button
            type="button"
            onClick={share}
            className="flex h-9 shrink-0 items-center gap-2 rounded-full bg-[#c2e7ff] px-3 text-[14px] font-medium text-[#001d35] hover:shadow sm:px-5"
          >
            <IconLock />
            <span className="hidden sm:inline">Ulashish</span>
          </button>
          <span className="h-8 w-8 shrink-0 overflow-hidden rounded-full" aria-hidden>
            <AuthorPhoto
              className="h-full w-full rounded-full"
              fallback={
                <span className="flex h-full w-full items-center justify-center rounded-full bg-[#1a73e8] text-[13px] font-medium text-white">
                  D
                </span>
              }
            />
          </span>
        </div>

        {/* Asboblar paneli */}
        <div
          aria-hidden
          className="mx-2 mb-1.5 hidden h-10 items-center gap-0.5 overflow-hidden rounded-full bg-[var(--gd-toolbar)] px-3 text-[var(--skin-muted)] md:flex"
        >
          <IconUndo />
          <IconRedo />
          <IconPrint />
          <Sep />
          <Pill w="w-14">100%</Pill>
          <Sep />
          <Pill w="w-28">Oddiy matn</Pill>
          <Sep />
          <Pill w="w-20">Arial</Pill>
          <Sep />
          <span className="px-1 text-[15px]">−</span>
          <span className="rounded border border-[#747775] px-1.5 text-[13px] leading-5 text-[var(--skin-text)]">11</span>
          <span className="px-1 text-[15px]">+</span>
          <Sep />
          <span className="px-1.5 text-[15px] font-bold text-[var(--skin-text)]">B</span>
          <span className="px-1.5 font-serif text-[15px] text-[var(--skin-text)] italic">I</span>
          <span className="px-1.5 text-[15px] text-[var(--skin-text)] underline">U</span>
          <span className="px-1.5 text-[15px] text-[var(--skin-text)]">
            A<span className="-mt-1 block h-[3px] bg-[var(--skin-text)]" />
          </span>
          <Sep />
          <IconLink />
          <IconComment />
          <IconImage />
          <Sep />
          <span className="hidden items-center gap-0.5 lg:flex">
            <IconAlign />
            <IconList />
            <IconChecklist />
          </span>
          <span className="ml-auto flex items-center gap-1 rounded-full px-2 py-1 text-[13px] text-[var(--skin-text)]">
            <IconPencil />
            <span className="hidden xl:inline">Tahrirlash</span>
          </span>
        </div>
        {/* Mobil: o'qish progressi */}
        <span aria-hidden className="absolute inset-x-0 bottom-0 h-0.5 md:hidden">
          <span className="block h-full bg-[var(--gd-blue)]" style={{ width: `${pct * 100}%` }} />
        </span>
      </header>

      <div className="flex">
        {/* Chap: hujjat tablari (darslar) */}
        <aside className="sticky top-[104px] hidden h-[calc(100vh-112px)] w-[260px] shrink-0 flex-col pl-3 lg:flex">
          <div className="flex items-center justify-between px-3 pt-3 pb-2 text-[14px] font-medium">
            Hujjat tablari
            <span aria-hidden className="text-[20px] leading-none text-[var(--skin-muted)]">
              +
            </span>
          </div>
          <div className="min-h-0 flex-1 space-y-0.5 overflow-y-auto pr-2 pb-4">{tabs()}</div>
          <div
            aria-hidden
            className="mr-2 mb-2 flex items-center gap-2 border-t border-[var(--skin-border)] px-3 pt-3 text-[12px] text-[var(--skin-muted)]"
          >
            <Stats words={words} pct={pct} />
          </div>
        </aside>

        {/* O'rta: qog'oz sahifa */}
        <main className="min-w-0 flex-1 pb-16 md:px-4">
          <Ruler />
          <div className="relative mx-auto max-w-[900px] bg-white px-4 pt-8 pb-12 sm:px-10 md:my-3 md:px-[72px] md:pt-[64px] md:shadow-[var(--gd-page-shadow)]">
            <PeerCaret />
            {header}
            {children}
          </div>
        </main>

        {/* O'ng: yon panel ikonkalari */}
        <aside aria-hidden className="sticky top-[104px] hidden h-[calc(100vh-112px)] w-14 shrink-0 flex-col items-center gap-5 pt-6 xl:flex">
          {["#fbbc04", "#1a73e8", "#34a853", "#ea4335"].map((c) => (
            <span key={c} className="h-5 w-5 rounded-md" style={{ background: c, opacity: 0.85 }} />
          ))}
          <span className="h-px w-5 bg-[var(--skin-border)]" />
          <span className="text-[20px] leading-none text-[var(--skin-muted)]">+</span>
        </aside>
      </div>

      {/* Pastki chap (planshet): so'zlar soni va o'qilgan qism; kompyuterda — tablar ostida */}
      <div
        aria-hidden
        className="fixed bottom-4 left-4 z-20 hidden items-center gap-2 rounded-lg border border-[var(--skin-border)] bg-white px-3 py-1.5 text-[12px] text-[var(--skin-muted)] shadow-sm md:flex lg:hidden"
      >
        <Stats words={words} pct={pct} />
      </div>

      {toast ? (
        <div
          role="status"
          className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded bg-[#1f1f1f] px-4 py-2.5 text-[14px] text-white shadow-lg"
        >
          {toast}
        </div>
      ) : null}

      {/* Mobil: hujjat tablari paneli */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[300px] max-w-[86vw] flex-col bg-white shadow-2xl">
            <div className="flex items-center gap-3 px-4 pt-4 pb-3">
              <DocIcon />
              <span className="font-medium">Hujjat tablari</span>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="ml-auto flex h-8 w-8 items-center justify-center rounded-full hover:bg-[var(--gd-hover)]"
              >
                ×
              </button>
            </div>
            <div className="min-h-0 flex-1 space-y-0.5 overflow-y-auto px-2 pb-24">
              {tabs(() => setDrawerOpen(false))}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}

function Stats({ words, pct }: { words: number | null; pct: number }) {
  return (
    <>
      {words !== null ? <span>{words.toLocaleString("en-US").replace(/,/g, " ")} so‘z</span> : null}
      <span className="opacity-50">·</span>
      <span className="tabular-nums">{Math.round(pct * 100)}% o‘qildi</span>
    </>
  );
}

/** Sahifaning o'ng yuqorisida boshqa foydalanuvchining kursori — dars mavzusiga ishora. */
function PeerCaret() {
  const p = PEERS[1];
  return (
    <span aria-hidden className="pointer-events-none absolute top-6 right-4 hidden items-start sm:flex md:top-10 md:right-10">
      <span className="relative">
        <span
          className="absolute -top-4 left-0 rounded-sm px-1 text-[10px] leading-4 whitespace-nowrap text-white"
          style={{ background: p.color }}
        >
          {p.name} tahrirlamoqda
        </span>
        <span className="gd-caret block h-5 w-0.5" style={{ background: p.color }} />
      </span>
    </span>
  );
}

function Ruler() {
  return (
    <div aria-hidden className="mx-auto hidden h-5 max-w-[900px] items-end md:flex">
      <div
        className="relative h-3 w-full border-b border-[var(--skin-border)]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(90deg, #c4c7c5 0 1px, transparent 1px 12px)",
          backgroundSize: "100% 4px",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "0 100%",
        }}
      >
        <span className="absolute bottom-0 left-[72px] h-0 w-0 border-x-[5px] border-t-[6px] border-x-transparent border-t-[var(--gd-blue)]" />
        <span className="absolute right-[72px] bottom-0 h-0 w-0 border-x-[5px] border-t-[6px] border-x-transparent border-t-[var(--gd-blue)]" />
      </div>
    </div>
  );
}

function Sep() {
  return <span className="mx-1 h-5 w-px shrink-0 bg-[#c7c7c7]" />;
}
function Pill({ children, w }: { children: ReactNode; w: string }) {
  return (
    <span className={`flex ${w} shrink-0 items-center justify-between rounded px-1.5 text-[13px] text-[var(--skin-text)]`}>
      {children}
      <span className="text-[9px] text-[var(--skin-muted)]">▼</span>
    </span>
  );
}

/** Soddalashtirilgan hujjat belgisi — rasmiy logotip emas. */
function DocIcon() {
  return (
    <svg viewBox="0 0 24 32" className="h-8 w-6" aria-hidden>
      <path d="M2 0h14l8 8v22a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2z" fill="#4285f4" />
      <path d="M16 0l8 8h-6a2 2 0 0 1-2-2z" fill="#a1c2fa" />
      <path d="M6 15h12M6 19h12M6 23h8" stroke="#fff" strokeWidth="2" />
    </svg>
  );
}

/* Ikonkalar — soddalashtirilgan, rasmiy emas */
const I = (d: string, cls = "h-5 w-5 shrink-0") =>
  function Icon() {
    return (
      <svg viewBox="0 0 24 24" className={cls} fill="none" aria-hidden>
        <path d={d} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  };
const IconMenu = I("M4 7h16M4 12h16M4 17h16");
const IconTab = I("M4 6h7l2 2h7v10H4z", "h-4 w-4 shrink-0");
const IconCloud = I("M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 11a3.5 3.5 0 0 0 1 7zM9.5 13.5l2 2 3.5-3.5", "h-4 w-4");
const IconHistory = I("M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4M12 8v4l3 2");
const IconComment = I("M5 5h14v10H9l-4 4z", "h-5 w-5 shrink-0 px-0.5");
const IconLock = I("M7 11V8a5 5 0 0 1 10 0v3M6 11h12v9H6z", "h-4 w-4");
const IconUndo = I("M9 7L5 11l4 4M5 11h9a5 5 0 0 1 0 10h-2", "h-5 w-5 shrink-0 px-0.5");
const IconRedo = I("M15 7l4 4-4 4M19 11h-9a5 5 0 0 0 0 10h2", "h-5 w-5 shrink-0 px-0.5");
const IconPrint = I("M7 9V4h10v5M7 17H5v-7h14v7h-2M7 14h10v6H7z", "h-5 w-5 shrink-0 px-0.5");
const IconLink = I("M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1", "h-5 w-5 shrink-0 px-0.5");
const IconImage = I("M4 5h16v14H4zM4 16l5-5 4 4 3-3 4 4M15 9h.01", "h-5 w-5 shrink-0 px-0.5");
const IconAlign = I("M4 6h16M4 10h10M4 14h16M4 18h10", "h-5 w-5 shrink-0 px-0.5");
const IconList = I("M9 6h11M9 12h11M9 18h11M5 6h.01M5 12h.01M5 18h.01", "h-5 w-5 shrink-0 px-0.5");
const IconChecklist = I("M4 6l1.5 1.5L8 5M4 12l1.5 1.5L8 11M4 18l1.5 1.5L8 17M11 6h9M11 12h9M11 18h9", "h-5 w-5 shrink-0 px-0.5");
const IconPencil = I("M4 20h4L19 9l-4-4L4 16zM13 7l4 4", "h-4 w-4");
function IconStar({ filled }: { filled: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill={filled ? "currentColor" : "none"} aria-hidden>
      <path
        d="M12 4l2.5 5.2 5.5.8-4 3.9 1 5.6L12 16.8 7 19.5l1-5.6-4-3.9 5.5-.8z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}
