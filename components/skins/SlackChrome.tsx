"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";

const channelName = (order: number, slug: string) =>
  `${String(order).padStart(2, "0")}-${slug}`;

/**
 * Slack skini: quyuq yon panel (kanallar = darslar) + yorug' xabar oqimi.
 * Presence nuqtalari, kanal sarlavhasi va bezak uchun xabar maydoni bor.
 */
export function SlackChrome({ slug, children }: { slug: string; children: ReactNode }) {
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

  const channels = (onNavigate?: () => void) => (
    <>
      <div className="px-2 py-1.5 text-[13px] font-semibold text-[var(--slack-side-text)]">
        Kanallar
      </div>
      {lessons.map((l) => {
        const active = l.slug === slug;
        const label = (
          <>
            <span aria-hidden className="w-3 shrink-0 text-center opacity-70">
              #
            </span>
            <span className="min-w-0 truncate">{channelName(l.order, l.slug)}</span>
          </>
        );
        return l.status === "tayyor" ? (
          <Link
            key={l.slug}
            href={`/darslar/${l.slug}/`}
            onClick={onNavigate}
            title={l.title}
            className={`flex items-center gap-1.5 rounded px-2 py-[5px] text-[15px] ${
              active
                ? "bg-[var(--slack-active)] font-bold text-white"
                : "text-[var(--slack-side-text)] hover:bg-[var(--slack-side-hover)]"
            }`}
          >
            {label}
          </Link>
        ) : (
          <span
            key={l.slug}
            title={`${l.title} — rejada`}
            className="flex cursor-default items-center gap-1.5 rounded px-2 py-[5px] text-[15px] text-[var(--slack-side-text)] opacity-45"
          >
            {label}
          </span>
        );
      })}
    </>
  );

  return (
    <div className="min-h-screen">
      {/* Yuqori panel */}
      <header className="sticky top-0 z-30 select-none bg-[var(--slack-rail)] text-white">
        <div className="flex items-center gap-2 px-3 py-1.5">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Kanallar ro'yxatini ochish"
            className="flex h-8 w-8 items-center justify-center rounded text-white/80 hover:bg-white/10 lg:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
              <path
                d="M4 7h16M4 12h16M4 17h16"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </button>

          <div
            aria-hidden
            className="mx-auto hidden w-full max-w-[560px] items-center gap-2 rounded-md bg-white/10 px-3 py-1 text-[13px] text-white/70 md:flex"
          >
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" aria-hidden>
              <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.8" />
              <path d="M16 16l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
            darslik ish maydonida qidirish
          </div>

          <div ref={menuRef} className="relative ml-auto">
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              className="flex items-center gap-2 rounded px-2 py-1 text-[13px] hover:bg-white/10"
            >
              <span className="relative flex h-6 w-6 items-center justify-center rounded bg-white/20 text-[11px] font-bold">
                DL
                <span
                  aria-hidden
                  className="absolute -right-0.5 -bottom-0.5 h-2.5 w-2.5 rounded-full border-2 border-[var(--slack-rail)] bg-[var(--slack-online)]"
                />
              </span>
              <span className="hidden sm:inline">
                #{channelName(current?.order ?? 6, slug)}
              </span>
              <span
                aria-hidden
                className={`opacity-70 transition-transform ${menuOpen ? "rotate-180" : ""}`}
              >
                ▾
              </span>
            </button>
            {menuOpen ? (
              <div
                role="menu"
                className="absolute top-full right-0 mt-1.5 max-h-[70vh] w-[300px] overflow-y-auto rounded-lg border border-[var(--skin-border)] bg-white p-1.5 text-[var(--skin-text)] shadow-2xl"
              >
                {lessons.map((l) => {
                  const body = (
                    <>
                      <span aria-hidden className="text-[var(--skin-muted)]">
                        #
                      </span>
                      <span className="min-w-0 flex-1 truncate">{l.title}</span>
                      {l.slug === slug ? (
                        <span className="text-[var(--slack-active)]">•</span>
                      ) : null}
                    </>
                  );
                  return l.status === "tayyor" ? (
                    <Link
                      key={l.slug}
                      href={`/darslar/${l.slug}/`}
                      role="menuitem"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 rounded px-3 py-2 text-sm hover:bg-[var(--skin-surface-2)]"
                    >
                      {body}
                    </Link>
                  ) : (
                    <span
                      key={l.slug}
                      className="flex cursor-default items-center gap-2 rounded px-3 py-2 text-sm opacity-40"
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

      <div className="flex">
        {/* Ish maydoni ustuni */}
        <div className="sticky top-[41px] hidden h-[calc(100vh-41px)] w-[68px] shrink-0 flex-col items-center gap-3 bg-[var(--slack-rail)] pt-3 lg:flex">
          <Link
            href="/"
            title="Bosh sahifa"
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-[13px] font-black text-[var(--slack-side)]"
          >
            SD
          </Link>
          <div
            aria-hidden
            className="h-9 w-9 rounded-xl border-2 border-dashed border-white/20"
          />
        </div>

        {/* Kanallar paneli */}
        <aside className="sticky top-[41px] hidden h-[calc(100vh-41px)] w-[232px] shrink-0 overflow-y-auto bg-[var(--slack-side)] px-2 pb-6 lg:block">
          <div className="sticky top-0 -mx-2 mb-2 border-b border-white/10 bg-[var(--slack-side)] px-4 py-3">
            <div className="text-[15px] font-black text-white">system-design</div>
            <div className="mt-0.5 flex items-center gap-1.5 text-[13px] text-[var(--slack-side-text)]">
              <span
                aria-hidden
                className="h-2 w-2 rounded-full bg-[var(--slack-online)]"
              />
              darslik
            </div>
          </div>
          {channels()}
          <div className="mt-4 px-2 text-[13px] text-[var(--slack-side-text)]/70">
            {ready.length} ta kanal faol · {lessons.length - ready.length} ta arxivda
          </div>
        </aside>

        {/* Xabar maydoni */}
        <div className="flex min-w-0 flex-1 flex-col bg-[var(--skin-bg)]">
          {/* Kanal sarlavhasi */}
          <div className="sticky top-[41px] z-20 flex items-center gap-3 border-b border-[var(--skin-border)] bg-[var(--skin-bg)] px-4 py-2.5 sm:px-6">
            <div className="min-w-0">
              <div className="truncate text-[15px] font-black">
                <span aria-hidden className="text-[var(--skin-muted)]">
                  #
                </span>
                {channelName(current?.order ?? 6, slug)}
              </div>
              <div className="truncate text-[13px] text-[var(--skin-muted)]">
                {current?.summary ?? "Tizim dizayni darsligi"}
              </div>
            </div>
            <div
              aria-hidden
              className="ml-auto hidden items-center gap-1 rounded border border-[var(--skin-border)] px-2 py-1 text-[13px] text-[var(--skin-muted)] sm:flex"
            >
              <span className="h-2 w-2 rounded-full bg-[var(--slack-online)]" />
              ulangan
            </div>
          </div>

          {/* Xabar */}
          <div className="mx-auto w-full max-w-[860px] px-4 pt-5 pb-24 sm:px-6">
            <div className="flex gap-3">
              <div
                aria-hidden
                className="relative hidden h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--skin-accent)] text-sm font-black text-white sm:flex"
              >
                DL
                <span className="absolute -right-1 -bottom-1 h-3 w-3 rounded-full border-2 border-white bg-[var(--slack-online)]" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex flex-wrap items-baseline gap-2">
                  <span className="text-[15px] font-black">darslik</span>
                  <span className="rounded bg-[var(--skin-surface-2)] px-1.5 py-0.5 text-[11px] font-bold tracking-wide text-[var(--skin-muted)] uppercase">
                    bot
                  </span>
                  <span className="text-[12px] text-[var(--skin-muted)]">
                    Dars {String(current?.order ?? 6).padStart(2, "0")} · {current?.minutes ?? 0}{" "}
                    daqiqa
                  </span>
                </div>
                {children}
              </div>
            </div>
          </div>

          {/* Bezak uchun xabar maydoni */}
          <div
            aria-hidden
            className="sticky bottom-0 mx-auto w-full max-w-[860px] px-4 pb-4 sm:px-6"
          >
            <div className="flex items-center gap-2 rounded-lg border border-[var(--skin-border)] bg-[var(--skin-bg)] px-3 py-2.5 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
              <span className="text-[var(--skin-muted)]">+</span>
              <span className="min-w-0 flex-1 truncate text-sm text-[var(--skin-muted)]">
                #{channelName(current?.order ?? 6, slug)} kanaliga yozish
              </span>
              <span className="flex h-6 w-6 items-center justify-center rounded bg-[var(--slack-online)] text-xs text-white">
                ➤
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobil panel */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col bg-[var(--slack-side)] p-2 shadow-2xl">
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              aria-label="Panelni yopish"
              className="absolute top-2 right-2 flex h-9 w-9 items-center justify-center rounded text-white/70 hover:bg-white/10"
            >
              ×
            </button>
            <div className="mt-1 mb-2 px-2 text-[15px] font-black text-white">system-design</div>
            <div className="min-h-0 flex-1 overflow-y-auto">
              {channels(() => setDrawerOpen(false))}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
