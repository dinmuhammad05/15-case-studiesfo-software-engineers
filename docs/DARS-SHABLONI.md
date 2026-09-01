# Dars shabloni

Barcha darslar bir xil yo‘ldan boradi. Bu tasodifiy emas: o‘quvchi ikkinchi darsdanoq
tuzilmani biladi va faqat mazmunga e’tibor beradi. Namuna — `app/darslar/chatgpt/page.mdx`.

## Majburiy o‘q (skelet)

**0. Bu darsda nima o‘rganasiz** — 3–4 abzas: nima qamrab olinadi, kimlar uchun.

**1. Muammo** — kim, nima uchun, qanday hajmda. `<StatGrid>` bilan 4 ta raqam, so‘ng talablar
jadvali. Har bir talab **o‘lchanadigan** ko‘rsatkich bilan.

**2. Nol nuqta — mexanizm** — tizimning eng ichki ishlash prinsipi, servisdan oldin.
Bu bo‘limsiz dars “diagramma ko‘rsatib, tushuntirmaslik”ka aylanadi. Misollar:
ChatGPT uchun — token, attention, sampling; Kafka uchun — append-only log va offset;
S3 uchun — obyekt, kalit, erasure coding; Uber uchun — yo‘l grafi va geoindeks.

**3. v0 — eng sodda ishlaydigan yechim** — haqiqiy kod yoki sxema, 30 satrdan oshmasin.
Bu yechim **ishlashi** kerak: “yomon” emas, shunchaki kichik.

**4. Nima sindi** — har bir muammo alohida sarlavha ostida, **raqam bilan**:
“500 token × 42 ms = 21 soniya”. Taxminiy gap yo‘q — o‘quvchi hisobni takrorlay olsin.

**5. Evolyutsiya qadamlari** — har biri `<Step n gain cost>` ichida. Qoida: **har bir qadamda
nima yo‘qotganini ham yozing.** Faqat yutuqni sanash — yomon darslik belgisi.

**6. Mahsulot / atrof qatlami** — asosiy mexanizm atrofidagi hamma narsa: holat, kesh,
integratsiyalar, tashqi tizimlar.

**7. Bugungi arxitektura** — `<Arch>` bilan qatlamli diagramma + yon tizimlar haqida abzas.

**7.5 Antinaqshlar** — shu domenda eng ko‘p uchraydigan xatolar, `<TradeOffs>` jadvalida:
xato qaror, uning ko‘rinishdagi foydasi va haqiqiy narxi.

**8. Ishonchlilik** — nosozlik stsenariylari: retry storm, hot spot, uzilish, graceful
degradation, versiya chiqarish. Bu bo‘lim ishlab chiqarish tajribasini ko‘rsatadi.

**9. Iqtisod** — bitta operatsiya qancha turadi. Aniq hisob-kitob (faraz → arifmetika →
xulosa) va undan kelib chiqadigan mahsulot qarorlari.

**10. Sifat nazorati va kuzatuv** — qanday metrikalar, qanday testlar, nima buzilganini
qanday bilamiz.

**11. Xavfsizlik** — shu tizimga xos hujum yuzasi.

**12. Trade-off‘lar** — `<TradeOffs>` jadvali va “qaysi metrikani optimallashtiryapsiz?”
degan `<Callout>`.

**13. Intervyu savollari** — 12–16 ta `<QA>`. Savol chinakam intervyu darajasida; javob
3–6 gap, mexanizmni tushuntiradigan, yodlanadigan emas.

**14. Amaliyot** — 3–4 daraja (`<Task>`): oson, asosiy, murakkab, sig‘im modeli. Har birida
**tekshiruv mezoni**: “ishladi” emas, o‘lchangan natija — grafik, foiz, taqqoslash.

**15. Lug‘at** — 15–20 ta atama jadvali.

**16. Manbalar** — asosiy maqolalar va hujjatlar.

## Hajm va chuqurlik mezoni

Namuna dars (ChatGPT) ko‘rsatkichlari — quyi chegara emas, **me’yor**:

| Ko‘rsatkich | Maqsad |
| --- | --- |
| So‘z | 10 000+ |
| `##` bo‘limlar | 18+ |
| `<Calc>` hisob bloklari | 15+ |
| Jadvallar | 15+ |
| Kod bloklari | 20+ |
| `<QA>` intervyu savollari | 20+ |
| `<Deep>` chuqur bloklari | 8+ |
| `<Check>` nazorat savollari | 6+ |
| `<Task>` amaliyot darajalari | 3–4 |

**Eng muhim mezon — hisob-kitob.** Har bir muhandislik qarori raqamdan kelib chiqishi kerak:
“batching kerak” emas, balki “arifmetik intensivlik 1, ridge point 295, demak GPU ning
0.3% i ishlatilyapti”. O‘quvchi har bir `<Calc>` blokini kalkulyatorda takrorlay olsin.

Uch qatlamli tuzilma:
1. **Asosiy matn** — hamma uchun, hisob natijalari bilan
2. **`<Deep>`** — matematika va past daraja; birinchi o‘qishda tashlansa mantiq uzilmaydi
3. **`<Check>`** — bo‘lim oxirida o‘z-o‘zini tekshirish

## Uslub qoidalari

- O‘zbek tilida, texnik atamalar asl holida (KV cache, throughput) + qavsda izoh
- Raqamlar taxminiy bo‘lsa — ochiq ayting va manbani ko‘rsating
- Ichki komponentlardan foydalaning; MDX ichida qat‘iy rang yoki inline `style` yozmang
- MDX‘da matn ichida `{` va `<` belgilarini ishlatmang (JSX deb o‘qiladi) — kod bloklarida bemalol
- `##` sarlavhalarga id avtomatik qo‘yiladi (rehype-slug) va mundarija o‘zi yig‘iladi
