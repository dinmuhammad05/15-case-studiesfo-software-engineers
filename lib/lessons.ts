export type LessonStatus = "tayyor" | "yozilmoqda" | "rejada";

export type Lesson = {
  /** Tartib raqami — sayt bo'ylab bir xil ketma-ketlik */
  order: number;
  slug: string;
  /** Dars sarlavhasi */
  title: string;
  /** Bir gapda: darsda nima o'rganiladi */
  summary: string;
  /** Kartochka va skin uchun asosiy rang */
  accent: string;
  status: LessonStatus;
  level: "boshlang'ich" | "o'rta" | "murakkab";
  /** Taxminiy o'qish vaqti, daqiqa */
  minutes: number;
  /** Darsning kalit tushunchalari */
  topics: string[];
};

/**
 * Ketma-ketlik ataylab oson -> murakkab tartibda.
 * ChatGPT birinchi o'rinda: u ham eng qiziqarli, ham skin tizimining namunasi.
 */
export const lessons: Lesson[] = [
  {
    order: 1,
    slug: "chatgpt",
    title: "ChatGPT qanday ishlaydi",
    summary:
      "Tokenizatsiyadan haftasiga yuz millionlab foydalanuvchiga xizmat qiladigan inference platformasigacha: model ichkarida nima qiladi va uni qanday qilib xizmatga aylantirishadi.",
    accent: "#10a37f",
    status: "tayyor",
    level: "murakkab",
    minutes: 150,
    topics: [
      "Tokenizatsiya",
      "Attention",
      "RLHF",
      "KV cache",
      "Continuous batching",
      "Streaming",
      "Tool calling",
      "RAG",
      "Prompt injection",
      "Roofline",
      "Sig'im rejalashtirish",
      "Inference iqtisodi",
    ],
  },
  {
    order: 2,
    slug: "url-shortener",
    title: "URL qisqartiruvchi qanday ishlaydi",
    summary:
      "Kalit maydoni matematikasidan chekka keshgacha: bitta kalit-qiymat qidiruv qanday qilib sekundiga 19 000 redirect'ga aylanadi.",
    accent: "#ee6123",
    status: "tayyor",
    level: "o'rta",
    minutes: 120,
    topics: [
      "Base62",
      "Tug'ilgan kun paradoksi",
      "301 vs 302",
      "Cache stampede",
      "Hot key",
      "Bloom filtri",
      "HyperLogLog",
      "Izchil xeshlash",
      "Ochiq redirect",
      "SSRF",
    ],
  },
  {
    order: 3,
    slug: "redis",
    title: "Redis'ning 12 ta asosiy stsenariysi",
    summary:
      "Event loop va xotira modelidan klasterga qadar: 12 ta amaliy stsenariy va ularning har biridagi tuzoqlar.",
    accent: "#dc382d",
    status: "tayyor",
    level: "o'rta",
    minutes: 130,
    topics: [
      "Event loop",
      "Xotira modeli",
      "Kodlashlar",
      "TTL va eviction",
      "RDB va AOF",
      "fork va COW",
      "ZSET",
      "Streams",
      "HyperLogLog",
      "Taqsimlangan lock",
      "Cluster",
    ],
  },
  {
    order: 4,
    slug: "twitter",
    title: "Twitter tasmasi qanday ishlaydi",
    summary: "Fan-out on write va fan-out on read: mashhur akkauntlar muammosi va gibrid yechim.",
    accent: "#1d9bf0",
    status: "rejada",
    level: "o'rta",
    minutes: 30,
    topics: ["Fan-out", "Timeline", "Hot key", "Ranking"],
  },
  {
    order: 5,
    slug: "reddit",
    title: "Reddit qanday ishlaydi",
    summary: "Ovoz berish, kommentariya daraxti va 'hot' reytingi qanday hisoblanadi.",
    accent: "#ff4500",
    status: "rejada",
    level: "o'rta",
    minutes: 28,
    topics: ["Ranking", "Nested comments", "Counter", "Kesh"],
  },
  {
    order: 6,
    slug: "slack",
    title: "Slack qanday ishlaydi",
    summary: "Real-time xabar yetkazish, WebSocket, presence va kanal tarixi.",
    accent: "#4a154b",
    status: "rejada",
    level: "o'rta",
    minutes: 28,
    topics: ["WebSocket", "Presence", "Fan-out", "Sharding"],
  },
  {
    order: 7,
    slug: "whatsapp",
    title: "WhatsApp qanday ishlaydi",
    summary: "Uchdan-uchgacha shifrlash, yetkazish kafolati va oflayn navbat.",
    accent: "#25d366",
    status: "rejada",
    level: "o'rta",
    minutes: 30,
    topics: ["E2E shifrlash", "Erlang", "Delivery receipt", "Navbat"],
  },
  {
    order: 8,
    slug: "youtube",
    title: "YouTube qanday ishlaydi",
    summary: "Yuklashdan transkodlashgacha, CDN va adaptiv bitreyt.",
    accent: "#ff0000",
    status: "rejada",
    level: "o'rta",
    minutes: 32,
    topics: ["Transkodlash", "CDN", "ABR", "Blob storage"],
  },
  {
    order: 9,
    slug: "spotify",
    title: "Spotify qanday ishlaydi",
    summary: "Audio yetkazish, pleylist saqlash va tavsiya tizimi.",
    accent: "#1db954",
    status: "rejada",
    level: "o'rta",
    minutes: 28,
    topics: ["Streaming", "CDN", "Tavsiya", "Kesh"],
  },
  {
    order: 10,
    slug: "google-docs",
    title: "Google Docs qanday ishlaydi",
    summary: "Bir vaqtda tahrirlash: OT va CRDT o'rtasidagi tanlov.",
    accent: "#4285f4",
    status: "rejada",
    level: "murakkab",
    minutes: 34,
    topics: ["OT", "CRDT", "Konflikt", "Versiyalash"],
  },
  {
    order: 11,
    slug: "airbnb",
    title: "Airbnb qanday ishlaydi",
    summary: "Qidiruv, band qilish va ikki marta bron bo'lmasligi kafolati.",
    accent: "#ff5a5f",
    status: "rejada",
    level: "o'rta",
    minutes: 30,
    topics: ["Geo qidiruv", "Bron", "Tranzaksiya", "Idempotentlik"],
  },
  {
    order: 12,
    slug: "uber-eta",
    title: "Uber ETA'ni qanday hisoblaydi",
    summary: "Yo'l grafi, real-time trafik va ML bilan yetib kelish vaqtini bashorat qilish.",
    accent: "#000000",
    status: "rejada",
    level: "murakkab",
    minutes: 32,
    topics: ["Graf", "H3 geoindeks", "ML", "Real-time"],
  },
  {
    order: 13,
    slug: "amazon-s3",
    title: "Amazon S3 qanday ishlaydi",
    summary: "11 ta to'qqizlik ishonchlilik: erasure coding, replikatsiya va metadata qatlami.",
    accent: "#ff9900",
    status: "rejada",
    level: "murakkab",
    minutes: 32,
    topics: ["Object storage", "Erasure coding", "Durability", "Metadata"],
  },
  {
    order: 14,
    slug: "kafka",
    title: "Apache Kafka qanday ishlaydi",
    summary: "Log abstraksiyasi, partition, consumer group va exactly-once semantikasi.",
    accent: "#e11d48",
    status: "rejada",
    level: "murakkab",
    minutes: 34,
    topics: ["Commit log", "Partition", "ISR", "Exactly-once"],
  },
  {
    order: 15,
    slug: "stock-exchange",
    title: "Fond birjasi qanday ishlaydi",
    summary: "Order book, matching engine va mikrosoniyalik kechikish talabi.",
    accent: "#16a34a",
    status: "rejada",
    level: "murakkab",
    minutes: 34,
    topics: ["Order book", "Matching", "Low latency", "Sequencer"],
  },
  {
    order: 16,
    slug: "bluesky",
    title: "Bluesky qanday ishlaydi",
    summary: "AT Protocol: federatsiya, PDS, relay va algoritmik tanlov erkinligi.",
    accent: "#0085ff",
    status: "rejada",
    level: "murakkab",
    minutes: 30,
    topics: ["AT Protocol", "Federatsiya", "Firehose", "DID"],
  },
  {
    order: 17,
    slug: "meta-serverless",
    title: "Meta Serverless qanday ishlaydi",
    summary: "XFaaS: million darajadagi funksiya chaqiruvi, sovuq start va rejalashtirish.",
    accent: "#0064e0",
    status: "rejada",
    level: "murakkab",
    minutes: 30,
    topics: ["FaaS", "Scheduling", "Cold start", "Quota"],
  },
];

export const lessonBySlug = (slug: string) => lessons.find((l) => l.slug === slug);

export const readyLessons = () => lessons.filter((l) => l.status === "tayyor");

export function neighbours(slug: string) {
  const i = lessons.findIndex((l) => l.slug === slug);
  return {
    prev: i > 0 ? lessons[i - 1] : undefined,
    next: i >= 0 && i < lessons.length - 1 ? lessons[i + 1] : undefined,
  };
}

/**
 * Qorong'i brend ranglari (Uber qora, Slack to'q siyohrang) qora fonda o'qilmaydi.
 * Shu sabab yorug'ligi past ranglar oq tomonga aralashtiriladi.
 */
export function readableAccent(hex: string): string {
  const m = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => {
    const c = v / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return luminance < 0.18 ? `color-mix(in oklab, ${hex} 55%, white)` : hex;
}
