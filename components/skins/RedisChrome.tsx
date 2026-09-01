"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";

/**
 * Redis skini: redis-cli terminal oynasi.
 * Chapda "keyspace" (darslar kalit sifatida), o'rtada terminal chiqishi,
 * pastda dekorativ prompt satri.
 */
export function RedisChrome({ slug, children }: { slug: string; children: ReactNode }) {
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
      {/* Terminal oynasining sarlavha paneli */}
      <header className="sticky top-0 z-30 select-none border-b border-[var(--skin-border)] bg-[var(--skin-surface)]">
        <div className="flex items-center gap-3 px-3 py-2">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Darslar ro'yxatini ochish"
            className="flex h-8 w-8 items-center justify-center rounded hover:bg-[var(--skin-surface-2)] lg:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>

          <div aria-hidden className="hidden items-center gap-2 lg:flex">
            <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          </div>

          <Link
            href="/"
            className="font-[family-name:var(--skin-mono)] text-sm text-[var(--skin-muted)] hover:text-[var(--skin-text)]"
          >
            darslik@system-design
          </Link>
          <span aria-hidden className="text-[var(--skin-muted)]">
            :
          </span>
          <span className="font-[family-name:var(--skin-mono)] text-sm text-[var(--skin-accent)]">
            ~/darslar/{slug}
          </span>

          <div ref={menuRef} className="relative ml-auto">
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              className="flex items-center gap-1.5 rounded border border-[var(--skin-border)] px-2.5 py-1 font-[family-name:var(--skin-mono)] text-xs hover:bg-[var(--skin-surface-2)]"
            >
              DB {String(current?.order ?? 3).padStart(2, "0")}
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
                className="absolute right-0 top-full mt-1.5 max-h-[70vh] w-[300px] overflow-y-auto rounded border border-[var(--skin-border)] bg-[var(--skin-surface)] p-1 shadow-2xl"
              >
                {lessons.map((l) => {
                  const ready = l.status === "tayyor";
                  const body = (
                    <>
                      <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-accent)]">
                        [{String(l.order).padStart(2, "0")}]
                      </span>
                      <span className="min-w-0 flex-1 truncate">{l.title}</span>
                      {l.slug === slug ? <span className="text-[var(--skin-accent)]">*</span> : null}
                    </>
                  );
                  return ready ? (
                    <Link
                      key={l.slug}
                      href={`/darslar/${l.slug}/`}
                      role="menuitem"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 rounded px-2.5 py-2 text-sm hover:bg-[var(--skin-surface-2)]"
                    >
                      {body}
                    </Link>
                  ) : (
                    <span
                      key={l.slug}
                      className="flex cursor-default items-center gap-2 rounded px-2.5 py-2 text-sm opacity-40"
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
        <aside className="sticky top-[45px] hidden h-[calc(100vh-45px)] w-[250px] shrink-0 flex-col border-r border-[var(--skin-border)] bg-[var(--skin-surface)] lg:flex">
          <SidebarContent slug={slug} />
        </aside>

        {drawerOpen ? (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              aria-label="Yopish"
              onClick={() => setDrawerOpen(false)}
              className="absolute inset-0 bg-black/60"
            />
            <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col bg-[var(--skin-surface)] shadow-2xl">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
              >
                ×
              </button>
              <SidebarContent slug={slug} onNavigate={() => setDrawerOpen(false)} />
            </aside>
          </div>
        ) : null}

        <div className="min-w-0 flex-1">
          <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">{children}</main>

          {/* Dekorativ prompt satri */}
          <div
            aria-hidden
            className="sticky bottom-0 border-t border-[var(--skin-border)] bg-[var(--skin-bg)]/90 px-4 py-2.5 backdrop-blur sm:px-6"
          >
            <div className="mx-auto flex max-w-3xl items-center gap-2 font-[family-name:var(--skin-mono)] text-sm">
              <span className="text-[var(--skin-accent)]">127.0.0.1:6379&gt;</span>
              <span className="inline-block h-4 w-2 animate-pulse bg-[var(--skin-text)]" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SidebarContent({ slug, onNavigate }: { slug: string; onNavigate?: () => void }) {
  return (
    <>
      <div className="border-b border-[var(--skin-border)] px-3 py-2.5 font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-muted)]">
        KEYS darslar:*
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-1.5">
        {lessons.map((l) => {
          const ready = l.status === "tayyor";
          const active = l.slug === slug;
          const inner = (
            <>
              <span className="font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">
                {String(l.order).padStart(2, "0")})
              </span>
              <span className="min-w-0 flex-1 truncate">{l.title}</span>
            </>
          );
          return ready ? (
            <Link
              key={l.slug}
              href={`/darslar/${l.slug}/`}
              onClick={onNavigate}
              title={l.title}
              className={`flex items-center gap-2 rounded px-2.5 py-1.5 text-sm hover:bg-[var(--skin-surface-2)] ${
                active
                  ? "bg-[var(--skin-surface-2)] text-[var(--skin-accent)]"
                  : "text-[var(--skin-text)]"
              }`}
            >
              {inner}
            </Link>
          ) : (
            <span
              key={l.slug}
              title={`${l.title} — rejada`}
              className="flex items-center gap-2 rounded px-2.5 py-1.5 text-sm opacity-40"
            >
              {inner}
            </span>
          );
        })}
      </div>
      <div className="border-t border-[var(--skin-border)] px-3 py-2 font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">
        ({lessons.length}) keys
      </div>
    </>
  );
}
