"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";

/**
 * ChatGPT skinining interaktiv qismi.
 * - Mobil'da ☰ tugmasi sidebar'ni chekka panel (drawer) sifatida ochadi
 * - Sarlavha tugmasi darslar ro'yxatini dropdown qilib ochadi (model tanlagichga o'xshab)
 * Kontent (children) serverda render qilinadi va shu yerga uzatiladi.
 */
export function ChatGptChrome({ slug, children }: { slug: string; children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const current = lessons.find((l) => l.slug === slug);

  // Escape ikkalasini ham yopadi
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

  // Dropdown tashqarisiga bosilsa yopiladi
  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [menuOpen]);

  // Drawer ochiq turganda orqa fon skroll qilmasin
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  return (
    <div className="flex min-h-screen">
      {/* Doimiy sidebar — katta ekranlarda */}
      <aside className="sticky top-0 hidden h-screen w-[260px] shrink-0 flex-col border-r border-[var(--skin-border)] bg-[#171717] lg:flex">
        <SidebarContent slug={slug} />
      </aside>

      {/* Mobil drawer */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85vw] flex-col border-r border-[var(--skin-border)] bg-[#171717] shadow-2xl">
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              aria-label="Panelni yopish"
              className="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-lg text-lg text-[var(--skin-muted)] hover:bg-white/10"
            >
              ×
            </button>
            <SidebarContent slug={slug} onNavigate={() => setDrawerOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Yuqori panel */}
        <div className="sticky top-0 z-30 flex select-none items-center gap-1 border-b border-[var(--skin-border)] bg-[var(--skin-bg)]/85 px-2 py-2 backdrop-blur sm:px-3">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            aria-label="Darslar ro'yxatini ochish"
            className="flex h-9 w-9 items-center justify-center rounded-lg hover:bg-white/10 lg:hidden"
          >
            <BurgerIcon />
          </button>

          <div ref={menuRef} className="relative">
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-medium hover:bg-white/10"
            >
              Dars {String(current?.order ?? 1).padStart(2, "0")}
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
                className="absolute left-0 top-full mt-1.5 max-h-[70vh] w-[300px] overflow-y-auto rounded-2xl border border-[var(--skin-border)] bg-[var(--skin-surface)] p-1.5 shadow-2xl"
              >
                {lessons.map((l) => {
                  const ready = l.status === "tayyor";
                  const active = l.slug === slug;
                  const body = (
                    <>
                      <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-muted)]">
                        {String(l.order).padStart(2, "0")}
                      </span>
                      <span className="min-w-0 flex-1 truncate">{l.title}</span>
                      {active ? <span className="text-[var(--skin-accent)]">✓</span> : null}
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
                      className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm hover:bg-white/10"
                    >
                      {body}
                    </Link>
                  ) : (
                    <span
                      key={l.slug}
                      className="flex cursor-default items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm opacity-45"
                    >
                      {body}
                    </span>
                  );
                })}
              </div>
            ) : null}
          </div>
        </div>

        <main className="mx-auto w-full max-w-3xl flex-1 px-4 pt-8 pb-4 sm:px-6">{children}</main>

        {/* Dekorativ kompozitor */}
        <div
          aria-hidden
          className="sticky bottom-0 bg-gradient-to-t from-[var(--skin-bg)] to-transparent px-4 pb-5 pt-8"
        >
          <div className="mx-auto flex max-w-3xl items-center gap-3 rounded-[26px] border border-[var(--skin-border)] bg-[var(--skin-surface)] px-5 py-3.5 text-sm text-[var(--skin-muted)]">
            <span className="flex-1">Savolingizni yozing…</span>
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--skin-accent)] text-[var(--skin-accent-text)]">
              ↑
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function SidebarContent({ slug, onNavigate }: { slug: string; onNavigate?: () => void }) {
  return (
    <>
      <div className="p-3">
        <Link
          href="/"
          onClick={onNavigate}
          className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-white/5"
        >
          <Logo className="h-5 w-5" />
          Darslik
        </Link>
        <Link
          href="/darslar/"
          onClick={onNavigate}
          className="mt-1 flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm hover:bg-white/5"
        >
          <span className="text-lg leading-none">+</span> Barcha darslar
        </Link>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-4">
        <div className="px-3 py-2 text-xs font-medium text-[var(--skin-muted)]">Kurs rejasi</div>
        {lessons.map((l) =>
          l.status === "tayyor" ? (
            <Link
              key={l.slug}
              href={`/darslar/${l.slug}/`}
              onClick={onNavigate}
              title={l.title}
              className={`block truncate rounded-lg px-3 py-2 text-sm hover:bg-white/5 ${
                l.slug === slug ? "bg-white/10" : "text-[var(--skin-muted)]"
              }`}
            >
              {l.title}
            </Link>
          ) : (
            <span
              key={l.slug}
              title={`${l.title} — rejada`}
              className="block truncate rounded-lg px-3 py-2 text-sm text-[var(--skin-muted)] opacity-50"
            >
              {l.title}
            </span>
          ),
        )}
      </div>
      <div className="border-t border-[var(--skin-border)] p-3 text-xs text-[var(--skin-muted)]">
        {lessons.length} ta case study · o‘zbek tilida
      </div>
    </>
  );
}

function BurgerIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path
        d="M4 7h16M4 12h16M4 17h16"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

/** Rasmiy logotip emas — soddalashtirilgan o'z belgimiz. */
function Logo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="var(--skin-accent)" strokeWidth="1.6" />
      <path
        d="M12 7.5v9M7.7 9.75l8.6 4.5M16.3 9.75l-8.6 4.5"
        stroke="var(--skin-accent)"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}
