import type { ReactNode } from "react";
import { LessonHeader } from "@/components/lesson/header";
import { LessonNav, SkinDisclaimer } from "@/components/lesson/nav";
import { Toc } from "@/components/lesson/Toc";
import { RedisChrome } from "./RedisChrome";

/** Redis darsi: redis-cli sessiyasi ko'rinishidagi sahifa. */
export function RedisShell({ children }: { children: ReactNode }) {
  return (
    <RedisChrome slug="redis">
      {/* Terminal sessiyasining boshlanishi */}
      <div className="mb-8 overflow-x-auto rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[#010409] p-4 font-[family-name:var(--skin-mono)] text-sm">
        <div className="text-[var(--skin-muted)]">$ redis-cli -h darslik --version</div>
        <div className="mt-1">redis-cli 7.4.0 · dars 03</div>
        <div className="mt-2 text-[var(--skin-muted)]">
          127.0.0.1:6379&gt; <span className="text-[var(--skin-text)]">INFO darslik</span>
        </div>
        <div className="mt-1 text-[var(--skin-accent)]"># 12 ta stsenariy, noldan ishlab chiqarishgacha</div>
      </div>

      <LessonHeader slug="redis" />
      <Toc />
      <article className="lesson-prose">{children}</article>
      <LessonNav slug="redis" />
      <SkinDisclaimer product="Redis" />
    </RedisChrome>
  );
}
