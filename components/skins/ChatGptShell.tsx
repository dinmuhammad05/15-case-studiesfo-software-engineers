import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { ChatGptChrome } from "./ChatGptChrome";

/**
 * ChatGPT skini.
 * Chrome (sidebar, yuqori panel, kompozitor) — interaktiv, alohida client komponentda.
 * Dars matni esa serverda render qilinib, children sifatida uzatiladi.
 */
export function ChatGptShell({ children }: { children: ReactNode }) {
  return (
    <ChatGptChrome slug="chatgpt">
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
    </ChatGptChrome>
  );
}

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
