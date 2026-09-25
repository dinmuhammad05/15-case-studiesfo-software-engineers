"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Muallif rasmlari: portret (pleyer, katta joylar) va yuzga yaqin kvadrat (avatarlar). */
export const AUTHOR_PHOTO_SRC = `${BASE}/author.jpg`;
export const AUTHOR_FACE_SRC = `${BASE}/author-face.jpg`;

/**
 * Muallif rasmi. Fayl bo'lmasa yoki yuklanmasa — `fallback` (masalan, bosh harflar).
 * `variant="face"` — kichik avatarlar uchun yuz kesimi (standart),
 * `variant="portrait"` — katta joylar uchun to'liq portret.
 * `position` — kesishda nima ko'rinib turishi (object-position).
 */
export function AuthorPhoto({
  className = "",
  fallback,
  alt = "Muallif",
  position,
  variant = "face",
}: {
  className?: string;
  fallback: ReactNode;
  alt?: string;
  position?: string;
  variant?: "face" | "portrait";
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
      src={variant === "portrait" ? AUTHOR_PHOTO_SRC : AUTHOR_FACE_SRC}
      alt={alt}
      className={`object-cover ${className}`}
      style={{ objectPosition: position ?? (variant === "portrait" ? "50% 25%" : "50% 50%") }}
      onError={() => setFailed(true)}
      decoding="async"
    />
  );
}
