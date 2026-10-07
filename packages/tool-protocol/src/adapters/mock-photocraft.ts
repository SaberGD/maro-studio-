import { ALLOWLIST } from '../commands/policy.ts';
import type { Anchor } from '../commands/actions.ts';
import type { CommandResult, ToolCommand } from '../commands/command.ts';
import type { ToolAdapter, UploadInfo } from './adapter.ts';
import { emptyDocument, type DocumentState, type LayerState } from './document.ts';

/** Position of a box of size (w, h) anchored inside a (W, H) frame. */
export function anchorOffset(anchor: Anchor, W: number, H: number, w: number, h: number): { x: number; y: number } {
  const col = anchor.endsWith('Left') || anchor === 'left' ? 0 : anchor.endsWith('Right') || anchor === 'right' ? 2 : 1;
  const row = anchor.startsWith('top') ? 0 : anchor.startsWith('bottom') ? 2 : 1;
  return {
    x: Math.round(col === 0 ? 0 : col === 2 ? W - w : (W - w) / 2),
    y: Math.round(row === 0 ? 0 : row === 2 ? H - h : (H - h) / 2),
  };
}

/**
 * Sprint 1 stand-in for PhotoCraft: applies the MVP actions to an in-memory document
 * state. The web preview renders that state, so the full plan → validate → execute →
 * show loop works before the real PhotoCraft bridge exists.
 */
export class MockPhotoCraftAdapter implements ToolAdapter {
  readonly tool = 'photocraft';
  private state: DocumentState;
  private readonly uploads: (id: string) => UploadInfo | undefined;

  constructor(opts: { uploads: (id: string) => UploadInfo | undefined; initial?: DocumentState }) {
    this.uploads = opts.uploads;
    this.state = structuredClone(opts.initial ?? emptyDocument());
  }

  async inspect(): Promise<DocumentState> {
    return structuredClone(this.state);
  }

  async execute(command: ToolCommand): Promise<CommandResult> {
    const label = ALLOWLIST[command.action].labelAr;
    try {
      const message = this.apply(command);
      return { commandId: command.id, action: command.action, ok: true, message: message ?? `تم: ${label}` };
    } catch (err) {
      const error = err instanceof Error ? err.message : String(err);
      return { commandId: command.id, action: command.action, ok: false, message: `تعذّر تنفيذ: ${label}`, error };
    }
  }

  private active(): LayerState {
    const layer = this.state.layers.find((l) => l.id === this.state.activeLayerId);
    if (!layer) throw new Error('no active layer: import an image first');
    return layer;
  }

  private apply(command: ToolCommand): string | undefined {
    const s = this.state;
    switch (command.action) {
      case 'import_image': {
        const upload = this.uploads(command.params.uploadId);
        if (!upload) throw new Error(`unknown upload "${command.params.uploadId}"`);
        const id = `layer_${s.layers.length + 1}`;
        if (!s.open) {
          s.open = true;
          s.width = upload.width;
          s.height = upload.height;
        }
        const { x, y } = anchorOffset('center', s.width, s.height, upload.width, upload.height);
        s.layers.push({
          id,
          name: upload.fileName,
          kind: 'image',
          source: upload.uploadId,
          x,
          y,
          width: upload.width,
          height: upload.height,
          backgroundRemoved: false,
        });
        s.activeLayerId = id;
        return undefined;
      }
      case 'resize_canvas': {
        if (!s.open) throw new Error('no open document');
        const { width, height, anchor, background } = command.params;
        // Layers keep their place relative to the anchor, like Image › Canvas Size.
        const shift = anchorOffset(anchor, width, height, s.width, s.height);
        for (const l of s.layers) {
          l.x += shift.x;
          l.y += shift.y;
        }
        s.width = width;
        s.height = height;
        if (background) s.background = background;
        return `تم تغيير المقاس إلى ${width}×${height}`;
      }
      case 'remove_background': {
        const layer = this.active();
        if (layer.kind !== 'image') throw new Error('active layer is not an image');
        layer.backgroundRemoved = true;
        return 'تم تعليم الطبقة لإزالة الخلفية (محاكاة في Sprint 1)';
      }
      case 'position_layer': {
        const layer = this.active();
        const { align, offsetX, offsetY } = command.params;
        const pos = anchorOffset(align, s.width, s.height, layer.width, layer.height);
        layer.x = pos.x + offsetX;
        layer.y = pos.y + offsetY;
        return undefined;
      }
      case 'export_image': {
        if (!s.open) throw new Error('no open document');
        const { format, quality, fileName } = command.params;
        const base = (fileName ?? 'maro-export').replace(/\.(png|jpe?g)$/i, '');
        s.lastExport = { format, quality, fileName: `${base}.${format}` };
        return `جاهز للتصدير: ${base}.${format}`;
      }
    }
  }
}
