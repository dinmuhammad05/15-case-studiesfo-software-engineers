import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { YouTubeChannelRow, YouTubeChrome } from "./YouTubeChrome";

/** YouTube darsi: tomosha sahifasi — pleyer, tavsif, "Keyingi" ro'yxati. */
export function YouTubeShell({ children }: { children: ReactNode }) {
  return (
    <YouTubeChrome slug="youtube">
      <LessonHeader slug="youtube" />
      <YouTubeChannelRow />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="youtube" />
      <SkinDisclaimer product="YouTube" />
    </YouTubeChrome>
  );
}
