import type { Metadata } from "next";
import { StockShell } from "@/components/skins/StockShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("stock-exchange");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="birja" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <StockShell>{children}</StockShell>
    </div>
  );
}
