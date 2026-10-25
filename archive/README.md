# Archive

نسخ احتياطية من الكود المصدري للبرامج المفتوحة المصدر اللي بنعتمد عليها، علشان لو اتمسحت من GitHub يفضل عندنا اللي نقدر نبني منه.

| الملف | المصدر | SHA-256 |
|---|---|---|
| `photocraft/photocraft-source-0.3.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.3.0` | `ca94413309e5f288662994f8a87e43a66030397bcc16de30bc369bd1813e9a0d` |
| `photocraft/photocraft-source-0.9.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.9.0`، أساس HORIX v0.2 | `0d1c431cdb4faa86b6d4faab49adc382211993296ff27fd42fe76c676695685f` |
| `photocraft/photocraft-source-0.15.1.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.15.1` (commit `60c87b9884fdae0e464614d482a3bc435cbbc578`)، أساس HORIX v0.3 | `c00833051f8e369195bfad2446d8a851315bd00527259d32ea0752f3f0bd40b1` |
| `vectorcraft/vectorcraft-source-0.16.0.tar.gz` | `git archive` لـ[storytold/vectorcraft](https://github.com/storytold/vectorcraft) عند tag `v0.16.0` (commit `10190753ef356ce8de7592626bcb99fd69db467c`)، أساس Horix Vectors | `70b4d4189198dd6855926182fbdc4c104ba55a54036ba343ee4bfb53ed74c2c5` |
| `lightcraft/lightcraft-source-0.13.0.tar.gz` | `git archive` لـ[storytold/lightcraft](https://github.com/storytold/lightcraft) عند tag `v0.13.0` (commit `23e181283cb448205d865e8cd288b56afe987986`)، أساس Horix Light | `ce9bd1a81669c1ddf23ed7108948ded8e43614eb7aa4b97a3edf75c9b4102df6` |

البناء من الكود (محتاج Rust ≥ 1.95):

```sh
tar -xzf photocraft-source-0.3.0.tar.gz && cd photocraft-0.3.0
rustup target add wasm32-unknown-unknown && cargo install trunk --locked
packaging/web/package.sh     # يطلع dist/photocraft-web-0.3.0.zip
```

الترخيص: MIT OR Apache-2.0 (الملفات جوه الأرشيف). علامات ArtCraft في `docs/brand/` مش مفتوحة المصدر.

النسخ القديمة من VectorCraft (0.11.0) وLightCraft (0.8.0) اتشالت من الفولدر بعد التحديث، ولسه موجودة في تاريخ git (`git log -- archive/`) لو احتجناها.
