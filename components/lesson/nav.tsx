import Link from "next/link";
import { lessons, neighbours, type Lesson } from "@/lib/lessons";

/** Dars ostidagi oldingi/keyingi tugmalari — barcha skinlar uchun umumiy. */
export function LessonNav({ slug }: { slug: string }) {
  const { prev, next } = neighbours(slug);
  return (
    <nav className="mt-14 grid gap-3 border-t border-[var(--skin-border)] pt-6 sm:grid-cols-2">
      {prev ? (
        <Link
          href={`/darslar/${prev.slug}/`}
          className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4 transition-colors hover:border-[var(--skin-accent)]"
        >
          <div className="text-xs text-[var(--skin-muted)]">← Oldingi dars</div>
          <div className="mt-1 text-sm font-medium">{prev.title}</div>
        </Link>
      ) : (
        <span />
      )}
      {next ? (
        <Link
          href={`/darslar/${next.slug}/`}
          className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4 text-right transition-colors hover:border-[var(--skin-accent)]"
        >
          <div className="text-xs text-[var(--skin-muted)]">Keyingi dars →</div>
          <div className="mt-1 text-sm font-medium">{next.title}</div>
        </Link>
      ) : null}
    </nav>
  );
}

/** Har bir darsda ko'rinadigan huquqiy izoh. */
export function SkinDisclaimer({ product }: { product: string }) {
  return (
    <p className="mt-10 text-[11px] leading-relaxed text-[var(--skin-muted)]">
      Ushbu sahifa dizayni {product} interfeysidan ilhomlangan o‘quv materiali. Loyiha {product} bilan
      bog‘liq emas, rasmiy logotip va shriftlardan foydalanilmagan.
    </p>
  );
}

/** Skin sidebar'lari uchun darslar ro'yxati. */
export function lessonList(): Lesson[] {
  return lessons;
}
