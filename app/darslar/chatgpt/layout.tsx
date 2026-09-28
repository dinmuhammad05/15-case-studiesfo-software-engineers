import type { Metadata } from "next";
import { ChatGptShell } from "@/components/skins/ChatGptShell";
import { lessonMetadata } from "@/lib/seo";
import "./theme.css";

export const metadata: Metadata = lessonMetadata("chatgpt");

export default function ChatGptLessonLayout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="chatgpt" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <ChatGptShell>{children}</ChatGptShell>
    </div>
  );
}
