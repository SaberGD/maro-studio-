# HORIX One

**HORIX One** برنامج واحد فيه **Vector** و**Pixel**، بديل Illustrator وPhotoshop مع بعض، بفكرة الـpersonas اللي في Affinity. فوق فيه شريط بتنقل منه بين الاتنين، وزرار بينقل شغلك من واحد للتاني بضغطة. **Layout** (بديل InDesign) هو الخطوة الجاية.

- الويب: https://one.horix.live/
- الديسكتوب (ويندوز وماك): من HORIX Launcher، أو صفحة الماك على https://horix.si/

## الـpersonas

| Persona | المحرّك | بيعمل إيه |
|---|---|---|
| Vector | Horix Vectors (VectorCraft 0.16) | فيكتور، ولوجوهات، ونص عربي |
| Pixel | HORIX (PhotoCraft 0.15.1) | تعديل صور، وتحديد بالـAI (MobileSAM وIS-Net) |
| Layout | قريبًا | صفحات وكتب ومجلات |

## نقل الشغل بين الـpersonas

- **Vector ← Pixel («افتح التصميم في Pixel»):**
  - Vector بيصدّر الرسمة SVG، والنص فيها بيتحوّل لأشكال (`outlineText`)، علشان يدخل Pixel بشكله بالظبط من غير ما يحتاج الخط.
  - Pixel بيفتحها كطبقات أشكال تقدر تعدّلها.
- **Pixel ← Vector («افتح الصورة في Vector»):**
  - Pixel بيعمل Quick Export as PNG.
  - الصفحة بتاخد الملف بدل ما يتنزّل (`window.horixOneCapture`)، وVector بيفتحه في مستند جديد.

## إزاي مبني

- **الويب:**
  - `web/index.html` هي الصفحة: فيها الشريط، والـpersonas، والنقل بينهم.
  - كل persona برنامج كامل في `iframe` على نفس الدومين: `vector/` نسخة Horix Vectors زي ما هي، و`pixel/` نسخة HORIX متبنية على المسار `/pixel/` (`HORIX_PUBLIC_URL`).
  - كل persona بتتحمّل أول مرة تفتحها بس.
  - Vector فيه API جاهز (`window.vectorcraft`).
  - Pixel اتضاف له API في `apps/sg-ps/patches/70-horix-one.diff`:
    - `wasmBindings.horix_command(id, params)` بيشغّل أي أمر زي القوايم.
    - `wasmBindings.horix_open(name, bytes)` بيفتح ملف.
- **الديسكتوب (`desktop/`):**
  - برنامج Rust صغير (tao وwry) بيفتح نافذة واحدة، وجواها نفس موقع HORIX One من فولدر البرنامج.
  - بيستخدم الـWebView بتاع النظام: WebView2 على ويندوز، وWKWebView على الماك.
  - العنوان آمن (`https://horixone.localhost/` على ويندوز)، فـWebGPU والـclipboard شغالين.
  - الحفظ بيفتح نافذة Save الأصلية بتاعة النظام، واللينكات الخارجية بتفتح في المتصفح.
  - رقم الإصدار جوه `horix-one.exe` هو رقم الـrelease، والـLauncher بيتأكد منه.
- **في الإصدار ده:**
  - المحرّكين شغالين في الديسكتوب جوه الـWebView، مش native.
  - HORIX وHorix Vectors الـnative لسه موجودين في الـLauncher للشغل التقيل.
  - دمج المحرّكين الـnative في برنامج واحد (مستند واحد بين الـpersonas) مرحلة جاية.

## البناء

```sh
apps/horix-one/build.sh                                   # الويب: deploy/horix-one/horix-one-<v>-web.zip
apps/horix-one/desktop/package.sh windows <site أو zip>   # على ويندوز: horix-one-<v>-windows-x64-portable.zip
apps/horix-one/desktop/package.sh macos <site أو zip>     # على ماك: horix-one-<v>-macos-universal.dmg
```

`build.sh` بيبني HORIX وHorix Vectors بالسكريبتات بتاعتهم. ولو عندك نسخ متبنية خلاص، استخدمها بـ`HORIX_ONE_PIXEL` و`HORIX_ONE_VECTOR`.

`.github/workflows/horix-one.yml` بيعمل التالي:
- **مع أي تعديل:** يبني الويب ونسختي ويندوز وماك.
- **على الفرع الأساسي:** ينشر الويب على `one.horix.live`، والـsubdomain بيتعمل لوحده أول مرة.
- **لما `VERSION` يتغيّر:** يطلّع release باسم `horix-one-v<v>`، وبعدها يحدّث ملف تحديثات الـLauncher وصفحة الماك.

الأيقونة متولدة بـ`apps/horix-common/tools/make_icons.py one apps/horix-one/assets/app-icon`.
