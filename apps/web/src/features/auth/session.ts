/** Anonymous Sprint 1 session id (not authentication). See services/api/src/auth/session.ts. */
export function sessionId(): string {
  const key = 'maro.session';
  try {
    const existing = sessionStorage.getItem(key);
    if (existing) return existing;
    const id = `sess_${crypto.randomUUID().replace(/-/g, '')}`;
    sessionStorage.setItem(key, id);
    return id;
  } catch {
    return `sess_${crypto.randomUUID().replace(/-/g, '')}`;
  }
}
