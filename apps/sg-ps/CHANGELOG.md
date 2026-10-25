# HORIX: سجل الإصدارات

رقم الإصدار في `VERSION` (زي `0.2`). أي تعديل بيتنشر بيرفع الرقم خطوة (`0.3`، `0.4`، …) ويتكتب هنا. وGitHub بيزوّد رقم البناء في الآخر تلقائيًا، فكل نسخة بتنزل ليها رقم مختلف (`0.2.57`). الرقم ده بيظهر في About، وSystem Info، وشاشة البداية، واسم ملف التحميل.

## v0.3

- HORIX بقى مبني على PhotoCraft **0.15.1** بدل 0.9.0 (6 إصدارات وحوالي 3,200 تعديل من الأصل).
- الجديد اللي جاي من الأصل:
  - Content-Aware Fill كامل، وContent-Aware Move بمعاينة حية، والـCrop بيملا الأطراف بـContent-Aware.
  - تصدير PDF، وفتح ملفات GIMP (XCF) وTIFF Lab وCineon، وتحسينات كتير في PSD (smart filters).
  - كارت الشاشة أسرع: دمج الطبقات العادية بقى في خطوة واحدة (111 → 28ms)، وحدود لذاكرة الكارت، وإصلاحات لكروت AMD، وSystem Info بيعرض ذاكرة الكارت.
  - طباعة على الديسكتوب، والملف بيفتح في نفس نافذة HORIX لو مفتوح.
  - Object Finder بيلاقي الحاجات الصغيرة أحسن، وSample All Layers بقى لكل أداة لوحدها، وSelect Subject العادي اتحسن على الخلفيات اللي لونها قريب من الموضوع.
  - Color Profile في New Document، و«Remember this choice» في رسالة Profile Mismatch.
  - مقابض Blur Gallery لـField وIris وSpin وTilt-Shift على الصورة، بأكتر من pin.
- **AI التحديد زي ما هو:** MobileSAM في Quick Selection وObject Selection، وIS-Net في Select Subject. الأصل لسه مفيهوش أي موديل AI للتحديد، فالأدوات العادية بتفضل الاحتياطي لو الموديل ما اتحمّلش.
- شلنا من الـpatches بتاعتنا اللي الأصل بقى بيعمله:
  - Color Profile في New Document (كان هيظهر مرتين).
  - مقابض Iris وSpin وTilt-Shift في Blur Gallery. مقابض **Path Blur** فضلت، لأنها لسه مش في الأصل.
  - تحسين Select Subject على الخلفية السادة: الأصل عمل نفس الفكرة (backdrop pass)، والطريق الأساسي هو IS-Net.
- فضلت من تحسيناتنا: P قبل/بعد في الفلاتر، وProfile Mismatch مقفولة من الأول، وعلامة «+» الحمرا للنص، وسؤال حذف الـgroup، وUngroup بالكليك اليمين، وEyedropper في Color، وProperties بتفتح لوحدها، ومعاينة Select › Modify، وزرار نسخ الديسكتوب، والخطوط من الجهاز على الويب، وكيبورد عربي في الاختصارات.
- اختبارات HORIX (`horix_ux_tests`، والـAI، وPath Blur، والـengine، والنص) عدّت كلها على 0.15.1، ما عدا اختبار واحد من الأصل محتاج كارت شاشة.

## v0.2

- HORIX بقى مبني على PhotoCraft 0.9.0 بدل 0.3.0. التفاصيل في `UPGRADE-0.9.md`.
- مميزات جديدة جاية من الأصل: 19 أداة جديدة (منها Remove و Patch و Content-Aware Move و Mixer Brush و Artboard و Perspective Crop)، وفتح ملفات SVG كأشكال تقدر تعدلها، وملفات Krita و Paint.NET و Affinity، وأداء أسرع على كارت الشاشة، و14 ثيم، و docking كامل للبانلز.
- الهوية والثيم وشاشة البداية والروابط اتنقلوا على 0.9.0، ومعاهم الأيقونات في كل المقاسات.
- الحاجات اللي الأصل بقى بيعملها لوحده (Magnetic Lasso، و Curvature Pen، و Blend If، وتعدد الـeffects، و Refine Edge Brush، …) اتشالت من الـpatches بتاعتنا.
- أدوات الـAI رجعت (`patches/50-horix-ai.diff`): MobileSAM في Quick Selection و Object Selection، و IS-Net في Select Subject. ولو الموديل مش موجود، الأدوات بتشتغل بطريقة PhotoCraft العادية.
- تحسينات الاستخدام (`patches/60-horix-ux.diff`):
  - مقابض Blur Gallery على الصورة (Iris و Spin و Tilt-Shift و Path)، وتقدر تحط أكتر من pin.
  - زرار P للمقارنة قبل وبعد في نوافذ الفلاتر.
  - رسالة Profile Mismatch مقفولة من الأول.
  - اختيار Color Profile في New Document.
  - علامة «+» حمرا لما النص يكون أكبر من البوكس.
  - Ungroup من القايمة اللي بتظهر بالكليك اليمين.
  - رسالة بتسألك لما تمسح group: تمسح الـgroup بس ولا اللي جواه كمان.
  - Eyedropper في بانل Color.
  - بانل Properties بتظهر لوحدها مع أدوات الأشكال والنص والقلم.
  - معاينة حية في Select › Modify.
- اتأكدنا إن 0.9.0 حلّت لوحدها: مشاكل الـundo والـcommit في Free Transform، والنسخ والقص والصق بالكيبورد العربي على الديسكتوب، والنسخ مع selection على الأشكال والنص.

## v0.1

HORIX على PhotoCraft 0.3.0. ده الإصدار المنشور على https://horix.live/.
