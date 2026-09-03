import Link from "next/link";
import { lessons, readyLessons } from "@/lib/lessons";
import { LessonCard } from "@/components/LessonCard";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function HomePage() {
  const ready = readyLessons();
  const totalMinutes = ready.reduce((a, l) => a + l.minutes, 0);
  const progress = Math.round((ready.length / lessons.length) * 100);

  return (
    <>
      <SiteHeader />
      <div className="mx-auto max-w-6xl px-5 py-12 sm:py-16">
      <header className="max-w-3xl">
        <div className="flex flex-wrap items-center gap-2 font-[family-name:var(--skin-mono)] text-sm">
          <span className="text-[var(--skin-accent)]">{lessons.length} ta case study</span>
          <span aria-hidden className="text-[var(--skin-muted)]">
            ·
          </span>
          <span className="text-[var(--skin-muted)]">o‘zbek tilida</span>
          <span aria-hidden className="text-[var(--skin-muted)]">
            ·
          </span>
          <span className="text-[var(--skin-muted)]">bepul</span>
        </div>

        <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-6xl">
          Dasturchilar uchun
          <br />
          <span className="text-[var(--skin-accent)]">system design</span> darsligi
        </h1>

        <p className="mt-6 text-lg text-[var(--skin-muted)]">
          Har bir dars bitta mahsulotni{" "}
          <strong className="text-[var(--skin-text)]">noldan hozirgi arxitekturasigacha</strong>{" "}
          ochib beradi: eng sodda yechim, u qayerda sindi, har bir evolyutsiya qadami nimani
          yutdi va nimani yo‘qotdi. Har bir qaror — hisob-kitob bilan.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href={`/darslar/${ready[0]?.slug ?? "chatgpt"}/`}
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

      {/* Har bir darsda nima bor */}
      <section className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            t: "Noldan boshlanadi",
            d: "Mexanizmning o‘zidan: token, redirect, event loop. Diagrammadan oldin — sabab.",
          },
          {
            t: "Raqam bilan",
            d: "Har bir qaror hisobdan chiqadi: roofline, KV cache byudjeti, navbat nazariyasi.",
          },
          {
            t: "Intervyuga tayyorlaydi",
            d: "Har darsda 20+ savol, javoblari yopiq — avval o‘zingiz javob berasiz.",
          },
          {
            t: "Amaliyot bilan",
            d: "3–4 daraja topshiriq va tekshiruv mezoni: “ishladi” emas, o‘lchangan natija.",
          },
        ].map((f) => (
          <div
            key={f.t}
            className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4"
          >
            <div className="text-sm font-semibold">{f.t}</div>
            <div className="mt-1.5 text-sm text-[var(--skin-muted)]">{f.d}</div>
          </div>
        ))}
      </section>

      <section className="mt-16">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <h2 className="text-sm font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
            Darslar
          </h2>
          <div className="font-[family-name:var(--skin-mono)] text-xs text-[var(--skin-muted)]">
            {ready.length}/{lessons.length} tayyor · ~{Math.round(totalMinutes / 60)} soat
            o‘qish
          </div>
        </div>

        <div
          className="mb-6 h-1 overflow-hidden rounded-full bg-[var(--skin-surface-2)]"
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Kurs tayyorlik darajasi"
        >
          <div className="h-full bg-[var(--skin-accent)]" style={{ width: `${progress}%` }} />
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {lessons.map((l) => (
            <LessonCard key={l.slug} lesson={l} />
          ))}
        </div>
      </section>

        <SiteFooter />
      </div>
    </>
  );
}
