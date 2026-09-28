import type { Metadata } from "next";
import { lessonBySlug, readyLessons, type Lesson } from "@/lib/lessons";
import { site } from "@/lib/site";

/**
 * Qidiruv tizimlari uchun metama'lumot va strukturali ma'lumot (JSON-LD).
 * Hamma dars sahifalari shu yerdan oladi — bitta joyda o'zgartiriladi.
 */

const lessonPath = (slug: string) => `/darslar/${slug}/`;
export const absUrl = (path: string) => `${site.url}${path}`;

const author = {
  "@type": "Person",
  name: site.author.name,
  url: site.author.portfolio,
  sameAs: [site.author.github, site.author.telegramUrl],
};

const provider = {
  "@type": "Organization",
  name: site.name,
  url: `${site.url}/`,
};

/** Dars sahifasining <head> ma'lumotlari: sarlavha, tavsif, canonical, OG. */
export function lessonMetadata(slug: string): Metadata {
  const l = lessonBySlug(slug)!;
  const og = `/og-${slug}.png`;
  const description = `${l.summary} Bepul, o‘zbek tilida: hisob-kitoblar, intervyu savollari va amaliyot.`;
  return {
    title: l.title,
    description,
    keywords: [...l.topics, "system design", "tizim dizayni", "o'zbek tilida", "intervyu savollari"],
    alternates: { canonical: lessonPath(slug) },
    openGraph: {
      type: "article",
      url: lessonPath(slug),
      title: l.title,
      description,
      images: [{ url: og, width: 1200, height: 630, alt: l.title }],
    },
    twitter: { card: "summary_large_image", title: l.title, description, images: [og] },
  };
}

function course(l: Lesson) {
  return {
    "@type": "Course",
    "@id": absUrl(`${lessonPath(l.slug)}#course`),
    name: l.title,
    description: l.summary,
    url: absUrl(lessonPath(l.slug)),
    image: absUrl(`/og-${l.slug}.png`),
    inLanguage: "uz",
    isAccessibleForFree: true,
    educationalLevel: l.level,
    teaches: l.topics,
    about: ["System design", "Tizim dizayni", ...l.topics],
    timeRequired: `PT${l.minutes}M`,
    author,
    provider,
    offers: { "@type": "Offer", category: "Free", price: 0, priceCurrency: "USD" },
    hasCourseInstance: {
      "@type": "CourseInstance",
      courseMode: "online",
      courseWorkload: `PT${l.minutes}M`,
    },
  };
}

/** Dars sahifasi uchun: Course + TechArticle + BreadcrumbList. */
export function lessonJsonLd(slug: string) {
  const l = lessonBySlug(slug);
  if (!l) return null;
  return {
    "@context": "https://schema.org",
    "@graph": [
      course(l),
      {
        "@type": "TechArticle",
        headline: l.title,
        description: l.summary,
        url: absUrl(lessonPath(l.slug)),
        image: absUrl(`/og-${l.slug}.png`),
        inLanguage: "uz",
        isAccessibleForFree: true,
        author,
        publisher: provider,
        keywords: l.topics.join(", "),
        mainEntityOfPage: absUrl(lessonPath(l.slug)),
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: site.name, item: `${site.url}/` },
          { "@type": "ListItem", position: 2, name: l.title, item: absUrl(lessonPath(l.slug)) },
        ],
      },
    ],
  };
}

/** Bosh sahifa uchun: WebSite + darslar ro'yxati (ItemList of Course). */
export function homeJsonLd() {
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        name: site.name,
        url: `${site.url}/`,
        description: site.description,
        inLanguage: "uz",
        author,
      },
      {
        "@type": "ItemList",
        name: `${site.name}: darslar`,
        itemListElement: readyLessons().map((l, i) => ({
          "@type": "ListItem",
          position: i + 1,
          item: course(l),
        })),
      },
    ],
  };
}

/** <script type="application/ld+json"> — "<" belgisi xavfsiz qochiriladi. */
export function JsonLd({ data }: { data: object | null }) {
  if (!data) return null;
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}
