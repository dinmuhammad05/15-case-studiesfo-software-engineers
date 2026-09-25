import type { Metadata } from "next";
import { GoogleDocsShell } from "@/components/skins/GoogleDocsShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("google-docs")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-google-docs.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-google-docs.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="google-docs" className="min-h-screen bg-[var(--gd-canvas)] text-[var(--skin-text)]">
      <GoogleDocsShell>{children}</GoogleDocsShell>
    </div>
  );
}
