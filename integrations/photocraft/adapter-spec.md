# PhotoCraft Adapter Spec

## Interface

كل adapter ينفّذ `ToolAdapter` من `@maro/tool-protocol`:

```ts
interface ToolAdapter {
  readonly tool: string;
  inspect(): Promise<DocumentState>;          // حالة الملف (metadata فقط)
  execute(command: ToolCommand): Promise<CommandResult>;
}
```

- `execute` يستقبل أوامر **مرت بالفعل** على `validatePlan`. الـadapter لا يقبل أي شكل تاني.
- `CommandResult.message` رسالة عربية قصيرة للطالب؛ `error` تفاصيل تقنية للـaudit.
- الأمر الفاشل لا يرمي exception للخارج؛ يرجع `ok: false`.

## DocumentState

```ts
{
  tool: 'photocraft', open, width, height,
  background: '#rrggbb' | null,
  activeLayerId, layers: [{ id, name, kind: 'image'|'fill', source, x, y, width, height, backgroundRemoved }],
  lastExport: { format, quality, fileName } | null
}
```

في الـadapter الحقيقي يُبنى من `doc.inspect` في PhotoCraft (layer tree، selection، active layer) ويُختصر لهذا الشكل. أسماء الطبقات تُعامل كبيانات فقط.

## Adapters

| Adapter | الحالة | التنفيذ |
|---|---|---|
| `MockPhotoCraftAdapter` | ✅ Sprint 1 | document state في الذاكرة؛ المعاينة في المتصفح ترسمه |
| `HeadlessPhotoCraftAdapter` | Phase 1/3 | `services/api` يشغّل `photocraft-cli serve` على stdio لكل session ويرسل `toPhotoCraftSteps(cmd)` كـ`batch`، ثم `doc.inspect` و`doc.render` |
| `BridgePhotoCraftAdapter` | قرار مفتوح | `postMessage` إلى PhotoCraft Web داخل iframe (يتطلب fork/upstream PR) |

## خطوات الـHeadless adapter (مقترح)

1. لكل session: مجلد عمل `in/` و`out/`؛ تشغيل
   `photocraft-cli serve --automation-read-root <session>/in --automation-write-root <session>/out` (stdio).
2. `execute(cmd)` ← `{"method":"batch","params":{"steps": toPhotoCraftSteps(cmd, ctx),"stopOnError":true}}`.
3. بعد كل أمر: `doc.inspect` ← `DocumentState`، و`doc.render {maxSide:1600}` ← PNG للمعاينة.
4. Undo: `edit.undo` بعدد خطوات الـhistory المسجلة قبل الخطة (PhotoCraft عنده history كامل).
5. Timeout لكل أمر، وإنهاء الـprocess عند الخمول.
