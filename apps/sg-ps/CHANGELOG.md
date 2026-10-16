# HORIX: سجل الإصدارات

رقم الإصدار في `VERSION` (زي `0.2`). أي تعديل بيتنشر بيرفع الرقم خطوة (`0.3`، `0.4`، …) ويتكتب هنا. وGitHub بيزوّد رقم البناء في الآخر تلقائيًا، فكل نسخة بتنزل ليها رقم مختلف (`0.2.57`). الرقم ده بيظهر في About، وSystem Info، وشاشة البداية، واسم ملف التحميل.

## v0.2 (قيد التطوير، فرع `claude/horix-0.9-port`)

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
