import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { SlackChrome } from "./SlackChrome";

/** Slack darsi: kanal ichidagi uzun xabar ko'rinishidagi sahifa. */
export function SlackShell({ children }: { children: ReactNode }) {
  return (
    <SlackChrome slug="slack">
      <LessonHeader slug="slack" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="slack" />
      <SkinDisclaimer product="Slack" />
    </SlackChrome>
  );
}
