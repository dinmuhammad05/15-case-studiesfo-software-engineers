"""ETA dvigateli — 2-daraja topshirig'i. Oltita funksiya TODO.

Hammasi darsdan: Dijkstra (5-bo'lim 1-qadam), A* (2-qadam), ikki tomonlama
qidiruv (3-qadam), jonli tezliklar va tarix bilan aralashtirish (7-8-qadamlar),
marshrut xatosini bashorat qiluvchi qoldiq modeli (10-qadam).

Kelishuvlar:
  * g — city.Graph. g.adj[u] = [(v, edge_id)], g.radj[v] = [(u, edge_id)].
  * w — qirra og'irliklari ro'yxati, soniyada (w[edge_id]). g.weights() beradi.
  * Qidiruv funksiyalari (vaqt, yo'l, o'rnatilgan_tugunlar) qaytaradi:
      vaqt  — s dan t gacha eng kichik soniya (yetib bo'lmasa: math.inf)
      yo'l  — tugunlar ro'yxati [s, ..., t] (yetib bo'lmasa: [])
      o'rnatilgan_tugunlar — navbatdan chiqarilib "yakunlangan" tugunlar soni
        (eskirgan navbat yozuvlari sanalmaydi). Ikki tomonlama qidiruvda —
        ikkala tomon yig'indisi.
  * Faqat Python standart kutubxonasi (heapq, statistics, math).

Tekshiruv: python check.py
"""
import heapq  # noqa: F401
import math  # noqa: F401
import statistics  # noqa: F401

MAX_KMH = 160.0  # bundan tez "o'tish" — GPS sakrashi, hisobga olinmaydi


def dijkstra(g, s, t, w):
    """Klassik Dijkstra. Javob t navbatdan CHIQARILGANDA aniq — unga birinchi
    marta yetilganda emas."""
    raise NotImplementedError("TODO: dijkstra")


def astar(g, s, t, w, vmax_kmh):
    """A*: navbat tartibi d(u) + h(u), h(u) = evklid_masofa(u, t) / vmax.

    vmax_kmh — grafdagi eng yuqori tezlik. h optimistik bo'lishi shart:
    hech qachon haqiqiy qolgan vaqtdan katta emas. (Masofalar metrda,
    tezlik km/soatda: 1 km/soat = 1000/3600 m/s; g.dist(a, b) — metr.)"""
    raise NotImplementedError("TODO: astar")


def bidirectional(g, s, t, w):
    """Ikki tomonlama Dijkstra: s dan g.adj bo'yicha, t dan g.radj bo'yicha.

    mu — topilgan eng yaxshi yo'l; qirra ikkinchi tomon ko'rgan tugunga
    olib borganda yangilanadi. To'xtash: oldinga navbat boshi + orqaga
    navbat boshi >= mu. Birinchi uchrashuvda to'xtash — XATO."""
    raise NotImplementedError("TODO: bidirectional")


def live_speeds(g, observations, now, hist_kmh, k=5.0, window=600.0):
    """Har qirra uchun joriy tezlik (km/soat) ro'yxati.

    observations — [(edge_id, o'tish_soniya, haydovchi_id, vaqt), ...]
    Faqat now - window <= vaqt <= now bo'lgan kuzatuvlar ishlatiladi.
    Kuzatuv tezligi = g.length[e] / o'tish_soniya (km/soatga aylantiring);
    MAX_KMH dan tez bo'lsa — tashlanadi.

    Har qirra uchun:
      1) har haydovchining qiymati — uning kuzatuvlari medianasi
         (bitta haydovchi ko'p kuzatuv bilan natijani egallab olmasin);
      2) jonli = haydovchilar qiymatlarining medianasi, n = haydovchilar soni;
      3) natija = (n * jonli + k * hist_kmh[e]) / (n + k).
    Kuzatuv bo'lmasa — hist_kmh[e] o'zi."""
    raise NotImplementedError("TODO: live_speeds")


def fit_residual(trips, min_count=20):
    """Qoldiq modeli: haqiqiy_vaqt / marshrut_ETA nisbatining MEDIANASI
    guruhlar bo'yicha. trips — [{"route_s", "actual_s", "hour", "zone"}, ...].

    Guruhlar: (zone, hour), hour, global. Guruhda min_count dan kam safar
    bo'lsa — u ishlatilmaydi (predict keyingi darajaga tushadi).
    Qaytaradi: istalgan obyekt — predict uni qabul qiladi."""
    raise NotImplementedError("TODO: fit_residual")


def predict(model, route_s, hour, zone):
    """Yakuniy ETA (soniya) = route_s x koeffitsient. Koeffitsient —
    (zone, hour) guruhidan; yetarli ma'lumot bo'lmasa — hour; bo'lmasa —
    global. Noma'lum zona ham ishlashi kerak."""
    raise NotImplementedError("TODO: predict")
