"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { ReadingProgress } from "@/components/lesson/Progress";
import { AuthorPhoto } from "@/components/AuthorPhoto";

const pad = (n: number) => String(n).padStart(2, "0");

/**
 * WhatsApp Web skini: yuqorida yashil tasma, chapda suhbatlar (darslar),
 * o'ngda gulqog'ozli suhbat oynasi. Dars — kiruvchi xabar pufakchasi.
 */
export function WhatsAppChrome({ slug, children }: { slug: string; children: ReactNode }) {
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

  const chatList = (onNavigate?: () => void) =>
    lessons.map((l) => {
      const ready = l.status === "tayyor";
      const active = l.slug === slug;
      const row = (
        <>
          <span
            aria-hidden
            className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
              ready ? "text-white" : "bg-[#dfe5e7] text-[#8696a0]"
            }`}
            style={ready ? { backgroundColor: l.accent } : undefined}
          >
            {pad(l.order)}
          </span>
          <span className="min-w-0 flex-1 border-b border-[#e9edef] py-3 pr-1">
            <span className="flex items-baseline gap-2">
              <span className="min-w-0 flex-1 truncate text-[16px] text-[var(--skin-text)]">
                {l.title}
              </span>
              <span
                className={`shrink-0 text-[12px] ${
                  ready && !active ? "text-[var(--wa-unread)]" : "text-[var(--skin-muted)]"
                }`}
              >
                {ready ? `${l.minutes} daq` : "rejada"}
              </span>
            </span>
            <span className="mt-0.5 flex items-center gap-2">
              <span className="min-w-0 flex-1 truncate text-[14px] text-[var(--skin-muted)]">
                {ready ? (
                  <>
                    <span aria-hidden className="mr-1 text-[var(--wa-tick)]">
                      ✓✓
                    </span>
                    {l.summary}
                  </>
                ) : (
                  l.summary
                )}
              </span>
              {ready && !active ? (
                <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-[var(--wa-unread)] px-1.5 text-[11px] font-bold text-white">
                  1
                </span>
              ) : null}
            </span>
          </span>
        </>
      );
      return ready ? (
        <Link
          key={l.slug}
          href={`/darslar/${l.slug}/`}
          onClick={onNavigate}
          title={l.title}
          className={`flex items-center gap-3 pl-3 hover:bg-[#f5f6f6] ${
            active ? "bg-[#f0f2f5]" : ""
          }`}
        >
          {row}
        </Link>
      ) : (
        <span
          key={l.slug}
          title={`${l.title} — rejada`}
          className="flex cursor-default items-center gap-3 pl-3 opacity-60"
        >
          {row}
        </span>
      );
    });

  return (
    <div className="relative min-h-screen">

      <div className="relative flex min-h-screen">
        {/* Chap: suhbatlar ro'yxati */}
        <aside className="sticky top-0 hidden h-screen w-[30%] max-w-[480px] min-w-[340px] shrink-0 flex-col border-r border-[#e9edef] bg-white lg:flex">
          <div className="flex h-[59px] shrink-0 items-center gap-3 bg-[var(--skin-surface-2)] px-4">
            <Link href="/" title="Bosh sahifa" className="h-10 w-10 shrink-0 overflow-hidden rounded-full">
              <AuthorPhoto
                className="h-full w-full"
                fallback={
                  <span className="flex h-full w-full items-center justify-center bg-[var(--skin-accent)] text-sm font-bold text-white">
                    SD
                  </span>
                }
              />
            </Link>
            <span className="text-[15px] font-medium">Darslar</span>
            <span aria-hidden className="ml-auto flex gap-4 text-[#54656f]">
              <IconChat />
              <IconDots />
            </span>
          </div>
          <div className="shrink-0 border-b border-[#e9edef] bg-white px-3 py-2">
            <div
              aria-hidden
              className="flex items-center gap-4 rounded-lg bg-[var(--skin-surface-2)] px-4 py-1.5 text-[14px] text-[var(--skin-muted)]"
            >
              <IconSearch />
              Qidirish yoki yangi suhbat
            </div>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">{chatList()}</div>
        </aside>

        {/* O'ng: suhbat oynasi */}
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 select-none bg-[var(--skin-surface-2)]">
            <div className="flex h-[59px] items-center gap-3 px-4">
              <button
                type="button"
                onClick={() => setDrawerOpen(true)}
                aria-label="Suhbatlar ro'yxatini ochish"
                className="-ml-1 flex h-9 w-9 items-center justify-center rounded-full text-[#54656f] hover:bg-black/5 lg:hidden"
              >
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
                  <path d="M15 6l-6 6 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <span aria-hidden className="h-10 w-10 shrink-0 overflow-hidden rounded-full">
                <AuthorPhoto
                  className="h-full w-full"
                  fallback={
                    <span
                      className="flex h-full w-full items-center justify-center text-sm font-bold text-white"
                      style={{ backgroundColor: current?.accent ?? "#25d366" }}
                    >
                      {pad(current?.order ?? 7)}
                    </span>
                  }
                />
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate text-[16px] leading-tight">{current?.title}</div>
                <div className="truncate text-[13px] text-[var(--skin-muted)]">
                  darslik · onlayn
                </div>
              </div>

              <div ref={menuRef} className="relative">
                <button
                  type="button"
                  onClick={() => setMenuOpen((v) => !v)}
                  aria-expanded={menuOpen}
                  aria-haspopup="menu"
                  aria-label="Darslar menyusi"
                  className="flex h-10 w-10 items-center justify-center rounded-full text-[#54656f] hover:bg-black/5"
                >
                  <IconDots />
                </button>
                {menuOpen ? (
                  <div
                    role="menu"
                    className="absolute top-full right-0 mt-1 max-h-[70vh] w-[290px] overflow-y-auto rounded-md bg-white py-2 shadow-[0_2px_5px_rgba(11,20,26,0.26),0_2px_10px_rgba(11,20,26,0.16)]"
                  >
                    {lessons.map((l) =>
                      l.status === "tayyor" ? (
                        <Link
                          key={l.slug}
                          href={`/darslar/${l.slug}/`}
                          role="menuitem"
                          onClick={() => setMenuOpen(false)}
                          className="flex items-center gap-3 px-6 py-2.5 text-[14.5px] hover:bg-[#f5f6f6]"
                        >
                          <span className="w-5 text-[var(--skin-muted)]">{pad(l.order)}</span>
                          <span className="min-w-0 flex-1 truncate">{l.title}</span>
                        </Link>
                      ) : (
                        <span
                          key={l.slug}
                          className="flex cursor-default items-center gap-3 px-6 py-2.5 text-[14.5px] opacity-40"
                        >
                          <span className="w-5">{pad(l.order)}</span>
                          <span className="min-w-0 flex-1 truncate">{l.title}</span>
                        </span>
                      ),
                    )}
                  </div>
                ) : null}
              </div>
            </div>
            <ReadingProgress />
          </header>

          <main className="wa-wallpaper flex-1 px-3 pt-4 pb-24 sm:px-[6%] lg:px-[5%]">
            {/* Shifrlash haqidagi tizim xabari */}
            <div className="mx-auto mb-4 max-w-[560px] rounded-lg bg-[var(--wa-notice)] px-3 py-2 text-center text-[12.5px] leading-snug text-[var(--wa-notice-text)] shadow-[0_1px_0.5px_rgba(11,20,26,0.13)]">
              <span aria-hidden>🔒 </span>
              Bu suhbatdagi xabarlar uchidan-uchiga shifrlangan. Hatto server ham ularni
              o‘qiy olmaydi — bu darsning asosiy mavzusi.
            </div>

            {/* Kiruvchi xabar pufakchasi */}
            <div className="relative mx-auto max-w-[900px]">
              <span
                aria-hidden
                className="absolute top-0 -left-2 h-3 w-3 bg-white [clip-path:polygon(100%_0,0_0,100%_100%)]"
              />
              <div className="rounded-lg rounded-tl-none bg-white px-4 pt-4 pb-2 shadow-[0_1px_0.5px_rgba(11,20,26,0.13)] sm:px-7 sm:pt-6">
                {children}
                <div className="mt-6 flex items-center justify-end gap-1 text-[11px] text-[var(--skin-muted)]">
                  <span>Dars {pad(current?.order ?? 7)}</span>
                  <span aria-hidden className="text-[13px] text-[var(--wa-tick)]">
                    ✓✓
                  </span>
                </div>
              </div>
            </div>
          </main>

          {/* Bezak uchun yozish maydoni */}
          <div
            aria-hidden
            className="sticky bottom-0 flex items-center gap-3 bg-[var(--skin-surface-2)] py-2.5 pr-28 pl-4 text-[#54656f]"
          >
            <IconSmile />
            <IconPlus />
            <div className="min-w-0 flex-1 truncate rounded-lg bg-white px-3 py-2 text-[15px] text-[var(--skin-muted)]">
              Xabar yozing
            </div>
            <IconMic />
          </div>
        </div>
      </div>

      {/* Mobil: suhbatlar paneli */}
      {drawerOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Yopish"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/50"
          />
          <aside className="absolute inset-y-0 left-0 flex w-[340px] max-w-[88vw] flex-col bg-white shadow-2xl">
            <div className="flex h-[59px] shrink-0 items-center gap-3 bg-[var(--skin-accent)] px-4 text-white">
              <span className="text-[17px] font-medium">Darslar</span>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Panelni yopish"
                className="ml-auto flex h-9 w-9 items-center justify-center rounded-full hover:bg-white/10"
              >
                ×
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">
              {chatList(() => setDrawerOpen(false))}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}

/* Ikonkalar — soddalashtirilgan, rasmiy emas */
function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="2" />
      <path d="M16 16l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
function IconDots() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden>
      <circle cx="12" cy="5" r="1.8" />
      <circle cx="12" cy="12" r="1.8" />
      <circle cx="12" cy="19" r="1.8" />
    </svg>
  );
}
function IconChat() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path
        d="M5 18l-1 3 3.5-1.2A8.5 8.5 0 1 0 5 18z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
    </svg>
  );
}
function IconSmile() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6 shrink-0" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="9" cy="10" r="1.2" fill="currentColor" />
      <circle cx="15" cy="10" r="1.2" fill="currentColor" />
      <path d="M8.5 14.5c1.8 2 5.2 2 7 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function IconPlus() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6 shrink-0" fill="none" aria-hidden>
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
function IconMic() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6 shrink-0" fill="none" aria-hidden>
      <rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
