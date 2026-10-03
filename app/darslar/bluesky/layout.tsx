import type { Metadata } from "next";
import { BlueskyShell } from "@/components/skins/BlueskyShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("bluesky");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="bluesky" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <BlueskyShell>{children}</BlueskyShell>
    </div>
  );
}
