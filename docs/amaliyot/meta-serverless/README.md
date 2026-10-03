# Amaliyot: serverless funksiyalar platformasining yuragi

Meta Serverless (XFaaS) darsining 2-daraja topshirig‘i uchun kod. Faqat
Python 3.9+ standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `scheduler.py` | **TODO** | Rejalashtiruvchi: kritiklik, muddat (EDF), kvota (token bucket), downstream chegaralari |
| `concurrency.py` | **TODO** | AIMD: downstream xizmatni ortiqcha yuklamaslik |
| `router.py` | **TODO** | Lokallik guruhlari (rendezvous xeshlash) va “to‘kilish” |
| `model.py` | Tayyor | `Call`, `Fn`, kritiklik darajalari, `stable_hash` |
| `check.py` | Tayyor | 17 ta tekshiruv, ~5 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Minglab jamoa o‘z kodini “funksiya” sifatida beradi, platforma esa uni
kerakli paytda ishga tushiradi. Funksiya chaqiruvlari navbatda kutadi.
Ularning bir qismi shoshilinch (soniyalar ichida bajarilishi kerak), ko‘pi
esa kutishi mumkin (24 soat ichida bo‘lsa bo‘ldi). Sizning vazifangiz —
platformaning uchta qarorini yozish:

1. **Har daqiqada nimani bajarish** (`scheduler.py`): avval muhimlari va
   muddati yaqinlari, har jamoa o‘z kvotasidan oshmasin, va bir xizmatga
   (masalan, ma’lumotlar bazasiga) ruxsat etilganidan ko‘p so‘rov ketmasin.
2. **Bazani qancha so‘rov bilan “bosish” mumkin** (`concurrency.py`): baza
   o‘z sig‘imini aytmaydi — faqat “og‘ir” deydi. Internetdagi TCP kabi:
   asta oshir, signal bo‘lsa — keskin kamaytir.
3. **Qaysi serverda bajarish** (`router.py`): har server hamma funksiyani
   “issiq” ushlay olmaydi. Har funksiyani kichik, barqaror serverlar
   guruhiga bog‘lash — sovuq startlar kam.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 17/17 OK`:

1. **Rejalashtiruvchi** (6 ta): takror chaqiruv, tartib, muddati o‘tganlar,
   aniq token bucket ketma-ketligi, downstream chegarasi, bo‘sh turmaslik.
2. **Fuzz va muddatlar** (3 ta): 40 ta tasodifiy yuklamada sodda model bilan
   aynan bir xil tanlov; bajarish mumkin bo‘lgan yuklamada birorta ham muddat
   buzilmaydi; ortiqcha yuklamada yuqori kritiklik himoyalangan.
3. **AIMD** (3 ta): yaqinlashish, keskin pasayishga javob, kam talabda o‘smaslik.
4. **Router** (3 ta): guruh barqarorligi, sovuq startlar tasodifiy taqsimotdan
   kamida 2 barobar kam, to‘kilish qoidasi.
5. **Bir kun**: kiruvchi cho‘qqi sig‘imdan 1.5 barobar ko‘p, downstream bir
   soat ishdan chiqadi — shoshilinchlar o‘z vaqtida, kechiktiriladiganlar
   24 soat ichida, o‘rtacha bandlik yuqori.
6. **Tezlik**: 300 000 chaqiruv — 6 soniyadan tez.

## Maslahatlar

- **Kalit — `(-crit, deadline, submit, cid)`**. Tartib to‘liq aniq bo‘lishi
  shart: fuzz test sodda model bilan har tikda aynan bir xil ro‘yxat kutadi.
- **Token bucket**: avval to‘ldiring (`min(burst, tokens + rate)`), keyin
  tanlang. Boshlang‘ich qiymat — `burst`.
- **Blok qilingan funksiya boshqalarni to‘smasin**: kvotasi yoki downstream
  o‘rni tugagan funksiyani shu tik uchun chetga qo‘ying, qolganlar bilan
  davom eting.
- **Har funksiyaga alohida heap** + “boshlar” heap’i: har tikda faqat
  tanlanganlar va ularning qo‘shnilari bilan ishlaysiz.
- **AIMD faqat to‘liq ishlatilganda o‘sadi**: aks holda kechasi bo‘sh o‘sgan
  chegara ertalabki birinchi to‘lqinda bazani bosib ketadi.
- **Rendezvous xeshlash**: `stable_hash(fn, ishchi)` — Python’ning `hash()`
  dan foydalanmang, u har jarayonda boshqacha.
