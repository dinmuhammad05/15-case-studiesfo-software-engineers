"""GF(256) arifmetikasi — chekli maydon, har element bitta bayt (tayyor).

Oddiy tilda: 0..255 sonlar ustida "qo'shish" va "ko'paytirish" shunday
aniqlanganki, natija har doim bitta baytga sig'adi va 0 dan boshqa har
qanday songa bo'lish mumkin. Reed-Solomon kodi shu arifmetikada ishlaydi.

  qo'shish = ayirish = XOR          add(a, b) == a ^ b
  ko'paytirish — jadvallar orqali   mul(a, b)
  bo'lish, teskari                  div(a, b), inv(a)

Tezlik uchun ikkita "blok" amali bor — ular butun bayt ketma-ketligi
ustida C tezligida ishlaydi (Python sikli emas):

  scale(block, c)   -> har baytni c ga ko'paytirilgan yangi bytes
  xor(a, b)         -> ikki teng uzunlikdagi bytes'ning XOR i

Va kichik matritsalar uchun:
  mat_inv(M)        -> teskari matritsa (GF(256) da), yoki ValueError
"""

_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D  # x^8 + x^4 + x^3 + x^2 + 1
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def add(a, b):
    return a ^ b


def mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def inv(a):
    if a == 0:
        raise ZeroDivisionError("GF(256): 0 ning teskarisi yo'q")
    return _EXP[255 - _LOG[a]]


def div(a, b):
    return mul(a, inv(b))


# scale(): har c uchun 256 baytlik jadval — bytes.translate bilan bir zumda
_TABLES = [bytes(mul(c, x) for x in range(256)) for c in range(256)]


def scale(block, c):
    """bytes ning har baytini c ga ko'paytiradi (GF(256) da)."""
    return bytes(block).translate(_TABLES[c])


def xor(a, b):
    """Ikki teng uzunlikdagi bytes ning XOR i."""
    if len(a) != len(b):
        raise ValueError("uzunliklar teng emas")
    n = len(a)
    return (int.from_bytes(a, "little") ^ int.from_bytes(b, "little")).to_bytes(n, "little")


def mat_inv(M):
    """k x k matritsaning teskarisi (Gauss-Jordan, GF(256)). Singulyar bo'lsa — ValueError."""
    k = len(M)
    A = [list(row) + [1 if i == j else 0 for j in range(k)] for i, row in enumerate(M)]
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] != 0), None)
        if piv is None:
            raise ValueError("matritsa teskarilanmaydi")
        A[col], A[piv] = A[piv], A[col]
        f = inv(A[col][col])
        A[col] = [mul(f, v) for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                g = A[r][col]
                A[r] = [a ^ mul(g, b) for a, b in zip(A[r], A[col])]
    return [row[k:] for row in A]
