import Link from "next/link";
import { site } from "@/lib/site";

/** Bosh sahifa va kurs rejasi uchun umumiy footer: muallif, havolalar, litsenziya. */
export function SiteFooter() {
  return (
    <footer className="mt-20 border-t border-[var(--skin-border)] pt-10">
      <div className="grid gap-8 sm:grid-cols-2">
        {/* Muallif */}
        <div>
          <div className="mb-3 text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
            Muallif
          </div>
          <div className="flex items-center gap-3">
            <span
              aria-hidden
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-[var(--skin-border)] bg-[var(--skin-surface)] font-[family-name:var(--skin-mono)] text-sm font-bold text-[var(--skin-accent)]"
            >
              dM
            </span>
            <div className="min-w-0">
              <div className="font-medium">{site.author.handle}</div>
              <div className="text-sm text-[var(--skin-muted)]">
                Loyihani yozgan va yuritadigan
              </div>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <a
              href={site.author.github}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full border border-[var(--skin-border)] px-3.5 py-1.5 text-sm hover:bg-[var(--skin-surface)]"
            >
              GitHub
            </a>
            <a
              href={site.author.telegramUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full border border-[var(--skin-border)] px-3.5 py-1.5 text-sm hover:bg-[var(--skin-surface)]"
            >
              Telegram {site.author.telegram}
            </a>
          </div>
        </div>

        {/* Loyiha haqida */}
        <div>
          <div className="mb-3 text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
            Loyiha haqida
          </div>
          <ul className="space-y-2 text-sm text-[var(--skin-muted)]">
            <li>
              Darslik bepul. Xato topsangiz yoki mavzu taklif qilmoqchi bo‘lsangiz —{" "}
              <a
                href={site.author.telegramUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--skin-accent)] underline underline-offset-2"
              >
                Telegram orqali yozing
              </a>
              .
            </li>
            <li>
              Internetsiz o‘qish uchun sahifaning o‘ng pastidagi tugmadan darslarni yuklab
              olish mumkin.
            </li>
            <li>
              Dars matnlari{" "}
              <a
                href={site.license.contentUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--skin-accent)] underline underline-offset-2"
              >
                {site.license.content}
              </a>{" "}
              litsenziyasi ostida: nom ko‘rsatilsa erkin foydalanish mumkin,{" "}
              <strong className="text-[var(--skin-text)]">tijorat maqsadida emas</strong>.
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-10 border-t border-[var(--skin-border)] pt-6 text-xs leading-relaxed text-[var(--skin-muted)]">
        O‘quv loyihasi. Dars sahifalarining dizayni mos mahsulotlar interfeysidan
        ilhomlangan; rasmiy logotip, shrift va brend materiallaridan foydalanilmagan.
        Barcha tovar belgilari o‘z egalariga tegishli.
        <div className="mt-2">
          © {new Date().getFullYear()} {site.author.handle} ·{" "}
          <Link href="/darslar/" className="hover:text-[var(--skin-text)]">
            Kurs rejasi
          </Link>
        </div>
      </div>
    </footer>
  );
}
