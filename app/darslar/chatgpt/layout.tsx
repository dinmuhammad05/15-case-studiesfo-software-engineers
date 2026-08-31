import type { Metadata } from "next";
import { ChatGptShell } from "@/components/skins/ChatGptShell";
import { lessonBySlug } from "@/lib/lessons";
import "./theme.css";

const lesson = lessonBySlug("chatgpt")!;

export const metadata: Metadata = {
  title: lesson.title,
  description: lesson.summary,
};

export default function ChatGptLessonLayout({ children }: { children: React.ReactNode }) {
  return (
    <div data-skin="chatgpt" className="min-h-screen bg-[var(--skin-bg)] text-[var(--skin-text)]">
      <ChatGptShell>{children}</ChatGptShell>
    </div>
  );
}
