# Mock testlar öyini — davom ettiriş uçun xulosa

## Arxitektura

- `index.html` — bitta statik sahifa (HTML + CSS + JS içida, build kerak emas). Şriftlar Google Fonts dan.
- `q/` — 24-mock, `q15/` — 15-mock, `q14/` — Mock 14 topşiriqlari (`q01.png` … `q32.png`, `q33.png` = 33–35 bloki, `q36.png` … `q45.png`).
- `tools/crop_questions.py` — PDF dan topşiriqlarni rasm qilib qirqadigan skript.
- `sources/` — asl PDF lar va kalit rasmlari. **Git ga kiritilmagan** (`.gitignore`): GitHub Pages da hammaga oçiq bölib qolmasin. Ular foydalanuvçi yuborgan zip da.
- Repo içida joyi: `bilimtest.github.io/mock-oyini/` → sayt manzili `/mock-oyini/`.

Ishga tuşiriş (rasmlar nisbiy yöl bilan yuklanadi, şuning uçun server kerak):

```
cd mock-oyini && python3 -m http.server 8000
```

### Ma'lumot tuzilmasi (`index.html` içida)

- `TESTS = { m24, m15, m14, u<id>… }`, har birida `name`, `meta`, `qs`, `count` (topşiriqlar soni, 33–35 = 3 ta), va:
  - qurilgan testlarda `dir` (rasm papkasi);
  - foydalanuvçi qöşganlarida `user: true`, `id`, `imgs` (`{q01: objectURL, …}`). `imgOf()` ikkalasini ham biladi.
- Savol turlari:
  - `mc` — yopiq test: `{n: 5, a: "D", ex: "yeçiş matni"}`
  - `match` — 33–35: `{n: "33–35", img: "q33", type: "match", parts: ["E","A","C"]}`
  - `open` — oçiq: `{n: 36, type: "open", parts: [O("a", [12], "12"), O("b", [3], "3")]}`; `vals` — qabul qilinadigan son qiymatlar, `show` — ekranda körinadigan javob.
- `ex` bölmasa, "faqat rasmiy kalit" (yoki foydalanuvçi mockida "faqat siz kiritgan kalit") degan izoh çiqadi.
- `evalExpr()` — oçiq javoblar uçun xavfsiz ifoda hisoblagiç: `2√3-2`, `27/2`, `13,5`, `-arctg5`, `3π/4`, `9/√58`, `(3-√3)/3`, `30°`, `x=5`, `2:7`. Tolerans: 0,2% (nisbiy).
- Ball: yopiq 10, moslaştiriş 3×4, oçiq 2×6; 3 tadan ortiq ketma-ket töğri javobga +2 bonus.
- `localStorage` (`store.get/set/del`, hammasi try/catch): `mz` (rasm masştabi), `best_<test>` (eng yaxşi foiz).

### Foydalanuvçi qöşgan mocklar (IndexedDB)

- Baza `mock-oyini`, versiya 1, store `mocks` (`keyPath: "id"`). Hamma murojaat `IDB.open/run/all/put/del` orqali, Promise + try/catch.
- Yozuv:
  ```
  { id: Date.now(), name, meta, created: ISO,
    key: { mc: "BBCC…" (32 harf), match: ["D","B","E"], open: { "36": ["1","0"], … } },
    imgs: { q01: Blob(png), …, q33: Blob, q36: Blob, … } }
  ```
- Oçiq javoblar matn sifatida saqlanadi, yuklanganda `openPart()` → `evalExpr()`. Matnda `°` bölsa radian qiymati ham qöşiladi.
- Öyinga faqat rasmi topilgan topşiriqlar kiradi (`userTest()`).
- Öçirişda object URL lar `revokeObjectURL` qilinadi va `best_u<id>` öçiriladi.

### Brauzerda PDF qirqiş (`cropPdf()`)

- pdf.js `3.11.174` cdnjs dan **faqat "Yangi mock qöşiş" da PDF tanlanganda** yuklanadi (`loadPdfJs()`), worker ham cdnjs dan.
- Algoritm `tools/crop_questions.py` bilan bir xil (140 DPI, `SC = 140/72`):
  1. `getTextContent()` → söz koordinatalari (px). Sarlavha (`< 5,9%` balandlik) va pastki kolontitul (`> 90,3%`) çiqarib taşlanadi.
  2. Raqamlar: `"N."` (yoki `"N"` + `"."`) sahifa matni boşlanişidan 20pt içida, tartib bilan (`expected`). Sozlaş (`--num-xmax`) kerak emas — 24, 15, 14 mocklarida 43/43 topdi.
  3. Çegara: oldingi topşiriq matni tugagan joy bilan keyingi raqam orasidagi eng uzun siyohsiz qatorlar oraliğining örtasi (`cutBetween`). Siyoh = R, G, B < 150 (rangli suv belgisi hisoblanmaydi).
  4. 33: sahifadagi birinçi raqam bölsa butun sahifa (sarlavhasi bilan) bitta rasm; 34, 35 alohida rasm emas. 36 şu sahifada bölsa, 33 bloki undan oldin tugaydi.
  5. "Diqqat" qatorlari kesib taşlanadi. Rasm siyoh böyiça qirqiladi (+10px).
- JS va Python natijalari Mock 14 da bir xil (±6px).

## Bajarilgan işlar

1. 24-mock: 45 topşiriq, rasmiy kalit, har biriga yeçiş.
2. 15-mock: 45 topşiriq, kalit `15-MOCK_kalitlar.pdf` dan. Yeçişlar yöq.
3. Rejimlar: hammasi, yopiq (1–35), oçiq (36–45), tasodifiy 10 ta; xatolarni qayta işlaş; natija ekrani.
4. **Mock 14** (2026-11-23): `q14/` qirqildi, `TESTS.m14` (kalit rasmdan qayta tekşirildi), 41-a `vals: [90, π/2]`.
5. **`crop_questions.py` tüzatildi**: çegara endi siyohsiz oraliqdan (oldin `keyingi raqam − 8pt` edi, 6-topşiriqning ildiz çizigi 5-rasmga tuşib qolardi); qirqiş siyoh böyiça, suv belgisi rasmni kattalaştirmaydi.
6. **Öyin içida yangi mock qöşiş**: PDF tanlaş → brauzerda qirqiş → qirqilgan rasmlarni körish → kalit formasi (1–32 A–D, 33–35 A–F, 36–45 a/b, tez to'ldiriş qatori, kirill А/В/С/Д/Е ham qabul qilinadi, oçiq javob ostida `≈ qiymat` yoki xato xabari) → IndexedDB ga saqlaş → menyuda öçiriş tugmasi bilan.
7. `exHtml()` dagi qattiq yozilgan "15-mock" test nomiga almaştirildi; foydalanuvçi nomlari `esc()` bilan.
8. 390px da 33–35 qatoridagi "F" tugmasi yangi qatorga tuşardi — `.mrow` oralığı 6px, yorliq 28px.
9. Tekşirildi (Playwright, 390 va 1280px): uçala qurilgan test "Hammasi" rejimida kalitdagi javoblar bilan 100%, har rejimda birinçi savol; yuklangan Mock 14 — 43/43 topildi, saqlaş, qayta yuklaş, 100% ötiş, öçiriş; konsolda xato yöq.

## Qilinmagan işlar

1. 15-mock va Mock 14 uçun yeçişlar (`ex`).
2. Offline: saqlangan mocklar internetsiz işlaydi, lekin pdf.js va şriftlar birinçi marta tarmoqdan yuklanadi. To'liq offline uçun pdf.js ni `vendor/` ga qöyiş yoki service worker kerak.
3. Foydalanuvçi mocki uçun nom/kalitni keyin tahrirlaş yöq (öçirib qayta qöşiş kerak).
4. Kalitni rasmdan avtomatik öqiş (OCR) yöq.
5. `q/` va `q15/` eski skript bilan qirqilgan; yangi skript bilan qayta qirqiş mumkin (`--match-page` qiymatlari ma'lum emas, 33 turgan sahifani PDF dan aniqlaş kerak).

## Ma'lum muammolar

- Topşiriq rasmlari keng (~690 px): telefonda gorizontal surish kerak bölishi mumkin, "−" tugmasi bilan kiçraytiriladi.
- 24-mock 16-masalada logarifm asosi PDF da noaniq öqiladi; javob (2 ta) rasmiy kalitga mos.
- 15-mock 37-a, 41-a: gradus yoki radian ekanini masala matnidan tekşiriş kerak.
- Brauzer qirqişi faqat matn qatlami bor PDF da işlaydi (skaner qilingan PDF uçun xabar çiqadi).
- 33 bloki ikki sahifaga börilgan bölsa, faqat birinçi sahifa olinadi.
- pdf.js uçun SRI (`integrity`) qöyilmagan: bu muhitdan cdnjs yopiq edi, hash ni tekşirib bölmadi. Worker baribir SRI ni qöllamaydi.
- Asosiy saytning `sw.js` (scope `/`) `/mock-oyini/` ni ham boşqaradi: `.png` rasmlar `bilimtest-img-v1` keşiga tuşadi. Rasmni almaştirsangiz, fayl nomini yoki keşni yangilaş kerak bölişi mumkin.

## Keyingi ustuvorliklar

1. Haqiqiy telefonda (iOS Safari) IndexedDB Blob saqlaş va PDF qirqişni tekşiriş.
2. pdf.js ni offline uçun lokal nusxa yoki SW keşi.
3. Foydalanuvçi mockini tahrirlaş (kalit, nom).
4. 15-mock va Mock 14 yeçişlari.
