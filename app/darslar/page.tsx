import type { Metadata } from "next";
import Link from "next/link";
import { lessons, readyLessons } from "@/lib/lessons";
import { LessonCard } from "@/components/LessonCard";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = { title: "Kurs rejasi" };

export default function LessonsPage() {
  const ready = readyLessons();
  const totalMinutes = lessons.reduce((a, l) => a + l.minutes, 0);
  return (
    <>
      <SiteHeader />
      <div className="mx-auto max-w-6xl px-5 py-12">
      <Link href="/" className="text-sm text-[var(--skin-muted)] hover:text-[var(--skin-text)]">
        ← Bosh sahifa
      </Link>
      <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">Kurs rejasi</h1>
      <p className="mt-3 max-w-2xl text-[var(--skin-muted)]">
        Darslar osondan murakkabga qarab tartiblangan. Har biri mustaqil o‘qiladi, lekin
        ketma-ket o‘qilsa tushunchalar bir-birining ustiga qurilib boradi.
      </p>
      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1 font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-muted)]">
        <span>
          <span className="text-[var(--skin-accent)]">{ready.length}</span> tayyor
        </span>
        <span>{lessons.length - ready.length} rejada</span>
        <span>~{Math.round(totalMinutes / 60)} soat o‘qish (to‘liq kurs)</span>
      </div>
      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {lessons.map((l) => (
          <LessonCard key={l.slug} lesson={l} />
        ))}
      </div>
        <SiteFooter />
      </div>
    </>
  );
}
