import type { Metadata } from "next";
import { KafkaShell } from "@/components/skins/KafkaShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("kafka");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="kafka" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <KafkaShell>{children}</KafkaShell>
    </div>
  );
}
