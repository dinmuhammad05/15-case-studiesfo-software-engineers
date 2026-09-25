import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { GoogleDocsChrome } from "./GoogleDocsChrome";

/** Google Docs darsi: dars — oq "qog'oz" sahifasi, darslar ro'yxati — hujjat tablari. */
export function GoogleDocsShell({ children }: { children: ReactNode }) {
  return (
    <GoogleDocsChrome slug="google-docs" header={<LessonHeader slug="google-docs" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="google-docs" />
      <SkinDisclaimer product="Google Docs" />
    </GoogleDocsChrome>
  );
}
