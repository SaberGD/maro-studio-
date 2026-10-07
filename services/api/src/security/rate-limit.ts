import type { RequestHandler } from 'express';

/**
 * Fixed-window, in-memory rate limit per session (or IP). Good enough for one API
 * process in the MVP; move to a shared store (Redis) before running several instances.
 */
export function rateLimit(perMinute: number, now: () => number = Date.now): RequestHandler {
  const windows = new Map<string, { start: number; count: number }>();
  return (req, res, next) => {
    const key = res.locals.sessionId ?? req.ip ?? 'unknown';
    const t = now();
    const w = windows.get(key);
    if (!w || t - w.start >= 60_000) {
      windows.set(key, { start: t, count: 1 });
      if (windows.size > 10_000) windows.clear();
      return next();
    }
    if (w.count >= perMinute) {
      res.setHeader('Retry-After', String(Math.ceil((w.start + 60_000 - t) / 1000)));
      return res.status(429).json({ error: 'rate_limited', message: 'طلبات كتير ورا بعض، استنى دقيقة وجرب تاني.' });
    }
    w.count += 1;
    next();
  };
}
