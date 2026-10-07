#!/usr/bin/env node
// Starts the API (:8787) and the web app (:5173) together. Ctrl+C stops both.
import { spawn } from 'node:child_process';

const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const procs = [
  ['api', ['run', 'dev', '-w', '@maro/api']],
  ['web', ['run', 'dev', '-w', '@maro/web']],
].map(([name, args]) => {
  const p = spawn(npm, args, { stdio: ['ignore', 'pipe', 'pipe'], shell: process.platform === 'win32' });
  const prefix = (chunk) =>
    chunk
      .toString()
      .split('\n')
      .filter(Boolean)
      .map((l) => `[${name}] ${l}`)
      .join('\n') + '\n';
  p.stdout.on('data', (c) => process.stdout.write(prefix(c)));
  p.stderr.on('data', (c) => process.stderr.write(prefix(c)));
  p.on('exit', (code) => {
    console.log(`[${name}] exited with ${code}`);
    stop(code ?? 0);
  });
  return p;
});

function stop(code) {
  for (const p of procs) if (p.exitCode === null) p.kill('SIGTERM');
  process.exitCode = code;
}
process.on('SIGINT', () => stop(0));
process.on('SIGTERM', () => stop(0));
