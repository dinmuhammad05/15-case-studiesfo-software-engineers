import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { UrlShortenerChrome } from "./UrlShortenerChrome";

/** URL qisqartiruvchi darsi: link boshqaruv paneli uslubidagi sahifa. */
export function UrlShortenerShell({ children }: { children: ReactNode }) {
  return (
    <UrlShortenerChrome slug="url-shortener">
      {/* "Qisqartirilgan havola" kartochkasi — dars sarlavhasi o'rnida */}
      <div className="mb-8 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
        <div className="flex flex-wrap items-center gap-2 font-[family-name:var(--skin-mono)] text-sm">
          <span className="font-semibold text-[var(--skin-accent)]">dars.uz/K7xQm2</span>
          <span aria-hidden className="text-[var(--skin-muted)]">
            →
          </span>
          <span className="min-w-0 truncate text-[var(--skin-muted)]">
            /darslar/url-qisqartiruvchi-qanday-ishlaydi
          </span>
        </div>
      </div>

      <LessonHeader slug="url-shortener" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="url-shortener" />
      <SkinDisclaimer product="bit.ly" />
    </UrlShortenerChrome>
  );
}
