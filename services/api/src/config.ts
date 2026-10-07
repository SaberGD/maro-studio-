/** Server-only configuration. Secrets live in env vars on the server and never reach the browser. */
export interface Config {
  port: number;
  corsOrigin: string;
  planner: string;
  auditLogPath: string;
  rateLimitPerMinute: number;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  return {
    port: Number(env.PORT ?? 8787),
    corsOrigin: env.CORS_ORIGIN ?? 'http://localhost:5173',
    planner: env.MARO_PLANNER ?? 'rules',
    auditLogPath: env.AUDIT_LOG_PATH ?? './data/audit.jsonl',
    rateLimitPerMinute: Number(env.RATE_LIMIT_PER_MINUTE ?? 30),
  };
}
