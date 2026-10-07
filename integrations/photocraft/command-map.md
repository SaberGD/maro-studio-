# Maro → PhotoCraft Command Map

المصدر: `packages/tool-protocol/src/adapters/photocraft-map.ts`. الأوامر من PhotoCraft command registry و`docs/control-protocol.md` (commit `e70deec`). خطوات `method` هي methods الـheadless server، وخطوات `command` تتنفذ عبر `engine.execute`.

| Maro action | PhotoCraft steps | الحالة |
|---|---|---|
| `import_image {uploadId}` | `doc.open {path: <read-root>/<uploadId>}` | موثّق في control protocol |
| `resize_canvas {width,height,anchor,background?}` | `image.canvasSize {width,height,anchor,extensionColor}` ثم لو فيه `background`: `layer.newFillLayer.solidColor {color}` | params من الـregistry. **verify:** الـfill layer بيتعمل فوق الطبقة النشطة؛ محتاج `layer.moveTo` تحت المنتج (الـid من `doc.inspect`) |
| `remove_background` | `select.subject` ← `layer.layerMask.revealSelection` ← `select.deselect` | `layer.removeBackground` **ليس** engine command (اختصار UI فقط)، فاستخدمنا mask غير مدمّر. **verify:** جودة Select Subject في الـheadless |
| `position_layer {align}` | `select.all` ← `layer.align.horizontalCenters` / `verticalCenters` / `*Edges` ← `select.deselect` | **verify:** المحاذاة مع selection (سلوك Photoshop) |
| `export_image {format,quality,fileName?}` | `doc.save {path: <write-root>/<name>.<ext>, format, quality}` | موثّق؛ يحتاج موافقة الطالب |

## مرشحين للمرحلة التالية

| Action مقترح | PhotoCraft |
|---|---|
| `fill_background {color}` | `layer.newFillLayer.solidColor` + `layer.moveTo` |
| `basic_adjustment` | `layer.newAdjustmentLayer.hueSaturation`، `…curves`، `…levels` |
| `add_text` | Type layer commands (`type.*`) |
| `add_shadow` | `layer.layerStyle.dropShadow` |
