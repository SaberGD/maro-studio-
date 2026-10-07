import { randomUUID } from 'node:crypto';
import type { RequestHandler } from 'express';

const SESSION_ID = /^[a-zA-Z0-9_-]{8,64}$/;

/**
 * Sprint 1 placeholder: an anonymous session id the web app keeps in sessionStorage
 * and sends as `X-Maro-Session`. It scopes rate limits and audit entries; it is NOT
 * authentication. Replace with Saber login (or the MVP auth decision) in Phase 1.
 */
export const session: RequestHandler = (req, res, next) => {
  const header = req.get('x-maro-session');
  res.locals.sessionId = header && SESSION_ID.test(header) ? header : `anon_${randomUUID()}`;
  next();
};
