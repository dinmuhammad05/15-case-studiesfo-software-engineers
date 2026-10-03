"""Tayyor qismlar (o'zgartirmang): funksiya, chaqiruv va barqaror xesh.

Vaqt — butun "tik"lar (masalan, 1 tik = 1 soniya). Har chaqiruv bitta tik
davomida bitta ishchi "slot"ida bajariladi (birlik ish). Bu soddalashtirish
rejalashtirish g'oyalarini aniq tekshirish imkonini beradi: muddatlar,
kvotalar, kritiklik, downstream chegaralari.
"""
import hashlib
from dataclasses import dataclass
from typing import Optional

LOW, NORMAL, HIGH = 0, 1, 2      # kritiklik


@dataclass(frozen=True)
class Call:
    """Funksiya chaqiruvi: submit — navbatga qo'yilgan tik, deadline — eng
    kech bajarilishi mumkin bo'lgan tik (shu tik ham hisob), crit — kritiklik."""
    cid: str
    fn: str
    submit: int
    deadline: int
    crit: int = NORMAL


@dataclass(frozen=True)
class Fn:
    """Funksiya spetsifikatsiyasi.
    rate, burst — kvota (token bucket): har tikda +rate token, ko'pi bilan burst.
    downstream — funksiya chaqiradigan tashqi xizmat (masalan, "tao") yoki None."""
    name: str
    rate: float = 1e9
    burst: int = 10**9
    downstream: Optional[str] = None


def stable_hash(*parts) -> int:
    """Jarayondan jarayonga o'zgarmaydigan 64 bitli xesh (Python hash() dan farqli)."""
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(h[:8], "big")
