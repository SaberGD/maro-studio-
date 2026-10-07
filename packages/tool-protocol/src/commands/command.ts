import { z } from 'zod';
import { ACTION_PARAMS, type ActionName, type ActionParams } from './actions.ts';

export const TOOL_IDS = ['photocraft'] as const;
export type ToolId = (typeof TOOL_IDS)[number];

/** A validated command: the only shape an adapter ever receives. */
export type ToolCommand = {
  [A in ActionName]: {
    id: string;
    tool: ToolId;
    action: A;
    params: ActionParams<A>;
    requiresApproval: boolean;
  };
}[ActionName];

/** Loose shape of a command as proposed by a planner (LLM or rules), before validation. */
export const rawCommandSchema = z.object({
  tool: z.string(),
  action: z.string(),
  params: z.record(z.unknown()).default({}),
  requiresApproval: z.boolean().optional(),
});
export type RawCommand = z.infer<typeof rawCommandSchema>;

export const toolCommandSchema = z.discriminatedUnion(
  'action',
  (Object.keys(ACTION_PARAMS) as ActionName[]).map((action) =>
    z.object({
      id: z.string(),
      tool: z.enum(TOOL_IDS),
      action: z.literal(action),
      params: ACTION_PARAMS[action],
      requiresApproval: z.boolean(),
    }),
  ) as unknown as [z.ZodDiscriminatedUnionOption<'action'>, ...z.ZodDiscriminatedUnionOption<'action'>[]],
);

export interface CommandResult {
  commandId: string;
  action: ActionName;
  ok: boolean;
  /** Short Arabic message for the student. */
  message: string;
  error?: string;
}
