# Horix Light

**Horix Light** هو برنامج تنظيم وتحميض الصور (بديل Lightroom) من عيلة HORIX بتاعة أكاديمية صابر جروب. مبني على [LightCraft](https://github.com/storytold/lightcraft) المفتوح المصدر (MIT OR Apache-2.0)، الإصدار **0.8.0** (commit `f34c7a8`).

زي HORIX بالظبط: إحنا مش بنعدّل الكود الأصلي بإيدينا. `rebrand.py` بيتطبّق على نسخة نظيفة من الكود وقت البناء، فالتحديث لأي إصدار جديد من LightCraft هو إن تحفظ الكود الجديد في `archive/lightcraft/` وتشغّل البناء تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| الاسم (القوايم، About، الرسايل، الترجمات، تبويب المتصفح) | LightCraft | `Horix Light` |
| الأيقونة | أيقونة LightCraft | صقر HORIX على Horus Ink، ومعاه شارة Horix Red فيها فتحة عدسة (Aperture) (`assets/app-icon/`، متولدة بـ`apps/horix-common/tools/make_icons.py`) |
| الألوان | ثيم Charcoal بلون أزرق | رمادي Horus Ink وGraphite الدافي، والنص Falcon Ivory، واللون الأساسي (Accent) Horix Red `#D63C32`، والتنبيهات Vision Amber `#EA993F`. الثيم الافتراضي اسمه دلوقتي HORIX |
| زرار Discord وروابط ArtCraft | Discord والموقع وGitHub | زرار «Saber Group» (فيسبوك الأكاديمية)، وموقع الأكاديمية، وصفحة تحميل الديسكتوب `horix.si`، والتواصل على واتساب |
| صفحة الويب | «Loading LightCraft…» | شاشة تحميل HORIX: الصقر، واسم البرنامج، وخط Horix Red، و`BY SABER GROUP` |

الأسماء الداخلية في الكود (`lightcraft_engine`، `LightcraftApp`، …) مش بتظهر للمستخدم، فسيبناها زي ما هي عشان التحديثات ما تتكسرش.

## الترخيص

- `LICENSE-MIT` و`LICENSE-APACHE` و`NOTICE` بيتنسخوا مع كل نسخة ويب زي ما هم.
- شاشة About بتقول بوضوح إن البرنامج مبني على برمجيات مفتوحة المصدر.
- علامات ArtCraft التجارية (`docs/brand/`) مش مستخدمة في أي حتة.

## البناء

المتطلبات: Rust ≥ 1.95، والـtarget بتاع wasm، و`wasm-bindgen-cli` بنفس الإصدار اللي في `Cargo.lock`، وPython 3 ومعاه Pillow، و`zip`.

```sh
rustup target add wasm32-unknown-unknown
pip install pillow
apps/horix-light/build.sh        # يطلع deploy/horix-light/horix-light-<version>-web.zip
```

الـzip فيه فولدر `horix-light/`، وده موقع static يشتغل على أي دومين وأي مسار (فيه `.htaccess` لـApache/Hostinger).

`.github/workflows/build-horix-family.yml` بيبني النسخة دي مع Horix Vectors على GitHub مع أي تعديل، وبيحفظ الـzip كـartifact. النشر لسه متوقف لحد ما نحدد الدومين.

## التحديث لإصدار جديد

1. `git archive --format=tar.gz --prefix=lightcraft-<version>/ -o archive/lightcraft/lightcraft-source-<version>.tar.gz <tag>` من ريبو LightCraft.
2. `apps/horix-light/build.sh archive/lightcraft/lightcraft-source-<version>.tar.gz`.
3. لو `rebrand.py` وقف برسالة `expected text not found`، يبقى الكود الأصلي اتغيّر في المكان ده. عدّل السطر ده بس وشغّل تاني.

## ملاحظة: Photo › Edit In

LightCraft بيفتح الصور في PhotoCraft كبرنامج تعديل خارجي. في Horix Light الأمر ده لسه بيدوّر على PhotoCraft زي الأصل. ربطه بـHORIX (`HORIX.exe` / `HORIX.app`) خطوة جاية.
