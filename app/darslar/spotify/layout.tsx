import type { Metadata } from "next";
import { SpotifyShell } from "@/components/skins/SpotifyShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("spotify");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="spotify" className="min-h-screen bg-[var(--sp-black)] text-[var(--skin-text)]">
      <SpotifyShell>{children}</SpotifyShell>
    </div>
  );
}
