import type { CommandResult, ToolCommand } from '../commands/command.ts';
import type { DocumentState } from './document.ts';

/**
 * What every tool integration implements (PhotoCraft now, VectorCraft/EffectCraft later).
 * Adapters only ever receive commands that already passed `validatePlan`.
 */
export interface ToolAdapter {
  readonly tool: string;
  inspect(): Promise<DocumentState>;
  execute(command: ToolCommand): Promise<CommandResult>;
}

export interface UploadInfo {
  uploadId: string;
  fileName: string;
  width: number;
  height: number;
}
