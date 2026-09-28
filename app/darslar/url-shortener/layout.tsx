import type { Metadata } from "next";
import { UrlShortenerShell } from "@/components/skins/UrlShortenerShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("url-shortener");

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
