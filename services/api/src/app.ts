import { randomUUID } from 'node:crypto';
import express, { type ErrorRequestHandler } from 'express';
import { ALLOWLIST, validatePlan } from '@maro/tool-protocol';
import { API_ROUTES, auditEventSchema, chatRequestSchema, type ChatResponse } from '@maro/shared';
import type { Config } from './config.ts';
import type { Planner } from './maro/planner.ts';
import { preview, type AuditLog } from './audit/audit-log.ts';
import { session } from './auth/session.ts';
import { rateLimit } from './security/rate-limit.ts';
import { securityHeaders } from './security/headers.ts';

export interface AppDeps {
  config: Config;
  planner: Planner;
  audit: AuditLog;
}

export function createApp({ config, planner, audit }: AppDeps) {
  const app = express();
  app.disable('x-powered-by');
  app.use(securityHeaders);
  app.use((req, res, next) => {
    // Dev CORS for the Vite origin; in production the web app is served from the same origin.
    if (req.get('origin') === config.corsOrigin) {
      res.setHeader('Access-Control-Allow-Origin', config.corsOrigin);
      res.setHeader('Vary', 'Origin');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Maro-Session');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
      if (req.method === 'OPTIONS') return res.sendStatus(204);
    }
    next();
  });
  app.use(express.json({ limit: '64kb' }));
  app.use(session);

  app.get(API_ROUTES.health, (_req, res) => {
    res.json({ ok: true, planner: planner.name });
  });

  app.post(API_ROUTES.chat, rateLimit(config.rateLimitPerMinute), async (req, res, next) => {
    try {
      const parsed = chatRequestSchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({
          error: 'invalid_request',
          issues: parsed.error.issues.map((i) => ({ path: i.path.join('.'), message: i.message })),
        });
      }
      const requestId = `req_${randomUUID()}`;
      const out = await planner.plan(parsed.data);
      const { commands, rejected } = validatePlan(
        parsed.data.mode === 'explain' ? [] : out.commands,
        (i) => `${requestId.slice(4, 12)}_${i + 1}`,
      );
      const body: ChatResponse = {
        requestId,
        reply: out.reply,
        steps: commands.map((c) => ({ commandId: c.id, labelAr: ALLOWLIST[c.action].labelAr })),
        commands,
        rejected,
        planner: planner.name,
      };
      await audit.write({
        sessionId: res.locals.sessionId,
        requestId,
        type: 'plan',
        mode: parsed.data.mode,
        messagePreview: preview(parsed.data.message),
        actions: commands.map((c) => c.action),
        rejected: rejected.map((r) => r.reason),
      });
      res.json(body);
    } catch (err) {
      next(err);
    }
  });

  app.post(API_ROUTES.audit, rateLimit(config.rateLimitPerMinute * 2), async (req, res, next) => {
    try {
      const parsed = auditEventSchema.safeParse(req.body);
      if (!parsed.success) return res.status(400).json({ error: 'invalid_request' });
      await audit.write({
        sessionId: res.locals.sessionId,
        requestId: parsed.data.requestId,
        type: 'execution',
        results: parsed.data.results,
      });
      res.status(204).end();
    } catch (err) {
      next(err);
    }
  });

  app.use((_req, res) => res.status(404).json({ error: 'not_found' }));

  const onError: ErrorRequestHandler = (err, _req, res, _next) => {
    const status = typeof err?.status === 'number' && err.status < 500 ? err.status : 500;
    if (status === 500) console.error(err);
    res.status(status).json({ error: status === 500 ? 'internal_error' : 'bad_request' });
  };
  app.use(onError);

  return app;
}
