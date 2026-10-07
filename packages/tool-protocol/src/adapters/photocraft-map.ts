import type { ToolCommand } from '../commands/command.ts';

/**
 * One step for PhotoCraft's headless JSON-lines server (`photocraft-cli serve`),
 * see storytold/photocraft docs/control-protocol.md ("Headless server").
 * Either an engine command (`engine.execute`) or a server method (`doc.open`, `doc.save`).
 */
export type PhotoCraftStep =
  | { command: string; params?: Record<string, unknown> }
  | { method: string; params?: Record<string, unknown> };

export interface TranslateContext {
  /** Resolves an upload id to a path inside the session's automation read root. */
  uploadPath(uploadId: string): string;
  /** Path inside the session's automation write root for an export. */
  exportPath(fileName: string): string;
}

const ALIGN_X: Record<string, string | null> = { left: 'leftEdges', center: 'horizontalCenters', right: 'rightEdges' };
const ALIGN_Y: Record<string, string | null> = { top: 'topEdges', center: 'verticalCenters', bottom: 'bottomEdges' };

function splitAnchor(anchor: string): { x: string; y: string } {
  const x = /Left$|^left$/.test(anchor) ? 'left' : /Right$|^right$/.test(anchor) ? 'right' : 'center';
  const y = /^top/.test(anchor) ? 'top' : /^bottom/.test(anchor) ? 'bottom' : 'center';
  return { x, y };
}

/**
 * Maps a validated Maro command to PhotoCraft engine steps. Command ids and params come
 * from PhotoCraft's command registry; rows marked "verify" in integrations/photocraft/command-map.md
 * still need a live check against the engine (Phase 1).
 */
export function toPhotoCraftSteps(cmd: ToolCommand, ctx: TranslateContext): PhotoCraftStep[] {
  switch (cmd.action) {
    case 'import_image':
      return [{ method: 'doc.open', params: { path: ctx.uploadPath(cmd.params.uploadId) } }];
    case 'resize_canvas': {
      const steps: PhotoCraftStep[] = [
        {
          command: 'image.canvasSize',
          params: {
            width: cmd.params.width,
            height: cmd.params.height,
            anchor: cmd.params.anchor,
            extensionColor: cmd.params.background ?? 'transparent',
          },
        },
      ];
      if (cmd.params.background) {
        steps.push({ command: 'layer.newFillLayer.solidColor', params: { color: cmd.params.background } });
      }
      return steps;
    }
    case 'remove_background':
      // `layer.removeBackground` is a UI-only shortcut in PhotoCraft, not an engine command.
      // Select Subject + Reveal Selection gives the same result as a non-destructive mask.
      return [
        { command: 'select.subject' },
        { command: 'layer.layerMask.revealSelection' },
        { command: 'select.deselect' },
      ];
    case 'position_layer': {
      const { x, y } = splitAnchor(cmd.params.align);
      // Photoshop semantics: Align with an active selection aligns the layer to the selection.
      const steps: PhotoCraftStep[] = [{ command: 'select.all' }];
      const ax = ALIGN_X[x];
      const ay = ALIGN_Y[y];
      if (ax) steps.push({ command: `layer.align.${ax}` });
      if (ay) steps.push({ command: `layer.align.${ay}` });
      steps.push({ command: 'select.deselect' });
      return steps;
    }
    case 'export_image': {
      const name = `${(cmd.params.fileName ?? 'maro-export').replace(/\.(png|jpe?g)$/i, '')}.${cmd.params.format}`;
      return [
        {
          method: 'doc.save',
          params: { path: ctx.exportPath(name), format: cmd.params.format, quality: cmd.params.quality },
        },
      ];
    }
  }
}
