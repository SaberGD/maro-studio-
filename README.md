# Maro Studio

**Maro Creative Studio** هي منصة ويب يفتح فيها متدرب أكاديمية صابر جروب أدوات تصميم داخل المتصفح، ومعه **مارو (Maro Assistant)**: مدرب ومساعد تنفيذ يقرأ حالة الملف، يقترح خطة، وينفذ أوامر حقيقية داخل الأداة — بأمان ومن خلال أوامر مسموح بها فقط.

> الحالة: **Sprint 1**: Studio shell + Maro Chat Panel + command protocol + adapter **mock**. التنفيذ على PhotoCraft الحقيقي هو Phase 1/3. التفاصيل في [`docs/sprint-01.md`](docs/sprint-01.md).

## ليه نبدأ بـ PhotoCraft؟

[PhotoCraft](https://github.com/storytold/photocraft) محرر صور مفتوح المصدر (MIT OR Apache-2.0) بيشتغل في المتصفح (WebAssembly)، وكل فعل فيه عبارة عن command من registry واحد (500+ أمر) متاح من CLI وJSON-lines server وMCP. ده بالظبط اللي محتاجينه علشان مارو يتحكم في الأداة. VectorCraft وEffectCraft هييجوا بعد ما تجربة الصور تثبت (Phase 5 و6).

## عيلة HORIX

| البرنامج | بديل | مبني على | المكان |
|---|---|---|---|
| HORIX | Photoshop | PhotoCraft 0.15.1 | [`apps/sg-ps/`](apps/sg-ps/README.md) |
| Horix Vectors | Illustrator | VectorCraft 0.16.0 | [`apps/horix-vectors/`](apps/horix-vectors/README.md) |
| Horix Light | Lightroom | LightCraft 0.13.0 | [`apps/horix-light/`](apps/horix-light/README.md) |
| HORIX One | Photoshop + Illustrator (زي Affinity) | HORIX + Horix Vectors | [`apps/horix-one/`](apps/horix-one/README.md): برنامج واحد فيه Vector وPixel، على one.horix.live والديسكتوب |
| HORIX Launcher | ArtCraft Launcher | craft-launcher 0.4.1 | [`apps/horix-launcher/`](apps/horix-launcher/README.md): بيسطّب البرامج دي ويحدّثها |

كلهم بنفس الطريقة: الكود الأصلي محفوظ في `archive/`، و`rebrand.py` بيغيّر الاسم واللوجو والألوان والروابط وقت البناء. الأدوات المشتركة بين Horix Vectors وHorix Light في `apps/horix-common/`.

## التشغيل المحلي

المتطلبات: Node.js 20+ (مُجرّب على 22) و npm 10.

```sh
npm install
npm run dev          # API على :8787 + الواجهة على http://localhost:5173
```

افتح http://localhost:5173، ارفع صورة، واكتب لمارو مثلًا:

> اعملي بوست 1080x1350، شيل الخلفية، حط المنتج في النص، وخلي الخلفية بيج، وصدرها png

مارو يرد بخطة ← تضغط «تنفيذ» ← الخطوات تتنفذ على «معاينة Maro» ← التصدير يستنى موافقتك ← الصورة تنزل.

أوامر أخرى:

| الأمر | الوظيفة |
|---|---|
| `npm run dev:api` / `npm run dev:web` | تشغيل جزء واحد |
| `npm test` | اختبارات الـschema والـplanner والـAPI والـadapter |
| `npm run typecheck` | TypeScript لكل الـworkspaces |
| `npm run build` | build للواجهة في `apps/web/dist` |
| `npm run verify` | فحص عدم وجود أسرار في كود المتصفح + typecheck + tests + build |

## Environment variables

| الملف | المحتوى |
|---|---|
| `services/api/.env` (انسخ من `.env.example`) | إعدادات السيرفر فقط: `PORT`، `CORS_ORIGIN`، `MARO_PLANNER`، `AUDIT_LOG_PATH`، `RATE_LIMIT_PER_MINUTE`، ولاحقًا مفاتيح الـLLM |
| `apps/web/.env.local` (انسخ من `.env.example`) | قيم عامة فقط: `VITE_PHOTOCRAFT_URL`. **أي متغير يبدأ بـ `VITE_` بيتشحن للمتصفح — ممنوع تحط فيه أي secret.** |

## هيكل المشروع

```text
apps/web/                 واجهة Studio (Vite + React + TypeScript، RTL)
  src/features/studio/    مساحة العمل، المعاينة، undo، التصدير
  src/features/chat/      Maro Chat Panel وتشغيل الخطة خطوة بخطوة
  src/features/auth/      session id مؤقت (مش auth حقيقي)
services/api/             الـbackend (Express): /api/maro/chat و /api/audit
  src/maro/               Planner interface، rules planner، system prompt للـLLM
  src/security/           rate limit و security headers
  src/audit/              audit log (JSON lines)
packages/tool-protocol/   تعريف الأوامر، الـallowlist، الـvalidation، الـadapters (mock + PhotoCraft map)
packages/shared/          schemas مشتركة بين الواجهة والـAPI
integrations/photocraft/  كل ما يخص PhotoCraft: التشغيل، adapter spec، command map
docs/                     architecture، mvp-scope، security، licensing، sprint-01
scripts/                  dev runner و verify
```

## إضافة tool adapter جديد

1. أضف الـactions الجديدة في `packages/tool-protocol/src/commands/actions.ts` (schema صارم بـ`.strict()`) وفي الـallowlist في `commands/policy.ts` (risk + هل تحتاج موافقة).
2. نفّذ `ToolAdapter` (`inspect()` و `execute()`) في `packages/tool-protocol/src/adapters/` أو في `integrations/<tool>/`.
3. اكتب ترجمة الأوامر لأوامر الأداة الفعلية ووثّقها في `integrations/<tool>/command-map.md`.
4. أضف tests: validation للـparams الغلط، وتنفيذ الـworkflow على الـadapter.
5. علّم المهارة للـplanner (rules أو الـsystem prompt).

## حدود الأمان (مختصر)

- المتصفح **لا** يكلم أي LLM API. كل المفاتيح في السيرفر فقط (`npm run verify` بيفحص ده).
- مارو ينفذ الأوامر الموجودة في الـallowlist فقط، وكل أمر بيعدي على schema validation في السيرفر وتاني في المتصفح قبل التنفيذ.
- `requiresApproval` بتحدده الـpolicy، مش الـLLM: التصدير دايمًا يستنى موافقة الطالب.
- الملفات المرفوعة: حد أقصى للحجم، فحص النوع الحقيقي من أول bytes، PNG/JPG/WebP فقط.
- rate limit لكل session، وaudit log مختصر بدون محتوى حساس.

التفاصيل والفجوات المعروفة في [`docs/security.md`](docs/security.md).

## حالة الترخيص

PhotoCraft وVectorCraft وEffectCraft كلهم **MIT OR Apache-2.0** (تمت المراجعة على commits محددة). علامة ArtCraft التجارية **ليست** مفتوحة المصدر ولا نستخدمها. لا يوجد كود خارجي منسوخ داخل هذا الريبو. التفاصيل والالتزامات في [`docs/licensing.md`](docs/licensing.md).
