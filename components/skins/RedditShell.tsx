import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { RedditChrome } from "./RedditChrome";

/** Reddit darsi: post + kommentariya oqimi ko'rinishidagi sahifa. */
export function RedditShell({ children }: { children: ReactNode }) {
  return (
    <RedditChrome slug="reddit">
      <div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-[var(--skin-muted)]">
        <span className="font-semibold text-[var(--skin-text)]">r/system_design</span>
        <span aria-hidden>·</span>
        <span>u/darslik joyladi</span>
        <span aria-hidden>·</span>
        <span>Dars 05</span>
      </div>

      <LessonHeader slug="reddit" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="reddit" />
      <SkinDisclaimer product="Reddit" />
    </RedditChrome>
  );
}
