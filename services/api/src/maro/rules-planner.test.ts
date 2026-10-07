import { describe, expect, it } from 'vitest';
import { emptyDocument, validatePlan } from '@maro/tool-protocol';
import { chatRequestSchema } from '@maro/shared';
import { RulesPlanner, normalizeArabic } from './rules-planner.ts';

const planner = new RulesPlanner();
const upload = { uploadId: 'up_1', fileName: 'product.png', width: 800, height: 600 };

function req(message: string, extra: Record<string, unknown> = {}) {
  return chatRequestSchema.parse({ message, document: emptyDocument(), uploads: [upload], ...extra });
}

describe('RulesPlanner', () => {
  it('plans the reference workflow from the MVP plan', async () => {
    const out = await planner.plan(req('مارو اعملي بوست 1080x1350، شيل الخلفية، حط المنتج في النص، وخلي الخلفية بيج.'));
    const { commands, rejected } = validatePlan(out.commands);
    expect(rejected).toEqual([]);
    expect(commands.map((c) => c.action)).toEqual(['import_image', 'resize_canvas', 'remove_background', 'position_layer']);
    expect(commands[1]?.params).toMatchObject({ width: 1080, height: 1350, background: '#F4E8D8' });
  });

  it('understands Arabic-Indic digits, presets and export', async () => {
    const a = await planner.plan(req('خليها ١٠٨٠×١٠٨٠ وصدرها jpg'));
    expect(a.commands.map((c) => c.action)).toEqual(['import_image', 'resize_canvas', 'export_image']);
    expect(a.commands[2]?.params).toEqual({ format: 'jpg' });
    const b = await planner.plan(req('اعمل ستوري'));
    expect(b.commands[1]?.params).toMatchObject({ width: 1080, height: 1920 });
  });

  it('returns no commands in explain mode', async () => {
    const out = await planner.plan(req('شيل الخلفية', { mode: 'explain' }));
    expect(out.commands).toEqual([]);
    expect(out.reply).toContain('الخطوات');
  });

  it('asks for an image when nothing is open or uploaded', async () => {
    const out = await planner.plan(req('شيل الخلفية', { uploads: [] }));
    expect(out.commands).toEqual([]);
  });

  it('normalizes Arabic text', () => {
    expect(normalizeArabic('إزالة الخلفيّة ٣')).toBe('ازاله الخلفيه 3');
  });
});
