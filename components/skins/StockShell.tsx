import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { StockChrome } from "./StockChrome";

/** Birja darsi: dars — instrument; bo'limlar — buyurtmalar kitobi darajalari; progress — narx. */
export function StockShell({ children }: { children: ReactNode }) {
  return (
    <StockChrome slug="stock-exchange" header={<LessonHeader slug="stock-exchange" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="stock-exchange" />
      <SkinDisclaimer product="birja savdo terminallari" />
    </StockChrome>
  );
}
