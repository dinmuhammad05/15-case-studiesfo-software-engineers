import type { Metadata } from "next";
import { S3Shell } from "@/components/skins/S3Shell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("amazon-s3");

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="amazon-s3" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <S3Shell>{children}</S3Shell>
    </div>
  );
}
