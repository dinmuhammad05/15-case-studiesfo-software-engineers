"""Simulyatsiya qilingan mijoz: qayta ulanish, jitter, kursorlar.

bench.py shu sinfdan minglab nusxa yaratadi.
"""
import asyncio
import os
import random
import time
import uuid

JITTER = os.environ.get("JITTER", "on") == "on"
BACKOFF_CAP = 30


class Client:
    def __init__(self, client_id: str, channels: list[str], gateways: list[str]):
        self.id = client_id
        self.channels = channels
        self.gateways = gateways
        # kanal -> oxirgi ko'rilgan ts (darsning 5.8-qadami)
        self.cursors = {c: "0" for c in channels}
        # bench shu ikkitasini o'qiydi — nomlarini o'zgartirmang
        self.seen: dict[str, set] = {c: set() for c in channels}
        self.dup_delivered = 0
        self.reconnects = 0
        # bench cho'qqini shu ro'yxatdan hisoblaydi — har qayta
        # ulanishda time.perf_counter() qo'shing
        self.reconnect_times: list[float] = []

    def reconnect_delay(self, attempt: int) -> float:
        """Qayta ulanishdan oldingi kutish.

        TODO:
          base = min(BACKOFF_CAP, 2 ** attempt)
          JITTER bo'lsa:  random.uniform(0, base)     <- TO'LIQ jitter
          JITTER bo'lmasa: base                        <- jittersiz

        Diqqat: `base + random.uniform(0, 1)` TO'LIQ JITTER EMAS.
        U to'lqinni tarqatmaydi, faqat biroz xiralashtiradi.
        Bench ikkala rejim orasida kamida 10 barobar farq kutadi.
        """
        raise NotImplementedError("TODO: reconnect_delay")

    async def run(self):
        """Ulanish halqasi: ulan, xabarlarni o'qi, uzilsa qayta ulan.

        TODO:
          attempt = 0
          while not stopped:
              try:
                  gw = random.choice(self.gateways)
                  ws = await connect(gw)
                  await ws.send(hello(cursors=self.cursors))
                  attempt = 0                       # muvaffaqiyat — nolga
                  async for raw in ws:
                      self.on_message(json.loads(raw))
              except ConnectionError:
                  self.reconnects += 1
                  self.reconnect_times.append(time.perf_counter())
                  await asyncio.sleep(self.reconnect_delay(attempt))
                  attempt += 1

        `attempt = 0` ni MUVAFFAQIYATLI ulanishdan keyin qo'ying,
        birinchi xabardan keyin emas — aks holda darhol uziladigan
        ulanish backoff'ni hech qachon oshirmaydi.
        """
        raise NotImplementedError("TODO: run")

    def on_message(self, msg: dict):
        """Xabarni qabul qilish va kursorni yangilash.

        TODO:
          1. ch = msg["channel"], ts = msg["ts"]  (ts SATR!)
          2. Agar msg["client_msg_id"] allaqachon ko'rilgan bo'lsa:
                 self.dup_delivered += 1  va QAYTING (ko'rsatmang)
          3. self.seen[ch].add(msg["client_msg_id"])
          4. KURSORNI OXIRIDA yangilang:
                 if ts > self.cursors[ch]: self.cursors[ch] = ts
             (satr taqqoslash to'g'ri ishlaydi — format qat'iy)

        4-qadamni 2-qadamdan OLDIN qilsangiz, dublikat aniqlanganda
        kursor allaqachon siljigan bo'ladi va keyingi quvib yetish
        xabarlarni o'tkazib yuboradi -> bench'da `lost` > 0.
        """
        raise NotImplementedError("TODO: on_message")
