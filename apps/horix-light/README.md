# Horix Light

العنوان: https://light.horix.live/

**Horix Light** هو برنامج تنظيم وتحميض الصور (بديل Lightroom) من عيلة HORIX بتاعة أكاديمية صابر جروب. مبني على [LightCraft](https://github.com/storytold/lightcraft) المفتوح المصدر (MIT OR Apache-2.0)، الإصدار **0.13.0** (tag `v0.13.0`، commit `23e1812`).

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

## تحديد بالذكاء الاصطناعي على الويب (HORIX AI)

النسخة الأصلية من LightCraft مفيهاش AI masks على الويب خالص: Object وDescribe محتاجين موديل SAM 3، وده حجمه 3.4 جيجا ورخصته مش مفتوحة المصدر وبيشتغل على الديسكتوب بس. وSubject وBackground كانوا تقدير تقريبي من غير موديل.

`patches/50-horix-ai.diff` بيدّي light.horix.live نفس موديلات HORIX، وكلها شغالة في المتصفح نفسه (onnxruntime-web: كارت الشاشة بـWebGPU لو موجود، وإلا البروسيسور):

- **Masking › Object:** اضغط على الحاجة اللي عايزها، وAlt+كليك يشيل جزء منها. الموديل MobileSAM (44 ميجا).
- **Masking › Subject وBackground:** بيظهر التقدير العادي الأول، وبعد ثواني بيتبدل بنتيجة IS-Net (89 ميجا) ويتسمّى «Subject» أو «Background». خطوة Undo واحدة بترجع للتقدير.
- **Describe:** لسه للديسكتوب بس، وعلى الويب بيظهر رسالة بتقول كده.

الموديلات بتنزل أول مرة بس، والمتصفح بيحتفظ بيها. النتيجة بتتخزن في الصورة كـAI mask عادي (`SegMask`)، فبتفتح زي ما هي في نسخة الديسكتوب وفي التصدير.

إزاي بيشتغل:
- الـengine بيحط الطلب في طابور (`Segmenter::external`، `crates/engine/src/segment/external.rs`).
- الصفحة بتشغّل الموديل (`window.horixLight` في `index.html`).
- النتيجة بترجع بأمر `mask.horixResult`، اللي بيرمي أي نتيجة قديمة لو المستخدم ضغط تاني في الوقت ده.
- الديسكتوب ما اتغيرش، ولسه بيستخدم SAM 3.

`build.sh` بيجيب الموديلات بـ`apps/sg-ps/ai/fetch.py web`، وبيحطها في `models/` مع رخصها، وبيتأكد من الـSHA-256 بتاعها. `deploy-static.sh` مش بيرفع موديل لو هو موجود على الموقع بنفس الحجم.

## الترخيص

- `LICENSE-MIT` و`LICENSE-APACHE` و`NOTICE` بيتنسخوا مع كل نسخة ويب زي ما هم.
- شاشة About بتقول بوضوح إن البرنامج مبني على برمجيات مفتوحة المصدر.
- علامات ArtCraft التجارية (`docs/brand/`) مش مستخدمة في أي حتة.

## البناء

المتطلبات: Rust ≥ 1.95، والـtarget بتاع wasm، و`wasm-bindgen-cli` بنفس الإصدار اللي في `Cargo.lock`، وPython 3 ومعاه `onnx` و`onnxruntime` (`pip install --user onnx onnxruntime`)، و`git`، و`zip`.

```sh
rustup target add wasm32-unknown-unknown
apps/horix-light/build.sh        # يطلع deploy/horix-light/horix-light-<version>-web.zip
```

الـzip فيه فولدر `horix-light/`، وده موقع static يشتغل على أي دومين وأي مسار (فيه `.htaccess` لـApache/Hostinger).

`.github/workflows/build-horix-family.yml` بيبني النسخة دي مع Horix Vectors على GitHub مع أي تعديل، وبيحفظ الـzip كـartifact. وعلى الفرع الافتراضي بينشرها على الدومين بتاعها (`apps/horix-common/deploy-static.sh`، بنفس secret `HOSTINGER_API_TOKEN` بتاع HORIX). أول نشر بيعمل الـsubdomain نفسه على Hostinger (`apps/horix-common/ensure-subdomain.sh`) جوه فولدر في `horix.live`، ويطلب له شهادة SSL.

## التحديث لإصدار جديد

1. `git archive --format=tar.gz --prefix=lightcraft-<version>/ -o archive/lightcraft/lightcraft-source-<version>.tar.gz <tag>` من ريبو LightCraft.
2. `apps/horix-light/build.sh archive/lightcraft/lightcraft-source-<version>.tar.gz`.
3. لو `rebrand.py` وقف برسالة `expected text not found`، يبقى الكود الأصلي اتغيّر في المكان ده. عدّل السطر ده بس وشغّل تاني.

## ملاحظة: Photo › Edit In

LightCraft بيفتح الصور في PhotoCraft كبرنامج تعديل خارجي. في Horix Light الأمر ده لسه بيدوّر على PhotoCraft زي الأصل. ربطه بـHORIX (`HORIX.exe` / `HORIX.app`) خطوة جاية.
