# Amaliyot: imzolangan repo va firehose indeksi

Bluesky darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `repo.py` | **TODO** | Merkle Search Tree: `build_tree`, `prove`, `verify_proof`, `diff` |
| `appview.py` | **TODO** | Firehose indeksi: `on_event`, `on_resync`, `timeline` va yordamchilar (6 ta) |
| `model.py` | Tayyor | Xesh, kalit darajasi, o‘quv imzosi (Schnorr), `Node`/`Entry`, hodisa turlari |
| `sim.py` | Tayyor | Foydalanuvchilar, PDS’lar va “yomon” relay: yo‘qolish, takror, soxta commitlar, kalit almashtirish |
| `check.py` | Tayyor | 19 ta tekshiruv, ~5 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Bluesky’da har foydalanuvchining postlari, like’lari va obunalari — uning
**shaxsiy repo**si. Repo daraxt shaklida saqlanadi va daraxtning ildiz
xeshi — bitta qator — butun repo’ni ifodalaydi. Foydalanuvchi shu ildizni
imzolaydi. Natijada repo istalgan serverda turishi mumkin: kim saqlasa ham,
uni soxtalashtirib bo‘lmaydi. Birinchi qismda shu daraxtni (MST) va
“bu yozuv repo’da bor” degan qisqa **isbot**ni yozasiz.

Ikkinchi qism — **AppView**: butun tarmoqning o‘zgarishlar oqimini
(firehose) o‘qib, “bu postga nechta like”, “mening tasmam” kabi savollarga
javob beradigan xizmat. Oqim yo‘qotadi, takrorlaydi va soxta xabarlar
aralashadi — AppView buni sezishi va tiklanishi kerak.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 19/19 OK`:

1. **Repo** (8 ta): tuzilma qoidalari; determinizm va aniq javob (200 kalitli
   repo’ning ildiz xeshi); 400 ta kalit va 60 ta yo‘q kalit isboti; 8 xil
   soxta isbot rad etiladi; `diff` to‘g‘ri va tejamkor (3 000 kalitda bitta
   o‘zgarish — 60 tugundan kam).
2. **AppView** (9 ta): like va follow “kim” bo‘yicha sanaladi; o‘chirishda
   yozuv eslab qolinadi; tasma tartibi va limiti; soxta imzo; takrorlar;
   bo‘shliq va resinxronizatsiya; hisob o‘chirilishi; kalit almashtirish;
   kech qo‘shilgan AppView; suratdan keyingi bo‘shliq.
3. **Xaos**: 25 ta stsenariy — yakuniy indeks haqiqiy repolar bilan aynan bir xil.
4. **Tezlik**: 100 000 postli, 500 muallifli “Following” tasmasi — 300 so‘rov
   3 soniyadan tez.

## Maslahatlar

- **Daraja — kalitning o‘zidan** (`key_level`): ildizda eng yuqori
  darajadagi kalitlar, ular orasidagi oraliqlar — rekursiv pastki daraxtlar.
  Kalitlarni avval saralang.
- **Isbotni tekshirishda daraxtga qaramang** — faqat `root_hash` va isbot
  baytlari. Har qadamda: xesh mosmi, kalit shu tugundami, yo‘q bo‘lsa —
  qaysi bolaga tushadi va keyingi tugun aynan o‘sha bolami.
- **Diff**: ikkala daraxtni bir vaqtda, kalitlar tartibida aylaning; ikki
  tomonda ham navbatda xeshi bir xil pastki daraxt bo‘lsa — ikkalasini
  ochmasdan o‘tkazib yuboring.
- **Delete’da yozuv kelmaydi**: AppView har repo’ning yozuvlarini o‘zi
  saqlaydi (`self.records`), aks holda o‘chirilgan like qaysi postniki
  ekanini bilolmaydi.
- **“Kim” bo‘yicha sanash**: `Counter(did -> yozuvlar soni)` — soni 0 ga
  tushganda kalitni o‘chiring, hisob esa `len(...)`.
- **Tasma**: har muallif postlari tartiblangan ro‘yxatda; so‘rovda
  `heapq.merge(..., reverse=True)` va `islice` — 100 000 postni saralash shart emas.
- Xaos yiqilsa, xabar seed’ni beradi: `Sim(AppView, seed=N, steps=1200)`
  ni o‘zingiz ishga tushirib, `s.app.records` ni `s.users[did].records` bilan
  solishtiring.
