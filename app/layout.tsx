import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "System Design darsligi — 17 ta case study",
    template: "%s · System Design darsligi",
  },
  description:
    "ChatGPT, YouTube, Kafka, S3 va boshqa tizimlar noldan hozirgi arxitekturasigacha — o‘zbek tilida.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}
