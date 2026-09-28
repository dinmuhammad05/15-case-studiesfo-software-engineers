"""Tayyor yordamchilar (o'zgartirmang): ulanish, tranzaksiya, narx,
xatolar va soxta to'lov provayderi.

Faqat Python standart kutubxonasi (sqlite3).
"""
import contextlib
import os
import sqlite3

HOLD_TTL = 15 * 60          # 5-bo'lim 2-qadam: ushlab turish 15 daqiqa
FEE_PERCENT = 15            # platforma ulushi (soddalashtirilgan)
MAX_NIGHTS = 365

HERE = os.path.dirname(os.path.abspath(__file__))


class Invalid(Exception):
    """Noto'g'ri so'rov: sanalar tartibi, minimal tunlar, noma'lum e'lon."""


class Busy(Exception):
    """Kamida bitta tun band."""


class IdemMismatch(Exception):
    """Idempotentlik kaliti boshqa parametrlar bilan qayta ishlatildi."""


class Declined(Exception):
    """Provayder to'lovni rad etdi (karta, mablag')."""


class Timeout(Exception):
    """Provayder javob bermadi. Pul yechilgan bo'lishi HAM, yechilmagan bo'lishi HAM mumkin."""


def connect(path):
    """Har jarayon o'z ulanishini ochadi. Avtokommit rejimi: tranzaksiyalar
    faqat tx() orqali, aniq boshlanadi va tugaydi."""
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init(path):
    conn = connect(path)
    with open(os.path.join(HERE, "schema.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


@contextlib.contextmanager
def tx(conn):
    """Yozish tranzaksiyasi: BEGIN IMMEDIATE ... COMMIT, istisnoda ROLLBACK.

    IMMEDIATE — yozish qulfini darhol oladi. SQLite'da bu butun bazaga
    bitta yozuvchi degani (darsning 7.1-bo'limidagi pessimistik qulf).
    Ichidagi istisno tranzaksiyani to'liq qaytaradi va yuqoriga uchadi.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def quote(conn, listing_id, n_nights):
    """(amount_minor, min_nights) yoki Invalid — e'lon topilmasa."""
    row = conn.execute(
        "SELECT nightly_minor, cleaning_minor, min_nights FROM listings WHERE id = ?",
        (listing_id,),
    ).fetchone()
    if row is None:
        raise Invalid(f"e'lon {listing_id} yo'q")
    return row["nightly_minor"] * n_nights + row["cleaning_minor"], row["min_nights"]


def split(amount_minor):
    """(host_minor, fee_minor): yig'indi har doim aynan amount_minor (8.2)."""
    fee = amount_minor * FEE_PERCENT // 100
    return amount_minor - fee, fee


class FakeProvider:
    """Soxta to'lov provayderi. Holati bazadagi provider_ops jadvalida,
    shuning uchun bir nechta jarayon uchun ham bitta.

    Haqiqiy provayderlar kabi idempotent: bir xil kalit bilan takroriy
    chaqiruv pulni qayta yechmaydi, birinchi natijani qaytaradi.

    mode:
      'ok'       — hammasi muvaffaqiyatli
      'decline'  — charge Declined ko'taradi (hech narsa yechilmaydi)
      'timeout'  — charge pulni YECHADI, lekin keyin Timeout ko'taradi
                   (javob yo'lda yo'qoldi — darsning 4.3-bo'limi)
    """

    def __init__(self, path, mode="ok"):
        self.conn = connect(path)
        # Provayder — alohida tizim. Agar u sizning tranzaksiyangiz ichidan
        # chaqirilsa, bazaning yozish qulfi sizda qoladi va provayder uni
        # kutib, 5 soniyadan keyin "database is locked" bilan yiqiladi (4.2).
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.mode = mode

    def _record(self, key, kind, amount_minor):
        with tx(self.conn):
            row = self.conn.execute(
                "SELECT kind, amount_minor FROM provider_ops WHERE key = ?", (key,)
            ).fetchone()
            if row is not None:
                if row["kind"] != kind or row["amount_minor"] != amount_minor:
                    raise ValueError(f"provayder: kalit {key!r} boshqa parametrlar bilan")
                self.conn.execute("UPDATE provider_ops SET calls = calls + 1 WHERE key = ?", (key,))
                return False
            self.conn.execute(
                "INSERT INTO provider_ops(key, kind, amount_minor) VALUES (?, ?, ?)",
                (key, kind, amount_minor),
            )
            return True

    def charge(self, key, amount_minor):
        """Mehmon kartasidan yechish. Muvaffaqiyatda None qaytaradi."""
        if self.mode == "decline":
            raise Declined(key)
        self._record(key, "charge", amount_minor)
        if self.mode == "timeout":
            raise Timeout(key)

    def refund(self, key, amount_minor):
        """Qaytarish. Idempotent, xuddi charge kabi."""
        self._record(key, "refund", amount_minor)

    # --- tekshiruv uchun ---
    def totals(self):
        rows = self.conn.execute(
            "SELECT kind, COUNT(*) AS n, COALESCE(SUM(amount_minor), 0) AS s "
            "FROM provider_ops GROUP BY kind"
        ).fetchall()
        return {r["kind"]: (r["n"], r["s"]) for r in rows}
