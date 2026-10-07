# PhotoCraft Integration

[storytold/photocraft](https://github.com/storytold/photocraft): محرر صور مفتوح المصدر مكتوب بـRust (MIT OR Apache-2.0)، يعمل كتطبيق desktop وكـWebAssembly في المتصفح. كل فعل فيه command من registry واحد، متاح من:

- `photocraft-cli run/batch`: تنفيذ headless.
- `photocraft-cli serve`: JSON-lines server (stdio أو loopback TCP) — **الأنسب لمارو**.
- `photocraft-cli mcp`: MCP server (headless، أو bridge لتطبيق desktop شغال).
- `photocraft --control`: control channel للتطبيق الـdesktop.

## ما اكتشفناه في Phase 0 (commit `e70deec`)

1. **PhotoCraft Web لا يوفر JS API.** `apps/photocraft-web` يشغّل نفس الـegui UI على canvas؛ مفيش `wasm_bindgen` exports ولا `postMessage` handler ولا control server (المتصفح لا يفتح sockets). يعني: نقدر نعرضه في iframe، لكن **لا نقدر نتحكم فيه برمجيًا من Maro Studio بدون تعديل**.
2. **التحكم البرمجي متاح headless** عبر `photocraft-cli serve`/`mcp` مع صلاحيات ملفات محصورة بـ`--automation-read-root` و`--automation-write-root`. أوامر `file.*` اللي فيها paths يرفضها PhotoCraft نفسه في وضع الـautomation.
3. **`layer.removeBackground` مش engine command** (اختصار في الـUI). البديل: `select.subject` + `layer.layerMask.revealSelection`.
4. الـwasm release حوالي 18.8MB (7.8MB gzip)، ويحتاج WebGPU أو WebGL2.

القرار المقترح والبدائل في [`docs/architecture.md`](../../docs/architecture.md#لماذا-التنفيذ-في-المتصفح-في-sprint-1).

## تشغيل PhotoCraft Web محليًا

المتطلبات: Rust ≥ 1.95 (rustup)، وtarget الـwasm، و[trunk](https://trunkrs.dev).

```sh
# خارج ريبو maro-studio (أو في vendor/ المتجاهل في git)
git clone https://github.com/storytold/photocraft
cd photocraft/apps/photocraft-web
rustup target add wasm32-unknown-unknown
cargo install trunk --locked
trunk serve --release            # http://127.0.0.1:8765
# أو: trunk build --release  ← ../../dist/web وتقدمه بأي static server
```

ثم في Maro Studio:

```sh
echo 'VITE_PHOTOCRAFT_URL=http://127.0.0.1:8765/' > apps/web/.env.local
npm run dev
```

واختر تبويب **PhotoCraft Web** في مساحة العمل. (الـCSP في `apps/web/index.html` يسمح بـiframe من `localhost:8765` و`127.0.0.1:8765` فقط.)

ملاحظات: أول build release ياخد وقت طويل (LTO كامل). `?webgl` في الرابط يجبر WebGL2، و`?cpu` يجبر الـCPU canvas لو الـGPU عامل مشاكل.

## تشغيل الـheadless server (للـadapter الحقيقي)

```sh
cargo build --release -p photocraft-cli
printf '%s\n' \
  '{"id":1,"method":"doc.open","params":{"path":"product.png"}}' \
  '{"id":2,"method":"batch","params":{"steps":[{"command":"image.canvasSize","params":{"width":1080,"height":1350,"anchor":"center","extensionColor":"#F4E8D8"}}]}}' \
  '{"id":3,"method":"doc.save","params":{"path":"out.png"}}' |
  ./target/release/photocraft-cli serve --automation-read-root ./work --automation-write-root ./work
```

## ملفات هذا المجلد

- [`adapter-spec.md`](adapter-spec.md): الـinterface وأنواع الـadapters وخطة الـheadless adapter.
- [`command-map.md`](command-map.md): ترجمة كل Maro action لأوامر PhotoCraft، وما يحتاج تحقق.
