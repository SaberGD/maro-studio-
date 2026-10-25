# Horix Vectors

العنوان: https://vectors.horix.live/

**Horix Vectors** هو برنامج الفيكتور (بديل Illustrator) من عيلة HORIX بتاعة أكاديمية صابر جروب. مبني على [VectorCraft](https://github.com/storytold/vectorcraft) المفتوح المصدر (MIT OR Apache-2.0)، الإصدار **0.16.0** (tag `v0.16.0`، commit `1019075`).

زي HORIX بالظبط: إحنا مش بنعدّل الكود الأصلي بإيدينا. `rebrand.py` بيتطبّق على نسخة نظيفة من الكود وقت البناء، فالتحديث لأي إصدار جديد من VectorCraft هو إن تحفظ الكود الجديد في `archive/vectorcraft/` وتشغّل البناء تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| الاسم (القوايم، About، الرسايل، الترجمات، تبويب المتصفح) | VectorCraft | `Horix Vectors` |
| الأيقونة | التنين بتاع VectorCraft | صقر HORIX على Horus Ink، ومعاه شارة Horix Red فيها نقطة Pen بالـHandles بتاعتها (`assets/app-icon/`، متولدة بـ`apps/horix-common/tools/make_icons.py`) |
| الألوان | رمادي أزرق بارد ولون Coral | رمادي Horus Ink وGraphite الدافي، والنص Falcon Ivory، والحالة النشطة Vision Amber `#EA993F`، وزراير الأكشن Horix Red `#D63C32`. أغمق درجة (Dark) هي الافتراضية |
| زرار Discord وروابط ArtCraft | Discord والموقع وGitHub | زرار «Saber Group» (فيسبوك الأكاديمية)، وموقع الأكاديمية، وصفحة تحميل الديسكتوب `horix.si`، والتواصل على واتساب |
| صفحة الويب | «Loading VectorCraft…» | شاشة تحميل HORIX: الصقر، واسم البرنامج، وخط Horix Red، و`BY SABER GROUP` |

الأسماء الداخلية في الكود (`vectorcraft_engine`، `VectorcraftApp`، …) مش بتظهر للمستخدم، فسيبناها زي ما هي عشان التحديثات ما تتكسرش.

## الترخيص

- `LICENSE-MIT` و`LICENSE-APACHE` و`NOTICE` بيتنسخوا مع كل نسخة ويب زي ما هم.
- شاشة About بتقول بوضوح إن البرنامج مبني على برمجيات مفتوحة المصدر.
- علامات ArtCraft التجارية (`docs/brand/`) مش مستخدمة في أي حتة.

## البناء

المتطلبات: Rust ≥ 1.95، والـtarget بتاع wasm، و`trunk`، وPython 3، و`zip`.

```sh
rustup target add wasm32-unknown-unknown
apps/horix-vectors/build.sh        # يطلع deploy/horix-vectors/horix-vectors-<version>-web.zip
```

الـzip فيه فولدر `horix-vectors/`، وده موقع static يشتغل على أي دومين وأي مسار (فيه `.htaccess` لـApache/Hostinger).

`.github/workflows/build-horix-family.yml` بيبني النسخة دي مع Horix Light على GitHub مع أي تعديل، وبيحفظ الـzip كـartifact. وعلى الفرع الافتراضي بينشرها على الدومين بتاعها (`apps/horix-common/deploy-static.sh`، بنفس secret `HOSTINGER_API_TOKEN` بتاع HORIX). أول نشر بيعمل الـsubdomain نفسه على Hostinger (`apps/horix-common/ensure-subdomain.sh`) جوه فولدر في `horix.live`، ويطلب له شهادة SSL.

## التحديث لإصدار جديد

1. `git archive --format=tar.gz --prefix=vectorcraft-<version>/ -o archive/vectorcraft/vectorcraft-source-<version>.tar.gz <tag>` من ريبو VectorCraft.
2. `apps/horix-vectors/build.sh archive/vectorcraft/vectorcraft-source-<version>.tar.gz`.
3. لو `rebrand.py` وقف برسالة `expected text not found`، يبقى الكود الأصلي اتغيّر في المكان ده. عدّل السطر ده بس وشغّل تاني.
