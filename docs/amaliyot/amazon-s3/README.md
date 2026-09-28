# Amaliyot: erasure coding bilan ob’ekt ombori

Amazon S3 darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `store.py` | **TODO** | `generator`, `encode`, `decode` (Reed–Solomon) va `Store`: `_place`, `put`, `get`, `scrub` |
| `gf.py` | Tayyor | GF(256) arifmetikasi: `mul`, `inv`, `scale(blok, c)`, `xor(a, b)`, `mat_inv(M)` |
| `cluster.py` | Tayyor | Soxta disklar: 3 AZ × 6 disk; `kill()` — disk o‘ladi, `corrupt()` — jim buzilish |
| `check.py` | Tayyor | 20 ta tekshiruv, ~1 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Har bir fayl (ob’ekt) 6 ta ma’lumot bo‘lagiga bo‘linadi va ulardan 3 ta
qo‘shimcha “tiklash” bo‘lagi hisoblanadi — jami 9 ta. 9 bo‘lak 9 xil diskka,
uchta AZ ga teng yoziladi. **Istalgan 6 tasi** faylni to‘liq tiklash uchun
yetadi. Har bo‘lak yonida uning nazorat summasi (`crc32`) saqlanadi — disk
jim buzilgan baytni qaytarsa, summa mos kelmaydi va bo‘lak “yo‘q” deb
hisoblanadi. `scrub()` — fon tekshiruvi: buzilgan bo‘laklarni topib, qayta
hisoblab, yangi disklarga yozadi.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 20/20 OK`:

1. **Reed–Solomon** (darsning 5-bo‘lim 7-qadami). Generator tizimli
   (birinchi `k` qator — birlik matritsa) va istalgan `k` ta qatori
   teskarilanadi — (4,2) va (8,4) uchun barcha kombinatsiyalar. `decode`
   0 baytdan 12 KB gacha bo‘lgan ma’lumotni **har qanday** `k` ta bo‘lakdan
   aniq tiklaydi; `k` tadan kam bo‘lsa — `LostError`. 1 MB kodlash va
   tiklash 3 soniyadan tez.
2. **Ob’ekt ombori** (2, 4, 5-qadamlar). 9 bo‘lak 9 xil diskda, har AZ da
   ko‘pi bilan 3 ta; disklar bir tekis to‘ladi; istalgan 3 disk yoki butun
   AZ o‘lsa — hammasi o‘qiladi; 2 bo‘lak jim buzilgan va 1 disk o‘lgan
   bo‘lsa ham — to‘g‘ri baytlar. Sog‘ bo‘laklar yetmasa — **xato**, hech
   qachon noto‘g‘ri baytlar emas.
3. **Scrub** (6-qadam). Ikki disk o‘lgan va 30 ta bo‘lak jim buzilgan
   klasterda har ob’ekt yana 9 ta sog‘ bo‘lakka ega bo‘ladi, qoidalarga mos;
   ikkinchi scrub hech narsa topmaydi; keyin yana 3 disk o‘lsa ham hammasi
   o‘qiladi. Butun AZ o‘lganda — qolgan 2 AZ ga qayta tarqatadi.

## Maslahatlar

- **Tezlik.** Baytma-bayt Python sikli 1 MB uchun juda sekin. `gf.scale(blok, c)`
  butun blokni bir zumda `c` ga ko‘paytiradi, `gf.xor(a, b)` — ikki blokni
  qo‘shadi. Paritet bo‘lagi: `acc = bytes(L)`, keyin har `j` uchun
  `acc = gf.xor(acc, gf.scale(d[j], C[i][j]))`.
- **Tiklash.** Qolgan bo‘laklardan istalgan `k` tasini oling; generator’dan
  **o‘sha** qatorlarni oling; `gf.mat_inv` bilan teskarilang; `r`-ma’lumot
  bo‘lagi = `XOR_c scale(bo‘lak_c, inv[r][c])`.
- **To‘ldirish.** `L = ceil(len / k)`; oxirgi bo‘lakni nol bilan to‘ldiring,
  tiklashda `size` gacha kesing. Bo‘sh fayl ham ishlashi kerak.
- **Nazorat summasi `get` da ham, `scrub` da ham.** Faqat o‘lik disklarni
  tekshiradigan scrub jim buzilishni hech qachon topmaydi.
- **Scrub joylashtirishi.** Yangi bo‘lak shu ob’ektning boshqa bo‘laklari
  turgan diskka tushmasin va AZ chegarasini buzmasin — aks holda keyingi
  nosozlikda bir disk ikki bo‘lakni olib ketadi.
