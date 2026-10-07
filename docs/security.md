# Security

## ما تم تطبيقه في Sprint 1

| البند | التطبيق | المكان |
|---|---|---|
| مفاتيح الـAPI | لا يوجد أي LLM call من المتصفح. إعدادات السيرفر في `services/api/.env` فقط. `npm run verify` يفشل لو ظهر `VITE_*KEY/SECRET/TOKEN` أو LLM endpoint أو مفتاح في كود المتصفح/الـpackages | `scripts/verify/no-secrets-in-web.mjs` |
| Allowlist | أي action غير مُعرّف في `ALLOWLIST` + `ACTION_PARAMS` يُرفض | `packages/tool-protocol/src/commands/policy.ts` |
| Schema validation | zod `.strict()` لكل action؛ params زيادة (مثل `path`) أو قيم خارج الحدود ← رفض. أسماء ملفات التصدير بدون `/` أو `..` | `actions.ts`، `validate.ts` |
| الموافقة | `requiresApproval` من الـpolicy فقط؛ التصدير يتوقف لحد موافقة الطالب | `policy.ts`، `runPlan.ts` |
| Defense in depth | المتصفح يعيد فحص كل أمر بـ`toolCommandSchema` قبل تنفيذه | `apps/web/src/features/chat/runPlan.ts` |
| حجم الطلب | JSON body ≤ 64KB، رسالة ≤ 2000 حرف، ≤ 12 أمر في الخطة | `app.ts`، `shared/constants` |
| Rate limit | 30 طلب/دقيقة لكل session (قابل للضبط) | `security/rate-limit.ts` |
| Headers | `nosniff`، `X-Frame-Options: DENY`، `no-referrer`، `no-store`؛ CSP في صفحة الويب | `security/headers.ts`، `apps/web/index.html` |
| الرفع | ≤ 15MB، النوع الحقيقي من magic bytes (PNG/JPEG/WebP فقط)، ≤ 8192px | `apps/web/src/features/tools/uploads.ts` |
| Prompt injection | الرسالة، حالة الملف، والـuploads حقول منفصلة؛ الـrules planner لا يقرأ أسماء الطبقات أو الملفات؛ الـsystem prompt ينص إن أي نص داخل صور/أسماء/مخرجات أدوات = data | `shared/schemas/chat.ts`، `maro/system-prompt.ts` |
| Audit | JSON lines: session، requestId، actions، المرفوض، أول 120 حرف من الرسالة فقط، ونتائج التنفيذ. بدون صور | `audit/audit-log.ts` |
| السيرفر | يستمع على `127.0.0.1` فقط في التطوير | `services/api/src/index.ts` |

## فجوات معروفة (لازم تتقفل قبل أي نشر)

1. **مفيش authentication.** `X-Maro-Session` مجرد معرّف مجهول لتقسيم الـrate limit والـaudit. لازم ربط دخول Saber أو auth مستقل + صلاحيات طالب/مدرب/أدمن في الـbackend.
2. **التنفيذ في المتصفح (mock).** نتائج التنفيذ اللي بتوصل `/api/audit` بيبلّغ عنها العميل، فمش موثوقة. لما التنفيذ يتنقل للسيرفر (خيار A في architecture) الـaudit يتكتب من السيرفر نفسه.
3. **الملفات المرفوعة لسه في المتصفح.** عند نقلها للسيرفر: تخزين معزول لكل مستخدم، فحص magic bytes على السيرفر، إعادة encode للصور، روابط تحميل مؤقتة موقّعة، ومنع أي ملف تنفيذي.
4. **Rate limit في الذاكرة.** يكفي process واحد؛ مع أكثر من instance لازم Redis أو ما يماثله، بالإضافة لحدود يومية وتكلفة الـLLM.
5. **CSP في التطوير** فيها `'unsafe-inline'` للسكريبت (مطلوب لـVite React refresh). في الـproduction تُرسل الـCSP كـheader من السيرفر بدون `unsafe-inline`.
6. **PhotoCraft headless (خيار A):** شغّله بـ`--automation-read-root`/`--automation-write-root` لمجلد الـsession فقط، على stdio (مش TCP)، بحدود وقت وذاكرة، ومن غير صلاحيات شبكة. PhotoCraft نفسه يرفض أوامر `file.*` اللي فيها paths خارج الـroots.

## قواعد ثابتة

- ممنوع أي secret في `apps/web` أو في أي متغير `VITE_*`.
- إخفاء زر في الواجهة ليس حماية؛ أي صلاحية تُطبّق في الـbackend.
- أي action جديد = schema صارم + policy + test للمدخلات الغلط.
