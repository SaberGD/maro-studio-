# HORIX Launcher

برنامج صغير بيسطّب HORIX و Horix Vectors و Horix Light، ويفتحهم، ويحدّثهم أول ما ينزل تحديث جديد. مبني على [ArtCraft Launcher](https://github.com/storytold/craft-launcher) المفتوح المصدر (MIT OR Apache-2.0)، الإصدار **0.4.1** (commit `307efcf`)، بنفس طريقة HORIX: `rebrand.py` بيتطبّق على الكود الأصلي وقت البناء.

- نسخة الويب (صفحة بتختار للزائر ملف التحميل المناسب لجهازه): https://horix.si/launcher/
- نسخ الديسكتوب: GitHub Releases بتاج `horix-launcher-v<الإصدار>`.

## إزاي التحديثات بتوصل بسرعة

1. كل برنامج بينزل كـGitHub Release في الريبو ده، والتاج بيبدأ باسمه: `horix-v0.1.57`، و`horix-vectors-v0.1.12`، و`horix-light-v0.1.12`، و`horix-launcher-v1.0.0`. الملفات اسمها بالشكل اللي الـLauncher بيفهمه (`<id>-<version>-<os>-<arch>.<ext>`)، ومعاها `SHA256SUMS.txt`.
2. بعد أي إصدار، `.github/workflows/horix-feed.yml` بيبني ملف التحديثات `release_info.json` (بـ`feed/make_feed.py`) وبيرفعه على https://horix.si/launcher/release_info.json. وبيتكرر كل 6 ساعات.
3. الـLauncher بيقرا الملف ده أول ما يفتح وعلى فترات. لو لقى إصدار أحدث، بيبعت إشعار، ويحدّث البرنامج بضغطة واحدة. ولو الملف مش متاح، بيرجع لـGitHub مباشرة، ومن غير ما يخلط إصدارات البرامج ببعض (بيفرّق بينهم بأول التاج).

## رسائل للمستخدمين

`feed/notices.json` فيه `announcements` (أخبار) و`alerts` (تنبيهات مهمة). أي رسالة تتضاف هنا بتظهر جوه الـLauncher عند كل الناس مع التحديث الجاي للملف:

```json
{"announcements": [{"id": "horix-v0.2", "title": "HORIX v0.2 نزل", "body": "19 أداة جديدة وتحديد بالذكاء الاصطناعي", "maybe_web_link": "https://horix.live", "created_at": "2026-10-20T10:00:00Z"}], "alerts": []}
```

## الإصدارات

| البرنامج | رقم الإصدار | بيتنشر لما |
|---|---|---|
| HORIX Launcher | `apps/horix-launcher/VERSION` (1.0.1) | يتغير الرقم ده (`horix-launcher.yml`) |
| HORIX | `apps/sg-ps/VERSION` + رقم البناء | يشتغل `desktop-sg-ps.yml` |
| Horix Vectors / Light | `apps/horix-<app>/VERSION` + رقم البناء | يتغير الرقم أو يشتغل `desktop-horix-family.yml` |

## اللي اتغيّر عن الأصل

- الاسم "HORIX Launcher"، والبرنامج `horix-launcher.exe`، وفولدر البيانات، وأيقونة الصقر بشارة فيها 4 مربعات، وشعار HORIX العريض، وألوان HORIX.
- الكتالوج: برامج HORIX الـ3 بدل برامج ArtCraft الـ13.
- ملف التحديثات بتاعنا بدل ArtCraft API.
- الروابط: فيسبوك الأكاديمية، وموقعها، وواتساب.

## البناء

```sh
apps/horix-launcher/build.sh                    # نسخة الويب: deploy/horix-launcher/horix-launcher-<v>-web.zip
apps/horix-launcher/desktop/package.sh windows  # على ويندوز
apps/horix-launcher/desktop/package.sh macos    # على ماك
```

## لسه

- النسخ مش موقّعة (Windows SmartScreen و Gatekeeper في ماك بيحذّروا أول مرة).
- مفيش نسخة Linux لسه، ومفيش MSI لويندوز (Portable بس).
- صفحات التفاصيل والصور جوه الـLauncher لسه فاضية لبرامجنا.
