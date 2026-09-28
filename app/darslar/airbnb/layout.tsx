import type { Metadata } from "next";
import { AirbnbShell } from "@/components/skins/AirbnbShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("airbnb")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-airbnb.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-airbnb.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="airbnb" className="min-h-screen bg-white text-[var(--skin-text)]">
      <AirbnbShell>{children}</AirbnbShell>
    </div>
  );
}
