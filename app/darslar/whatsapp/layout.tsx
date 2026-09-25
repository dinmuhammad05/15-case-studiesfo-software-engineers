import type { Metadata } from "next";
import { WhatsAppShell } from "@/components/skins/WhatsAppShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("whatsapp")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-whatsapp.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-whatsapp.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="whatsapp" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <WhatsAppShell>{children}</WhatsAppShell>
    </div>
  );
}
