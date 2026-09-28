"""Soxta disklar klasteri (tayyor, o'zgartirmang).

Disk — bo'laklar lug'ati: chunk_id -> bytes. Nosozliklarni tekshiruv
skripti kiritadi:
  disk.kill()                 — disk butunlay o'ladi: har qanday amal DiskDead
  disk.corrupt(chunk_id)      — JIM buzilish: bitta bayt o'zgaradi, disk xato bermaydi
"""
import itertools


class DiskDead(Exception):
    pass


class Disk:
    _ids = itertools.count(1)

    def __init__(self, disk_id, az):
        self.id = disk_id
        self.az = az
        self.alive = True
        self._chunks = {}

    # --- Store ishlatadigan amallar ---
    def write(self, data):
        """Bo'lakni yozadi va uning chunk_id sini qaytaradi."""
        self._check()
        cid = f"c{next(Disk._ids)}"
        self._chunks[cid] = bytes(data)
        return cid

    def read(self, chunk_id):
        """Bo'lak baytlari. Bo'lmasa KeyError, disk o'lik bo'lsa DiskDead."""
        self._check()
        return self._chunks[chunk_id]

    def delete(self, chunk_id):
        self._check()
        self._chunks.pop(chunk_id, None)

    @property
    def used(self):
        """Band baytlar (joylashtirishda muvozanat uchun). O'lik diskda ham o'qiladi."""
        return sum(len(v) for v in self._chunks.values())

    # --- tekshiruv uchun nosozliklar ---
    def kill(self):
        self.alive = False

    def corrupt(self, chunk_id, pos=0):
        b = bytearray(self._chunks[chunk_id])
        if b:
            b[pos % len(b)] ^= 0x5A
        self._chunks[chunk_id] = bytes(b)

    def chunk_ids(self):
        return list(self._chunks)

    def _check(self):
        if not self.alive:
            raise DiskDead(self.id)


def make_cluster(azs=("az-a", "az-b", "az-c"), per_az=6):
    """3 ta AZ, har birida 6 ta disk."""
    return [Disk(f"{az}-d{i}", az) for az in azs for i in range(per_az)]
