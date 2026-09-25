import type { Metadata } from "next";
import { SlackShell } from "@/components/skins/SlackShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("slack")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-slack.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-slack.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="slack" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <SlackShell>{children}</SlackShell>
    </div>
  );
}
