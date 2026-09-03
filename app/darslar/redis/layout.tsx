import type { Metadata } from "next";
import { RedisShell } from "@/components/skins/RedisShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("redis")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-redis.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-redis.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="redis" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <RedisShell>{children}</RedisShell>
    </div>
  );
}
