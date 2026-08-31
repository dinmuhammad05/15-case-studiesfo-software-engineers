# Dars shabloni

Barcha darslar bir xil 8 bosqichdan iborat. Bu tasodifiy emas: o‘quvchi ikkinchi darsdanoq
tuzilmani biladi va faqat mazmunga e’tibor beradi.

## 1. Muammo
Kim, nima uchun, qanday hajmda. `<StatGrid>` bilan 4 ta raqam: foydalanuvchi soni, yozish
yuki, o‘qish yuki, kechikish maqsadi. So‘ng talablar jadvali — har bir talab **o‘lchanadigan**
ko‘rsatkich bilan.

## 2. v0 — eng sodda ishlaydigan yechim
Haqiqiy kod yoki sxema. 30 satrdan oshmasin. Bu yechim **ishlashi** kerak — “yomon” emas,
shunchaki kichik. `<Flow>` bilan diagramma.

## 3. Nima sindi
Har bir muammo alohida sarlavha ostida, **raqam bilan**: “500 token × 42 ms = 21 soniya”.
Taxminiy gap yo‘q — o‘quvchi hisobni o‘zi takrorlay olsin.

## 4. Evolyutsiya qadamlari
Har biri `<Step n gain cost>` ichida. Qoida: **har bir qadamda nima yo‘qotganini ham yozing.**
Faqat yutuqni sanash — eng keng tarqalgan yomon darslik belgisi.

## 5. Bugungi arxitektura
`<Arch>` bilan qatlamli diagramma + yon tizimlar (baza, kesh, kuzatuv) haqida abzas.

## 6. Trade-off‘lar
`<TradeOffs>` jadvali va “qaysi metrikani optimallashtiryapsiz?” degan `<Callout>`.

## 7. Intervyu savollari
8–12 ta `<QA>`. Savol — chinakam intervyuda so‘raladigan darajada; javob — 3–6 gap,
mexanizmni tushuntiradigan, yodlanadigan emas.

## 8. Amaliyot
`<Task>` ichida bajarish mumkin bo‘lgan topshiriq + **tekshiruv mezoni**. Yaxshi topshiriq
darsning asosiy g‘oyasini raqamda ko‘rsatadi (masalan: batch limitini 1 ga tushiring va
throughput farqini o‘lchang).

## Uslub qoidalari
- O‘zbek tilida, texnik atamalar asl holida (KV cache, throughput) + qavsda izoh.
- Raqamlar taxminiy bo‘lsa — ochiq ayting va manbani ko‘rsating.
- Ichki komponentlardan foydalaning; MDX ichida qat‘iy rang yoki inline `style` yozmang.
- Har dars oxirida manbalar ro‘yxati.
