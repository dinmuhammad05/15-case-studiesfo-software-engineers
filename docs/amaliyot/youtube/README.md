# Amaliyot: bitreyt zinapoyasi va ABR

YouTube darsining 1- va 2-daraja topshiriqlari uchun kod.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `ladder.py` | Tayyor | 1-daraja: ffmpeg bilan zinapoya, I-kadrlar tekisligi, HLS |
| `traces.py` | Tayyor | 4 ta deterministik tarmoq izi |
| `sim.py` | Tayyor | ABR simulyatori, QoE hisobi, tekshiruvlar |
| `abr.py` | **TODO** | `throughput_based`, `buffer_based`, `hybrid` |

## 1-daraja: zinapoya

```bash
pip install -r requirements.txt     # imageio-ffmpeg — ffmpeg yo'q bo'lsa
python ladder.py                    # sintetik video
python ladder.py video.mp4          # o'z videongiz (birinchi 20 s)
```

Natija: `out/` da 4 ta MP4, har biri uchun HLS bo‘laklari va `master.m3u8`.
Skript har pog‘onaning haqiqiy bitreytini va I-kadr vaqtlarini chiqaradi.

“Haqiqiy” bitreyt maqsaddan ~60–80 kbit/s yuqori bo‘ladi — unga 64 kbit/s
audio ham kiradi. Buni farqlang: zinapoyadagi raqam odatda **video** bitreyti.

Tajriba: `ladder.py` dagi `-force_key_frames` va `-sc_threshold 0`
qatorlarini olib tashlab qayta ishga tushiring. I-kadrlar tekisligi
buziladi — darsning 2.4-bo‘limidagi Check aynan shu haqida.

## 2-daraja: ABR (asosiy topshiriq)

`abr.py` dagi uchta funksiyani to‘ldiring, keyin:

```bash
python sim.py                   # barcha algoritmlar, barcha izlar
python sim.py --trace metro     # bitta iz
python sim.py --verbose         # birinchi algoritm uchun har bo'lak jurnali
```

Hech qanday tarmoq yoki ffmpeg kerak emas — simulyatsiya bir soniyadan
kam vaqtda tugaydi.

### Izlar

| Iz | Tavsif |
| --- | --- |
| `4g_barqaror` | ~8 Mbit/s, kichik shovqin |
| `3g_tebranuvchi` | ~2 Mbit/s, katta “yopishqoq” o‘zgarishlar |
| `metro` | ~6 Mbit/s, har ~2 daqiqada 20–40 s ga ~0.2 Mbit/s |
| `sekin_boshlanish` | 30 s ~0.8 Mbit/s, keyin ~10 Mbit/s |

### Tekshiruv mezoni

1. Har bir algoritm har bir izda `eng_yuqori` dan ko‘p buferlamasin va
   `eng_past` dan yuqori bitreyt bersin.
2. `3g_tebranuvchi` va `metro` da `hybrid` ning sifat almashishlari
   `buffer` nikidan **kam** bo‘lsin — gisterezis ishlayotganining belgisi.
3. `hybrid` ning QoE si kamida 3 ta izda uchala algoritm ichida eng yaxshi
   bo‘lsin (0.05 tolerans bilan).

Uchinchi mezon oson emas: faqat `throughput_based` yoki faqat
`buffer_based` ni qaytarish o‘tmaydi. Oddiy chiziqli bufer xaritasi
tebranuvchi tarmoqda juda ko‘p almashadi (darsning 6.3-bo‘limi) — sizga
gisterezis kerak bo‘ladi.

### Hisobotni o‘qish

- **boshlanish** — birinchi bo‘lak kelguncha vaqt
- **buferlash** — sessiya vaqtining to‘xtashda o‘tgan ulushi
- **bitreyt** — tanlangan pog‘onalarning o‘rtachasi, Mbit/s
- **almashish** — pog‘ona necha marta o‘zgargan
- **QoE** — bo‘lak boshiga: bitreyt − almashish jarimasi − 4.3 × (buferlash + boshlanish)

`eng_yuqori` 3G izida ~52% vaqtni to‘xtashda o‘tkazadi va QoE si manfiy —
bu 4.1-bo‘limdagi “bitta fayl hammaga noto‘g‘ri” hisobining simulyatsiyadagi
ko‘rinishi.
