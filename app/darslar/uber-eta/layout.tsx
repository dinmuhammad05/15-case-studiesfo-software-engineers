import type { Metadata } from "next";
import { UberShell } from "@/components/skins/UberShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("uber-eta");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="uber-eta" className="min-h-screen bg-white text-[var(--skin-text)]">
      <UberShell>{children}</UberShell>
    </div>
  );
}
