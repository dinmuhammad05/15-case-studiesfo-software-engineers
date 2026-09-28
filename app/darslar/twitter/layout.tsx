import type { Metadata } from "next";
import { TwitterShell } from "@/components/skins/TwitterShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("twitter");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="twitter" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <TwitterShell>{children}</TwitterShell>
    </div>
  );
}
