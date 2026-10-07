import type { RawCommand } from '@maro/tool-protocol';
import type { ChatRequest } from '@maro/shared';
import type { Planner, PlannerOutput } from './planner.ts';

/** Arabic-Indic and Persian digits → ASCII, and common letter variants unified. */
export function normalizeArabic(text: string): string {
  return text
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06f0))
    .replace(/[ً-ْـ]/g, '') // tashkeel, tatweel
    .replace(/[أإآ]/g, 'ا')
    .replace(/ة/g, 'ه')
    .replace(/ى/g, 'ي')
    .toLowerCase();
}

const COLORS: [RegExp, string, string][] = [
  [/بيج|beige/, '#F4E8D8', 'بيج'],
  [/ابيض|بيضا|white/, '#FFFFFF', 'أبيض'],
  [/اسود|سودا|black/, '#000000', 'أسود'],
  [/رمادي|gr[ae]y/, '#BDBDBD', 'رمادي'],
  [/ازرق|زرقا|blue/, '#2F6FDE', 'أزرق'],
  [/احمر|حمرا|red/, '#D64545', 'أحمر'],
  [/اخضر|خضرا|green/, '#3FA34D', 'أخضر'],
  [/وردي|بينك|pink/, '#F4B6C2', 'وردي'],
];

const PRESETS: [RegExp, number, number, string][] = [
  [/ستوري|story|ريلز|reels/, 1080, 1920, 'ستوري'],
  [/مربع|square/, 1080, 1080, 'مربع'],
  [/بوست|post/, 1080, 1350, 'بوست'],
];

/**
 * Offline planner for Sprint 1: recognises the MVP actions in Arabic (Egyptian and MSA)
 * or English requests. It proves the plan → validate → execute loop without an LLM.
 */
export class RulesPlanner implements Planner {
  readonly name = 'rules';

  async plan(req: ChatRequest): Promise<PlannerOutput> {
    const text = normalizeArabic(req.message);
    const doc = req.document;
    const commands: RawCommand[] = [];
    const said: string[] = [];
    const cmd = (action: string, params: Record<string, unknown> = {}) =>
      commands.push({ tool: 'photocraft', action, params });

    // 1. Import: needed when nothing is open yet and the student uploaded something.
    const latestUpload = req.uploads.at(-1);
    if (!doc.open && latestUpload) {
      cmd('import_image', { uploadId: latestUpload.uploadId });
      said.push('هفتح الصورة اللي رفعتها');
    }
    const willBeOpen = doc.open || Boolean(latestUpload);

    // 2. Canvas size and background colour.
    const size = text.match(/(\d{2,4})\s*[x×*×]\s*(\d{2,4})/) ?? text.match(/(\d{2,4})\s*(?:في|ف)\s*(\d{2,4})/);
    const preset = PRESETS.find(([re]) => re.test(text));
    const color = COLORS.find(([re]) => re.test(text));
    let width: number | undefined;
    let height: number | undefined;
    if (size) {
      width = Number(size[1]);
      height = Number(size[2]);
    } else if (preset) {
      width = preset[1];
      height = preset[2];
    }
    if (width === undefined && color && doc.open) {
      width = doc.width;
      height = doc.height;
    }
    if (width !== undefined && height !== undefined) {
      cmd('resize_canvas', { width, height, anchor: 'center', ...(color ? { background: color[1] } : {}) });
      said.push(
        `هخلي المقاس ${width}×${height}${preset && !size ? ` (${preset[3]})` : ''}${color ? ` بخلفية ${color[2]}` : ''}`,
      );
    }

    // 3. Background removal.
    if (/(شيل|احذف|امسح|ازل|ازاله|شيلي|نضف).{0,12}خلفي|remove\s+(the\s+)?background/.test(text)) {
      cmd('remove_background');
      said.push('هشيل خلفية المنتج');
    }

    // 4. Position.
    if (/(في|ف|على|علي)\s*(ال)?(نص|منتصف|وسط)|سنتر|center|توسيط|وسط/.test(text)) {
      cmd('position_layer', { align: 'center' });
      said.push('هحط العنصر في نص التصميم');
    }

    // 5. Export (always asks for approval, by policy).
    if (/صدر|تصدير|export|نزل|حمل|download/.test(text)) {
      const format = /jpe?g|جي ?بي ?جي/.test(text) ? 'jpg' : 'png';
      cmd('export_image', { format });
      said.push(`وبعدها هجهز التصدير ${format.toUpperCase()} وأستنى موافقتك`);
    }

    if (req.mode === 'explain') {
      return { reply: this.explain(said), commands: [] };
    }

    if (commands.length === 0 || (commands.length === 1 && commands[0]?.action === 'import_image' && said.length === 1)) {
      return {
        reply: willBeOpen
          ? 'أنا جاهز! أقدر حاليًا: أغير مقاس مساحة العمل (مثلًا 1080×1350 أو "بوست"/"ستوري")، أشيل الخلفية، أحط العنصر في النص، وأصدّر الصورة. قولي عايز إيه بالظبط.'
          : 'ارفع صورة الأول من زرار "رفع صورة"، وبعدين قولي عايز تعمل فيها إيه.',
        commands: commands,
      };
    }

    const missingDoc = !willBeOpen;
    return {
      reply: missingDoc
        ? 'محتاج صورة مفتوحة الأول. ارفع صورة وبعدين ابعتلي الطلب تاني.'
        : `تمام! ${said.join('، ')}. راجع الخطة تحت واضغط "تنفيذ".`,
      commands: missingDoc ? [] : commands,
    };
  }

  private explain(said: string[]): string {
    if (said.length === 0) {
      return 'في وضع "اشرح لي" بشرحلك الخطوات من غير ما أنفذها. اكتب طلبك (مثلًا: اعمل بوست 1080×1350 وشيل الخلفية).';
    }
    const steps = said.map((s, i) => `${i + 1}. ${s.replace(/^و?بعدها /, '')}`).join('\n');
    return `دي الخطوات اللي هتعملها بنفسك في PhotoCraft:\n${steps}\nجرّبها، ولو حبيت أنفذها عنك حوّل لوضع "نفّذ".`;
  }
}
