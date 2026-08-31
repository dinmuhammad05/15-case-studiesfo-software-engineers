import Link from "next/link";
import type { ReactNode } from "react";
import { lessons } from "@/lib/lessons";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";

/**
 * ChatGPT skini.
 * Chap tomonda "suhbatlar tarixi" (darslar ro'yxati), o'rtada assistant javobi
 * ko'rinishidagi dars matni, pastda dekorativ kompozitor.
 */
export function ChatGptShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar — "suhbatlar tarixi" */}
      <aside className="hidden w-[260px] shrink-0 flex-col border-r border-[var(--skin-border)] bg-[#171717] lg:flex">
        <div className="p-3">
          <Link
            href="/"
            className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-white/5"
          >
            <Logo className="h-5 w-5" />
            Darslik
          </Link>
          <Link
            href="/darslar/"
            className="mt-1 flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm hover:bg-white/5"
          >
            <span className="text-lg leading-none">+</span> Barcha darslar
          </Link>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-4">
          <div className="px-3 py-2 text-xs font-medium text-[var(--skin-muted)]">Kurs rejasi</div>
          {lessons.map((l) => (
            <Link
              key={l.slug}
              href={`/darslar/${l.slug}/`}
              className={`block truncate rounded-lg px-3 py-2 text-sm hover:bg-white/5 ${
                l.slug === "chatgpt" ? "bg-white/10" : "text-[var(--skin-muted)]"
              }`}
              title={l.title}
            >
              {l.title}
            </Link>
          ))}
        </div>
        <div className="border-t border-[var(--skin-border)] p-3 text-xs text-[var(--skin-muted)]">
          17 ta case study · o‘zbek tilida
        </div>
      </aside>

      {/* Asosiy ustun */}
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-[var(--skin-border)] bg-[var(--skin-bg)]/85 px-4 py-3 backdrop-blur">
          <Link href="/" className="flex items-center gap-2 lg:hidden">
            <Logo className="h-5 w-5" />
          </Link>
          <span className="rounded-lg px-2 py-1 text-sm font-medium">
            Dars 01 <span className="text-[var(--skin-muted)]">▾</span>
          </span>
        </div>

        <main className="mx-auto w-full max-w-3xl flex-1 px-4 pt-8 pb-4 sm:px-6">
          {/* Foydalanuvchi "savoli" */}
          <div className="mb-8 flex justify-end">
            <p className="max-w-[80%] rounded-3xl bg-[var(--skin-surface)] px-5 py-3 text-sm">
              ChatGPT ichkarida qanday ishlaydi? Noldan hozirgi holatigacha tushuntirib ber.
            </p>
          </div>

          {/* Assistant "javobi" = dars matni */}
          <div className="flex gap-4">
            <span className="mt-1 hidden h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[var(--skin-border)] sm:flex">
              <Logo className="h-5 w-5" />
            </span>
            <div className="min-w-0 flex-1">
              <LessonHeader slug="chatgpt" />
              <article className="lesson-prose">{children}</article>
              <LessonNav slug="chatgpt" />
              <SkinDisclaimer product="ChatGPT" />
            </div>
          </div>
        </main>

        {/* Dekorativ kompozitor */}
        <div aria-hidden className="sticky bottom-0 bg-gradient-to-t from-[var(--skin-bg)] to-transparent px-4 pb-5 pt-8">
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
