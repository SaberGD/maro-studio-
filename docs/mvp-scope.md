# MVP Scope

الهدف: رابط يفتحه الطالب، يرفع صورة، يطلب من مارو تعديل واضح بالعربي، ومارو ينفذ تعديل حقيقي داخل أداة التصميم أمامه.

## داخل النطاق

- دخول بسيط أو ربط مبدئي مع نظام Saber.
- صفحة Studio بـPhotoCraft كأول أداة.
- رفع صورة، Maro Assistant بجانب مساحة العمل، طلب بالعربي.
- تحويل الطلب لخطة أوامر، وتنفيذ أول مجموعة أوامر داخل PhotoCraft.
- عرض النتيجة، التصدير، وسجل مختصر للأوامر.

## أول 5 Actions

| Action | الحالة في Sprint 1 |
|---|---|
| `import_image` | ✅ mock + map لـ`doc.open` |
| `resize_canvas` | ✅ mock + map لـ`image.canvasSize` (+ solid fill للخلفية) |
| `remove_background` | ⚠️ mock (محاكاة تقريبية بلون الأركان) + map لـ`select.subject` → `layer.layerMask.revealSelection` |
| `position_layer` | ✅ mock + map لـ`layer.align.*` |
| `export_image` | ✅ تنزيل PNG/JPG فعلي من المعاينة، بموافقة + map لـ`doc.save` |

بعدها: Background Fill (مستقل)، Basic Adjustment، Text Layer، Shadow، Template Apply.

## خارج النطاق

دعم كل أوامر PhotoCraft، الفيديو والـmotion، marketplace، billing، تعاون live، استضافة ملفات كبيرة، VectorCraft وEffectCraft.

## Success criteria

راجع القسم 10 في خطة الـMVP. الحالة الحالية لكل بند في [`sprint-01.md`](sprint-01.md).
