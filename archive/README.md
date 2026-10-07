# Archive

نسخ احتياطية من الكود المصدري للبرامج المفتوحة المصدر اللي بنعتمد عليها، علشان لو اتمسحت من GitHub يفضل عندنا اللي نقدر نبني منه.

| الملف | المصدر | SHA-256 |
|---|---|---|
| `photocraft/photocraft-source-0.3.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.3.0` | `ca94413309e5f288662994f8a87e43a66030397bcc16de30bc369bd1813e9a0d` |

البناء من الكود (محتاج Rust ≥ 1.95):

```sh
tar -xzf photocraft-source-0.3.0.tar.gz && cd photocraft-0.3.0
rustup target add wasm32-unknown-unknown && cargo install trunk --locked
packaging/web/package.sh     # يطلع dist/photocraft-web-0.3.0.zip
```

الترخيص: MIT OR Apache-2.0 (الملفات جوه الأرشيف). علامات ArtCraft في `docs/brand/` مش مفتوحة المصدر.
