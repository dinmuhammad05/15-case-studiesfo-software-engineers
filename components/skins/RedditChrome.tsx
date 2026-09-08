"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";

/**
 * Reddit skini: ovoz ustuni + post kartochkasi.
 * Chapda "subredditlar" (darslar), o'rtada post, o'ngda jamoa paneli.
 */
export function RedditChrome({ slug, children }: { slug: string; children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [vote, setVote] = useState<"up" | "down" | null>(null);
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
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 select-none border-b border-[var(--skin-border)] bg-[var(--skin-surface)]">
        <div className="mx-auto flex max-w-[1200px] items-center gap-3 px-3 py-2">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Darslar ro'yxatini ochish"
            className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-[var(--skin-surface-2)] lg:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>

          <Link href="/" className="flex items-center gap-2">
            <Snoo className="h-8 w-8" />
            <span className="hidden font-bold sm:inline">darslik</span>
          </Link>

          <div
            aria-hidden
            className="ml-2 hidden min-w-0 flex-1 items-center rounded-full border border-[var(--skin-border)] bg-[var(--skin-bg)] px-4 py-1.5 text-sm text-[var(--skin-muted)] md:flex"
          >
            r/system_design ichida qidirish…
          </div>

          <div ref={menuRef} className="relative ml-auto">
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              className="flex items-center gap-1.5 rounded-full border border-[var(--skin-border)] px-3 py-1.5 text-sm font-medium hover:bg-[var(--skin-surface-2)]"
            >
              r/dars{String(current?.order ?? 5).padStart(2, "0")}
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
                className="absolute right-0 top-full mt-1.5 max-h-[70vh] w-[300px] overflow-y-auto rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-surface)] p-1.5 shadow-2xl"
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
                      className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm hover:bg-[var(--skin-surface-2)]"
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

      <div className="mx-auto flex max-w-[1200px] gap-6 px-3 py-5">
        {/* Chap: "subredditlar" */}
        <aside className="sticky top-[61px] hidden h-[calc(100vh-80px)] w-[240px] shrink-0 overflow-y-auto rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-surface)] p-2 lg:block">
          <div className="px-3 py-2 text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
            Darslar
          </div>
          {lessons.map((l) =>
            l.status === "tayyor" ? (
              <Link
                key={l.slug}
                href={`/darslar/${l.slug}/`}
                title={l.title}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-[var(--skin-surface-2)] ${
                  l.slug === slug ? "bg-[var(--skin-surface-2)] font-semibold" : ""
                }`}
              >
                <span
                  aria-hidden
                  className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--skin-accent)] text-[10px] font-bold text-[var(--skin-accent-text)]"
                >
                  {l.order}
                </span>
                <span className="min-w-0 truncate">{l.title}</span>
              </Link>
            ) : (
              <span
                key={l.slug}
                title={`${l.title} — rejada`}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm opacity-40"
              >
                <span
                  aria-hidden
                  className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[var(--skin-border)] text-[10px]"
                >
                  {l.order}
                </span>
                <span className="min-w-0 truncate">{l.title}</span>
              </span>
            ),
          )}
        </aside>

        {/* O'rta: post kartochkasi */}
        <div className="min-w-0 flex-1">
          <div className="rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-surface)]">
            <div className="flex">
              {/* Ovoz ustuni */}
              <div className="flex w-12 shrink-0 flex-col items-center gap-1 rounded-l-2xl bg-[var(--skin-surface-2)] py-4">
                <button
                  type="button"
                  onClick={() => setVote(vote === "up" ? null : "up")}
                  aria-label="Yoqdi"
                  className={`flex h-7 w-7 items-center justify-center rounded hover:bg-[var(--skin-border)] ${
                    vote === "up" ? "text-[var(--skin-accent)]" : "text-[var(--skin-muted)]"
                  }`}
                >
                  ▲
                </button>
                <span className="font-[family-name:var(--skin-mono)] text-xs font-bold">
                  {vote === "up" ? "4.3k" : vote === "down" ? "4.3k" : "4.3k"}
                </span>
                <button
                  type="button"
                  onClick={() => setVote(vote === "down" ? null : "down")}
                  aria-label="Yoqmadi"
                  className={`flex h-7 w-7 items-center justify-center rounded hover:bg-[var(--skin-border)] ${
                    vote === "down" ? "text-[#7193ff]" : "text-[var(--skin-muted)]"
                  }`}
                >
                  ▼
                </button>
              </div>

              <div className="min-w-0 flex-1 px-4 py-4 sm:px-6">{children}</div>
            </div>
          </div>
        </div>

        {/* O'ng: jamoa paneli */}
        <aside className="sticky top-[61px] hidden h-fit w-[300px] shrink-0 xl:block">
          <div className="rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
            <div className="mb-3 font-bold">r/system_design</div>
            <p className="mb-4 text-sm text-[var(--skin-muted)]">
              Tizim dizayni bo‘yicha o‘zbek tilidagi darslik. Har bir dars noldan bugungi
              arxitekturagacha, hisob-kitob bilan.
            </p>
            <div className="grid grid-cols-2 gap-3 border-t border-[var(--skin-border)] pt-3 text-sm">
              <div>
                <div className="font-bold">{ready.length}</div>
                <div className="text-xs text-[var(--skin-muted)]">tayyor dars</div>
              </div>
              <div>
                <div className="font-bold">{lessons.length - ready.length}</div>
                <div className="text-xs text-[var(--skin-muted)]">rejada</div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      {/* Mobil drawer */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col bg-[var(--skin-surface)] p-3 shadow-2xl">
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              aria-label="Panelni yopish"
              className="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-full text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
            >
              ×
            </button>
            <div className="mb-3 mt-1 px-2 text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
              Darslar
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">
              {lessons.map((l) =>
                l.status === "tayyor" ? (
                  <Link
                    key={l.slug}
                    href={`/darslar/${l.slug}/`}
                    onClick={() => setDrawerOpen(false)}
                    className={`block truncate rounded-lg px-3 py-2.5 text-sm hover:bg-[var(--skin-surface-2)] ${
                      l.slug === slug ? "font-bold" : ""
                    }`}
                  >
                    {l.title}
                  </Link>
                ) : (
                  <span
                    key={l.slug}
                    className="block truncate rounded-lg px-3 py-2.5 text-sm opacity-40"
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

/** Rasmiy logotip emas — soddalashtirilgan belgi. */
function Snoo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <circle cx="16" cy="16" r="15" fill="var(--skin-accent)" />
      <circle cx="16" cy="19" r="9" fill="#fff" />
      <circle cx="12.5" cy="18" r="1.7" fill="var(--skin-accent)" />
      <circle cx="19.5" cy="18" r="1.7" fill="var(--skin-accent)" />
      <path d="M12.5 22.5c1.2 1.1 5.8 1.1 7 0" stroke="var(--skin-accent)" strokeWidth="1.3" fill="none" strokeLinecap="round" />
      <circle cx="16" cy="7" r="2" fill="#fff" />
      <path d="M16 9v3" stroke="#fff" strokeWidth="1.3" />
    </svg>
  );
}
