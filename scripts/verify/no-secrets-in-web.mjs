#!/usr/bin/env node
// Fails if the browser app references server-only secrets or calls an LLM API directly.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const ROOTS = ['apps/web/src', 'apps/web/index.html', 'apps/web/vite.config.ts', 'packages'];
const FORBIDDEN = [
  [/VITE_[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD)/, 'secret-looking VITE_ variable (would ship to the browser)'],
  [/api\.openai\.com|generativelanguage\.googleapis\.com|api\.anthropic\.com/, 'direct LLM API call from shared/browser code'],
  [/sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}/, 'hard-coded API key'],
  [/process\.env\.(LLM|OPENAI|GEMINI|ANTHROPIC)/, 'server env var read in browser/shared code'],
];

function* files(p) {
  const st = statSync(p);
  if (st.isFile()) return yield p;
  for (const name of readdirSync(p)) {
    if (name === 'node_modules' || name === 'dist') continue;
    yield* files(join(p, name));
  }
}

let failures = 0;
for (const root of ROOTS) {
  for (const f of files(root)) {
    if (!/\.(ts|tsx|js|mjs|html|json)$/.test(f)) continue;
    const text = readFileSync(f, 'utf8');
    for (const [re, why] of FORBIDDEN) {
      if (re.test(text)) {
        console.error(`✕ ${f}: ${why}`);
        failures++;
      }
    }
  }
}
if (failures) process.exit(1);
console.log('✓ no secrets or direct LLM calls in browser/shared code');
