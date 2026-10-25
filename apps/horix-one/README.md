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
- **الديسكتوب (`native/`):** من 0.2 البرنامج native بالكامل.
  - HORIX نفسه هو البرنامج، وHorix Vectors جواه كمكتبة (library)، والاتنين شغالين في نفس النافذة وعلى نفس كارت الشاشة.
  - الشريط اللي فوق (`native/horix_one.rs`) بيبدّل بين الـpersonas، وبيرجّع لكل واحد الخطوط والشكل بتوعه.
  - نقل الشغل بيحصل جوه البرنامج نفسه من غير متصفح:
    - Vector بيصدّر SVG والنص فيه بيتحوّل لأشكال، وPixel بيفتحه كطبقات أشكال.
    - Pixel بيعمل Quick Export as PNG، وVector بيفتحه.
  - القفل: Vector بيسأل عن الشغل اللي ما اتحفظش الأول، وبعده Pixel.
  - كل persona ليه إعداداته ومستنداته. على ويندوز البرنامج portable: الإعدادات في `HORIX-Data` و`VectorCraftData` جنب البرنامج، فما بيشاركش HORIX العادي.
  - على الماك القوايم جوه النافذة، علشان كل persona يبقى ليه قوايمه.
  - إزاي بيتبني:
    - `native/prepare.sh` بيجهّز سورس HORIX في `pixel/` وسورس Horix Vectors في `vector/`، كل واحد زي ما بيتبني لوحده (rebrand.py وpatches بتاعته).
    - بعدها بيطبّق patches HORIX One: `patches/vector` بيخلّي Horix Vectors مكتبة (`horix_one_persona`)، و`patches/pixel` بيخلّي نافذة HORIX تشيله، بأسماء HORIX One.
    - و`native/Cargo.lock` فيه dependencies البرنامجين مع بعض.
- **في الإصدار ده:**
  - Layout لسه «قريبًا».
  - كل persona ليه مستنداته، والنقل بينهم بزرار. مستند واحد مشترك بين الاتنين مرحلة جاية.

## البناء

```sh
apps/horix-one/build.sh                    # الويب: deploy/horix-one/horix-one-<v>-web.zip
apps/horix-one/native/package.sh windows   # على ويندوز: horix-one-<v>-windows-x64-portable.zip
apps/horix-one/native/package.sh macos     # على ماك: horix-one-<v>-macos-universal.dmg
apps/horix-one/native/prepare.sh /tmp/one  # السورس بس (تجربة على لينكس: cd /tmp/one/pixel && cargo run -p photocraft)
```

`build.sh` بيبني HORIX وHorix Vectors بالسكريبتات بتاعتهم. ولو عندك نسخ متبنية خلاص، استخدمها بـ`HORIX_ONE_PIXEL` و`HORIX_ONE_VECTOR`.

`.github/workflows/horix-one.yml` بيعمل التالي:
- **مع أي تعديل:** يبني الويب، ونسختي ويندوز وماك الـnative، ويتأكد إن البرنامج بيفتح ورقم إصداره صح.
- **على الفرع الأساسي:** ينشر الويب على `one.horix.live`، والـsubdomain بيتعمل لوحده أول مرة.
- **لما `VERSION` يتغيّر:** يطلّع release باسم `horix-one-v<v>`، وبعدها يحدّث ملف تحديثات الـLauncher وصفحة الماك.

الأيقونة متولدة بـ`apps/horix-common/tools/make_icons.py one apps/horix-one/assets/app-icon`.
