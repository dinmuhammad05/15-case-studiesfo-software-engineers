import type { Metadata } from "next";
import { YouTubeShell } from "@/components/skins/YouTubeShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("youtube");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="youtube" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <YouTubeShell>{children}</YouTubeShell>
    </div>
  );
}
