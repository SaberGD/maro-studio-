# HORIX One

**HORIX One** برنامج واحد فيه **Vector** و**Pixel** و**Layout**، بديل Illustrator وPhotoshop وInDesign مع بعض، بفكرة الـpersonas اللي في Affinity. فوق فيه شريط بتنقل منه بينهم، وزراير بتنقل شغلك من واحد للتاني بضغطة.

- الويب: https://one.horix.live/
- الديسكتوب (ويندوز وماك): من HORIX Launcher، أو صفحة الماك على https://horix.si/

## الـpersonas

| Persona | المحرّك | بيعمل إيه |
|---|---|---|
| Vector | Horix Vectors (VectorCraft 0.16) | فيكتور، ولوجوهات، ونص عربي |
| Pixel | HORIX (PhotoCraft 0.15.1) | تعديل صور، وتحديد بالـAI (MobileSAM وIS-Net) |
| Layout | Horix Layout (DesignCraft 0.12) | صفحات وكتب ومجلات: spreads، وtext frames متوصلة، وstyles، وجداول. بيفتح IDML وبيصدّر PDF وEPUB |

## نقل الشغل بين الـpersonas

| من | لـ | بيتنقل إزاي | فين |
|---|---|---|---|
| Vector | Pixel | SVG، والنص بيتحوّل لأشكال، وبيتفتح كطبقات أشكال | الويب والديسكتوب |
| Pixel | Vector | PNG في مستند جديد | الويب والديسكتوب |
| Vector | Layout | PDF بيتحط على الـspread اللي قدامك | الديسكتوب |
| Pixel | Layout | PNG بيتحط على الـspread اللي قدامك | الديسكتوب |
| Layout | Vector | PDF لأول صفحة في المستند | الديسكتوب |

اللي بيروح لـLayout بيتحط على الـspread المفتوح، ولو مفيش مستند مفتوح بيتعمل مستند جديد. على الويب Layout بيتفتح من الشريط، لكن لسه مفيهوش زراير نقل.

- **Vector ← Pixel («افتح التصميم في Pixel»):**
  - Vector بيصدّر الرسمة SVG، والنص فيها بيتحوّل لأشكال (`outlineText`)، علشان يدخل Pixel بشكله بالظبط من غير ما يحتاج الخط.
  - Pixel بيفتحها كطبقات أشكال تقدر تعدّلها.
- **Pixel ← Vector («افتح الصورة في Vector»):**
  - Pixel بيعمل Quick Export as PNG.
  - الصفحة بتاخد الملف بدل ما يتنزّل (`window.horixOneCapture`)، وVector بيفتحه في مستند جديد.
- **لـLayout ومنه («Place in Layout» و«Open in Vector»، على الديسكتوب):**
  - Vector بيصدّر PDF، وPixel بيصدّر PNG، وLayout بيحطهم على الـspread (`place_bytes`).
  - Layout بيصدّر أول صفحة PDF، وVector بيفتحها.

## إزاي مبني

- **الويب:**
  - `web/index.html` هي الصفحة: فيها الشريط، والـpersonas، والنقل بينهم.
  - كل persona برنامج كامل في `iframe` على نفس الدومين: `vector/` نسخة Horix Vectors زي ما هي، و`pixel/` نسخة HORIX متبنية على المسار `/pixel/` (`HORIX_PUBLIC_URL`)، و`layout/` نسخة Horix Layout زي ما هي.
  - شاشة تحميل HORIX بشارة HORIX One (`VECTOR · PIXEL · LAYOUT`) بتفضل فوق الـpersona لحد ما يشتغل، ونسبتها ماشية مع شاشة تحميل الـpersona نفسه.
  - كل persona بتتحمّل أول مرة تفتحها بس.
  - Vector فيه API جاهز (`window.vectorcraft`).
  - Pixel اتضاف له API في `apps/sg-ps/patches/70-horix-one.diff`:
    - `wasmBindings.horix_command(id, params)` بيشغّل أي أمر زي القوايم.
    - `wasmBindings.horix_open(name, bytes)` بيفتح ملف.
- **الديسكتوب (`native/`):** من 0.2 البرنامج native بالكامل، ومن 0.3 فيه Layout.
  - HORIX نفسه هو البرنامج، وHorix Vectors وHorix Layout جواه كمكتبات (library)، والتلاتة شغالين في نفس النافذة وعلى نفس كارت الشاشة.
  - الشريط اللي فوق (`native/horix_one.rs`) بيبدّل بين الـpersonas، وبيرجّع لكل واحد الخطوط والشكل بتوعه.
  - نقل الشغل بيحصل جوه البرنامج نفسه من غير متصفح، بالطرق اللي في الجدول فوق.
  - القفل: Layout بيسأل عن الشغل اللي ما اتحفظش الأول، وبعده Vector، وبعدهم Pixel.
  - كل persona ليه إعداداته ومستنداته. على ويندوز البرنامج portable: إعدادات Pixel وVector في `HORIX-Data` و`VectorCraftData` جنب البرنامج، فما بيشاركوش HORIX العادي. أما Layout فإعداداته واسترجاع الشغل بعد الـcrash مشتركين مع Horix Layout العادي.
  - على الماك القوايم جوه النافذة، علشان كل persona يبقى ليه قوايمه.
  - إزاي بيتبني:
    - `native/prepare.sh` بيجهّز سورس HORIX في `pixel/`، وسورس Horix Vectors في `vector/`، وسورس Horix Layout في `layout/`، كل واحد زي ما بيتبني لوحده (rebrand.py وpatches بتاعته).
    - بعدها بيطبّق patches HORIX One: `patches/vector` و`patches/layout` بيخلّوا Horix Vectors وHorix Layout مكتبات (`horix_one_persona`)، و`patches/pixel` بيخلّي نافذة HORIX تشيلهم، بأسماء HORIX One.
    - و`native/Cargo.lock` فيه dependencies التلات برامج مع بعض، بنسخة واحدة من مكتبات الـPDF (`[patch.crates-io]`).
- **في الإصدار ده (0.3):**
  - كل persona ليه مستنداته، والنقل بينهم بزرار. مستند واحد مشترك بينهم مرحلة جاية.
  - على الويب Layout من غير زراير نقل لسه.

## البناء

```sh
apps/horix-one/build.sh                    # الويب: deploy/horix-one/horix-one-<v>-web.zip
apps/horix-one/native/package.sh windows   # على ويندوز: horix-one-<v>-windows-x64-portable.zip
apps/horix-one/native/package.sh macos     # على ماك: horix-one-<v>-macos-universal.dmg
apps/horix-one/native/prepare.sh /tmp/one  # السورس بس (تجربة على لينكس: cd /tmp/one/pixel && cargo run -p photocraft)
```

`build.sh` بيبني HORIX وHorix Vectors وHorix Layout بالسكريبتات بتاعتهم. ولو عندك نسخ متبنية خلاص، استخدمها بـ`HORIX_ONE_PIXEL` و`HORIX_ONE_VECTOR` و`HORIX_ONE_LAYOUT`.

`.github/workflows/horix-one.yml` بيعمل التالي:
- **مع أي تعديل:** يبني الويب، ونسختي ويندوز وماك الـnative، ويتأكد إن البرنامج بيفتح ورقم إصداره صح.
- **على الفرع الأساسي:** ينشر الويب على `one.horix.live`، والـsubdomain بيتعمل لوحده أول مرة.
- **لما `VERSION` يتغيّر:** يطلّع release باسم `horix-one-v<v>`، وبعدها يحدّث ملف تحديثات الـLauncher وصفحة الماك.

الأيقونة متولدة بـ`apps/horix-common/tools/make_icons.py one apps/horix-one/assets/app-icon`.
