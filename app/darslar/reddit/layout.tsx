import type { Metadata } from "next";
import { RedditShell } from "@/components/skins/RedditShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("reddit");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="reddit" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <RedditShell>{children}</RedditShell>
    </div>
  );
}
