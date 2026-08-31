import { lessonBySlug } from "@/lib/lessons";

/** Dars sarlavhasi + meta ma'lumot. Skin ichida ishlatiladi. */
export function LessonHeader({ slug }: { slug: string }) {
  const lesson = lessonBySlug(slug);
  if (!lesson) return null;
  return (
    <header className="mb-8">
      <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--skin-muted)]">
        <span className="rounded-full bg-[var(--skin-accent)] px-2.5 py-1 font-[family-name:var(--skin-mono)] font-semibold text-[var(--skin-accent-text)]">
          {String(lesson.order).padStart(2, "0")}
        </span>
        <span>{lesson.level}</span>
        <span aria-hidden>•</span>
        <span>{lesson.minutes} daqiqa</span>
      </div>
      <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{lesson.title}</h1>
      <p className="mt-3 max-w-2xl text-[var(--skin-muted)]">{lesson.summary}</p>
      <div className="mt-4 flex flex-wrap gap-1.5">
        {lesson.topics.map((t) => (
          <span
            key={t}
            className="rounded-full border border-[var(--skin-border)] px-2.5 py-1 font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]"
          >
            {t}
          </span>
        ))}
      </div>
    </header>
  );
}
