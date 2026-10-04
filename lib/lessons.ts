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
      "TinyURL'dan goo.gl yopilishigacha: kalit maydoni, Feistel, chekka kesh va havola umri — bitta kalit-qiymat qidiruv qanday qilib sekundiga 19 000 redirect'ga aylanadi.",
    accent: "#ee6123",
    status: "tayyor",
    level: "o'rta",
    minutes: 165,
    topics: [
      "Base62",
      "Feistel",
      "Tug'ilgan kun paradoksi",
      "301 vs 302",
      "Cache stampede",
      "Hot key",
      "Bloom filtri",
      "HyperLogLog",
      "Zipf va yarim yemirilish",
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
      "LLOOGG'dan Valkey'gacha: event loop, xotira modeli, skiplist va HyperLogLog ichidan, 12 ta amaliy stsenariy va ularning har biridagi tuzoqlar.",
    accent: "#dc382d",
    status: "tayyor",
    level: "o'rta",
    minutes: 165,
    topics: [
      "Event loop",
      "Xotira modeli",
      "Kodlashlar",
      "TTL va eviction",
      "RDB va AOF",
      "fork va COW",
      "ZSET va skiplist",
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
    summary:
      "Ishni qachon bajarish kerak — yozishdami yoki o'qishda? 100 million obunachili akkaunt bu savolni qanday o'zgartiradi.",
    accent: "#1d9bf0",
    status: "tayyor",
    level: "o'rta",
    minutes: 125,
    topics: [
      "Fan-out on write",
      "Fan-out on read",
      "Gibrid fan-out",
      "Hot key",
      "Snowflake ID",
      "Hidratsiya",
      "Tombstone",
      "Reyting",
      "Qayta qurish",
    ],
  },
  {
    order: 5,
    slug: "reddit",
    title: "Reddit qanday ishlaydi",
    summary:
      "Ovozni ballga aylantiruvchi matematika: 'hot' formulasi, Wilson intervali, 500 000 kommentariyali daraxt va ovoz manipulyatsiyasiga qarshi himoya.",
    accent: "#ff4500",
    status: "tayyor",
    level: "murakkab",
    minutes: 150,
    topics: [
      "Ranking formulasi",
      "Wilson intervali",
      "Ovoz navbati",
      "ZSET ro'yxatlar",
      "Kommentariya daraxti",
      "Sharding",
      "Vote manipulation",
      "Sig'im rejalashtirish",
    ],
  },
  {
    order: 6,
    slug: "slack",
    title: "Slack qanday ishlaydi",
    summary:
      "Doimiy ulanish iqtisodi: WebSocket nima turadi, presence nega xabarlardan 50 000 barobar qimmat, va qayta ulanish bo'roni qanday to'xtatiladi.",
    accent: "#4a154b",
    status: "tayyor",
    level: "murakkab",
    minutes: 180,
    topics: [
      "WebSocket",
      "Ulanish iqtisodi",
      "Presence obunasi",
      "Chekka kesh",
      "Xabar tartibi",
      "Qayta ulanish bo'roni",
      "Jitter va backoff",
      "Ko'p ijarachi izolyatsiya",
    ],
  },
  {
    order: 7,
    slug: "whatsapp",
    title: "WhatsApp qanday ishlaydi",
    summary:
      "Server o'qiy olmaydigan xabar: Diffie-Hellman'dan Double Ratchet'gacha, oflayn telefonga saqla-va-uzat navbati, guruhlardagi kvadratik tuzoq va nega bularning hammasi juda arzon.",
    accent: "#25d366",
    status: "tayyor",
    level: "murakkab",
    minutes: 185,
    topics: [
      "Diffie-Hellman",
      "X3DH va prekey",
      "Double Ratchet",
      "Sender Keys",
      "Saqla va uzat",
      "Little qonuni",
      "Push va uyg'onish",
      "Metama'lumot",
    ],
  },
  {
    order: 8,
    slug: "youtube",
    title: "YouTube qanday ishlaydi",
    summary:
      "Kuniga 1 eksabayt: kodek videoni 150 barobar qanday siqadi, pleyer har 4 soniyada qanday qaror qiladi, va nega eng yaxshi kodek faqat videolarning 2% i uchun o'zini oqlaydi.",
    accent: "#ff0000",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Kodek va I-kadr",
      "Bitreyt zinapoyasi",
      "HLS / DASH",
      "ABR algoritmlari",
      "Transkodlash quvuri",
      "Uzun dum iqtisodi",
      "Provayder keshlari",
      "QoE",
    ],
  },
  {
    order: 9,
    slug: "spotify",
    title: "Spotify qanday ishlaydi",
    summary:
      "Kuniga 8.6 milliard tinglash: qo'shiq 250 ms da qanday boshlanadi, treklar orasidagi pauza qanday yo'qoladi, har bir tinglash qanday qilib pulga aylanadi, va nega infratuzilma huquq to'lovlaridan 50 barobar arzon.",
    accent: "#1db954",
    status: "tayyor",
    level: "murakkab",
    minutes: 180,
    topics: [
      "Psixoakustik kodek",
      "Gapless ijro",
      "Oldindan yuklash",
      "Qurilma keshi va oflayn",
      "Tinglashlar kitobi",
      "Royalti modellari",
      "Matritsa faktorizatsiyasi",
      "ANN qidiruv",
      "Bot fermalari",
    ],
  },
  {
    order: 10,
    slug: "google-docs",
    title: "Google Docs qanday ishlaydi",
    summary:
      "Yuz kishi bitta paragrafni bir vaqtda yozadi, hech kim kutmaydi va hamma bir xil matnni ko'radi: operatsion transformatsiya, CRDT, hujjat egalari va nega eng qiyin muammo ikki kishida ham paydo bo'ladi.",
    accent: "#4285f4",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Operatsiyalar",
      "Operatsion transformatsiya",
      "Jupiter protokoli",
      "CRDT",
      "Kursorlar va presence",
      "Jurnal va suratlar",
      "Hujjat egasi va fencing",
      "Versiyalar tarixi",
    ],
  },
  {
    order: 11,
    slug: "airbnb",
    title: "Airbnb qanday ishlaydi",
    summary:
      "Kuniga 350 ming bron, lekin bitta kecha uchun ikki bron — nol: sana va tun modeli, ma'lumotlar bazasi cheklovlari, vaqtincha ushlab turish, idempotent to'lovlar, buxgalteriya kitobi va xarita bo'yicha qidiruv.",
    accent: "#ff5a5f",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Tun va kalendar modeli",
      "Ikki marta bron bo'lmasligi",
      "Vaqtincha ushlab turish",
      "Idempotentlik",
      "To'lov va buxgalteriya",
      "Geo qidiruv",
      "Qidiruv reytingi",
      "Monolitdan servislarga",
    ],
  },
  {
    order: 12,
    slug: "uber-eta",
    title: "Uber ETA'ni qanday hisoblaydi",
    summary:
      "Ilovadagi \"7 daqiqa\" ortida: yo'l grafi va Dijkstra'dan Contraction Hierarchies'gacha, GPS nuqtalaridan jonli tirbandlik, H3 geoindeksi va marshrut xatosini tuzatuvchi DeepETA modeli.",
    accent: "#276ef1",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Yo'l grafi",
      "Dijkstra va A*",
      "Contraction Hierarchies",
      "Map matching",
      "Jonli tirbandlik",
      "H3 geoindeks",
      "DeepETA",
      "Dispetcherlik",
    ],
  },
  {
    order: 13,
    slug: "amazon-s3",
    title: "Amazon S3 qanday ishlaydi",
    summary:
      "Yuzlab trillion fayl va \"11 ta to'qqizlik\" va'dasi: disklar har kuni buziladi, lekin ma'lumot yo'qolmaydi. Replikatsiya va erasure coding, metadata indeksi, kuchli izchillik va xatolarni jim tuzatuvchi tizimlar.",
    accent: "#ff9900",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Object storage",
      "Durability (11 ta to'qqiz)",
      "Replikatsiya",
      "Erasure coding",
      "Metadata indeksi",
      "Kuchli izchillik",
      "Saqlash sinflari",
      "Nazorat summalari",
    ],
  },
  {
    order: 14,
    slug: "kafka",
    title: "Apache Kafka qanday ishlaydi",
    summary:
      "Kuniga trillionlab xabar bitta oddiy g'oya ustida: faqat oxiriga yoziladigan jurnal. Partition va offset, replikatsiya va ISR, consumer group'lar, idempotent producer va exactly-once, ZooKeeper'siz Kafka.",
    accent: "#e11d48",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: [
      "Commit log",
      "Partition va offset",
      "Replikatsiya va ISR",
      "High watermark",
      "Consumer group",
      "Exactly-once",
      "Log compaction",
      "KRaft",
    ],
  },
  {
    order: 15,
    slug: "stock-exchange",
    title: "Fond birjasi qanday ishlaydi",
    summary:
      "Sekundiga millionlab buyurtma, mikrosekundlar va bir tiyin ham xatosiz: buyurtmalar kitobi, matching engine, sekvenser va jurnal, bozor ma'lumotlari oqimi, adolat va nosozliklarga chidamlilik.",
    accent: "#16a34a",
    status: "tayyor",
    level: "murakkab",
    minutes: 180,
    topics: ["Order book", "Matching engine", "Sekvenser", "Deterministik replay", "Market data", "Kechikish", "Risk nazorati", "Adolat"],
  },
  {
    order: 16,
    slug: "bluesky",
    title: "Bluesky qanday ishlaydi",
    summary:
      "Hisobingiz — sizniki, algoritm — tanlovingiz: imzolangan shaxsiy repolar, DID va domen-handle, butun tarmoq firehose'i, relay va AppView, maxsus feed'lar va moderatsiya qatlamlari.",
    accent: "#0085ff",
    status: "tayyor",
    level: "murakkab",
    minutes: 175,
    topics: ["AT Protocol", "PDS va repo", "Merkle Search Tree", "DID va handle", "Firehose", "Relay va AppView", "Maxsus feed'lar", "Moderatsiya"],
  },
  {
    order: 17,
    slug: "meta-serverless",
    title: "Meta Serverless qanday ishlaydi",
    summary:
      "Kuniga trillionlab funksiya chaqiruvi va 66% o'rtacha bandlik: sovuq startni yo'qotish, kechiktiriladigan ishni tunga surish, muddat va kvota bilan rejalashtirish, ma'lumotlar bazasini TCP kabi himoya qilish.",
    accent: "#0064e0",
    status: "tayyor",
    level: "murakkab",
    minutes: 170,
    topics: ["FaaS", "Sovuq start", "Universal worker", "Rejalashtirish (EDF)", "Kvotalar", "Vaqt bo'yicha surish", "AIMD", "Lokallik guruhlari"],
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
