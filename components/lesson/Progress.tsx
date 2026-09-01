"use client";

import { useEffect, useState } from "react";

/** O'qish progressi — uzun darslarda qancha qolganini ko'rsatadi. */
export function ReadingProgress() {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setPct(max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div aria-hidden className="absolute inset-x-0 bottom-0 h-0.5 bg-transparent">
      <div
        className="h-full bg-[var(--skin-accent)] transition-[width] duration-150"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
