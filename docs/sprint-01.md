# Sprint 1

الفترة: بدأ 7 أكتوبر 2026. الهدف: تثبيت الريبو، تشغيل PhotoCraft Web محليًا، أول Studio shell، وإثبات إن مارو يرجّع خطة أوامر منظمة (التنفيذ mock).

## المهام

| # | المهمة | الحالة | ملاحظات |
|---|---|---|---|
| 1 | الريبو + README | ✅ | [`README.md`](../README.md) |
| 2 | اختيار الـstack | ✅ | Vite + React + TS، Express + zod، npm workspaces، Vitest ([architecture](architecture.md#stack)) |
| 3 | تشغيل PhotoCraft Web محليًا وتوثيقه | ⏳ خطوات التشغيل موثقة؛ تجربة البناء الكامل جارية | [`integrations/photocraft/README.md`](../integrations/photocraft/README.md) |
| 4 | طريقة الـembedding / integration | ✅ قرار مبدئي | iframe للعرض اليدوي فقط. لا يوجد JS API في الـweb build، فالتنفيذ المقترح headless على السيرفر ([architecture](architecture.md)) |
| 5 | شاشة Studio (Top bar، Tool area، Chat Panel، Export) | ✅ | Export يعمل فعليًا (PNG من المعاينة)، مش placeholder |
| 6 | `POST /api/maro/chat` | ✅ | يستقبل الرسالة + حالة الملف + الـuploads، يرجع `{reply, steps, commands, rejected}` |
| 7 | Command schema + allowlist | ✅ | `packages/tool-protocol` |
| 8 | Adapter mock لأول 5 Actions | ✅ | `MockPhotoCraftAdapter` + `toPhotoCraftSteps` للـPhotoCraft الحقيقي |
| 9 | هذا الملف | ✅ | |
| 10 | مخاطر الترخيص والتكامل | ✅ | [licensing](licensing.md)، والمخاطر تحت |

## Definition of Done

| البند | الحالة |
|---|---|
| تشغيل المشروع بأمر واضح | ✅ `npm install && npm run dev` |
| صفحة Studio تفتح بدون أخطاء | ✅ متجربة في Chromium (Playwright): بدون console errors |
| PhotoCraft أو placeholder موثق داخل الواجهة | ✅ تبويب «PhotoCraft Web» (iframe عند ضبط `VITE_PHOTOCRAFT_URL`، وإلا placeholder بخطوات التشغيل) |
| Maro Chat Panel يرد بخطة منظمة | ✅ |
| لا مفاتيح API في المتصفح | ✅ ويتفحص آليًا بـ`npm run verify` |
| كل أوامر Maro تمر عبر schema | ✅ في السيرفر، ومرة تانية في المتصفح قبل التنفيذ |
| docs تشرح ما تم وما لم يتم | ✅ |

## اللي اتعمل زيادة عن الخطة

- تنفيذ الخطة خطوة بخطوة مع progress، توقف للموافقة قبل التصدير، undo للخطة كاملة.
- وضع «اشرح لي» (بدون تنفيذ) ووضع «نفّذ».
- Rules planner عربي offline (أرقام عربية، "بوست/ستوري/مربع"، ألوان) — بديل مؤقت للـLLM بنفس الـinterface.
- Rate limit، security headers، CSP، فحص نوع الملف الحقيقي، audit log.
- 19 test (validation، adapter، command map، planner، API).

## اللي لسه متعملش

- التنفيذ على PhotoCraft الحقيقي (الـadapter الـheadless) — Phase 1/3.
- LLM planner عبر LLM gateway في السيرفر — Phase 2. الـsystem prompt جاهز في `services/api/src/maro/system-prompt.ts`.
- Authentication وصلاحيات — حاليًا session id مجهول فقط.
- تخزين الملفات على السيرفر؛ الصور حاليًا في المتصفح فقط.
- إزالة الخلفية في المعاينة **محاكاة** (key بلون الأركان)، تنجح مع الخلفيات السادة فقط.

## المخاطر المفتوحة

| الخطر | التأثير | الخطوة التالية |
|---|---|---|
| PhotoCraft Web بدون JS API | مارو لا يقدر يعدّل داخل الـUI الحي | Phase 1: headless adapter؛ وفتح issue/PR upstream لـ`postMessage` bridge |
| PhotoCraft "early alpha" | تغييرات في الأوامر أو الـprotocol | تثبيت commit، و`command-map.md` + tests للـmap |
| أوامر محتاجة تحقق (`select.subject` headless، align مع selection، ترتيب fill layer) | نتيجة مختلفة عن المعاينة | تجربة كل صف "verify" في command-map على `photocraft-cli serve` |
| حجم الـwasm (~19MB) ومتطلبات WebGPU/WebGL2 | تحميل بطيء أو أجهزة طلاب ضعيفة | ضغط Brotli + CDN؛ أو الاعتماد على الـrender من السيرفر |
| علامة ArtCraft | مخالفة لو ظهرت في منتجنا | لا نستخدمها؛ أي build معدّل يشيلها |
| اسم "PhotoCraft" في الواجهة | غير محسوم في ملف العلامة | سؤال للـArtCraft team أو مراجعة قانونية |
| Auth غير موجود | لا يصلح للنشر | قرار: ربط Saber أو auth مستقل للـMVP |

## Sprint 2 المقترح

1. `HeadlessPhotoCraftAdapter` في `services/api` على `photocraft-cli serve` + render للمعاينة، وتنفيذ أمر واحد end-to-end (`resize_canvas`) ثم الخمسة.
2. رفع الصور للسيرفر في workspace معزول لكل session.
3. LLM gateway (provider في السيرفر) خلف `Planner` interface، مع نفس الـvalidation.
4. قرار الـauth وتطبيقه.
