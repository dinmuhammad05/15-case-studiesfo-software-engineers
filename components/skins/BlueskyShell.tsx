import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { BlueskyChrome } from "./BlueskyChrome";

/** Bluesky darsi: dars — post, bo'limlar — firehose hodisalari, darslar — feed'lar. */
export function BlueskyShell({ children }: { children: ReactNode }) {
  return (
    <BlueskyChrome slug="bluesky" header={<LessonHeader slug="bluesky" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="bluesky" />
      <SkinDisclaimer product="Bluesky" />
    </BlueskyChrome>
  );
}
