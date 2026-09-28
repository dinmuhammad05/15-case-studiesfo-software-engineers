import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { AirbnbChrome } from "./AirbnbChrome";

/** Airbnb darsi: dars — e'lon sahifasi; o'ng tomonda "bron" kartasi o'qish progressini ko'rsatadi. */
export function AirbnbShell({ children }: { children: ReactNode }) {
  return (
    <AirbnbChrome slug="airbnb" header={<LessonHeader slug="airbnb" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="airbnb" />
      <SkinDisclaimer product="Airbnb" />
    </AirbnbChrome>
  );
}
