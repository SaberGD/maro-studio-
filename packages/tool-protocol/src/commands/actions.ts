import { z } from 'zod';

/**
 * The MVP command set. Every action Maro may run is declared here with a strict
 * params schema; anything not in this file cannot be executed.
 */

const hexColor = z
  .string()
  .regex(/^#[0-9a-fA-F]{6}$/, 'expected a #rrggbb colour');

const dimension = z.number().int().min(16).max(8192);

export const anchorSchema = z.enum([
  'topLeft',
  'top',
  'topRight',
  'left',
  'center',
  'right',
  'bottomLeft',
  'bottom',
  'bottomRight',
]);
export type Anchor = z.infer<typeof anchorSchema>;

export const importImageParams = z
  .object({
    /** Id of an upload the user already made in this session (never a path or URL). */
    uploadId: z.string().min(1).max(128),
    fileName: z.string().max(255).optional(),
  })
  .strict();

export const resizeCanvasParams = z
  .object({
    width: dimension,
    height: dimension,
    anchor: anchorSchema.default('center'),
    background: hexColor.optional(),
  })
  .strict();

export const removeBackgroundParams = z
  .object({
    layer: z.literal('active').default('active'),
  })
  .strict();

export const positionLayerParams = z
  .object({
    layer: z.literal('active').default('active'),
    align: anchorSchema.default('center'),
    /** Extra offset in px after alignment. */
    offsetX: z.number().int().min(-8192).max(8192).default(0),
    offsetY: z.number().int().min(-8192).max(8192).default(0),
  })
  .strict();

export const exportImageParams = z
  .object({
    format: z.enum(['png', 'jpg']).default('png'),
    quality: z.number().int().min(1).max(100).default(90),
    fileName: z
      .string()
      .regex(/^[\w\-. ]{1,100}$/u, 'plain file name only')
      .optional(),
  })
  .strict();

export const ACTION_PARAMS = {
  import_image: importImageParams,
  resize_canvas: resizeCanvasParams,
  remove_background: removeBackgroundParams,
  position_layer: positionLayerParams,
  export_image: exportImageParams,
} as const;

export type ActionName = keyof typeof ACTION_PARAMS;
export type ActionParams<A extends ActionName> = z.infer<(typeof ACTION_PARAMS)[A]>;

export const ACTION_NAMES = Object.keys(ACTION_PARAMS) as ActionName[];
