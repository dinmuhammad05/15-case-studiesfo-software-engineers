"""Telefon: yuborish, qayta urinish, qabul qilish, belgilar. TODO qismlarini to'ldiring."""
from common import LOST, Envelope


class Phone:
    RETRY_AFTER = 5.0  # soniya: ✓ kelmagan xabarni qayta yuborish oralig'i

    def __init__(self, device_id: str, net, relay, clock):
        self.id = device_id
        self.net = net
        self.relay = relay
        self.clock = clock
        self._seq = 0

        # TAYYOR tuzilmalar — bench ularni o'qiydi, nomlarini o'zgartirmang:
        self.outbox: dict[str, Envelope] = {}   # msg_id -> yuborilgan xabar
        self.status: dict[str, int] = {}        # msg_id -> 0 kutilmoqda, 1 ✓, 2 ✓✓
        self.inbox: list[Envelope] = []         # EKRANDA KO'RSATILGAN xabarlar

        self._last_try: dict[str, float] = {}

    def new_msg_id(self) -> str:
        """TAYYOR: mijoz yaratadigan noyob identifikator (darsning 4.4-bo'limi)."""
        self._seq += 1
        return f"{self.id}-{self._seq}"

    # ---- TODO ----------------------------------------------------------------
    def send(self, to: str, body: str) -> str:
        """Xabar yuborish. TODO:
          1. msg_id = self.new_msg_id(); env = Envelope(self.id, to, msg_id, body)
          2. outbox ga yozing, status = 0
          3. self._try_submit(msg_id)
          4. msg_id qaytaring
        """
        raise NotImplementedError("TODO: send")

    def tick(self) -> None:
        """Har soniyada (faqat onlayn bo'lganda) chaqiriladi.
        TODO: status == 0 va oxirgi urinishdan RETRY_AFTER o'tgan xabarlarni
        XUDDI SHU msg_id bilan qayta yuboring."""
        raise NotImplementedError("TODO: tick")

    def on_deliver(self, env: Envelope) -> bool:
        """Server xabar yetkazdi. True qaytarish = ack (telefon SAQLADI).

        TODO:
          1. Agar (env.frm, env.msg_id) allaqachon inbox'da bo'lsa —
             qayta KO'RSATMANG, lekin baribir True qaytaring (server
             oldingi ack'ni olmagan bo'lishi mumkin)
          2. Aks holda inbox ga qo'shing
          3. True qaytaring — SAQLAGANDAN KEYIN (darsning 10.2 Deep bloki)

        Tezlik uchun inbox'ni har safar ko'rib chiqmang — alohida set tuting.
        """
        raise NotImplementedError("TODO: on_deliver")

    def on_receipt(self, msg_id: str, kind: str) -> bool:
        """Belgi keldi: kind = "delivered" (✓✓). True = qabul qilindi.

        TODO: status[msg_id] = max(joriy, yangi). Belgilar tartibsiz keladi:
        ✓✓ server ✓ javobi yo'qolgandan keyin kelishi mumkin — va keyin
        kechikkan ✓ kelsa, holat 2 dan 1 ga TUSHMASLIGI kerak.
        """
        raise NotImplementedError("TODO: on_receipt")

    # Ichki yordamchi — o'zingiz yozing:
    # def _try_submit(self, msg_id): ...
    #     res = self.net.call(self.relay.submit, self.outbox[msg_id])
    #     res is True -> status monoton ravishda kamida 1
    #     res is LOST -> hech narsa; tick() qayta urinadi
