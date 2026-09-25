import type { Metadata } from "next";
import { YouTubeShell } from "@/components/skins/YouTubeShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("youtube")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-youtube.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-youtube.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="youtube" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <YouTubeShell>{children}</YouTubeShell>
    </div>
  );
}
