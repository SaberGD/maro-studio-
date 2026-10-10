# HORIX

**HORIX** (اسمه القديم SG - PS) هو محرر الصور بتاع أكاديمية صابر جروب: *The Visionary AI Editor by Saber Group*. شغال على https://studio.engsaber.space/

الهوية البصرية الرسمية (الشعار، الألوان، قواعد الاستخدام) في [`brand/`](brand/HORIX-Brand-Guide.md). الأسماء الداخلية (فولدر `apps/sg-ps`، وملفات `sg-ps-<hash>.js`، ومفاتيح `sgps.*`، والـsecrets) فضلت زي ما هي عشان النشر وإعدادات المستخدمين ما يتكسروش.

البرنامج مبني على محرر صور مفتوح المصدر بترخيص MIT. إحنا مش بنعدّل الكود الأصلي بإيدينا، لكن بنطبّق عليه سكريبت إعادة التسمية (`rebrand.py`) وقت البناء. ده بيخلّي التحديث لأي إصدار جديد مجرد تشغيل السكريبت تاني.

## اللي اتغيّر

| الجزء | قبل | بعد |
|---|---|---|
| اسم البرنامج (العنوان، شاشة البداية، About، القوايم، الترجمات، تبويب المتصفح) | الاسم الأصلي | `HORIX` |
| اللوجو | أيقونة البرنامج الأصلي | صقر HORIX: اللوجو الكامل (`assets/horix-lockup.svg`) على شاشة البداية وشاشة التحميل، والصقر لوحده (`assets/horix-symbol.svg`) في About، و`assets/horix-favicon.svg` في تبويب المتصفح. كلهم متولّدين من `brand/horix-master.svg` من غير أي تعديل في الرسمة |
| الثيم الافتراضي | رمادي بلون أزرق | **HORIX (Dark)**: الخلفية Horus Ink `#141314`، والبانلز Graphite `#2A2727`، والنص Falcon Ivory `#F3EFE8`، والأزرار الأساسية Horix Red `#D63C32`، والحالة النشطة (التحديد والتبويب المفتوح) Vision Amber `#EA993F` |
| خط العناوين | Inter | **Barlow Condensed ExtraBold** (`assets/fonts/`، ترخيص OFL): خط condensed grotesk تقيل زي ما دليل الهوية طالب. خط الواجهة لسه Inter |
| زرار Discord وروابط المطور الأصلي | موجودة في الشريط العلوي وشاشة البداية وHelp | اتشالت. الروابط بقت لـ `sabergroupacademy.com` و `studio.engsaber.space` |
| أسماء ملفات البرنامج على السيرفر | باسم البرنامج الأصلي | `sg-ps-<hash>.js` و `sg-ps-<hash>_bg.wasm` |

الثيمات التانية لسه موجودة في Window › Theme.

## اللي لازم يفضل (شرط الترخيص)

- **`LICENSE.txt`**: نص ترخيص MIT، ومعاه سطر حقوق المطوّر الأصلي. ترخيص MIT بيشترط إن السطر ده يفضل مع أي نسخة بنوزعها. هو ملف نصي على السيرفر، **ومش بيظهر في واجهة البرنامج**.
- **`THIRD-PARTY-NOTICES.txt`**: تراخيص الخطوط (Inter وJetBrains Mono وBarlow Condensed) والأيقونات (Lucide) وقاموس الإملاء (SCOWL) المدمجين في البرنامج.
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

## قائمة الانتظار والتجربة المجانية

في شاشة البداية، كروت **SG - AI / SG - PR / SG - AE** (زرار Notify me) وزرار **Book your free trial** بتفتح فورم عربي فيه:
- الاسم.
- رقم الواتساب.
- «مهتم تتعلم إيه؟»: Graphic Design 101، وAdvertising Mastery، وAI 101 وMastery و100x Creatives، أو «لسه مش متأكد».
- الموافقة على التواصل.

الفورم بيبعت البيانات لـ`hosting/waitlist.php`، واللي بيحفظها سطر سطر في:

**`public_html/sgps-data/leads.csv` على `engsaber.space`**

(File Manager في hPanel ← engsaber.space). الملف بيفتح في Excel والعربي ظاهر صح.

- الفولدر ده برّه فولدر HORIX، فالنشر التلقائي مش بيلمسه، وعليه `.htaccess` بيمنع فتحه من المتصفح.
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
- **ويندوز:** `HORIX-<version>-windows-x64-portable.zip`. فكّه وشغّل `HORIX.exe`، ومش محتاج تسطيب. الإعدادات بتتحفظ في فولدر `HORIX-Data` جنبه.
- **ماك:** `HORIX-<version>-macos-universal.zip` فيه `HORIX.app`، وبيشتغل على أجهزة Apple Silicon وIntel. اسحبه لـApplications.

**تشغيله:** من Actions ← Desktop HORIX ← Run workflow، أو اعمل push لـtag بالشكل `desktop-v0.3.0`. البناء بياخد من 20 لـ40 دقيقة. وتقدر تبني من جهاز ويندوز أو ماك بـ`apps/sg-ps/desktop/package.sh windows|macos`.

**التوقيع:** النسخ دي **مش موقّعة**:
- **ويندوز:** أول تشغيل بيظهر «Windows protected your PC». اضغط More info ← Run anyway.
- **ماك:** أول تشغيل اعمل كليك يمين على البرنامج ← Open ← Open.

عشان التحذيرات دي تختفي، محتاج شهادة توقيع لويندوز، وحساب Apple Developer للماك (99 دولار في السنة) عشان التوقيع والـnotarization.

## النشر التلقائي (GitHub Actions)

أي push على **الفرع الافتراضي** للريبو بيغيّر حاجة في `apps/sg-ps/` أو `archive/photocraft/` بيشغّل `.github/workflows/deploy-sg-ps.yml`، والـworkflow ده:
1. بيبني البرنامج بـ`build.sh`.
2. بيرفعه على هوستينجر بـ`deploy.sh`.
3. بيستنى لحد ما https://studio.engsaber.space يعرض النسخة الجديدة.

لو أي خطوة فشلت، الـAction بيطلع أحمر، والموقع بيفضل على النسخة اللي قبلها.

**إعداد لمرة واحدة:** في GitHub افتح Settings ← Secrets and variables ← Actions ← New repository secret، واعمل secret اسمه `HOSTINGER_API_TOKEN`. قيمته مفتاح API من hPanel (صورة الحساب ← Account Information ← API ← New token)، والمفتاح محتاج صلاحية على الاستضافة.

- **تشغيل يدوي:** تبويب Actions ← Deploy HORIX ← Run workflow.
- **مدة البناء:** أول build حوالي 25 دقيقة، والـbuilds اللي بعده أسرع، لأن المكتبات اللي اتبنت بتتحفظ في cache.
- **دومين أو حساب تاني:** حط repository variables باسم `SGPS_DOMAIN` و`HOSTINGER_USERNAME`.
- **النشر من جهازك:** `HOSTINGER_API_TOKEN=... apps/sg-ps/deploy.sh`.

## الرفع على هوستينجر يدويًا

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
