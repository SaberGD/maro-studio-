# رفع PhotoCraft على هوستينجر

النسخة: **PhotoCraft Web v0.3.0**، وهي النسخة الرسمية من صفحة الإصدارات على GitHub (`photocraft-web-0.3.0.zip`، SHA-256 `1825b2beb2b84331124f6cb78e5eb6eb9584612e8ad6a4e817b7f27cb3f93d06`) من غير أي تعديل في البرنامج.

| الملف | إيه هو |
|---|---|
| `photocraft-web-0.3.0-hostinger.zip` | **الملف اللي هترفعه.** فيه البرنامج + `.htaccess` مظبوط لهوستينجر + ملفات الترخيص (SHA-256 `20efbfe358a30fd10728bf9398de6cf2c2e00a09c121a451baf9c4a2c9b73e51`) |
| `.htaccess` | نفس الموجود جوه الـzip، لو حبيت تعدله |
| `../../archive/photocraft/photocraft-source-0.3.0.tar.gz` | نسخة احتياطية من الكود المصدري لنفس الإصدار |

البرنامج **ملفات ثابتة بس**: مفيش قاعدة بيانات ولا PHP ولا Node. وجربناه: مبيكلمش أي سيرفر غير السيرفر اللي متركب عليه.

## الخطوات

### 1. اعمل الـsubdomain
hPanel ← **Websites** ← اختار الدومين ← **Domains › Subdomains** ← اكتب الاسم (مثلًا `studio`) ← **Create**.
هوستينجر هيعمل فولدر للـsubdomain، غالبًا `public_html/studio`.

### 2. فعّل SSL
hPanel ← **Security › SSL** ← اختار الـsubdomain ← **Install** (مجاني). استنى لحد ما يبقى Active.
مهم: البرنامج بيستخدم WebGPU، ودي مبتشتغلش غير على `https`.

### 3. ارفع الملفات
hPanel ← **Files › File Manager** ← افتح فولدر الـsubdomain:
1. امسح أي ملفات افتراضية فيه (زي `default.php`).
2. **Upload** ← ارفع `photocraft-web-0.3.0-hostinger.zip`.
3. كليك يمين على الـzip ← **Extract** ← في نفس الفولدر (`.`).
4. اتأكد إن `index.html` و`.htaccess` موجودين **مباشرة** في فولدر الـsubdomain، مش جوه فولدر فرعي.
5. امسح الـzip بعد الفك.

> لو `.htaccess` مش ظاهر: File Manager ← Settings ← Show hidden files.

### 4. جرّب
افتح `https://studio.<الدومين>/`. أول مرة هياخد ثواني لتحميل البرنامج (حوالي 8 ميجا مضغوط)، والمرات اللي بعدها هيفتح من الكاش.

## لو حصلت مشكلة

| العَرَض | الحل |
|---|---|
| فاضل على «Loading PhotoCraft…» | DevTools ← Network: لو ملف `.wasm` نوعه مش `application/wasm`، اتأكد إن `.htaccess` موجود جنب `index.html` |
| شاشة سودا أو مشاكل رسم | افتح الرابط بـ`?webgl`، ولو لسه فيه مشكلة جرّب `?cpu` |
| بطء في التحميل | اتأكد إن الضغط شغال: في Network لازم يظهر `content-encoding: gzip` أو `br` على ملف الـwasm. ولو مش ظاهر فعّل Cloudflare من hPanel |
| 403 أو صفحة هوستينجر الافتراضية | الملفات اترفعت في فولدر غلط أو جوه فولدر فرعي |

## ملاحظات الترخيص

- PhotoCraft ترخيصه MIT OR Apache-2.0، يعني نقدر نستضيفه ونستخدمه تجاريًا. ملفات `LICENSE-MIT` و`LICENSE-APACHE` و`NOTICE` لازم تفضل مع البرنامج على السيرفر.
- إحنا بنستضيف النسخة **الرسمية من غير تعديل**، فشعار ArtCraft وروابطهم اللي جوه البرنامج طبيعية ومسموحة.
- **لو عدّلنا البرنامج بعدين** (لوجو صابر، ربط مارو...) لازم نشيل علامات ArtCraft من النسخة المعدلة، وميبقاش فيه أي إيحاء إن ArtCraft بتدعم منتجنا. التفاصيل في [`docs/licensing.md`](../../docs/licensing.md).

## التحديث لإصدار جديد

1. حمّل `photocraft-web-<version>.zip` من صفحة الإصدارات: https://github.com/storytold/photocraft/releases
2. جرّبه الأول على subdomain تجريبي.
3. ارفعه بنفس الخطوات وحط معاه نفس `.htaccess` و`NOTICE`.
4. احفظ الـzip الجديد والكود المصدري بتاعه في الريبو ده زي الإصدار الحالي.
