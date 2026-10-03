"""Repo: soddalashtirilgan Merkle Search Tree (MST) — 2-daraja topshirig'ining 1-qismi.
To'rtta funksiya TODO.

Darsdan: 5-bo'lim 3-4-qadamlar, 7-bo'lim. Foydalanuvchining hamma yozuvlari
(postlar, like'lar, follow'lar) — kalit -> qiymat: "kolleksiya/rkey" -> yozuv xeshi.
Ular daraxtga joylanadi, va daraxtning ildiz xeshi bitta son bilan BUTUN
repo'ni ifodalaydi. Commit shu ildizni imzolaydi.

Daraxt qoidalari (model.key_level, Node, Entry, tree_hash tayyor):
  * Har kalitning darajasi — key_level(kalit). Bitta tugundagi kalitlar bir
    xil darajada va tartiblangan.
  * Kalitlar to'plamining ildizi — to'plamdagi ENG YUQORI darajadagi kalitlar.
    Ular orasidagi (va birinchisidan oldingi) kalitlar — pastki daraxtlar,
    ular ham shu qoida bilan quriladi (o'z eng yuqori darajasi bilan).
    Bo'sh oraliq — None (bo'sh ichki tugun yo'q).
  * Bo'sh repo — Node() (kalitsiz bitta tugun).
Natija: bir xil kalitlar va qiymatlar — har doim bir xil daraxt va bir xil
ildiz xeshi, kiritish tartibidan qat'i nazar.

Tekshiruv: python check.py
"""
from model import (Entry, Node, decode_node, key_level, node_bytes, sha,  # noqa: F401
                   tree_hash)


def build_tree(items: dict) -> Node:
    """{kalit: qiymat} dan MST quradi va ildiz tugunini qaytaradi."""
    raise NotImplementedError("TODO: build_tree")


def prove(root: Node, key: str) -> list:
    """Kalit uchun isbot: ildizdan boshlab yo'ldagi tugunlarning node_bytes()
    ro'yxati — kalit topilgan tugungacha, yoki (kalit yo'q bo'lsa) qidiruv
    None bolaga yetgan tugungacha.

    Tugunda kalit yo'q bo'lsa, qaysi bolaga tushiladi: kalitdan kichik
    oxirgi yozuvning right'i, bunday yozuv bo'lmasa — left."""
    raise NotImplementedError("TODO: prove")


def verify_proof(root_hash: str, key: str, value, proof: list) -> bool:
    """Isbotni FAQAT root_hash ga tayanib tekshiradi (daraxtga qaramasdan).

    value=None — "kalit yo'q" degan da'vo. True faqat agar:
      * proof[0] ning xeshi root_hash; har keyingi tugun xeshi — oldingi
        tugundagi tegishli bola xeshi (decode_node bilan o'qing);
      * oxirgi tugunda kalit bor va qiymati value ga teng, yoki kalit yo'q,
        tegishli bola None va value is None;
      * isbotda ortiqcha tugun yo'q.
    Har qanday buzilgan, kesilgan yoki boshqa daraxtdagi isbot — False."""
    raise NotImplementedError("TODO: verify_proof")


def diff(a: Node, b: Node):
    """Ikki repo farqi: ({kalit: (eski, yangi)}, ochilgan_tugunlar_soni).
    Yo'q tomon — None. Masalan qo'shilgan kalit: (None, yangi).

    Tejamkorlik sharti: xeshi bir xil pastki daraxtlarga KIRMANG — ular aynan
    bir xil. 3 000 kalitli repoda bitta o'zgarish uchun 60 dan ko'p tugun
    ochilmasin; bir xil daraxtlarda — 0. "Ochildi" — tugun ichidagi yozuvlar
    va bolalarga qaraldi. Maslahat: ikkala daraxtni bir vaqtda, kalitlar
    tartibida aylanib chiqing (stek bilan), har qadamda ikki tomonning
    navbatdagi elementini solishtiring."""
    raise NotImplementedError("TODO: diff")
