import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { WhatsAppChrome } from "./WhatsAppChrome";

/** WhatsApp darsi: suhbat oynasidagi uzun kiruvchi xabar ko'rinishi. */
export function WhatsAppShell({ children }: { children: ReactNode }) {
  return (
    <WhatsAppChrome slug="whatsapp">
      <LessonHeader slug="whatsapp" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="whatsapp" />
      <SkinDisclaimer product="WhatsApp" />
    </WhatsAppChrome>
  );
}
