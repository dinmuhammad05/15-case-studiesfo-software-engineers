import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { KafkaChrome } from "./KafkaChrome";

/** Kafka darsi: dars — topic; bo'limlar — offset'lar; o'qish progressi — consumer lag. */
export function KafkaShell({ children }: { children: ReactNode }) {
  return (
    <KafkaChrome slug="kafka" header={<LessonHeader slug="kafka" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="kafka" />
      <SkinDisclaimer product="Apache Kafka" />
    </KafkaChrome>
  );
}
