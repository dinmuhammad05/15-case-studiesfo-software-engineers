"use client";

import { useEffect } from "react";
import { site } from "@/lib/site";

/**
 * Kontentni tasodifiy nusxalashdan himoyalash.
 *
 * MUHIM: bu chora jiddiy nusxa ko'chirishni TO'XTATA OLMAYDI —
 * DevTools, "sahifa manbasini ko'rish", reader rejimi yoki JS ni o'chirish
 * bilan chetlab o'tiladi. U faqat oddiy foydalanuvchining "belgila va nusxa ol"
 * harakatini qiyinlashtiradi.
 */
export function ContentGuard() {
  useEffect(() => {
    const p = site.protection;
    if (!p.copyGuard && !p.blockPrint) return;

    const stop = (e: Event) => {
      // Kirish maydonlarida (agar keyin qo'shilsa) to'smaymiz
      const t = e.target as HTMLElement | null;
      if (t && (t.closest("input, textarea, [contenteditable='true']") as HTMLElement | null))
        return;
      e.preventDefault();
    };

    const onKey = (e: KeyboardEvent) => {
      const k = e.key.toLowerCase();
      const mod = e.ctrlKey || e.metaKey;
      if (!mod) return;
      // Nusxa olish, kesish, hammasini belgilash, saqlash, chop etish
      if (p.copyGuard && ["c", "x", "a", "s"].includes(k)) e.preventDefault();
      if (p.blockPrint && k === "p") e.preventDefault();
    };

    if (p.copyGuard) {
      document.addEventListener("copy", stop);
      document.addEventListener("cut", stop);
      document.addEventListener("contextmenu", stop);
      document.addEventListener("dragstart", stop);
    }
    document.addEventListener("keydown", onKey);

    return () => {
      document.removeEventListener("copy", stop);
      document.removeEventListener("cut", stop);
      document.removeEventListener("contextmenu", stop);
      document.removeEventListener("dragstart", stop);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  return null;
}

/**
 * Suv belgisi: skrinshotni to'xtatmaydi, lekin tarqalgan skrinshotda
 * manba va muallif ko'rinib turadi.
 */
export function Watermark() {
  if (!site.protection.watermark) return null;
  const text = `${site.author.handle} · ${site.author.telegram}`;
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[5] select-none overflow-hidden"
      style={{ contain: "strict" }}
    >
      <div
        className="absolute -inset-1/4 flex flex-wrap content-start gap-x-16 gap-y-24 opacity-[0.035]"
        style={{ transform: "rotate(-24deg)" }}
      >
        {Array.from({ length: 60 }).map((_, i) => (
          <span
            key={i}
            className="font-[family-name:var(--skin-mono)] text-sm whitespace-nowrap text-[var(--skin-text)]"
          >
            {text}
          </span>
        ))}
      </div>
    </div>
  );
}
