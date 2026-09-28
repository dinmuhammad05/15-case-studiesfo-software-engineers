# Amaliyot: matching engine va bozor ma’lumotlari oqimi

Fond birjasi darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `book.py` | **TODO** | Buyurtmalar kitobi: `submit`, `cancel`, `modify`, `depth`, `best_bid`/`best_ask` va boshqalar (9 ta usul) |
| `feed.py` | **TODO** | L2 oqimi mijozi: `on_update`, `on_snapshot` |
| `model.py` | Tayyor | `Order`, hodisalar (`Accepted`, `Trade`, `Cancelled`, ...), `Update`, `Snapshot` |
| `exchange.py` | Tayyor | Sekvenser: buyruqlarga tartib raqami, jurnal, L2 oqimi, jurnalni qayta o‘ynash |
| `check.py` | Tayyor | 21 ta tekshiruv, ~6 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Birjaning yuragi — **buyurtmalar kitobi**: “100.50 dan 300 ta sotaman”,
“100.40 dan 200 ta olaman” degan buyurtmalar ro‘yxati. Yangi buyurtma
kelganda uni kitobdagi mos buyurtmalar bilan juftlash kerak — adolatli
(eng yaxshi narx birinchi, bir narxda — kim oldin kelgan), aniq (bir tiyin
ham adashmaydi) va tez. Siz shu kitobni yozasiz.

Ikkinchi qism — kitobning **nusxasi**. Birja har o‘zgarishni tarmoqqa
e’lon qiladi, minglab mijozlar shu xabarlardan o‘z nusxasini quradi.
Xabarlar yo‘qolishi, takrorlanishi va aralashishi mumkin — mijoz buni
sezishi va tiklanishi kerak.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 21/21 OK`:

1. **Kitob** (12 ta birlik testi): narx-vaqt ustuvorligi, bitim narxi,
   qisman bajarilish, market, IOC, FOK, post-only, o‘z-o‘zi bilan savdoni
   oldini olish (STP), bekor qilish, o‘zgartirish (qachon navbat saqlanadi,
   qachon yo‘qoladi), tekshiruvlar (float narx yo‘q!), chuqurlik.
2. **Fuzz**: 40 ta tasodifiy ketma-ketlik — har buyruqdan keyin sizning
   kitobingiz sodda, sekin, lekin aniq model bilan aynan bir xil hodisalar
   va bir xil holatni beradi. Kitob hech qachon “kesishgan” qolmaydi.
3. **Determinizm**: jurnalni qayta o‘ynash aynan o‘sha natijani beradi —
   zaxira server shunday ishlaydi.
4. **L2 mijozi**: bo‘shliqda surat so‘rash, kutish paytida buferlash,
   suratdan eski xabarlarni tashlash, takrorlarni e’tiborsiz qoldirish;
   30 ta “yomon tarmoq” stsenariysi.
5. **Tezlik**: 20 000 buyurtmali kitobda 200 000 buyruq 6 soniyadan tez.
   Har buyruqda butun kitobni saralaydigan yechim bu yerda to‘xtaydi.

## Maslahatlar

- **Narx — butun son** (tick’larda). `100.5` narx `"tick"` bilan rad etiladi:
  pul bilan ishlashda float ishlatilmaydi.
- **Har narx darajasi — `OrderedDict`**: navbat tartibi saqlanadi, birinchisini
  olish ham, o‘rtasidan o‘chirish ham O(1). Oddiy `dict` da ko‘p o‘chirishdan
  keyin `next(iter(d))` sekinlashadi.
- **Narxlar — saralangan ro‘yxat** (`bisect.insort`): eng yaxshi xarid —
  oxirgisi, eng yaxshi sotuv — birinchisi. Daraja bo‘shaganda uni ro‘yxatdan
  o‘chirishni unutmang.
- **FOK avval sanaydi, keyin bajaradi**: yetmasa, kitobga umuman tegmang.
- **STP**: navbatda o‘z buyurtmangizga yetganda to‘xtang — undan keyingi
  buyurtmalar bilan ham savdo qilmang.
- **L2 da qiymat absolyut**: eski xabarni yangi holat ustiga qo‘llash —
  eng xavfli xato; takrorni qo‘llash esa zararsiz, lekin baribir tashlang.
- Fuzz yiqilsa, xabar seed va qadam raqamini beradi: `check.rand_cmd` bilan
  shu ketma-ketlikni o‘zingiz takrorlab, `book.state()` ni solishtiring.
