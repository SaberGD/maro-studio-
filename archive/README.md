# Archive

نسخ احتياطية من الكود المصدري للبرامج المفتوحة المصدر اللي بنعتمد عليها، علشان لو اتمسحت من GitHub يفضل عندنا اللي نقدر نبني منه.

| الملف | المصدر | SHA-256 |
|---|---|---|
| `photocraft/photocraft-source-0.3.0.tar.gz` | `git archive` لـ[storytold/photocraft](https://github.com/storytold/photocraft) عند tag `v0.3.0` | `ca94413309e5f288662994f8a87e43a66030397bcc16de30bc369bd1813e9a0d` |
| `vectorcraft/vectorcraft-source-0.11.0.tar.gz` | `git archive` لـ[storytold/vectorcraft](https://github.com/storytold/vectorcraft) عند commit `06b33b0d2d49e1d36b8f864e56fd89790a6a804a` (0.11.0)، أساس Horix Vectors | `99b22b46377add78ea666aa1b004173fb812796c5037a42a515a5234b90bcba7` |
| `lightcraft/lightcraft-source-0.8.0.tar.gz` | `git archive` لـ[storytold/lightcraft](https://github.com/storytold/lightcraft) عند commit `f34c7a8a89e0d1bade0a6889185f40acecc84a9f` (0.8.0)، أساس Horix Light | `5da130ccc5b5f4c45ac9c0e27e0809c7fef2adde7eecb10fdd833fe7e16ad717` |

البناء من الكود (محتاج Rust ≥ 1.95):

```sh
tar -xzf photocraft-source-0.3.0.tar.gz && cd photocraft-0.3.0
rustup target add wasm32-unknown-unknown && cargo install trunk --locked
packaging/web/package.sh     # يطلع dist/photocraft-web-0.3.0.zip
```

الترخيص: MIT OR Apache-2.0 (الملفات جوه الأرشيف). علامات ArtCraft في `docs/brand/` مش مفتوحة المصدر.
