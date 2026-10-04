"""Kesh — 2-daraja topshirig'ining 3-qismi. Uchta usul TODO.

Darsdan: 6-bo'lim 2-3-qadamlar, 8-bo'lim (kesh matematikasi),
10.1 (cache stampede). Vaqt — soniyalarda (float), `now` hech qachon
kamaymaydi. Baza "sekin": o'qish db_latency soniyada tugaydi.

Qoidalar (check.py sodda model bilan har so'rovni AYNAN solishtiradi):

  get(key, now) -> (url yoki None, kutish_soniyasi)
    0. Avval _settle(now): tugagan yuklanishlarni keshga yozish.
    1. Ijobiy yozuv bor:
       - now < fresh_until  -> LRU da "eng yangi" qiling, (url, 0.0).
       - now < stale_until  -> LRU da "eng yangi"; shu kalit yuklanmayotgan
         bo'lsa — FONDA yuklashni boshlang (_start); (eski url, 0.0).
         Bu — stale-while-revalidate: foydalanuvchi kutmaydi.
       - aks holda yozuvni o'chiring va davom eting.
    2. Salbiy yozuv bor: now < expires -> (None, 0.0); aks holda o'chiring.
    3. Kalit hozir yuklanmoqda -> o'sha yuklanish natijasi,
       kutish = ready_at - now. Bu — single-flight: bazaga ikkinchi so'rov YO'Q.
    4. Aks holda _start(key, now): (natija, db_latency).

  _start(key, now) (tayyor): bazadan o'qiydi (reads += 1), natija
    ready_at = now + db_latency da tayyor bo'ladi.

  _settle(now): ready_at <= now bo'lgan yuklanishlarni (ready_at, kalit)
    tartibida yozing:
    - url bor: salbiy yozuvni o'chiring; ijobiy yozuv
      (url, fresh_until = ready_at + ttl, stale_until = fresh_until + stale)
      LRU da "eng yangi"; ijobiylar soni capacity dan oshsa — eng eskisi chiqadi.
    - url yo'q: ijobiy yozuvni o'chiring; salbiy yozuv
      (expires = ready_at + neg_ttl) "eng yangi"; neg_capacity dan oshsa —
      eng eskisi chiqadi.
    Ijobiy va salbiy yozuvlar — IKKI ALOHIDA LRU: skaner yuborgan million
    yo'q kalit issiq havolalarni siqib chiqarmasligi kerak.

  invalidate(key): ijobiy, salbiy yozuvni va tugallanmagan yuklanishni
    o'chiradi (havola o'chirilganda yoki manzili o'zgarganda).

Muddati o'tgan yozuvlar faqat so'ralganda o'chiriladi (1 va 2-band), shu
sababli ular LRU sig'imida joy egallab turadi — sodda model ham shunday.

Tekshiruv: python check.py
"""
import heapq  # noqa: F401
from collections import OrderedDict


class LinkCache:
    def __init__(self, store, capacity, neg_capacity, ttl, neg_ttl, stale, db_latency):
        self.store = store
        self.capacity = capacity
        self.neg_capacity = neg_capacity
        self.ttl = ttl
        self.neg_ttl = neg_ttl
        self.stale = stale
        self.db_latency = db_latency
        self.pos = OrderedDict()     # kalit -> (url, fresh_until, stale_until); boshida — eng eski
        self.neg = OrderedDict()     # kalit -> expires
        self.inflight = {}           # kalit -> (ready_at, natija)
        self.heap = []               # (ready_at, kalit) — _settle uchun

    def _start(self, key, now):
        value = self.store.get(key)
        ready = now + self.db_latency
        self.inflight[key] = (ready, value)
        heapq.heappush(self.heap, (ready, key))
        return ready, value

    def _settle(self, now):
        # TODO: tugagan yuklanishlarni (ready_at, kalit) tartibida keshga yozish.
        # Eslatma: heap'da bekor qilingan (invalidate) yuklanishlar qolishi mumkin —
        # self.inflight da yo'q yoki ready_at boshqa bo'lsa, o'tkazib yuboring.
        raise NotImplementedError("LinkCache._settle")

    def get(self, key, now):
        # TODO: yuqoridagi 0-4 bandlar
        raise NotImplementedError("LinkCache.get")

    def invalidate(self, key):
        # TODO
        raise NotImplementedError("LinkCache.invalidate")
