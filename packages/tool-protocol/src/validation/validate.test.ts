import { describe, expect, it } from 'vitest';
import { validatePlan, MAX_COMMANDS_PER_PLAN } from './validate.ts';

describe('validatePlan', () => {
  it('accepts allowlisted commands and fills defaults', () => {
    const { commands, rejected } = validatePlan([
      { tool: 'photocraft', action: 'resize_canvas', params: { width: 1080, height: 1350, background: '#F4E8D8' } },
    ]);
    expect(rejected).toEqual([]);
    expect(commands).toHaveLength(1);
    expect(commands[0]).toMatchObject({
      id: 'cmd_1',
      action: 'resize_canvas',
      params: { width: 1080, height: 1350, anchor: 'center', background: '#F4E8D8' },
      requiresApproval: false,
    });
  });

  it('rejects actions outside the allowlist', () => {
    const { commands, rejected } = validatePlan([{ tool: 'photocraft', action: 'delete_all_files', params: {} }]);
    expect(commands).toEqual([]);
    expect(rejected[0]?.reason).toMatch(/not in the allowlist/);
  });

  it('rejects unknown tools', () => {
    const { rejected } = validatePlan([{ tool: 'shell', action: 'resize_canvas', params: { width: 100, height: 100 } }]);
    expect(rejected[0]?.reason).toMatch(/unknown tool/);
  });

  it('rejects bad and extra params instead of coercing them', () => {
    const { commands, rejected } = validatePlan([
      { tool: 'photocraft', action: 'resize_canvas', params: { width: 99999, height: 100 } },
      { tool: 'photocraft', action: 'export_image', params: { format: 'png', path: '/etc/passwd' } },
      { tool: 'photocraft', action: 'export_image', params: { fileName: '../../secret' } },
    ]);
    expect(commands).toEqual([]);
    expect(rejected).toHaveLength(3);
  });

  it('takes requiresApproval from policy, not from the planner', () => {
    const { commands } = validatePlan([
      { tool: 'photocraft', action: 'export_image', params: {}, requiresApproval: false },
    ]);
    expect(commands[0]?.requiresApproval).toBe(true);
  });

  it('caps the plan length and rejects non-arrays', () => {
    const many = Array.from({ length: MAX_COMMANDS_PER_PLAN + 2 }, () => ({
      tool: 'photocraft',
      action: 'remove_background',
      params: {},
    }));
    expect(validatePlan(many).commands).toHaveLength(MAX_COMMANDS_PER_PLAN);
    expect(validatePlan({ action: 'x' }).rejected[0]?.index).toBe(-1);
  });
});
