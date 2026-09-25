"""Umumiy tuzilmalar. TAYYOR — o'zgartirish shart emas."""
from dataclasses import dataclass

LOST = object()  # tarmoq so'rovi yoki javobi yo'qoldi


@dataclass(frozen=True)
class Envelope:
    frm: str       # yuboruvchi qurilma
    to: str        # qabul qiluvchi qurilma
    msg_id: str    # mijoz yaratgan identifikator
    body: str      # haqiqiy tizimda — shifrlangan baytlar
