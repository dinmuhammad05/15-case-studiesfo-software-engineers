import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { S3Chrome } from "./S3Chrome";

/** Amazon S3 darsi: dars — bucket'dagi ob'ekt; o'qish progressi — multipart upload qismlari. */
export function S3Shell({ children }: { children: ReactNode }) {
  return (
    <S3Chrome slug="amazon-s3" header={<LessonHeader slug="amazon-s3" />}>
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="amazon-s3" />
      <SkinDisclaimer product="Amazon S3" />
    </S3Chrome>
  );
}
