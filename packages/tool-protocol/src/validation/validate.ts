import { ACTION_PARAMS } from '../commands/actions.ts';
import { rawCommandSchema, TOOL_IDS, type ToolCommand, type ToolId } from '../commands/command.ts';
import { ALLOWLIST, isAllowedAction } from '../commands/policy.ts';

export interface RejectedCommand {
  index: number;
  reason: string;
  raw: unknown;
}

export interface ValidatedPlan {
  commands: ToolCommand[];
  rejected: RejectedCommand[];
}

export const MAX_COMMANDS_PER_PLAN = 12;

function isToolId(tool: string): tool is ToolId {
  return (TOOL_IDS as readonly string[]).includes(tool);
}

/**
 * Validates planner output against the allowlist and per-action schemas.
 * Unknown tools/actions and bad params are rejected, never coerced into something else.
 * `requiresApproval` always comes from policy; a planner can't turn it off.
 */
export function validatePlan(raw: unknown, makeId: (i: number) => string = (i) => `cmd_${i + 1}`): ValidatedPlan {
  const commands: ToolCommand[] = [];
  const rejected: RejectedCommand[] = [];
  const list = Array.isArray(raw) ? raw : [];

  if (!Array.isArray(raw)) {
    rejected.push({ index: -1, reason: 'plan is not a list of commands', raw });
  }

  list.forEach((item, index) => {
    if (index >= MAX_COMMANDS_PER_PLAN) {
      rejected.push({ index, reason: `plan exceeds ${MAX_COMMANDS_PER_PLAN} commands`, raw: item });
      return;
    }
    const shape = rawCommandSchema.safeParse(item);
    if (!shape.success) {
      rejected.push({ index, reason: 'malformed command', raw: item });
      return;
    }
    const { tool, action, params } = shape.data;
    if (!isToolId(tool)) {
      rejected.push({ index, reason: `unknown tool "${tool}"`, raw: item });
      return;
    }
    if (!isAllowedAction(action)) {
      rejected.push({ index, reason: `action "${action}" is not in the allowlist`, raw: item });
      return;
    }
    const parsed = ACTION_PARAMS[action].safeParse(params);
    if (!parsed.success) {
      const detail = parsed.error.issues.map((i) => `${i.path.join('.') || 'params'}: ${i.message}`).join('; ');
      rejected.push({ index, reason: `invalid params for ${action}: ${detail}`, raw: item });
      return;
    }
    commands.push({
      id: makeId(commands.length),
      tool,
      action,
      params: parsed.data,
      requiresApproval: ALLOWLIST[action].requiresApproval,
    } as ToolCommand);
  });

  return { commands, rejected };
}
