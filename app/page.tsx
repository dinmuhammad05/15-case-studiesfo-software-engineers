import Link from "next/link";
import { lessons, readyLessons } from "@/lib/lessons";
import { LessonCard } from "@/components/LessonCard";

export default function HomePage() {
  const ready = readyLessons().length;
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:py-24">
      <header className="max-w-3xl">
        <p className="font-[family-name:var(--skin-mono)] text-sm text-[var(--skin-accent)]">
          {lessons.length} ta case study · {ready} tasi tayyor
        </p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">
          Dasturchilar uchun
          <br />
          <span className="text-[var(--skin-accent)]">system design</span> darsligi
        </h1>
        <p className="mt-6 text-lg text-[var(--skin-muted)]">
          Har bir dars bitta mahsulotni <strong className="text-[var(--skin-text)]">noldan
          hozirgi arxitekturasigacha</strong> ochib beradi: eng sodda yechim, u qayerda sindi, har
          bir evolyutsiya qadami nimani yutdi va nimani yo‘qotdi. Har bir dars sahifasi o‘sha
          mahsulot interfeysidan ilhomlangan dizaynda.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/darslar/chatgpt/"
            className="rounded-[var(--skin-radius)] bg-[var(--skin-accent)] px-5 py-3 text-sm font-semibold text-[var(--skin-accent-text)]"
          >
            Birinchi darsdan boshlash
          </Link>
          <Link
            href="/darslar/"
            className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] px-5 py-3 text-sm font-semibold hover:bg-[var(--skin-surface)]"
          >
            Kurs rejasi
          </Link>
        </div>
      </header>

      <section className="mt-16">
        <h2 className="mb-5 text-sm font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
          Darslar
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {lessons.map((l) => (
            <LessonCard key={l.slug} lesson={l} />
          ))}
        </div>
      </section>

      <footer className="mt-20 border-t border-[var(--skin-border)] pt-8 text-xs text-[var(--skin-muted)]">
        O‘quv loyihasi. Sahifa dizaynlari mos mahsulotlar interfeysidan ilhomlangan; rasmiy
        logotip, shrift va brend materiallaridan foydalanilmagan.
      </footer>
    </div>
  );
}
