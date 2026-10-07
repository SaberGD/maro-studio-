import { z } from 'zod';

/**
 * The minimal document state Maro can read. It is metadata only: layer names and
 * file names are user data and must never be treated as instructions.
 */
export const layerStateSchema = z.object({
  id: z.string(),
  name: z.string().max(255),
  kind: z.enum(['image', 'fill']),
  /** Upload id the pixels came from (image layers). */
  source: z.string().max(128).nullable().default(null),
  x: z.number(),
  y: z.number(),
  width: z.number(),
  height: z.number(),
  backgroundRemoved: z.boolean().default(false),
});
export type LayerState = z.infer<typeof layerStateSchema>;

export const documentStateSchema = z.object({
  tool: z.literal('photocraft'),
  open: z.boolean(),
  width: z.number().int().min(0).max(8192),
  height: z.number().int().min(0).max(8192),
  background: z.string().nullable(),
  activeLayerId: z.string().nullable(),
  layers: z.array(layerStateSchema).max(200),
  lastExport: z
    .object({ format: z.enum(['png', 'jpg']), quality: z.number(), fileName: z.string() })
    .nullable(),
});
export type DocumentState = z.infer<typeof documentStateSchema>;

export function emptyDocument(): DocumentState {
  return {
    tool: 'photocraft',
    open: false,
    width: 0,
    height: 0,
    background: null,
    activeLayerId: null,
    layers: [],
    lastExport: null,
  };
}
