import type { Metadata } from "next";
import { GoogleDocsShell } from "@/components/skins/GoogleDocsShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("google-docs");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="google-docs" className="min-h-screen bg-[var(--gd-canvas)] text-[var(--skin-text)]">
      <GoogleDocsShell>{children}</GoogleDocsShell>
    </div>
  );
}
