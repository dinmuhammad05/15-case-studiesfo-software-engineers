import type { Metadata } from "next";
import { AirbnbShell } from "@/components/skins/AirbnbShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("airbnb");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="airbnb" className="min-h-screen bg-white text-[var(--skin-text)]">
      <AirbnbShell>{children}</AirbnbShell>
    </div>
  );
}
