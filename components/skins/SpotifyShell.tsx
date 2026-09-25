import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { SpotifyChrome } from "./SpotifyChrome";

/** Spotify darsi: pleylist sahifasi — muqova, sarlavha, "treklar" (bo'limlar). */
export function SpotifyShell({ children }: { children: ReactNode }) {
  return (
    <SpotifyChrome slug="spotify" header={<LessonHeader slug="spotify" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="spotify" />
      <SkinDisclaimer product="Spotify" />
    </SpotifyChrome>
  );
}
