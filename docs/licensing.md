# Licensing

تمت المراجعة في 7 أكتوبر 2026 على الـcommits التالية. **هذه مراجعة هندسية وليست رأيًا قانونيًا**؛ يُنصح بمراجعة قانونية قبل الإطلاق التجاري.

| Repo | Commit | الترخيص | ملاحظات |
|---|---|---|---|
| [storytold/photocraft](https://github.com/storytold/photocraft) | `e70deec` | MIT OR Apache-2.0 ([MIT](https://github.com/storytold/photocraft/blob/main/LICENSE-MIT)، [Apache](https://github.com/storytold/photocraft/blob/main/LICENSE-APACHE)، [NOTICE](https://github.com/storytold/photocraft/blob/main/NOTICE)) | علامات ArtCraft في `docs/brand/` **ليست** مفتوحة المصدر. خطوط Inter/JetBrains Mono (OFL 1.1)، أيقونات Lucide (ISC)، SCOWL. الـweb build لا يضم craft-fonts |
| [storytold/vectorcraft](https://github.com/storytold/vectorcraft) | `5cacbe3` | MIT OR Apache-2.0 | نفس شروط علامة ArtCraft. Phase 5 |
| [storytold/effectcraft](https://github.com/storytold/effectcraft) | `3af4649` | MIT OR Apache-2.0 | نفس شروط علامة ArtCraft. Phase 6 |

## إجابات أسئلة الخطة

| السؤال | الإجابة |
|---|---|
| استخدام تجاري؟ | نعم (MIT وApache-2.0 كلاهما يسمح) |
| تعديل وإعادة توزيع؟ | نعم |
| نشر الكود المشتق إلزامي؟ | لا (ليست copyleft). |
| Third-party بترخيص مختلف؟ | نعم لكن permissive: OFL 1.1 للخطوط، ISC للأيقونات، SCOWL، CC0 لملفات ICC. لازم نشحن ملفات الترخيص معهم |
| الاسم والعلامة؟ | **علامات ArtCraft (الاسم والـwordmark والـlogo) ممنوعة** في أي منتج غير PhotoCraft نفسه، وأي نسخة معدّلة يجب أن تزيلها. مسموح نكتب نصًا: "based on PhotoCraft by the ArtCraft team". استخدام اسم "PhotoCraft" نفسه في الواجهة غير مذكور صراحة في ملف العلامة ← سؤال مفتوح |

## قرار الاستخدام

- **Sprint 1:** لا يوجد أي كود أو asset من PhotoCraft داخل هذا الريبو. الـcommand ids في `photocraft-map.ts` مجرد أسماء أوامر (واجهة عامة) موثقة في الـcontrol protocol.
- **PhotoCraft Web في iframe** يُبنى ويُشغّل محليًا كـPoC فقط، من checkout منفصل خارج الريبو (`vendor/` متجاهل في git).
- **لا production** مبني على PhotoCraft قبل: (1) قرار fork/package، (2) تجهيز ملف NOTICE وملفات تراخيص الـthird-party، (3) التأكد من إزالة أي علامة ArtCraft من أي build معدّل، (4) مراجعة قانونية سريعة.

## التزامات Saber عند التوزيع

1. إرفاق نص MIT أو Apache-2.0 (حسب اختيارنا) و`NOTICE` الخاص بـPhotoCraft.
2. لو استخدمنا Apache-2.0 وعدّلنا ملفات: توضيح إن الملفات اتعدلت.
3. إرفاق تراخيص الخطوط والأيقونات وSCOWL مع أي build نوزعه.
4. عدم استخدام أي من علامات ArtCraft، وعدم الإيحاء بأن ArtCraft تدعم Maro Studio.
5. تحديث هذا الملف مع كل dependency أو commit جديد.
