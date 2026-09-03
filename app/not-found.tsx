import Link from "next/link";
import { readyLessons } from "@/lib/lessons";

export default function NotFound() {
  const ready = readyLessons();
  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center px-5 py-16">
      <div className="font-[family-name:var(--skin-mono)] text-sm text-[var(--skin-accent)]">
        404
      </div>
      <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Bunday sahifa yo‘q</h1>
      <p className="mt-4 text-[var(--skin-muted)]">
        Havola eskirgan yoki dars hali yozilmagan bo‘lishi mumkin. Quyidagilardan birini
        tanlang:
      </p>

      <div className="mt-8 space-y-2">
        {ready.map((l) => (
          <Link
            key={l.slug}
            href={`/darslar/${l.slug}/`}
            className="flex items-center gap-3 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] px-4 py-3 transition-colors hover:border-[var(--skin-accent)]"
          >
            <span className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-accent)]">
              {String(l.order).padStart(2, "0")}
            </span>
            <span className="min-w-0 flex-1 truncate text-sm font-medium">{l.title}</span>
            <span aria-hidden className="text-[var(--skin-muted)]">
              →
            </span>
          </Link>
        ))}
      </div>

      <div className="mt-8 flex gap-3">
        <Link
          href="/"
          className="rounded-[var(--skin-radius)] bg-[var(--skin-accent)] px-4 py-2.5 text-sm font-semibold text-[var(--skin-accent-text)]"
        >
          Bosh sahifa
        </Link>
        <Link
          href="/darslar/"
          className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] px-4 py-2.5 text-sm font-semibold hover:bg-[var(--skin-surface)]"
        >
          Kurs rejasi
        </Link>
      </div>
    </div>
  );
}
