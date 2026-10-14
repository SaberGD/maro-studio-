# HORIX

**HORIX** (اسمه القديم SG - PS) هو محرر الصور بتاع أكاديمية صابر جروب: *The Visionary AI Editor by Saber Group*. عنوان المحرر الجديد https://horix.live/، وصفحة تحميل نسخ الديسكتوب https://horix.si/.

النشر يرفع محتوى `horix/` لجذر `horix.live` ومحتوى `downloads/` لجذر `horix.si`. بعد التأكد من الموقعين وملفات المحرر، يحول `/horix/` و`/downloads/` على موقع الأكاديمية إلى العناوين الجديدة. ملفات WordPress وباقي موقع الأكاديمية لا يتم استبدالها. `?legacy=1` يفتح الصفحة القديمة عند الحاجة إلى إعدادات المتصفح المحفوظة على الدومين السابق.

الفورم في كل دومين يرسل إلى `waitlist.php` على نفس الدومين. بيانات التسجيل تظل في `domains/sabergroupacademy.com/sgps-data/leads.csv`، وإعداد webhook السابق يستخدم تلقائيًا عند غياب إعداد محلي. الخطوط موجودة في `fonts/` بجوار كل صفحة؛ روابط نسخ ويندوز وماك تظل على `engsaber.space/sgps-downloads/`.

إعدادات النشر: `HOSTINGER_USERNAME` و`HORIX_EDITOR_DOMAIN` (الافتراضي `horix.live`) و`HORIX_DOWNLOAD_DOMAIN` (الافتراضي `horix.si`) و`HORIX_LEGACY_DOMAIN` (الافتراضي `sabergroupacademy.com`) و`HORIX_OLD_DOMAIN` (الافتراضي `studio.engsaber.space`). وصف النشر القديم أدناه يشرح الوضع السابق على موقع الأكاديمية.

الهوية البصرية الرسمية (الشعار، الألوان، قواعد الاستخدام) في [`brand/`](brand/HORIX-Brand-Guide.md). الأسماء الداخلية (فولدر `apps/sg-ps`، وملفات `sg-ps-<hash>.js`، ومفاتيح `sgps.*`، والـsecrets) فضلت زي ما هي عشان النشر وإعدادات المستخدمين ما يتكسروش.

البرنامج مبني على محرر صور مفتوح المصدر بترخيص MIT. إحنا مش بنعدّل الكود الأصلي بإيدينا، لكن بنطبّق عليه سكريبت إعادة التسمية (`rebrand.py`) وقت البناء. ده بيخلّي التحديث لأي إصدار جديد مجرد تشغيل السكريبت تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| اسم البرنامج (العنوان، شاشة البداية، About، القوايم، الترجمات، تبويب المتصفح) | الاسم الأصلي | `HORIX` |
| اللوجو | أيقونة البرنامج الأصلي | صقر HORIX: اللوجو الكامل (`assets/horix-lockup.svg`) على شاشة البداية وشاشة التحميل، والصقر لوحده (`assets/horix-symbol.svg`) في About، و`assets/horix-favicon.svg` في تبويب المتصفح. كلهم متولّدين من `brand/horix-master.svg` من غير أي تعديل في الرسمة |
| الثيم الافتراضي | رمادي بلون أزرق | **HORIX (Dark)**: بنية الـPro الكاملة التي تعرض كل البانلز وخيارات الأدوات، بألوان الـStudio الداكنة الهادئة، والنص Falcon Ivory `#F3EFE8` والحالة النشطة Vision Amber `#EA993F` |
| خط العناوين | Inter | **Barlow Condensed ExtraBold** (`assets/fonts/`، ترخيص OFL): خط condensed grotesk تقيل زي ما دليل الهوية طالب. خط الواجهة لسه Inter |
| زرار Discord وروابط المطور الأصلي | موجودة في الشريط العلوي وشاشة البداية وHelp | اتشالت. الروابط بقت لـ `sabergroupacademy.com` و`sabergroupacademy.com/horix` |
| أسماء ملفات البرنامج على السيرفر | باسم البرنامج الأصلي | `sg-ps-<hash>.js` و `sg-ps-<hash>_bg.wasm` |

الثيم القديم المختصر `Studio (Dark)` اتشال من القائمة ومن دورة التبديل لأنه كان يخفي أجزاء من البانلز. أي إعداد قديم كان مختاره بيتحوّل تلقائيًا إلى `HORIX (Dark)`؛ والثيمات البديلة المتبقية موجودة في Window › Theme.

## تحسينات المحرر في HORIX

- **Spot Healing:** مساحة التحليل بقت أوسع، واختيار النسيج أدق، والحواف بتندمج بتدرّج أنظف بدل نتيجة قريبة من الـBlur.
- **Magnetic Lasso:** موجودة داخل مجموعة الـLasso وبتنجذب تلقائيًا للحواف الأعلى تباينًا، مع تحكم مستقل في عرض منطقة البحث.
- **Pen Tool:** شريط الخيارات فيه `Pen` و`Curvature Pen` و`Add Anchor Point` و`Delete Anchor Point` و`Convert Point`. وضع Curvature يبني Handles ناعمة تلقائيًا، وإضافة النقطة تقسّم منحنى Bézier نفسه من غير ما تغيّر شكله.
- **Shape Tools:** لون الـFill ولون الـStroke مستقلان، ومعاهم عرض الـStroke في نفس شريط الخيارات. نفس الإعدادات متاحة للـPen في وضع Shape.
- **Camera Raw Curves:** النقطة بتتمسك من لحظة الضغط نفسها وتتحرك مع المؤشر بسلاسة، مع تثبيت نقطتي البداية والنهاية على طرفي المنحنى.
- **Color Picker:** زر `Pick from Image` يسمح بأخذ اللون من الصورة المفتوحة بدون إغلاق نافذة اختيار اللون.
- **Panels:** اسحب شريط أي Panel ناحية مساحة العمل عشان يتحول لنافذة حرة، واضغط `Dock` لإرجاعه. `Window > Workspace > Reset Essentials` يرجع الترتيب الافتراضي بالكامل.

## شاشة التحميل والضغط

- **الضغط:** السيرفر مش بيضغط ملف البرنامج (`sg-ps_bg.wasm`، 25 ميجا) لوحده. عشان كده `build.sh` بيجهّز نسختين مضغوطتين جنبه: `.br` (حوالي 8.4 ميجا) و`.gz` (حوالي 11 ميجا). و`.htaccess` بيبعت لكل متصفح أصغر نسخة يقدر يفكها.
- **أمان النشر:** بعد الرفع، `deploy.sh` بيطلب الملف بنفس طريقة متصفح بيدعم Brotli، وواحد بيدعم gzip بس، وواحد مبيدعمش ضغط خالص. بعدها بيفك الضغط ويقارن بالملف الأصلي بايت ببايت. لو أي حاجة اختلفت، بيرفع `.htaccess` من غير الضغط (البرنامج يفضل شغال) والنشر يطلع أحمر.
- **شاشة التحميل «العين بتفتح»:** اللوجو بيتكشف ناحية المنقار على حسب نسبة التحميل الحقيقية، والخط الأحمر اللي في اللوجو هو شريط التقدّم، وتحته النسبة بالعربي. بعد التحميل بيظهر «بنجهّز الأدوات…»، ولما البرنامج يشتغل العين بتفتح وتظهر «جاهز» والشاشة بتختفي تدريجيًا.
- **إزاي بتتحسب النسبة:** الصفحة بتعدّ البايتات وهي بتوصل، وبتقارنها بحجم الملف اللي `build.sh` بيكتبه في الصفحة وقت البناء.
- **الكود:** كله في `LOADER_CSS` و`LOADER_SCRIPT` جوه `rebrand.py`، وهو CSS وSVG جوه الصفحة نفسها، يعني من غير أي ملف زيادة.
- **حالات خاصة:** لو التحميل وقف 15 ثانية بتظهر رسالة «اعمل Reload». واللي مفعّل تقليل الحركة في جهازه بيشوف شريط التقدّم بس.

## اللي لازم يفضل (شرط الترخيص)

- نسخة Windows النظيفة لا تعرض ملفات ترخيص منفصلة بجانب `HORIX.exe`. نص MIT وإشعارات وتراخيص المكونات المدمجة محفوظة داخل البرنامج نفسه، ويمكن قراءتها من **Help > About HORIX > Open-source licences**.
- `README.txt` هو الملف النصي الوحيد في حزمة Windows، وفيه التشغيل السريع وروابط صابر جروب.
- نسخة macOS ما زالت تحفظ نصوص الترخيص داخل Resources الخاصة بالتطبيق.
- شاشة About تذكر بوضوح أن البرنامج مبني على مكونات مفتوحة المصدر، من غير استخدام اسم المشروع الأصلي كعلامة تجارية أو دعاية.

الأسماء الداخلية في الكود (زي `photocraft_engine`) مش بتوصل للمستخدم، وتغييرها هيكسر التحديثات، فسيبناها زي ما هي.

## البناء

المتطلبات: Rust ≥ 1.95، وtarget الـwasm، و`trunk`، و`zip`.

```sh
rustup target add wasm32-unknown-unknown
cargo install trunk --locked
apps/sg-ps/build.sh                # يطلع deploy/sg-ps/sg-ps-<version>-hostinger.zip
```

أول build بياخد وقت طويل (حوالي ساعة على 4 cores)، والـbuilds اللي بعده أسرع.

## قائمة الانتظار والتجربة المجانية

في شاشة البداية فيه قسم «قريبًا: بدائل After Effects و Premiere و Illustrator و Lightroom» وزرار **احجز تجربتك المُبكرة**، وبيفتح فورم عربي فيه:
- الاسم.
- رقم الواتساب.
- «مهتم تتعلم إيه؟»: Graphic Design 101، وAdvertising Mastery، وAI 101 وMastery و100x Creatives، أو «لسه مش متأكد».
- الموافقة على التواصل.

الفورم بيبعت البيانات لـ`hosting/waitlist.php`، واللي بيحفظها سطر سطر في:

**`domains/sabergroupacademy.com/sgps-data/leads.csv`** (فولدر فوق `public_html` بمستوى)

(File Manager في hPanel). الملف بيفتح في Excel والعربي ظاهر صح. الـleads اللي اتسجلت قبل النقل لسه في `public_html/sgps-data/leads.csv` على `engsaber.space`.

- الفولدر ده برّه `public_html`، فالنشر مش بيلمسه، ومحدش يقدر يفتحه من المتصفح. وعليه `.htaccess` بيمنع فتحه برضه.
- فيه حد 5 طلبات في الساعة لكل جهاز ضد السبام.
- بعد الإرسال بيظهر زرار واتساب، ومعاه رسالة جاهزة فيها الاسم والمنتج.

### تنبيه تليجرام لكل lead (n8n)

`n8n/sgps-leads-telegram.json` هو workflow فيه خطوتين: Webhook، وبعده رسالة تليجرام فيها الاسم والرقم والمنتج والاهتمامات ورابط واتساب. الإعداد مرة واحدة:
1. **بوت تليجرام:** في تليجرام كلّم **@BotFather** واكتب `/newbot` واخد الـtoken. وكلّم **@userinfobot** عشان تعرف رقم الـchat id بتاعك (أو بتاع جروب الفريق، بعد ما تضيف البوت للجروب).
2. **الـworkflow:** في n8n اعمل Import from file للـworkflow (النسخة اللي فيها المسار السري). في خطوة Telegram اعمل Credential جديد بالـtoken، وحط الـchat id مكان `PUT_YOUR_TELEGRAM_CHAT_ID`، وبعدين فعّله (Active).
3. **الرابط في GitHub:** في الريبو افتح Settings ← Secrets and variables ← Actions، واعمل secret اسمه `SGPS_LEAD_WEBHOOK`. القيمة هي **Production URL** بتاع الـWebhook (`https://n8n.engsaber.space/webhook/sgps-lead-…`).
4. **التشغيل:** شغّل Deploy HORIX. النشر بيكتب الرابط في `sgps-config.php` على السيرفر، والمتصفح ممنوع يفتحه.

الـlead بيتحفظ في `leads.csv` الأول، فلو n8n أو تليجرام وقعوا مفيش بيانات بتضيع.

## نسخ الديسكتوب (ويندوز وماك)

`.github/workflows/desktop-sg-ps.yml` بيبني البرنامج على أجهزة ويندوز وماك حقيقية عند GitHub، وبينزّل الملفين في صفحة **Releases** في الريبو:
- **ويندوز:** `HORIX-<version>-windows-x64-portable.zip`. الحزمة النظيفة فيها `HORIX.exe` و`README.txt` فقط. فكّها وشغّل البرنامج من غير تثبيت؛ وضع Portable مدمج في النسخة، وبيعمل `HORIX-Data` جنب البرنامج تلقائيًا لحفظ الإعدادات.
- **ماك:** `HORIX-<version>-macos-universal.zip` فيه `HORIX.app`، وبيشتغل على أجهزة Apple Silicon وIntel. اسحبه لـApplications.

**تشغيله:** من Actions ← Desktop HORIX ← Run workflow، أو اعمل push لـtag بالشكل `desktop-v0.3.0`. البناء بياخد من 20 لـ40 دقيقة. وتقدر تبني من جهاز ويندوز أو ماك بـ`apps/sg-ps/desktop/package.sh windows|macos`.

**التوقيع:** النسخ دي **مش موقّعة**:
- **ويندوز:** أول تشغيل بيظهر «Windows protected your PC». اضغط More info ← Run anyway.
- **ماك:** أول تشغيل اعمل كليك يمين على البرنامج ← Open ← Open.

عشان التحذيرات دي تختفي، محتاج شهادة توقيع لويندوز، وحساب Apple Developer للماك (99 دولار في السنة) عشان التوقيع والـnotarization.

## النشر التلقائي (GitHub Actions)

أي push على **الفرع الافتراضي** للريبو بيغيّر حاجة في `apps/sg-ps/` أو `archive/photocraft/` بيشغّل `.github/workflows/deploy-sg-ps.yml`، والـworkflow ده:
1. بيبني البرنامج بـ`build.sh`. الـzip فيه 3 فولدرات: `horix/` (البرنامج)، و`downloads/` (صفحة التحميل)، و`redirect/` (التحويل من العنوان القديم).
2. بيرفع ملفات `horix/` و`downloads/` واحد واحد على `public_html` بتاع `sabergroupacademy.com` بـ`deploy.sh`. **مش بيفك zip فوق الموقع**، لأن نفس الفولدر فيه WordPress وصفحة الأكاديمية والـsubdomains. الرفع بيضيف ويستبدل الملفات دي بس.
3. بيستنى لحد ما https://sabergroupacademy.com/horix/ يعرض النسخة الجديدة (بيقارن `meta horix-build`).
4. بيحط ملفات التحويل على `studio.engsaber.space`، ويتأكد إن العنوان القديم بيحوّل.

أسماء ملفات البرنامج ثابتة (`sg-ps.js` و`sg-ps_bg.wasm`) من غير hash، عشان الـAPI مش بيقدر يمسح ملفات، وكل نشر بيستبدل نفس الملفات بدل ما يكدّس نسخ قديمة. و`.htaccess` بيخلّي المتصفح يتأكد من السيرفر كل مرة (304 لو الملف ما اتغيرش).

صفحة الأكاديمية (ريبو `saber-group-academy-landingpage`) فيها service worker، ولازم يسيب `/horix` و`/downloads` للشبكة (التعديل ده في `dist/sw.js` هناك).

لو أي خطوة فشلت، الـAction بيطلع أحمر، والموقع بيفضل على النسخة اللي قبلها.

**إعداد لمرة واحدة:** في GitHub افتح Settings ← Secrets and variables ← Actions ← New repository secret، واعمل secret اسمه `HOSTINGER_API_TOKEN`. قيمته مفتاح API من hPanel (صورة الحساب ← Account Information ← API ← New token)، والمفتاح محتاج صلاحية على الاستضافة.

- **تشغيل يدوي:** تبويب Actions ← Deploy HORIX ← Run workflow.
- **مدة البناء:** أول build حوالي 25 دقيقة، والـbuilds اللي بعده أسرع، لأن المكتبات اللي اتبنت بتتحفظ في cache.
- **دومين أو حساب تاني:** حط repository variables باسم `HORIX_DOMAIN` و`HORIX_OLD_DOMAIN` و`HOSTINGER_USERNAME`.
- **النشر من جهازك:** `HOSTINGER_API_TOKEN=... apps/sg-ps/deploy.sh`.

## الرفع على هوستينجر يدويًا

**متفكّش الـzip فوق `public_html` بتاع `sabergroupacademy.com`**، ولا تستخدم «Deploy static site archive» على الدومين ده، لأنهم ممكن يمسحوا WordPress وصفحة الأكاديمية. بدل كده:
1. فك `deploy/sg-ps/sg-ps-<version>-hostinger.zip` على جهازك.
2. من File Manager ارفع محتوى `horix/` جوه `public_html/horix/`، ومحتوى `downloads/` جوه `public_html/downloads/`، وخلّي `index.html` آخر ملف.

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
