import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { TwitterChrome } from "./TwitterChrome";

/** Twitter darsi: tasma ichidagi uzun post ko'rinishidagi sahifa. */
export function TwitterShell({ children }: { children: ReactNode }) {
  return (
    <TwitterChrome slug="twitter">
      {/* "Post" boshi */}
      <div className="mb-6 flex items-center gap-3 border-b border-[var(--skin-border)] pb-5">
        <span
          aria-hidden
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[var(--skin-surface-2)] font-[family-name:var(--skin-mono)] text-sm font-bold text-[var(--skin-accent)]"
        >
          SD
        </span>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-bold">System Design darsligi</span>
            <span aria-hidden className="text-[var(--skin-accent)]">
              ✓
            </span>
          </div>
          <div className="text-sm text-[var(--skin-muted)]">@darslik · Dars 04</div>
        </div>
      </div>

      <LessonHeader slug="twitter" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="twitter" />
      <SkinDisclaimer product="Twitter/X" />
    </TwitterChrome>
  );
}
