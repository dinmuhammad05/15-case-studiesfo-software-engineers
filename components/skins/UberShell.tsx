import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { UberChrome } from "./UberChrome";

/** Uber darsi: dars — safar; o'qish progressi xaritadagi marshrut bo'ylab harakatlanayotgan mashina. */
export function UberShell({ children }: { children: ReactNode }) {
  return (
    <UberChrome slug="uber-eta" header={<LessonHeader slug="uber-eta" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="uber-eta" />
      <SkinDisclaimer product="Uber" />
    </UberChrome>
  );
}
