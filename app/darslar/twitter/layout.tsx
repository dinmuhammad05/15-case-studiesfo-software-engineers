import type { Metadata } from "next";
import { TwitterShell } from "@/components/skins/TwitterShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("twitter")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-twitter.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-twitter.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="twitter" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <TwitterShell>{children}</TwitterShell>
    </div>
  );
}
