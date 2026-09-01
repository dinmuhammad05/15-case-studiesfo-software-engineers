import type { Metadata } from "next";
import "./globals.css";
import { PwaManager } from "@/components/pwa/PwaManager";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export const viewport = {
  themeColor: "#0b0d10",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: {
    default: "System Design darsligi — 17 ta case study",
    template: "%s · System Design darsligi",
  },
  description:
    "ChatGPT, YouTube, Kafka, S3 va boshqa tizimlar noldan hozirgi arxitekturasigacha — o‘zbek tilida.",
  manifest: `${BASE}/manifest.webmanifest`,
  appleWebApp: {
    capable: true,
    title: "SD darslik",
    statusBarStyle: "black-translucent",
  },
  icons: {
    icon: [
      { url: `${BASE}/icon-192.png`, sizes: "192x192", type: "image/png" },
      { url: `${BASE}/icon.svg`, type: "image/svg+xml" },
    ],
    apple: `${BASE}/apple-touch-icon.png`,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body>
        {children}
        <PwaManager />
      </body>
    </html>
  );
}
