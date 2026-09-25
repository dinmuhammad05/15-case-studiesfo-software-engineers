"""Gateway: WebSocket ulanishlari, obunalar, pub/sub va quvib yetish.

Ikkita nusxa ishlaydi (PORT=8001 va PORT=8002). Ular bir-birini bilmaydi —
faqat Redis pub/sub orqali bog'langan.
"""
import asyncio
import os

import redis.asyncio as aioredis
import websockets

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
PORT = int(os.environ.get("PORT", "8001"))
MAX_QUEUE = 500  # Sekin mijoz chegarasi (darsning 13.1-bo'limi)

# channel_id -> set(websocket).  Faqat SHU gateway'dagi ulanishlar.
# Darsning 6.2-bo'limi: bu jadval markazlashtirilmaydi — u gateway
# bilan birga o'ladi, va aynan shu kerak.
subscribers: dict[str, set] = {}


async def on_connect(ws):
    """Mijoz ulandi: obuna va quvib yetish.

    Mijoz birinchi xabarda kursorlarini yuboradi:
      {"type": "hello", "cursors": {"C1": "1405894322.002768", "C2": "0"}}

    TODO:
      1. hello xabarini o'qing
      2. Har bir kanal uchun subscribers[ch].add(ws)
      3. Har bir kanal uchun GET /history?after=<kursor> va
         natijani mijozga yuboring — BU QUVIB YETISH (5.8-qadam)
      4. Quvib yetish tugagach {"type": "ready"} yuboring

    Tartib muhim: avval OBUNA, keyin tarix. Teskari qilsangiz,
    ikkisi orasida kelgan xabar yo'qoladi. (Obuna oldin bo'lsa
    dublikat bo'lishi mumkin — bu xavfsiz, mijoz ts bo'yicha
    tanib oladi.)
    """
    raise NotImplementedError("TODO: on_connect")


async def pubsub_loop():
    """Redis pub/sub'dan xabarlarni olib, obunachilarga tarqatadi.

    TODO:
      1. psubscribe("ch:*")
      2. Har bir xabarda: kanal nomini ajrating, subscribers[ch] ni oling
      3. Har bir ws ga yuboring

    MUHIM — darsning 3-bo'limidagi Deep bloki:
    `for ws in subs: await ws.send(payload)` YOZMANG.
    Bitta sekin mijoz butun halqani to'xtatadi (head-of-line blocking).

    O'rniga: har bir ulanish uchun alohida navbat va yuborish vazifasi,
    yoki asyncio.gather(..., return_exceptions=True).
    Navbat MAX_QUEUE dan oshsa — ulanishni uzing. Mijoz qayta ulanadi
    va quvib yetadi; sekin mijozga xizmat qilishdan bu arzonroq.
    """
    raise NotImplementedError("TODO: pubsub_loop")


async def ping_loop():
    """Har 30 soniyada ping, ikki javobsiz ping'dan keyin uzish.

    TODO: websockets kutubxonasi ping_interval/ping_timeout bilan buni
    o'zi qiladi — serve() chaqiruvida sozlang va bu funksiyani o'chiring.
    Qo'lda yozsangiz, opcode 0x9/0xA ishlatiling (RFC 6455, 5.5).
    """
    raise NotImplementedError("TODO: ping_loop (yoki serve() da sozlang)")


async def main():
    async with websockets.serve(on_connect, "0.0.0.0", PORT):
        await asyncio.gather(pubsub_loop())


if __name__ == "__main__":
    asyncio.run(main())
