import { describe, expect, it } from 'vitest';
import { validatePlan } from '../validation/validate.ts';
import { MockPhotoCraftAdapter } from './mock-photocraft.ts';
import { toPhotoCraftSteps } from './photocraft-map.ts';

const uploads = (id: string) =>
  id === 'up_1' ? { uploadId: 'up_1', fileName: 'product.png', width: 800, height: 600 } : undefined;

const plan = validatePlan([
  { tool: 'photocraft', action: 'import_image', params: { uploadId: 'up_1' } },
  { tool: 'photocraft', action: 'resize_canvas', params: { width: 1080, height: 1350, background: '#F4E8D8' } },
  { tool: 'photocraft', action: 'remove_background', params: {} },
  { tool: 'photocraft', action: 'position_layer', params: { align: 'center' } },
  { tool: 'photocraft', action: 'export_image', params: { format: 'jpg', fileName: 'post' } },
]).commands;

describe('MockPhotoCraftAdapter', () => {
  it('runs the MVP workflow end to end', async () => {
    const adapter = new MockPhotoCraftAdapter({ uploads });
    for (const cmd of plan) {
      const r = await adapter.execute(cmd);
      expect(r.ok, r.error).toBe(true);
    }
    const doc = await adapter.inspect();
    expect(doc).toMatchObject({ width: 1080, height: 1350, background: '#F4E8D8', open: true });
    expect(doc.layers[0]).toMatchObject({ x: 140, y: 375, backgroundRemoved: true });
    expect(doc.lastExport).toEqual({ format: 'jpg', quality: 90, fileName: 'post.jpg' });
  });

  it('fails cleanly without an open document', async () => {
    const adapter = new MockPhotoCraftAdapter({ uploads });
    const r = await adapter.execute(plan[3]!);
    expect(r.ok).toBe(false);
    expect(r.error).toMatch(/no active layer/);
  });
});

describe('toPhotoCraftSteps', () => {
  const ctx = { uploadPath: (id: string) => `/work/in/${id}`, exportPath: (n: string) => `/work/out/${n}` };

  it('maps commands to PhotoCraft engine command ids', () => {
    const steps = plan.flatMap((c) => toPhotoCraftSteps(c, ctx));
    expect(steps).toEqual([
      { method: 'doc.open', params: { path: '/work/in/up_1' } },
      {
        command: 'image.canvasSize',
        params: { width: 1080, height: 1350, anchor: 'center', extensionColor: '#F4E8D8' },
      },
      { command: 'layer.newFillLayer.solidColor', params: { color: '#F4E8D8' } },
      { command: 'select.subject' },
      { command: 'layer.layerMask.revealSelection' },
      { command: 'select.deselect' },
      { command: 'select.all' },
      { command: 'layer.align.horizontalCenters' },
      { command: 'layer.align.verticalCenters' },
      { command: 'select.deselect' },
      { method: 'doc.save', params: { path: '/work/out/post.jpg', format: 'jpg', quality: 90 } },
    ]);
  });
});
