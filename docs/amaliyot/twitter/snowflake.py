"""Snowflake ID — 2-daraja topshirig'ining 1-qismi. Ikkita joy TODO.

Darsdan: 6-bo'lim 7-qadam. 64 bitli ID:

   1 bit (0) | 41 bit: vaqt (ms, TWEPOCH dan) | 10 bit: mashina | 12 bit: ketma-ketlik

Qoidalar:
  * next_id():
      ts = clock()
      ts < oxirgi ts            -> ClockMovedBackwards (takror ID dan ko'ra xato yaxshi)
      ts == oxirgi ts           -> ketma-ketlik + 1 (12 bit, & 4095). U 0 ga qaytsa —
                                   shu millisekund to'ldi: clock() ni qayta-qayta
                                   chaqirib, KEYINGI millisekundni kuting
      ts > oxirgi ts            -> ketma-ketlik 0
      id = (ts - TWEPOCH) << 22 | mashina << 12 | ketma-ketlik
  * parse(id) -> (ts_ms, mashina, ketma-ketlik) — teskari amal.
  * Mashina ID 0..1023, aks holda ValueError (konstruktor tayyor).

Tekshiruv: python check.py
"""

TWEPOCH = 1288834974657          # Twitter epoch: 2010-11-04
MACHINE_BITS = 10
SEQ_BITS = 12
MAX_MACHINE = (1 << MACHINE_BITS) - 1
SEQ_MASK = (1 << SEQ_BITS) - 1


class ClockMovedBackwards(Exception):
    pass


class Snowflake:
    def __init__(self, machine_id, clock):
        if not 0 <= machine_id <= MAX_MACHINE:
            raise ValueError("mashina ID 0..1023")
        self.machine = machine_id
        self.clock = clock         # chaqirilsa millisekund qaytaradi
        self.last = -1             # oxirgi ID berilgan millisekund
        self.seq = 0

    def next_id(self):
        # TODO
        raise NotImplementedError("Snowflake.next_id")


def parse(sid):
    # TODO: (ts_ms, mashina, ketma-ketlik)
    raise NotImplementedError("parse")
