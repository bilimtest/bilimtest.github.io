# BilimTest — katta o'zgarish rejasi (2026-10-01)

Maqsad: dastur bitta fanga (matematika) emas, **har bir fanga o'z vositalari bilan** moslashadi.
Yadro umumiy bo'ladi (login, sinflar, testlar, natijalar, import); har fan o'z modulini qo'shadi.

## Asosiy qoida
- Har bosqichdan keyin sayt **ishlaydigan** holatda qoladi.
- Eski savollar (`type` maydoni yo'q) avtomatik `choice` turi deb hisoblanadi — hech narsa buzilmaydi.
- Har savol turi bitta joyda ro'yxatdan o'tadi (`QTYPES`): ko'rsatish, javobni tekshirish, ustoz muharriri.

## Savol tuzilishi (yangi)
```
{ id, subject, topic, type, text, img, teacherId, level?, data:{...turga xos...} }
```
| type | data | Tekshirish |
|---|---|---|
| `choice` (hozirgi) | options, correct, isMulti | hozirgidek |
| `fill` — bo'sh joy | text ichida `___`, answers:[[variantlar]] | katta-kichik harf/bo'shliqqa befarq |
| `match` — moslashtirish | pairs:[[chap, o'ng]] | har juft uchun ball |
| `order` — tartiblash | items:[to'g'ri tartibda] | to'liq yoki qisman ball |
| `open` — ochiq javob | rubric, maxScore | AI (Groq) baholaydi, ustoz tasdiqlaydi |
| `hotspot` — rasmda belgilash | img, zones:[{x,y,r}] | nuqta zona ichidami |
| `map` — xaritada | region kodi (ISO) | to'g'ri davlat bosildimi |

## O'zlashtirish tizimi (hamma fanda, 1-bosqichdan boshlab ma'lumot yig'iladi)
- **Har javob yoziladi**: o'quvchi, savol id, fan, mavzu, savol turi, ko'nikma (`skill`: grammar/reading/vocab/...), to'g'ri/xato yoki qisman ball, vaqt.
- **Zaif joylar**: mavzu va ko'nikma bo'yicha o'zlashtirish foizi (oxirgi urinishlar og'irroq). 60% dan past → "Bu mavzuni ko'proq tayyorlang" + shu mavzudan mashq tugmasi. Xato qilingan savollar "Xatolarim" ro'yxatiga tushadi.
- **Takrorlash jadvali (spaced repetition)**: Ebbinghaus unutish egri chizig'iga asoslangan **SM-2** algoritmi (Anki ishlatadigan). Har so'z/savol uchun: oraliq (1 kun → 3 → 7 → 16 → ...), "osonlik" koeffitsienti, keyingi takrorlash sanasi. To'g'ri javob → oraliq uzayadi, xato → qaytadan 1 kun. Ingliz so'zlari uchun asosiy, lekin xato qilingan har qanday savolga ham qo'llanadi.
- **O'quvchi statistikasi sahifasi**: fanlar bo'yicha o'zlashtirish, mavzular "issiqlik xaritasi" (yashil/sariq/qizil), vaqt bo'yicha o'sish grafigi, yodlangan so'zlar soni, bugungi takrorlash navbati, ketma-ket kunlar (streak).
- **Ustoz uchun**: sinf bo'yicha eng qiyin mavzular va savollar.

## Bosqichlar
1. **Yadro: savol turlari tizimi** — `QTYPES` registry; `renderQ`/`submitTest`/natija sahifasi/ustoz muharriri shu orqali ishlaydi. Yangi turlar: `fill`, `match`, `order`. Ball: qisman ball qo'llab-quvvatlanadi.
2. **Ingliz tili** — Grammar (`fill`, `choice`), Reading (matn + savollar guruhi), CEFR darajasi (A1–C2), AI matndan test tuzadi.
3. **Listening** — audio savol (R2'ga yuklash yoki brauzer TTS), **Writing** — `open` + AI baholash.
3a. **IELTS / CEFR baholash** — imtihon formatidagi to'liq testlar (bo'limlar, vaqt):
   - Listening/Reading: xom ball /40 → rasmiy IELTS band jadvali (Academic va General alohida jadval).
   - Writing: AI 4 rasmiy mezon (TA/TR, CC, LR, GRA) bo'yicha band + izoh; Task 1 va Task 2; ustoz tasdiqlaydi.
   - Speaking: yozib olish → Groq Whisper → AI 4 mezon (FC, LR, GRA, P*) — taxminiy.
   - Umumiy band = 4 ko'nikma o'rtachasi (IELTS yaxlitlash qoidasi: .25→.5, .75→keyingi butun) → CEFR (4.0–5.0 B1, 5.5–6.5 B2, 7.0–8.0 C1, 8.5+ C2).
   - Multilevel (O'zbekiston, CEFR) formati: A1–C1 natija.
   - Natijada "taxminiy" deb aniq yoziladi; haqiqiy IELTS savollari ko'chirilmaydi (mualliflik huquqi).
4. **So'z kartochkalari** — to'plamlar, spaced repetition (Bildim/Qiynaldim/Bilmadim), kunlik takrorlash eslatmasi; o'yinlar: moslashtirish, tez tanlash, harflardan yig'ish, eshitib yozish, duel.
5. **Geografiya** — interaktiv xarita (`map`), bayroqlar, poytaxtlar; "Davlatni top" o'yini.
6. **Kimyo / Fizika / Tarix / Biologiya** — davriy jadval tugmalari, birlik tanlagich, vaqt chizig'i (`order`), rasmda belgilash (`hotspot`).
7. **Baza**: bitta JSON blob o'rniga Postgres jadvallari (savollar ko'payganda shart bo'ladi).

## Holat
- [x] 1-bosqich (yadro): QTYPES registry, fill/match/order, qisman ball, muharrir, natija tahlili — 2026-10-01
- [x] 1b: o'zlashtirish yozuvi (db.mastery[userId]: q - SM-2 holati, t - mavzu EMA avg), natijada maslahat — 2026-10-01
- [ ] 1c: o'quvchi statistikasi sahifasi, "Xatolarim" va bugungi takrorlash testi (myDueQuestionIds)
- [x] 4-bosqich (qisman): So'z kartochkalari — ustoz "Kartochkalar" tabi (so'z|tarjima qatorlari, ro'yxatdan joylash), o'quvchi "So'z yodlash" tabi (aylanadigan karta, 🔊, Bilmadim/Qiynaldim/Bildim, SM-2: mastery.c) — 2026-10-01
- [ ] UI QOIDASI: har yangi imkoniyat alohida katta tugma; maxsus sintaksis yo'q. Savol turlari muharririni ham shunga moslash (ustun-forma, `___`/`=` sintaksisisiz)
