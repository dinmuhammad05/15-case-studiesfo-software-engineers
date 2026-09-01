"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";

/**
 * URL qisqartiruvchi skini: link boshqaruv paneli ko'rinishi.
 * Yuqorida "qisqartirish" paneli (dekorativ), chapda linklar ro'yxati,
 * o'rtada tanlangan linkning batafsil sahifasi.
 */
export function UrlShortenerChrome({ slug, children }: { slug: string; children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const current = lessons.find((l) => l.slug === slug);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setDrawerOpen(false);
        setMenuOpen(false);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [menuOpen]);

  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  return (
    <div className="min-h-screen">
      {/* Yuqori panel — "link qisqartirish" satri */}
      <header className="sticky top-0 z-30 select-none border-b border-[var(--skin-border)] bg-[var(--skin-bg)]">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-3 py-2.5 sm:px-5">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Darslar ro'yxatini ochish"
            className="flex h-9 w-9 items-center justify-center rounded-lg hover:bg-[var(--skin-surface-2)] lg:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>

          <Link href="/" className="flex shrink-0 items-center gap-2 font-semibold">
            <LinkMark className="h-6 w-6" />
            <span className="hidden sm:inline">Darslik</span>
          </Link>

          {/* Dekorativ qisqartirish paneli */}
          <div
            aria-hidden
            className="ml-2 hidden min-w-0 flex-1 items-center gap-2 rounded-full border border-[var(--skin-border)] bg-[var(--skin-surface)] py-1.5 pr-1.5 pl-4 md:flex"
          >
            <span className="truncate text-sm text-[var(--skin-muted)]">
              https://example.com/juda/uzun/manzil?utm_source=...
            </span>
            <span className="ml-auto shrink-0 rounded-full bg-[var(--skin-accent)] px-4 py-1.5 text-sm font-semibold text-[var(--skin-accent-text)]">
              Qisqartirish
            </span>
          </div>

          <div ref={menuRef} className="relative ml-auto md:ml-0">
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              className="flex items-center gap-1.5 rounded-lg border border-[var(--skin-border)] px-3 py-1.5 text-sm font-medium hover:bg-[var(--skin-surface-2)]"
            >
              Dars {String(current?.order ?? 2).padStart(2, "0")}
              <span
                aria-hidden
                className={`text-[var(--skin-muted)] transition-transform ${menuOpen ? "rotate-180" : ""}`}
              >
                ▾
              </span>
            </button>
            {menuOpen ? (
              <div
                role="menu"
                className="absolute right-0 top-full mt-1.5 max-h-[70vh] w-[300px] overflow-y-auto rounded-xl border border-[var(--skin-border)] bg-[var(--skin-bg)] p-1.5 shadow-xl"
              >
                {lessons.map((l) => {
                  const ready = l.status === "tayyor";
                  const body = (
                    <>
                      <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-muted)]">
                        {String(l.order).padStart(2, "0")}
                      </span>
                      <span className="min-w-0 flex-1 truncate">{l.title}</span>
                      {l.slug === slug ? <span className="text-[var(--skin-accent)]">✓</span> : null}
                      {!ready ? (
                        <span className="text-[10px] text-[var(--skin-muted)]">rejada</span>
                      ) : null}
                    </>
                  );
                  return ready ? (
                    <Link
                      key={l.slug}
                      href={`/darslar/${l.slug}/`}
                      role="menuitem"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm hover:bg-[var(--skin-surface-2)]"
                    >
                      {body}
                    </Link>
                  ) : (
                    <span
                      key={l.slug}
                      className="flex cursor-default items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm opacity-45"
                    >
                      {body}
                    </span>
                  );
                })}
              </div>
            ) : null}
          </div>
        </div>
        <ReadingProgress />
      </header>

      <div className="mx-auto flex max-w-7xl">
        <aside className="sticky top-[57px] hidden h-[calc(100vh-57px)] w-[260px] shrink-0 flex-col border-r border-[var(--skin-border)] lg:flex">
          <SidebarContent slug={slug} />
        </aside>

        {drawerOpen ? (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              aria-label="Yopish"
              onClick={() => setDrawerOpen(false)}
              className="absolute inset-0 bg-black/40"
            />
            <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col bg-[var(--skin-bg)] shadow-2xl">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-lg text-lg text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
              >
                ×
              </button>
              <SidebarContent slug={slug} onNavigate={() => setDrawerOpen(false)} />
            </aside>
          </div>
        ) : null}

        <main className="min-w-0 flex-1 px-4 py-8 sm:px-8">
          <div className="mx-auto max-w-3xl">{children}</div>
        </main>
      </div>
    </div>
  );
}

function SidebarContent({ slug, onNavigate }: { slug: string; onNavigate?: () => void }) {
  return (
    <>
      <div className="border-b border-[var(--skin-border)] px-4 py-3.5">
        <div className="text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
          Havolalar
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {lessons.map((l) => {
          const ready = l.status === "tayyor";
          const active = l.slug === slug;
          const inner = (
            <>
              <div className="flex items-center gap-2">
                <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-accent)]">
                  /{shortKey(l.slug)}
                </span>
                {active ? (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-[var(--skin-accent)]" />
                ) : null}
              </div>
              <div className="mt-0.5 truncate text-sm">{l.title}</div>
            </>
          );
          return ready ? (
            <Link
              key={l.slug}
              href={`/darslar/${l.slug}/`}
              onClick={onNavigate}
              title={l.title}
              className={`block rounded-lg px-3 py-2 hover:bg-[var(--skin-surface-2)] ${
                active ? "bg-[var(--skin-surface-2)] font-medium" : ""
              }`}
            >
              {inner}
            </Link>
          ) : (
            <span
              key={l.slug}
              title={`${l.title} — rejada`}
              className="block rounded-lg px-3 py-2 opacity-45"
            >
              {inner}
            </span>
          );
        })}
      </div>
      <div className="border-t border-[var(--skin-border)] px-4 py-3 text-xs text-[var(--skin-muted)]">
        {lessons.length} ta case study
      </div>
    </>
  );
}

/**
 * Slug'dan barqaror "qisqartirilgan kalit" yasaydi — skin uchun bezak.
 * Haqiqiy tizimda kalit tasodifiy bo'ladi (3-bo'limga qarang), bu yerda esa
 * har safar bir xil ko'rinishi uchun deterministik.
 */
function shortKey(slug: string): string {
  const ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let h = 2166136261;
  for (let i = 0; i < slug.length; i++) {
    h ^= slug.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  let out = "";
  for (let i = 0; i < 6; i++) {
    out += ALPHABET[h % 62];
    h = Math.floor(h / 62) + slug.length * (i + 7);
  }
  return out;
}

/** Rasmiy logotip emas — soddalashtirilgan zanjir belgisi. */
function LinkMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" aria-hidden>
      <rect x="1.5" y="1.5" width="21" height="21" rx="6" fill="var(--skin-accent)" />
      <path
        d="M10 14a3 3 0 0 0 4.2.2l2-1.9a3 3 0 0 0-4.1-4.4l-.9.8M14 10a3 3 0 0 0-4.2-.2l-2 1.9a3 3 0 0 0 4.1 4.4l.9-.8"
        stroke="#fff"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}
