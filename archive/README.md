# Archive

نسخ احتياطية من الكود المصدري للبرامج المفتوحة المصدر اللي بنعتمد عليها، علشان لو اتمسحت من GitHub يفضل عندنا اللي نقدر نبني منه.

| الملف | المصدر | SHA-256 |
|---|---|---|
| `photocraft/photocraft-source-0.3.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.3.0` | `ca94413309e5f288662994f8a87e43a66030397bcc16de30bc369bd1813e9a0d` |
| `photocraft/photocraft-source-0.9.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.9.0`، أساس HORIX v0.2 | `0d1c431cdb4faa86b6d4faab49adc382211993296ff27fd42fe76c676695685f` |
| `photocraft/photocraft-source-0.23.1.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.23.1` (commit `45066c48292e92229ada3459a83453439514c83d`)، أساس HORIX | `a0d3293915be130d81ebd383b87eda5eadc13aafc4991d78422ded710a287e9b` |
| `photocraft/craft-i18n-e02939ef-ar.tar.gz` | الترجمة العربية فقط من [storytold/craft-i18n](https://github.com/storytold/craft-i18n) عند commit `e02939ef` (نقلها PhotoCraft 0.21 لمستودع منفصل)، بتتضمّن في HORIX بدل باقي اللغات (HORIX عربي وإنجليزي بس) | `1d780c7532cc04486d1baf0b8404a2ecc6a01d92a1100a4f4db0c0cbbbe43f58` |
| `vectorcraft/vectorcraft-source-0.24.1.tar.gz` | `git archive` لـ[storytold/vectorcraft](https://github.com/storytold/vectorcraft) عند tag `v0.24.1` (commit `f4922aa7ac99a4f6d56fc68a83a44945207ec610`)، أساس Horix Vectors | `00cef492f340aa229ea50b6f1bc770d759c063a585add5a46c0751ad3b1058c9` |
| `lightcraft/lightcraft-source-0.21.1.tar.gz` | `git archive` لـ[storytold/lightcraft](https://github.com/storytold/lightcraft) عند tag `v0.21.1` (commit `361e3bc0c838ffe5e5cea515b1fe5b71951989c6`)، أساس Horix Light | `11fb21660f07b42c85263f19aa58b050da2a1ace6870f3a71a406858a49634d8` |
| `designcraft/designcraft-source-0.20.1.tar.gz` | `git archive` لـ[storytold/designcraft](https://github.com/storytold/designcraft) عند tag `v0.20.1` (commit `33a467872268c98536231491865b4011b0275b17`)، أساس Horix Layout | `1ddc7235152828d5cc4e9a2cbd393d7f2f72f737e4cb501f5e8817247bf266a8` |

البناء من الكود (محتاج Rust ≥ 1.95):

```sh
tar -xzf photocraft-source-0.3.0.tar.gz && cd photocraft-0.3.0
rustup target add wasm32-unknown-unknown && cargo install trunk --locked
packaging/web/package.sh     # يطلع dist/photocraft-web-0.3.0.zip
```

الترخيص: MIT OR Apache-2.0 (الملفات جوه الأرشيف). علامات ArtCraft في `docs/brand/` مش مفتوحة المصدر.

النسخ القديمة من VectorCraft (0.11.0 و0.16.0) وLightCraft (0.8.0) وPhotoCraft 0.15.1 وDesignCraft 0.12.0 اتشالت من الفولدر بعد التحديث، ولسه موجودة في تاريخ git (`git log -- archive/`) لو احتجناها.
