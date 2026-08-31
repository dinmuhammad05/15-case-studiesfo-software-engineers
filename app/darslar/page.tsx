import type { Metadata } from "next";
import Link from "next/link";
import { lessons } from "@/lib/lessons";
import { LessonCard } from "@/components/LessonCard";

export const metadata: Metadata = { title: "Kurs rejasi" };

export default function LessonsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16">
      <Link href="/" className="text-sm text-[var(--skin-muted)] hover:text-[var(--skin-text)]">
        ← Bosh sahifa
      </Link>
      <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">Kurs rejasi</h1>
      <p className="mt-3 max-w-2xl text-[var(--skin-muted)]">
        Darslar oson dan murakkabga qarab tartiblangan. Har biri mustaqil o‘qiladi, lekin
        ketma-ket o‘qilsa tushunchalar bir-birining ustiga qurilib boradi.
      </p>
      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {lessons.map((l) => (
          <LessonCard key={l.slug} lesson={l} />
        ))}
      </div>
    </div>
  );
}
