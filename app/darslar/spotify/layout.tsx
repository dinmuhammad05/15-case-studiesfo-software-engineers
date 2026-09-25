import type { Metadata } from "next";
import { SpotifyShell } from "@/components/skins/SpotifyShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("spotify")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
  openGraph: {
    title: lesson.title,
    description: lesson.summary,
    images: [{ url: "/og-spotify.png", width: 1200, height: 630, alt: lesson.title }],
  },
  twitter: { card: "summary_large_image", images: ["/og-spotify.png"] },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="spotify" className="min-h-screen bg-[var(--sp-black)] text-[var(--skin-text)]">
      <SpotifyShell>{children}</SpotifyShell>
    </div>
  );
}
