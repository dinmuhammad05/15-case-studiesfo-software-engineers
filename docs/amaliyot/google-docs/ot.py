"""Operatsion transformatsiya (OT) — matn uchun (TODO).

Operatsiya — komponentlar ro'yxati, hujjatni chapdan o'ngga "yuradi":

    musbat int  n  -> retain: n ta belgini o'zgarishsiz o'tkazish
    str         s  -> insert: s matnni shu joyga qo'shish
    manfiy int -n  -> delete: keyingi n ta belgini o'chirish

Misol: "salom dunyo" -> "salom, dunyo"
    [5, ",", 6]
Misol: "abc" dan "b" ni o'chirish
    [1, -1, 1]

Qoida: retain va delete uzunliklari yig'indisi = hujjat uzunligi
(`base_len`). Natija uzunligi — `target_len`.

Darsdagi bo'limlar: 2.1 (yozuv), 5-bo'lim 3-5-qadamlar (transform,
holat mashinasi, compose), 6.1 (ikki ko'rsatkich bilan yurish).

Faqat pastdagi TODO funksiyalarni yozing. Yordamchilar tayyor.
"""


# ---------------- tayyor yordamchilar ----------------

def is_retain(c):
    return isinstance(c, int) and c > 0


def is_insert(c):
    return isinstance(c, str)


def is_delete(c):
    return isinstance(c, int) and c < 0


def base_len(op):
    """Operatsiya qo'llanadigan hujjat uzunligi."""
    return sum(abs(c) for c in op if isinstance(c, int))


def target_len(op):
    """Operatsiyadan keyingi hujjat uzunligi."""
    return sum(c if isinstance(c, int) and c > 0 else len(c) if isinstance(c, str) else 0
               for c in op)


def normalize(op):
    """Qo'shni bir xil turdagi komponentlarni birlashtiradi, bo'shlarini olib
    tashlaydi. Kanonik shakl: insert har doim delete'dan OLDIN turadi
    (ikkalasi bir joyda bo'lsa) — shunda teng operatsiyalar bir xil ko'rinadi.
    """
    out = []
    for c in op:
        if c == 0 or c == "":
            continue
        if out:
            last = out[-1]
            if is_retain(c) and is_retain(last):
                out[-1] = last + c
                continue
            if is_delete(c) and is_delete(last):
                out[-1] = last + c
                continue
            if is_insert(c) and is_insert(last):
                out[-1] = last + c
                continue
            if is_insert(c) and is_delete(last):
                # "o'chir, keyin qo'sh" == "qo'sh, keyin o'chir" — kanonik: insert oldin
                if len(out) >= 2 and is_insert(out[-2]):
                    out[-2] = out[-2] + c
                else:
                    out.insert(len(out) - 1, c)
                continue
        out.append(c)
    return out


# ---------------- TODO ----------------

def apply(doc, op):
    """Operatsiyani matnga qo'llash.

    base_len(op) != len(doc) bo'lsa — ValueError (server buni validatsiya
    sifatida ishlatadi, 6.2).
    """
    # TODO
    raise NotImplementedError


def transform(a, b):
    """(a', b') — a va b BIR XIL hujjatga nisbatan parallel operatsiyalar.

    Kafolat (TP1):  apply(apply(d, a), b') == apply(apply(d, b), a')

    Bog'lash qoidasi: ikkalasi BIR JOYGA qo'shsa, a ning qo'shimchasi
    oldinga tushadi. Simulyatorda `a` doim serverda allaqachon tartiblangan
    operatsiya (darsdagi 6-bo'lim Check: "server tartibi yutadi").
    Natijalar `normalize` qilingan bo'lsin.
    """
    # TODO
    raise NotImplementedError


def compose(a, b):
    """Bitta operatsiya: "avval a, keyin b" ga teng.

    Shart: target_len(a) == base_len(b), aks holda ValueError.
    Kafolat: apply(apply(d, a), b) == apply(d, compose(a, b))
    Natija `normalize` qilingan bo'lsin.
    """
    # TODO
    raise NotImplementedError


def transform_cursor(pos, op):
    """Kursor pozitsiyasi `op` qo'llangandan keyin qayerga siljiydi.

    - kursordan oldingi qo'shish -> kursor o'ngga suriladi
    - aynan kursor joyidagi qo'shish -> kursor qo'shilgan matndan KEYIN
    - kursordan oldingi o'chirish -> kursor chapga suriladi
    - kursorni o'z ichiga olgan o'chirish -> kursor o'chirish boshiga
    """
    # TODO
    raise NotImplementedError
