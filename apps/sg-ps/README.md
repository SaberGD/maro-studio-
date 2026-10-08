# SG - PS

**SG - PS** هو محرر الصور بتاع أكاديمية صابر جروب، بثيم مارو. شغال على https://studio.engsaber.space/

البرنامج مبني على محرر صور مفتوح المصدر بترخيص MIT. إحنا مش بنعدّل الكود الأصلي بإيدينا، لكن بنطبّق عليه سكريبت إعادة التسمية (`rebrand.py`) وقت البناء. ده بيخلّي التحديث لأي إصدار جديد مجرد تشغيل السكريبت تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| اسم البرنامج (العنوان، شاشة البداية، About، القوايم، الترجمات، تبويب المتصفح) | الاسم الأصلي | `SG - PS` |
| الأيقونة | أيقونة البرنامج الأصلي | رأس مارو (`assets/sg-ps-logo.svg`) على شاشة البداية وفي About وتبويب المتصفح |
| الثيم الافتراضي | رمادي بلون أزرق | **Maro (Dark)**: خلفية `#151515` و`#1c1c1c`، أحمر برتقالي `#c4321f` و`#e85c3b`، وأصفر `#fbbf24` |
| زرار Discord وروابط المطور الأصلي | موجودة في الشريط العلوي وشاشة البداية وHelp | اتشالت. الروابط بقت لـ `sabergroupacademy.com` و `studio.engsaber.space` |
| أسماء ملفات البرنامج على السيرفر | باسم البرنامج الأصلي | `sg-ps-<hash>.js` و `sg-ps-<hash>_bg.wasm` |

الثيمات التانية لسه موجودة في Window › Theme.

## اللي لازم يفضل (شرط الترخيص)

- **`LICENSE.txt`**: نص ترخيص MIT، ومعاه سطر حقوق المطوّر الأصلي. ترخيص MIT بيشترط إن السطر ده يفضل مع أي نسخة بنوزعها. هو ملف نصي على السيرفر، **ومش بيظهر في واجهة البرنامج**.
- **`THIRD-PARTY-NOTICES.txt`**: تراخيص الخطوط (Inter وJetBrains Mono) والأيقونات (Lucide) وقاموس الإملاء (SCOWL) المدمجين في البرنامج.
- شاشة About فيها سطر عام: «Built on open-source software (MIT / Apache-2.0)» من غير ما تذكر أي اسم.

الأسماء الداخلية في الكود (زي `photocraft_engine`) مش بتوصل للمستخدم، وتغييرها هيكسر التحديثات، فسيبناها زي ما هي.

## البناء

المتطلبات: Rust ≥ 1.95، وtarget الـwasm، و`trunk`، و`zip`.

```sh
rustup target add wasm32-unknown-unknown
cargo install trunk --locked
apps/sg-ps/build.sh                # يطلع deploy/sg-ps/sg-ps-<version>-hostinger.zip
```

أول build بياخد وقت طويل (حوالي ساعة على 4 cores)، والـbuilds اللي بعده أسرع.

## الرفع على هوستينجر

نفس خطوات `deploy/photocraft-web/README.md`، بس بالملف `deploy/sg-ps/sg-ps-<version>-hostinger.zip`. ولو عندك Hostinger connector:
1. Generate upload URL للدومين `studio.engsaber.space`، وارفع الـzip بـTUS.
2. Deploy static site archive، بـ`archive_path` = اسم الـzip.

## التحديث لإصدار جديد

1. احفظ الكود المصدري للإصدار الجديد في `archive/photocraft/`.
2. شغّل `apps/sg-ps/build.sh archive/photocraft/photocraft-source-<version>.tar.gz`.
3. لو `rebrand.py` وقف برسالة `expected text not found`، يبقى الكود الأصلي اتغيّر في المكان ده. عدّل السطر ده بس في السكريبت، وشغّله تاني.

## قياس أدوات التحديد (`segeval/`)

`segeval/segeval.rs` بيقيس دقة Select Subject وQuick Selection (IoU) على صور معروف فيها الإجابة الصح. لتشغيله: انسخه لـ`crates/algo/examples/` في نسخة الكود المصدري، وشغّل `cargo run --release -p photocraft-algo --example segeval -- <فولدر الصور>`.

النتايج على 15 حالة (مارو على خلفيات سادة، ومتدرجة، ودافية، ومزحومة؛ وصور close-up، وعنصر عريض، وعنصر صغير):

| الأداة | قبل | بعد |
|---|---|---|
| Select Subject: متوسط الـIoU | 0.756 | **0.867** |
| Select Subject: خلفيات مزحومة | 0.26–0.43 | **0.76–0.94** |
| Quick Selection: الدقة (الجزء المحدد اللي جوه العنصر فعلًا) | 1.00 | 1.00 (من غير تغيير) |

الحالة اللي لسه بتفشل: عنصر صغير جدًا على خلفية مزحومة، وكانت بتفشل في النسخة الأصلية برضه. التحسن الأكبر بعد كده محتاج موديل ذكاء اصطناعي للتحديد (زي RMBG أو U²-Net) يشتغل في المتصفح.
