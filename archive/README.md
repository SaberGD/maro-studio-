# Archive

نسخ احتياطية من الكود المصدري للبرامج المفتوحة المصدر اللي بنعتمد عليها، علشان لو اتمسحت من GitHub يفضل عندنا اللي نقدر نبني منه.

| الملف | المصدر | SHA-256 |
|---|---|---|
| `photocraft/photocraft-source-0.3.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.3.0` | `ca94413309e5f288662994f8a87e43a66030397bcc16de30bc369bd1813e9a0d` |
| `photocraft/photocraft-source-0.9.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.9.0`، أساس HORIX v0.2 | `0d1c431cdb4faa86b6d4faab49adc382211993296ff27fd42fe76c676695685f` |
| `photocraft/photocraft-source-0.20.1.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.20.1` (commit `327c4cc82e737a3e0af7c147a477126d77525495`)، أساس HORIX v0.6 وPixel في HORIX One | `0142685a41ab707fc1b430c194c4c82f0c1c351b00e02bd24ce756ab7d97e592` |
| `vectorcraft/vectorcraft-source-0.21.0.tar.gz` | `git archive` لـ[storytold/vectorcraft](https://github.com/storytold/vectorcraft) عند tag `v0.21.0` (commit `11862f61198c8f62c0b22b6c9a331cc5950ac98d`)، أساس Horix Vectors وVector في HORIX One | `05f9400bf4935efb1bddfaf838bf8985109fca052fce382f199a09e85a9b0237` |
| `lightcraft/lightcraft-source-0.13.0.tar.gz` | `git archive` لـ[storytold/lightcraft](https://github.com/storytold/lightcraft) عند tag `v0.13.0` (commit `23e181283cb448205d865e8cd288b56afe987986`)، أساس Horix Light | `ce9bd1a81669c1ddf23ed7108948ded8e43614eb7aa4b97a3edf75c9b4102df6` |
| `designcraft/designcraft-source-0.17.0.tar.gz` | `git archive` لـ[storytold/designcraft](https://github.com/storytold/designcraft) عند tag `v0.17.0` (commit `e79d682e02dc66f14370958b193bfa46072b2f41`)، أساس Horix Layout وLayout في HORIX One | `a05aad8696bd8e5f57f45ce33dd8d1a073a023565aedfd5449eac27ccaa72458` |

البناء من الكود (محتاج Rust ≥ 1.95):

```sh
tar -xzf photocraft-source-0.3.0.tar.gz && cd photocraft-0.3.0
rustup target add wasm32-unknown-unknown && cargo install trunk --locked
packaging/web/package.sh     # يطلع dist/photocraft-web-0.3.0.zip
```

الترخيص: MIT OR Apache-2.0 (الملفات جوه الأرشيف). علامات ArtCraft في `docs/brand/` مش مفتوحة المصدر.

النسخ القديمة من VectorCraft (0.11.0 و0.16.0) وLightCraft (0.8.0) وPhotoCraft 0.15.1 وDesignCraft 0.12.0 اتشالت من الفولدر بعد التحديث، ولسه موجودة في تاريخ git (`git log -- archive/`) لو احتجناها.
