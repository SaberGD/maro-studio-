import { describe, expect, it } from 'vitest';
import request from 'supertest';
import { emptyDocument } from '@maro/tool-protocol';
import { createApp } from './app.ts';
import { MemoryAuditLog } from './audit/audit-log.ts';
import { loadConfig } from './config.ts';
import type { Planner } from './maro/planner.ts';
import { RulesPlanner } from './maro/rules-planner.ts';

function setup(planner: Planner = new RulesPlanner(), rate = 30) {
  const audit = new MemoryAuditLog();
  const config = { ...loadConfig({}), rateLimitPerMinute: rate };
  return { app: createApp({ config, planner, audit }), audit };
}

const body = {
  message: 'اعملي بوست 1080x1350 وشيل الخلفية وحط المنتج في النص وخلي الخلفية بيج',
  document: emptyDocument(),
  uploads: [{ uploadId: 'up_1', fileName: 'p.png', width: 800, height: 600 }],
};

describe('POST /api/maro/chat', () => {
  it('returns a validated plan and writes an audit entry', async () => {
    const { app, audit } = setup();
    const res = await request(app).post('/api/maro/chat').set('X-Maro-Session', 'sess_test_1').send(body);
    expect(res.status).toBe(200);
    expect(res.body.commands.map((c: { action: string }) => c.action)).toEqual([
      'import_image',
      'resize_canvas',
      'remove_background',
      'position_layer',
    ]);
    expect(res.body.steps).toHaveLength(4);
    expect(audit.entries[0]).toMatchObject({ sessionId: 'sess_test_1', type: 'plan' });
  });

  it('drops commands the planner invents', async () => {
    const rogue: Planner = {
      name: 'rogue',
      plan: async () => ({
        reply: 'ok',
        commands: [
          { tool: 'photocraft', action: 'run_shell', params: { cmd: 'rm -rf /' } },
          { tool: 'photocraft', action: 'export_image', params: {}, requiresApproval: false },
        ],
      }),
    };
    const res = await request(setup(rogue).app).post('/api/maro/chat').send(body);
    expect(res.body.commands).toHaveLength(1);
    expect(res.body.commands[0]).toMatchObject({ action: 'export_image', requiresApproval: true });
    expect(res.body.rejected[0].reason).toMatch(/allowlist/);
  });

  it('rejects malformed requests', async () => {
    const { app } = setup();
    expect((await request(app).post('/api/maro/chat').send({ message: '' })).status).toBe(400);
    expect((await request(app).post('/api/maro/chat').send({ ...body, extra: 1 })).status).toBe(400);
  });

  it('rate limits per session', async () => {
    const { app } = setup(new RulesPlanner(), 2);
    const send = () => request(app).post('/api/maro/chat').set('X-Maro-Session', 'sess_rate_1').send(body);
    expect((await send()).status).toBe(200);
    expect((await send()).status).toBe(200);
    expect((await send()).status).toBe(429);
  });
});

describe('POST /api/audit', () => {
  it('records execution results', async () => {
    const { app, audit } = setup();
    const res = await request(app)
      .post('/api/audit')
      .send({ requestId: 'req_1', results: [{ commandId: 'c1', action: 'resize_canvas', ok: true, message: 'تم' }] });
    expect(res.status).toBe(204);
    expect(audit.entries[0]).toMatchObject({ type: 'execution', requestId: 'req_1' });
  });
});
