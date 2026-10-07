import { appendFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

export interface AuditEntry {
  ts: string;
  sessionId: string;
  requestId: string;
  type: 'plan' | 'execution';
  [key: string]: unknown;
}

export interface AuditLog {
  write(entry: Omit<AuditEntry, 'ts'>): Promise<void>;
}

/** Append-only JSON lines. Stores short previews, not full prompts or images. */
export class FileAuditLog implements AuditLog {
  private ready: Promise<unknown> | null = null;
  constructor(private readonly path: string) {}

  async write(entry: Omit<AuditEntry, 'ts'>): Promise<void> {
    this.ready ??= mkdir(dirname(this.path), { recursive: true });
    await this.ready;
    await appendFile(this.path, `${JSON.stringify({ ts: new Date().toISOString(), ...entry })}\n`, 'utf8');
  }
}

export class MemoryAuditLog implements AuditLog {
  readonly entries: AuditEntry[] = [];
  async write(entry: Omit<AuditEntry, 'ts'>): Promise<void> {
    this.entries.push({ ts: new Date().toISOString(), ...entry } as AuditEntry);
  }
}

export function preview(text: string, max = 120): string {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}
