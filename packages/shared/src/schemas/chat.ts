import { z } from 'zod';
import { documentStateSchema, type ToolCommand, type RejectedCommand } from '@maro/tool-protocol';
import { LIMITS } from '../constants/index.ts';

export const chatModeSchema = z.enum(['explain', 'execute']);
export type ChatMode = z.infer<typeof chatModeSchema>;

export const uploadRefSchema = z.object({
  uploadId: z.string().min(1).max(128),
  fileName: z.string().max(255),
  width: z.number().int().min(1).max(8192),
  height: z.number().int().min(1).max(8192),
});
export type UploadRef = z.infer<typeof uploadRefSchema>;

/** POST /api/maro/chat body. The user message, document metadata and uploads stay separate fields. */
export const chatRequestSchema = z
  .object({
    message: z.string().trim().min(1).max(LIMITS.maxMessageChars),
    mode: chatModeSchema.default('execute'),
    document: documentStateSchema,
    uploads: z.array(uploadRefSchema).max(10).default([]),
  })
  .strict();
export type ChatRequest = z.infer<typeof chatRequestSchema>;

export interface PlanStep {
  commandId: string;
  labelAr: string;
}

export interface ChatResponse {
  requestId: string;
  /** Arabic reply for the student. */
  reply: string;
  /** Short steps, in order, as shown in the plan card. */
  steps: PlanStep[];
  /** Validated commands only; anything else is listed in `rejected`. */
  commands: ToolCommand[];
  rejected: RejectedCommand[];
  planner: string;
}

export const auditEventSchema = z
  .object({
    requestId: z.string().max(64),
    results: z
      .array(
        z.object({
          commandId: z.string().max(64),
          action: z.string().max(64),
          ok: z.boolean(),
          message: z.string().max(500),
          error: z.string().max(500).optional(),
        }),
      )
      .max(50),
  })
  .strict();
export type AuditEvent = z.infer<typeof auditEventSchema>;
