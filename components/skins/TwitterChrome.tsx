"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";

/**
 * Twitter tasmasi skini: uch ustunli tasma ko'rinishi.
 * Chapda navigatsiya, o'rtada "tasma" (dars matni), o'ngda "nima bo'lyapti" paneli.
 */
export function TwitterChrome({ slug, children }: { slug: string; children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const current = lessons.find((l) => l.slug === slug);
  const ready = lessons.filter((l) => l.status === "tayyor");

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
    <div className="mx-auto flex max-w-[1265px] justify-center">
      {/* Chap ustun — navigatsiya */}
      <nav className="sticky top-0 hidden h-screen w-[68px] shrink-0 flex-col items-center gap-1 border-r border-[var(--skin-border)] px-2 py-3 sm:flex xl:w-[275px] xl:items-start">
        <Link
          href="/"
          className="mb-2 flex h-12 w-12 items-center justify-center rounded-full hover:bg-[var(--skin-surface)]"
        >
          <Bird className="h-7 w-7" />
        </Link>
        {[
          { label: "Bosh sahifa", href: "/", icon: "⌂" },
          { label: "Kurs rejasi", href: "/darslar/", icon: "☰" },
        ].map((it) => (
          <Link
            key={it.href}
            href={it.href}
            className="flex items-center gap-4 rounded-full px-3 py-3 text-lg hover:bg-[var(--skin-surface)] xl:pr-6"
          >
            <span aria-hidden className="w-6 text-center">
              {it.icon}
            </span>
            <span className="hidden xl:inline">{it.label}</span>
          </Link>
        ))}
        <div className="mt-auto hidden w-full rounded-2xl border border-[var(--skin-border)] p-3 text-xs text-[var(--skin-muted)] xl:block">
          {ready.length}/{lessons.length} dars tayyor
        </div>
      </nav>

      {/* O'rta ustun — tasma */}
      <div className="min-w-0 flex-1 border-x border-[var(--skin-border)] sm:max-w-[600px]">
        <header className="sticky top-0 z-30 select-none border-b border-[var(--skin-border)] bg-[var(--skin-bg)]/80 backdrop-blur">
          <div className="flex items-center gap-3 px-4 py-3">
            <button
              type="button"
              onClick={() => setDrawerOpen(true)}
              aria-label="Darslar ro'yxatini ochish"
              className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-[var(--skin-surface)] sm:hidden"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
                <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
            <div className="min-w-0">
              <div className="truncate font-bold">Tasma</div>
              <div className="truncate text-xs text-[var(--skin-muted)]">
                Dars {String(current?.order ?? 4).padStart(2, "0")}
              </div>
            </div>
            <div ref={menuRef} className="relative ml-auto">
              <button
                type="button"
                onClick={() => setMenuOpen((v) => !v)}
                aria-expanded={menuOpen}
                aria-haspopup="menu"
                className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-[var(--skin-surface)]"
                aria-label="Darslar ro'yxati"
              >
                <span aria-hidden className="text-xl leading-none">
                  ⋯
                </span>
              </button>
              {menuOpen ? (
                <div
                  role="menu"
                  className="absolute right-0 top-full mt-1 max-h-[70vh] w-[290px] overflow-y-auto rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-bg)] p-1.5 shadow-2xl"
                >
                  {lessons.map((l) => {
                    const isReady = l.status === "tayyor";
                    const body = (
                      <>
                        <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-accent)]">
                          {String(l.order).padStart(2, "0")}
                        </span>
                        <span className="min-w-0 flex-1 truncate">{l.title}</span>
                        {l.slug === slug ? <span className="text-[var(--skin-accent)]">•</span> : null}
                      </>
                    );
                    return isReady ? (
                      <Link
                        key={l.slug}
                        href={`/darslar/${l.slug}/`}
                        role="menuitem"
                        onClick={() => setMenuOpen(false)}
                        className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm hover:bg-[var(--skin-surface)]"
                      >
                        {body}
                      </Link>
                    ) : (
                      <span
                        key={l.slug}
                        className="flex cursor-default items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm opacity-40"
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

        <main className="px-4 py-6 sm:px-6">{children}</main>
      </div>

      {/* O'ng ustun */}
      <aside className="sticky top-0 hidden h-screen w-[350px] shrink-0 overflow-y-auto px-6 py-4 lg:block">
        <div className="rounded-2xl bg-[var(--skin-surface)] p-4">
          <div className="mb-3 text-lg font-bold">Kursda nima bor</div>
          <div className="space-y-3">
            {ready.map((l) => (
              <Link key={l.slug} href={`/darslar/${l.slug}/`} className="block group">
                <div className="text-xs text-[var(--skin-muted)]">
                  Dars {String(l.order).padStart(2, "0")} · {l.minutes} daq
                </div>
                <div className="text-sm font-semibold group-hover:underline">{l.title}</div>
              </Link>
            ))}
          </div>
        </div>
        <div className="mt-4 rounded-2xl bg-[var(--skin-surface)] p-4 text-sm text-[var(--skin-muted)]">
          Keyingi darslar tayyorlanmoqda — {lessons.length - ready.length} ta mavzu rejada.
        </div>
      </aside>

      {/* Mobil drawer */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 sm:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col bg-[var(--skin-bg)] p-3 shadow-2xl">
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              aria-label="Panelni yopish"
              className="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-full text-[var(--skin-muted)] hover:bg-[var(--skin-surface)]"
            >
              ×
            </button>
            <Link href="/" className="mb-2 flex h-12 w-12 items-center justify-center">
              <Bird className="h-7 w-7" />
            </Link>
            <div className="min-h-0 flex-1 overflow-y-auto">
              {lessons.map((l) =>
                l.status === "tayyor" ? (
                  <Link
                    key={l.slug}
                    href={`/darslar/${l.slug}/`}
                    onClick={() => setDrawerOpen(false)}
                    className={`block truncate rounded-full px-4 py-2.5 text-sm hover:bg-[var(--skin-surface)] ${
                      l.slug === slug ? "font-bold" : ""
                    }`}
                  >
                    {l.title}
                  </Link>
                ) : (
                  <span
                    key={l.slug}
                    className="block truncate rounded-full px-4 py-2.5 text-sm opacity-40"
                  >
                    {l.title}
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

/** Rasmiy logotip emas — soddalashtirilgan qush belgisi. */
function Bird({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" aria-hidden>
      <path
        d="M21 5.2c-.7.3-1.4.5-2.2.6.8-.5 1.4-1.2 1.7-2.1-.7.4-1.6.8-2.4 1a3.8 3.8 0 0 0-6.5 3.4A10.8 10.8 0 0 1 3.8 4.1a3.8 3.8 0 0 0 1.2 5.1c-.6 0-1.2-.2-1.7-.5v.1c0 1.8 1.3 3.4 3 3.7-.5.2-1.1.2-1.7.1a3.8 3.8 0 0 0 3.6 2.6A7.7 7.7 0 0 1 3 17c1.8 1.1 3.8 1.8 6 1.8 7.2 0 11.1-6 11.1-11.1v-.5c.8-.6 1.4-1.3 1.9-2Z"
        fill="var(--skin-accent)"
      />
    </svg>
  );
}
