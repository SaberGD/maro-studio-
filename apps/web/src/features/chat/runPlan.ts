import { toolCommandSchema, type CommandResult, type ToolCommand } from '@maro/tool-protocol';
import type { Studio } from '../studio/useStudio.ts';

export type StepStatus = 'pending' | 'running' | 'done' | 'failed' | 'awaiting-approval' | 'skipped';

export interface RunState {
  statuses: StepStatus[];
  results: CommandResult[];
  /** Index to resume from after the student approves. */
  pausedAt: number | null;
  finished: boolean;
}

export function initialRun(commands: ToolCommand[]): RunState {
  return { statuses: commands.map(() => 'pending'), results: [], pausedAt: null, finished: false };
}

/**
 * Runs validated commands in order. Stops before any command that needs approval
 * until the student approves it, and stops at the first failure.
 */
export async function runPlan(
  studio: Studio,
  commands: ToolCommand[],
  from: RunState,
  approvedIndex: number | null,
  onUpdate: (s: RunState) => void,
): Promise<RunState> {
  let state: RunState = { ...from, statuses: [...from.statuses], pausedAt: null };
  const start = from.pausedAt ?? 0;
  if (start === 0) await studio.checkpoint();

  for (let i = start; i < commands.length; i++) {
    const cmd = commands[i]!;
    // Defence in depth: the browser re-checks the schema before touching the tool.
    if (!toolCommandSchema.safeParse(cmd).success) {
      state.statuses[i] = 'failed';
      state.results.push({ commandId: cmd.id, action: cmd.action, ok: false, message: 'أمر غير صالح', error: 'schema' });
      break;
    }
    if (cmd.requiresApproval && approvedIndex !== i) {
      state.statuses[i] = 'awaiting-approval';
      state.pausedAt = i;
      onUpdate({ ...state });
      return state;
    }
    state.statuses[i] = 'running';
    onUpdate({ ...state, statuses: [...state.statuses] });
    const result = await studio.execute(cmd);
    if (result.ok && cmd.action === 'export_image') {
      try {
        await studio.downloadExport();
      } catch (err) {
        result.ok = false;
        result.error = err instanceof Error ? err.message : String(err);
      }
    }
    state.results.push(result);
    state.statuses[i] = result.ok ? 'done' : 'failed';
    if (!result.ok) {
      for (let j = i + 1; j < commands.length; j++) state.statuses[j] = 'skipped';
      break;
    }
  }
  state = { ...state, finished: true };
  onUpdate(state);
  return state;
}
