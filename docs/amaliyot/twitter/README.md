# Amaliyot: tasmaning yuragi — Snowflake va gibrid fan-out

Twitter tasmasi darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `snowflake.py` | **TODO** | Vaqt bo‘yicha tartiblanadigan taqsimlangan ID |
| `timeline.py` | **TODO** | Gibrid fan-out: push, pull, k-way merge, filtrlar, kursor |
| `model.py` | Tayyor | Soxta soat, darajali (power-law) obunalar grafi |
| `check.py` | Tayyor | 13 ta tekshiruv, ~12 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

1. **Raqam beruvchi** (`snowflake.py`). Har post o‘z raqamini oladi. Raqamning
   boshida vaqt yozilgan, shuning uchun raqam bo‘yicha saralash vaqt bo‘yicha
   saralashga teng. Mingta server bir-biridan so‘ramasdan raqam beradi: har
   birining o‘z “seriya raqami” bor.
2. **Pochtachi** (`timeline.py`). Oddiy odam xat yozsa, pochtachi uni darhol
   har bir obunachining qutisiga tashlaydi (**push**). Mashhur odamning xati
   esa million qutiga tashlanmaydi: u e’lonlar taxtasiga osiladi va har kim
   qutisini ochganda taxtaga ham qarab oladi (**pull**). Siz qutini ochish
   vaqtida ikkalasini bitta tartiblangan ro‘yxatga qo‘shasiz.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 13/13 OK`:

1. **Snowflake** (4 ta):
   - bitlar joylashuvi va `parse`;
   - millisekundiga 4096 dan ko‘p so‘rovda keyingi millisekundni kutish;
   - soat orqaga ketganda xato berish;
   - uch mashina: takrorsiz va vaqt bo‘yicha tartiblangan.
2. **Tasma, birlik testlari** (3 ta):
   - push va pull, yozuvlar soni;
   - obuna vaqti, o‘chirish, bloklash, qayta obuna;
   - tasma uzunligi va kursor.
3. **Fuzz** (3 ta):
   - “JOIN” bilan ishlaydigan sodda model bilan har o‘qishni solishtirish;
   - barcha sahifalar birlashmasi to‘liq tasmaga teng;
   - k-way merge tezligi.
4. **Narx** (2 ta): darajali grafda sof pull, gibrid va sof push.
5. **Tezlik**.

## Maslahatlar

- **Snowflake to‘lishi**: `seq = (seq + 1) & 4095`. U 0 ga qaytsa —
  `while ts <= self.last: ts = self.clock()`.
- **Kursor**: tartiblangan ro‘yxatda `bisect_left(lst, cursor)` — `cursor` dan
  qat’iy kichiklar shu indeksgacha.
- **k-way merge**: uyumga har ro‘yxatning eng katta (oxirgi) elementini
  `(-pid, ro‘yxat_raqami, indeks)` ko‘rinishida qo‘ying. Birini olganda
  o‘sha ro‘yxatning keyingisini qo‘shing. Limitga yetganda to‘xtang.
- **Filtrdan keyin limit**: avval limit ta olib, keyin filtrlash xato —
  o‘chirilgan va bloklanganlar o‘rnini keyingilar to‘ldirishi kerak.
- **Narx bo‘limidagi saboq**: o‘qish yozishdan ko‘p bo‘lsa, amallar soni
  bo‘yicha sof push eng arzon chiqadi. Gibridning foydasi boshqa joyda:
  u **bitta postning fan-out’ini** (va demak navbat kechikishini)
  chegaralaydi.
