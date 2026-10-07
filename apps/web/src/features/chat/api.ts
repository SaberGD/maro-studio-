import { API_ROUTES, type AuditEvent, type ChatMode, type ChatResponse, type UploadRef } from '@maro/shared';
import type { DocumentState } from '@maro/tool-protocol';
import { sessionId } from '../auth/session.ts';

const headers = () => ({ 'Content-Type': 'application/json', 'X-Maro-Session': sessionId() });

export async function sendChat(input: {
  message: string;
  mode: ChatMode;
  document: DocumentState;
  uploads: UploadRef[];
}): Promise<ChatResponse> {
  const res = await fetch(API_ROUTES.chat, { method: 'POST', headers: headers(), body: JSON.stringify(input) });
  if (res.status === 429) throw new Error((await res.json()).message ?? 'rate limited');
  if (!res.ok) throw new Error(`مارو مش قادر يرد دلوقتي (HTTP ${res.status})`);
  return res.json();
}

export async function sendAudit(event: AuditEvent): Promise<void> {
  try {
    await fetch(API_ROUTES.audit, { method: 'POST', headers: headers(), body: JSON.stringify(event) });
  } catch {
    // Audit is best effort from the browser; the plan itself is already logged server-side.
  }
}
