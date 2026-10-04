"""Skiplist — 2-daraja topshirig'ining 1-qismi. Beshta usul TODO.

Darsdan: 5-bo'lim 4-stsenariy (reyting), 7-bo'lim (strukturalar ichidan).
Redis'ning ZSET'i — lug'at (a'zo -> ball) va SKIPLIST: ball bo'yicha
tartiblangan, har qidiruv O(log N). Pastdagi ZSet qobig'i tayyor; siz
uning ostidagi skiplistni yozasiz.

Qoidalar (Redis t_zset.c ga yaqin):
  * Tartib — (score, member): avval ball, teng bo'lsa a'zo nomi. before()
    yordamchisi tayyor.
  * header — MAX_LEVEL darajali bo'sh tugun. self.level — hozirgi eng
    baland tugun darajasi (bo'sh ro'yxatda 1).
  * random_level() tayyor: 1 dan boshlab, P=0.25 ehtimol bilan +1.
  * span[i] — forward[i] ko'rsatkichi 0-darajada nechta tugunni sakrab
    o'tadi (header'dan birinchi tugungacha span = 1). Rank — yo'l bo'yicha
    span'lar yig'indisi. check.py har ko'rsatkichning span'ini tekshiradi.
  * backward — 0-darajadagi oldingi tugun (birinchisida None). tail — oxirgi.
  * Bo'sh qolgan yuqori darajalarni delete'dan keyin olib tashlang (self.level).

  insert(member, score)    — a'zo yo'qligi kafolatlangan (ZSet tekshiradi)
  delete(member, score)    — topilsa True, aks holda False
  rank(member, score)      — 0 dan boshlanadigan o'rin yoki None
  by_rank(start, stop)     — ZRANGE kabi: ikkala chegara kiradi, manfiy
                             indeks oxirdan (-1 — oxirgi). [(member, score), ...]
                             Boshlanishga span bo'yicha SAKRANG (O(log N)),
                             keyin 0-darajada yuring.
  range_by_score(lo, hi, offset=0, count=None)
                           — lo <= score <= hi, offset tasini o'tkazib,
                             ko'pi bilan count ta.

Tekshiruv: python check.py
"""
import random

from model import MAX_LEVEL, P, Node


def before(score, member, node):
    """node (score, member) tartibida berilgan juftlikdan QAT'IY oldin turadimi."""
    return node.score < score or (node.score == score and node.member < member)


class SkipList:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.header = Node(None, None, MAX_LEVEL)
        self.tail = None
        self.level = 1
        self.length = 0

    def __len__(self):
        return self.length

    def random_level(self):
        lvl = 1
        while self.rng.random() < P and lvl < MAX_LEVEL:
            lvl += 1
        return lvl

    def insert(self, member, score):
        # TODO: har darajada "update" (oxirgi oldingi tugun) va "rank" (u yerga
        # qadar span yig'indisi) ni toping; yangi tugun darajasini random_level()
        # bilan oling; ko'rsatkichlar va span'larni yangilang; backward va tail.
        raise NotImplementedError("SkipList.insert")

    def delete(self, member, score):
        # TODO
        raise NotImplementedError("SkipList.delete")

    def rank(self, member, score):
        # TODO
        raise NotImplementedError("SkipList.rank")

    def by_rank(self, start, stop):
        # TODO
        raise NotImplementedError("SkipList.by_rank")

    def range_by_score(self, lo, hi, offset=0, count=None):
        # TODO
        raise NotImplementedError("SkipList.range_by_score")


class ZSet:
    """Tayyor qobiq: Redis'dagi kabi lug'at + skiplist."""

    def __init__(self, seed=0):
        self.dict = {}
        self.sl = SkipList(seed)

    def zadd(self, member, score):
        score = float(score)
        old = self.dict.get(member)
        if old is not None:
            if old == score:
                return 0
            self.sl.delete(member, old)
        self.sl.insert(member, score)
        self.dict[member] = score
        return 1 if old is None else 0

    def zincrby(self, member, delta):
        new = self.dict.get(member, 0.0) + delta
        self.zadd(member, new)
        return new

    def zscore(self, member):
        return self.dict.get(member)

    def zrank(self, member):
        s = self.dict.get(member)
        return None if s is None else self.sl.rank(member, s)

    def zrem(self, member):
        s = self.dict.pop(member, None)
        if s is None:
            return False
        self.sl.delete(member, s)
        return True

    def zcard(self):
        return len(self.dict)

    def zrange(self, start, stop):
        return self.sl.by_rank(start, stop)

    def zrevrange(self, start, stop):
        n = len(self.dict)
        start = start + n if start < 0 else start
        stop = stop + n if stop < 0 else stop
        a, b = max(0, n - 1 - stop), n - 1 - max(0, start)
        if b < 0 or a > b:
            return []
        return list(reversed(self.sl.by_rank(a, b)))

    def zrangebyscore(self, lo, hi, offset=0, count=None):
        return self.sl.range_by_score(lo, hi, offset, count)
