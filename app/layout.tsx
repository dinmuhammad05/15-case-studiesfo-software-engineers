import type { Metadata } from "next";
import "./globals.css";
import { PwaManager } from "@/components/pwa/PwaManager";
import { site } from "@/lib/site";
import { ContentGuard, Watermark } from "@/components/lesson/ContentGuard";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export const viewport = {
  themeColor: "#0b0d10",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name} — 17 ta case study`,
    template: `%s · ${site.name}`,
  },
  description: site.description,
  keywords: [
    "system design",
    "tizim dizayni",
    "o'zbek tilida",
    "intervyu",
    "ChatGPT",
    "Redis",
    "Kafka",
    "arxitektura",
    "dasturlash",
  ],
  authors: [{ name: site.author.handle, url: site.author.github }],
  creator: site.author.handle,
  openGraph: {
    type: "website",
    locale: "uz_UZ",
    url: site.url,
    siteName: site.name,
    title: `${site.name} — 17 ta case study`,
    description: site.description,
    images: [{ url: "/og.png", width: 1200, height: 630, alt: site.name }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${site.name} — 17 ta case study`,
    description: site.description,
    images: ["/og.png"],
  },
  manifest: `${BASE}/manifest.webmanifest`,
  appleWebApp: {
    capable: true,
    title: "SD darslik",
    statusBarStyle: "black-translucent",
  },
  robots: site.protection.noindex
    ? { index: false, follow: false, nocache: true, googleBot: { index: false, follow: false } }
    : undefined,
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
        <Watermark />
        <ContentGuard />
        <PwaManager />
      </body>
    </html>
  );
}
