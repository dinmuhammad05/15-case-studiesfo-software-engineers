"""Router: lokallik guruhlari — 2-daraja topshirig'ining 3-qismi. Ikkita usul TODO.

Darsdan: 5-bo'lim 4-5-qadamlar, 7-bo'lim. Har ishchida keshda faqat
cheklangan sondagi funksiya "issiq" turadi (JIT kodi, ma'lumot). Har funksiya
hamma ishchiga tarqalsa — keshlar doim sovuq. Shuning uchun har funksiya
kichik, BARQAROR ishchilar guruhiga bog'lanadi.

Qoidalar:
  * group(fn): rendezvous (eng yuqori ball) xeshlash — har ishchi uchun
    ball = stable_hash(fn, ishchi); eng katta group_size ta ball egasi,
    teng bo'lsa — ishchi nomi bo'yicha. Natija ro'yxat tartibiga bog'liq
    emas, ishchi qo'shilganda faqat ~group_size/N funksiya guruhini o'zgartiradi.
    (Har chaqiruvda hamma ishchilar xeshini qayta hisoblamaslik uchun keshlang;
    ishchi qo'shilsa yoki olinsa — keshni tozalang.)
  * route(fn, load, limit=None): guruh ichida eng kam yuklangan ishchi
    (load: ishchi -> shu tikdagi chaqiruvlar soni; teng bo'lsa — guruhdagi
    tartib bo'yicha). Agar limit berilgan va u ishchi ham limitga yetgan
    bo'lsa — guruhdan tashqariga: hamma ishchilar ichidan eng kam yuklangani
    (teng bo'lsa — nomi bo'yicha). Bu — "issiq" funksiyaning to'kilishi:
    sovuq start evaziga navbatsiz bajarilish.

Tekshiruv: python check.py
"""
from model import stable_hash  # noqa: F401


class Router:
    def __init__(self, workers, group_size=3):
        self.workers = list(workers)
        self.group_size = group_size
        self.cache = {}

    def add_worker(self, w):
        if w not in self.workers:
            self.workers.append(w)
            self.cache.clear()

    def remove_worker(self, w):
        self.workers.remove(w)
        self.cache.clear()

    def group(self, fn):
        raise NotImplementedError("TODO: group")

    def route(self, fn, load, limit=None):
        raise NotImplementedError("TODO: route")
