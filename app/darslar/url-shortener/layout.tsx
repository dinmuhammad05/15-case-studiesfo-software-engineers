import type { Metadata } from "next";
import { UrlShortenerShell } from "@/components/skins/UrlShortenerShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("url-shortener")!;

export const metadata: Metadata = { title: lesson.title, description: lesson.summary };

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div
      data-skin="url-shortener"
      className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]"
    >
      <UrlShortenerShell>{children}</UrlShortenerShell>
    </div>
  );
}
