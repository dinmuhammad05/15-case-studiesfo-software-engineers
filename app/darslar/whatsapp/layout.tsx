import type { Metadata } from "next";
import { WhatsAppShell } from "@/components/skins/WhatsAppShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("whatsapp");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="whatsapp" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <WhatsAppShell>{children}</WhatsAppShell>
    </div>
  );
}
