import type { Metadata } from "next";
import { RedditShell } from "@/components/skins/RedditShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("reddit")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-reddit.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-reddit.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="reddit" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <RedditShell>{children}</RedditShell>
    </div>
  );
}
