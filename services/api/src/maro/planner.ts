import type { RawCommand } from '@maro/tool-protocol';
import type { ChatRequest } from '@maro/shared';

export interface PlannerOutput {
  reply: string;
  /** Proposed commands. They are untrusted until `validatePlan` accepts them. */
  commands: RawCommand[];
}

/**
 * Turns a student request into a reply and a proposed command list.
 * Implementations: the offline rules planner (Sprint 1); an LLM planner behind the
 * server-side LLM gateway (Phase 2) using the prompt in `system-prompt.ts`.
 */
export interface Planner {
  readonly name: string;
  plan(req: ChatRequest): Promise<PlannerOutput>;
}
