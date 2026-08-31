"use client";

import { useEffect, useState } from "react";

type Item = { id: string; text: string };

/**
 * Mundarija. Sahifadagi h2 sarlavhalarni o'zi topadi (id'lar rehype-slug bilan qo'yiladi),
 * shuning uchun dars matni o'zgarganda qo'lda yangilash shart emas.
 * Skroll bo'yicha joriy bo'lim ajratib ko'rsatiladi.
 */
export function Toc() {
  const [items, setItems] = useState<Item[]>([]);
  const [active, setActive] = useState<string>("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const nodes = Array.from(
      document.querySelectorAll<HTMLHeadingElement>(".lesson-prose h2[id]"),
    );
    setItems(nodes.map((n) => ({ id: n.id, text: n.textContent ?? "" })));

    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: "-80px 0px -70% 0px" },
    );
    nodes.forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, []);

  if (items.length === 0) return null;

  return (
    <nav className="my-8 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)]">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full select-none items-center justify-between gap-3 px-4 py-3 text-left text-sm font-semibold"
      >
        <span>Mundarija · {items.length} ta bo‘lim</span>
        <span
          aria-hidden
          className={`text-[var(--skin-accent)] transition-transform sm:hidden ${open ? "rotate-90" : ""}`}
        >
          ▸
        </span>
      </button>
      <ol
        className={`${open ? "block" : "hidden"} border-t border-[var(--skin-border)] px-2 py-2 sm:block`}
      >
        {items.map((it) => (
          <li key={it.id}>
            <a
              href={`#${it.id}`}
              onClick={() => setOpen(false)}
              className={`flex gap-2.5 rounded-lg px-3 py-1.5 text-sm no-underline hover:bg-white/5 ${
                active === it.id ? "text-[var(--skin-accent)]" : "text-[var(--skin-muted)]"
              }`}
            >
              <span aria-hidden className="opacity-40">·</span>
              <span className="min-w-0">{it.text}</span>
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
