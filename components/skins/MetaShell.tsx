import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { MetaChrome } from "./MetaChrome";

/** Meta Serverless darsi: dars — funksiya, bo'limlar — navbatdagi chaqiruvlar, progress — bandlik. */
export function MetaShell({ children }: { children: ReactNode }) {
  return (
    <MetaChrome slug="meta-serverless" header={<LessonHeader slug="meta-serverless" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="meta-serverless" />
      <SkinDisclaimer product="ichki ishlab chiquvchi konsollari" />
    </MetaChrome>
  );
}
