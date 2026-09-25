"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Muallif rasmi: public/author.jpg */
export const AUTHOR_PHOTO_SRC = `${BASE}/author.jpg`;

/**
 * Muallif rasmi. Fayl bo'lmasa yoki yuklanmasa — `fallback` (masalan, bosh harflar).
 * `position` — portretni kesishda yuz ko'rinib turishi uchun (object-position).
 */
export function AuthorPhoto({
  className = "",
  fallback,
  alt = "Muallif",
  position = "50% 25%",
}: {
  className?: string;
  fallback: ReactNode;
  alt?: string;
  position?: string;
}) {
  const [failed, setFailed] = useState(false);
  const ref = useRef<HTMLImageElement>(null);

  // Gidratsiyadan oldin xato bo'lgan bo'lsa, onError ishlamaydi — shuning uchun qo'lda tekshiramiz
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) setFailed(true);
  }, []);

  if (failed) return <>{fallback}</>;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      ref={ref}
      src={AUTHOR_PHOTO_SRC}
      alt={alt}
      className={`object-cover ${className}`}
      style={{ objectPosition: position }}
      onError={() => setFailed(true)}
      decoding="async"
    />
  );
}
