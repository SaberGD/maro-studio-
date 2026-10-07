# Architecture

## الشكل العام

```text
Browser (apps/web)
  ├─ Studio shell: Top bar · Workspace · Maro Chat Panel
  ├─ Workspace: «معاينة Maro» (mock adapter) | PhotoCraft Web (iframe، اختياري)
  └─ fetch /api/*  (بدون أي مفاتيح)
          │
          ▼
Maro Studio API (services/api)
  ├─ session (مؤقت) → rate limit → zod validation للطلب
  ├─ Planner  (rules الآن · LLM gateway لاحقًا)
  ├─ validatePlan: allowlist + schema لكل action + approval policy
  └─ Audit log (JSON lines)
          │  ChatResponse { reply, steps, commands, rejected }
          ▼
Browser: runPlan → يعيد فحص الـschema → ToolAdapter.execute → render → audit
```

## تدفق طلب واحد

1. الطالب يكتب رسالة. الواجهة تبعت `{message, mode, document, uploads}` لـ`POST /api/maro/chat`. الرسالة وحالة الملف والـuploads **حقول منفصلة**؛ أسماء الطبقات والملفات بيانات وليست تعليمات.
2. السيرفر يتحقق من الطلب (`chatRequestSchema`)، يطلب خطة من الـ`Planner`، ثم يمرر الأوامر المقترحة على `validatePlan`:
   - tool غير معروف أو action خارج الـallowlist ← `rejected`.
   - params غلط أو زيادة (`.strict()`) ← `rejected`، بدون أي "تصحيح" تلقائي.
   - `requiresApproval` يُحسب من `ALLOWLIST`، ويتجاهل أي قيمة من الـplanner.
   - حد أقصى 12 أمر في الخطة.
3. الواجهة تعرض الخطة. عند «تنفيذ»: snapshot للـundo، ثم تنفيذ الأوامر بالترتيب. قبل أي أمر يحتاج موافقة (التصدير) يتوقف التنفيذ لحد ما الطالب يوافق. أول فشل يوقف باقي الخطوات.
4. النتائج تتبعت لـ`POST /api/audit`.

## لماذا التنفيذ في المتصفح في Sprint 1؟

PhotoCraft Web لا يوفر حاليًا أي JavaScript API أو `postMessage` bridge (الـwasm build يشغّل الـUI فقط؛ راجع [`integrations/photocraft/README.md`](../integrations/photocraft/README.md)). لذلك Sprint 1 يستخدم `MockPhotoCraftAdapter`: نفس الـ`ToolAdapter` interface ونفس الأوامر، على document state في الذاكرة، والمعاينة ترسمه على canvas. الطريقان المرشحان للتنفيذ الحقيقي:

| الخيار | الشكل | المميزات | العيوب |
|---|---|---|---|
| **A. Headless server-side** | `services/api` يشغل `photocraft-cli serve` (JSON-lines) لكل session داخل workspace معزول، وينفذ `toPhotoCraftSteps(...)`، ويرجع render PNG | يشتغل اليوم بدون تعديل PhotoCraft؛ صلاحيات الملفات بـ read/write roots؛ نفس الـengine | الطالب يشوف نتيجة (render) مش الـUI الحي؛ تكلفة process لكل session |
| **B. Browser bridge** | fork صغير لـPhotoCraft Web يضيف `postMessage` handler يستدعي `engine.execute` داخل الـwasm | الطالب يشوف التعديل حي في الأداة نفسها | يحتاج fork وصيانة أو PR upstream |

التوصية: **A للـMVP** (أسرع وأأمن، والسيرفر يطبق الصلاحيات)، مع فتح نقاش upstream لـ B. القرار النهائي في Phase 0/1 بعد تجربة `photocraft-cli serve` فعليًا.

## الطبقات

| الطبقة | المكان | المسؤولية |
|---|---|---|
| Frontend | `apps/web` | Studio UI، رفع الصور، Chat Panel، progress، approve/undo/export |
| Backend | `services/api` | session، rate limit، planner، validation، audit |
| Protocol | `packages/tool-protocol` | الأوامر، الـallowlist، `validatePlan`، `ToolAdapter`، mock adapter، PhotoCraft command map |
| Shared | `packages/shared` | schemas الطلب والرد والـaudit، الحدود والـroutes |
| Integration | `integrations/photocraft` | توثيق التشغيل والـadapter spec والـcommand map |

## Stack

- **Web:** Vite 5 + React 18 + TypeScript، RTL عربي، بدون UI library.
- **API:** Node 20+ + Express 4 + zod، تشغيل TypeScript مباشرة بـ`tsx`.
- **Monorepo:** npm workspaces؛ الـpackages تُستهلك كـTypeScript source (بدون build step).
- **Tests:** Vitest + supertest.
