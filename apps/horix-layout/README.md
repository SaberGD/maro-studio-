# Horix Layout

العنوان: https://layout.horix.live/

**Horix Layout** هو برنامج تصميم الصفحات والنشر (بديل InDesign) من عيلة HORIX بتاعة أكاديمية صابر جروب. مبني على [DesignCraft](https://github.com/storytold/designcraft) المفتوح المصدر (MIT OR Apache-2.0)، الإصدار **0.12.0** (tag `v0.12.0`، commit `5e8ef67`).

بيعمل spreads وparent pages، وtext frames متوصلة ببعض (threaded)، وparagraph وcharacter styles، وجداول، وtext wrap. بيفتح IDML وملفات InDesign، وبيصدّر PDF (PDF/X-4 وPDF/A-2b) وEPUB وPNG وPowerPoint.

زي باقي العيلة: إحنا مش بنعدّل الكود الأصلي بإيدينا. `rebrand.py` بيتطبّق على نسخة نظيفة من الكود وقت البناء، فالتحديث لأي إصدار جديد من DesignCraft هو إن تحفظ الكود الجديد في `archive/designcraft/` وتشغّل البناء تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| الاسم (القوايم، About، الرسايل، الترجمات، تبويب المتصفح) | DesignCraft | `Horix Layout` |
| الأيقونة | أيقونة DesignCraft | صقر HORIX ومعاه شارة Horix Red فيها صفحة (`assets/app-icon/`، متولدة بـ`make_icons.py layout`) |
| شعار ArtCraft (About وشاشة البداية) | شعار ArtCraft الأزرق | صقر HORIX بلون Vision Amber |
| الألوان | رمادي محايد ولون أساسي أزرق | Horus Ink وGraphite، واللون الأساسي Vision Amber، والزراير الأساسية Horix Red، والدرجة الأغمق هي الافتراضية |
| زرار Discord وروابط ArtCraft | Discord والموقع وGitHub | زرار «Saber Group» (فيسبوك الأكاديمية)، وموقع الأكاديمية، وصفحة تحميل الديسكتوب `horix.si`، والتواصل على واتساب |
| «More ArtCraft apps» في About | تطبيقات ArtCraft | «The HORIX family»: HORIX وHorix Vectors وHorix Light |
| صفحة الويب | «Loading DesignCraft…» | شاشة تحميل HORIX |

الترجمات القديمة للعناوين اللي اتغيّرت (اللي كانت بتتكلم عن ArtCraft وDiscord وGitHub) اتشالت، والعربي ليه ترجمة جديدة.

## العربي

- **على الويب:** المتصفح مفيهوش خطوط النظام، فالبناء بيحط Noto Sans Arabic جوه البرنامج من craft-fonts. النسخة اللي DesignCraft 0.12 بيستخدمها مفيهاش خط عربي، فبنستخدم النسخة اللي Horix Vectors بيستخدمها (`CRAFT_FONTS_REF`).
- **الحروف العربية دايمًا بتتكتب بخط فيه الحروف دي.** إعداد «Draw Missing Glyphs from Fallback Fonts» مقفول في المستندات الجديدة زي InDesign، وكان النص العربي بيطلع مربعات بالخط الافتراضي (Source Serif). دلوقتي الحروف العربية بتاخد الخط البديل في كل الأحوال.
- **على الديسكتوب:** بيستخدم خطوط الجهاز العربي.

## البناء

```sh
apps/horix-layout/build.sh                              # الويب: deploy/horix-layout/horix-layout-<v>-web.zip
apps/horix-common/desktop-package.sh layout windows     # ويندوز: horix-layout-<v>-windows-x64-portable.zip
apps/horix-common/desktop-package.sh layout macos       # ماك: horix-layout-<v>-macos-universal.dmg
```

- `build-horix-family.yml` بيبني الويب مع كل تعديل، وعلى الفرع الأساسي بينشره على `layout.horix.live`.
- `desktop-horix-family.yml` بيطلّع release باسم `horix-layout-v<v>` لما `VERSION` يتغيّر، والـLauncher وصفحة الماك على horix.si بيتحدّثوا بعدها.

## الخطوة الجاية

Horix Layout هيبقى الـpersona التالتة في HORIX One (Vector وPixel وLayout)، بنفس طريقة دمج Horix Vectors: البرنامج كمكتبة جوه نافذة HORIX.
