import Link from "next/link";
import { readableAccent, type Lesson } from "@/lib/lessons";

const statusLabel: Record<Lesson["status"], string> = {
  tayyor: "Tayyor",
  yozilmoqda: "Yozilmoqda",
  rejada: "Rejada",
};

export function LessonCard({ lesson }: { lesson: Lesson }) {
  const ready = lesson.status === "tayyor";
  const inner = (
    <>
      <div className="flex items-start justify-between gap-3">
        <span
          className="font-[family-name:var(--skin-mono)] text-sm font-bold"
          style={{ color: readableAccent(lesson.accent) }}
        >
          {String(lesson.order).padStart(2, "0")}
        </span>
        <span
          className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${
            ready
              ? "border-transparent bg-[var(--skin-accent)] text-[var(--skin-accent-text)]"
              : "border-[var(--skin-border)] text-[var(--skin-muted)]"
          }`}
        >
          {statusLabel[lesson.status]}
        </span>
      </div>
      <h3 className="mt-3 text-base font-semibold">{lesson.title}</h3>
      <p className="mt-2 line-clamp-3 text-sm text-[var(--skin-muted)]">{lesson.summary}</p>
      <div className="mt-4 flex items-center gap-2 text-[11px] text-[var(--skin-muted)]">
        <span>{lesson.level}</span>
        <span aria-hidden>•</span>
        <span>{lesson.minutes} daq</span>
      </div>
    </>
  );

  const base =
    "group relative block overflow-hidden rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-5";

  if (!ready) {
    return (
      <div className={`${base} opacity-55`} aria-disabled>
        {inner}
      </div>
    );
  }

  return (
    <Link href={`/darslar/${lesson.slug}/`} className={`${base} transition-colors hover:bg-[var(--skin-surface-2)]`}>
      <span
        aria-hidden
        className="absolute inset-x-0 top-0 h-[3px]"
        style={{ background: lesson.accent }}
      />
      {inner}
      <span className="mt-4 inline-block text-sm font-medium text-[var(--skin-accent)]">
        Darsni ochish →
      </span>
    </Link>
  );
}
