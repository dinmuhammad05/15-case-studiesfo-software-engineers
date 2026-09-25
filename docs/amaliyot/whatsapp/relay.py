"""Server: saqla va uzat navbati. TODO qismlarini to'ldiring.

Server xabar MAZMUNINI ko'rmaydi (env.body shifrlangan deb faraz qilinadi) —
faqat konvert: kimdan, kimga, msg_id.

Tarmoq chaqiruvlari `self.net.call(fn, *args)` orqali: u LOST qaytarishi
mumkin (so'rov yoki javob yo'qoldi). LOST bo'lsa, fn chaqirilgan bo'lishi
ham, bo'lmasligi ham mumkin — siz bilmaysiz. Shuning uchun hamma narsa
idempotent bo'lishi kerak.
"""
from collections import OrderedDict

from common import LOST, Envelope


class Relay:
    REDELIVER_EVERY = 3.0  # soniya: tasdiqlanmagan xabarni qayta yetkazish oralig'i

    def __init__(self, net, phones: dict, clock):
        self.net = net
        self.phones = phones          # device_id -> Phone (yetkazish uchun)
        self.clock = clock            # clock() -> hozirgi virtual vaqt (s)
        self.online: set[str] = set()

        # TAYYOR tuzilma — bench uni o'qiydi, nomini o'zgartirmang:
        # qabul qiluvchi qurilma -> OrderedDict[(frm, msg_id) -> Envelope]
        self.queue: dict[str, OrderedDict] = {}

        # TAYYOR: Little qonuni uchun statistika. Siz faqat chaqirasiz.
        self.stats_accepted: dict[tuple, float] = {}   # kalit -> qabul vaqti
        self.stats_removed: dict[tuple, float] = {}    # kalit -> o'chirilgan vaqti

    # ---- TAYYOR yordamchilar ------------------------------------------------
    def _accepted(self, key):
        """Xabar BIRINCHI marta navbatga kirganda chaqiring."""
        self.stats_accepted.setdefault(key, self.clock())

    def _removed(self, key):
        """Xabar navbatdan o'chirilganda chaqiring (✓✓ olingandan keyin)."""
        self.stats_removed.setdefault(key, self.clock())

    def queue_size(self) -> int:
        return sum(len(q) for q in self.queue.values())

    # ---- TODO ----------------------------------------------------------------
    def submit(self, env: Envelope) -> bool:
        """Telefondan xabar keldi. True qaytarish = ✓ (server saqladi).

        TODO:
          1. key = (env.frm, env.msg_id)
          2. Agar key allaqachon ko'rilgan bo'lsa (navbatda YOKI allaqachon
             yetkazilgan) — hech narsa qilmang, True qaytaring. Bu idempotentlik:
             telefon javobni olmay qayta yuborgan.
             Maslahat: stats_accepted allaqachon "ko'rilganlar" ro'yxati.
          3. Aks holda: self.queue[env.to][key] = env; self._accepted(key)
          4. Agar env.to onlayn bo'lsa — darhol yetkazishga urining
          5. True qaytaring

        MUHIM: True ni navbatga yozgandan KEYIN qaytaring (darsning 5-bo'limi,
        2-qadam). Bu simulyatsiyada yozish bir zumda, lekin tartib — odat.
        """
        raise NotImplementedError("TODO: submit")

    def connect(self, device_id: str) -> None:
        """Telefon ulandi. TODO: onlayn to'plamga qo'shing va navbatni
        TARTIB bilan yetkazishga urining (OrderedDict tartibi)."""
        raise NotImplementedError("TODO: connect")

    def disconnect(self, device_id: str) -> None:
        """Telefon uzildi. TODO: onlayn to'plamdan olib tashlang.
        Navbatga TEGMANG — xabarlar keyingi ulanishni kutadi."""
        raise NotImplementedError("TODO: disconnect")

    def tick(self) -> None:
        """Har soniyada chaqiriladi. TODO: onlayn qurilmalar uchun
        tasdiqlanmagan xabarlarni (va yuboruvchilarga kutayotgan ✓✓
        belgilarini) qayta yetkazishga urining — lekin REDELIVER_EVERY
        oralig'idan tez-tez emas."""
        raise NotImplementedError("TODO: tick")

    # Ichki yordamchi — o'zingiz yozing, masalan:
    # def _try_deliver(self, device_id, key, env): ...
    #     res = self.net.call(self.phones[device_id].on_deliver, env)
    #     res is True  -> telefon SAQLADI: navbatdan o'chiring, self._removed(key),
    #                     yuboruvchiga "delivered" (✓✓) belgisini yuborish uchun
    #                     navbatga qo'ying (u ham oflayn bo'lishi mumkin!)
    #     res is LOST  -> hech narsa qilmang, keyingi tick'da qayta urinasiz
