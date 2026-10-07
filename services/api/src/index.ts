import { createApp } from './app.ts';
import { FileAuditLog } from './audit/audit-log.ts';
import { loadConfig } from './config.ts';
import { RulesPlanner } from './maro/rules-planner.ts';
import type { Planner } from './maro/planner.ts';

const config = loadConfig();

function createPlanner(name: string): Planner {
  switch (name) {
    case 'rules':
      return new RulesPlanner();
    default:
      throw new Error(`Unknown MARO_PLANNER "${name}". Available: rules`);
  }
}

const app = createApp({ config, planner: createPlanner(config.planner), audit: new FileAuditLog(config.auditLogPath) });

app.listen(config.port, '127.0.0.1', () => {
  console.log(`Maro API on http://127.0.0.1:${config.port} (planner: ${config.planner})`);
});
