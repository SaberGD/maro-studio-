import { useRef, useState, type FormEvent } from 'react';
import type { ChatMode, ChatResponse } from '@maro/shared';
import type { Studio } from '../studio/useStudio.ts';
import { sendAudit, sendChat } from './api.ts';
import { initialRun, runPlan, type RunState, type StepStatus } from './runPlan.ts';

export interface ChatMessage {
  id: number;
  role: 'user' | 'maro' | 'system';
  text: string;
  plan?: ChatResponse;
  run?: RunState;
}

interface Props {
  studio: Studio;
  messages: ChatMessage[];
  setMessages: (fn: (m: ChatMessage[]) => ChatMessage[]) => void;
}

const STATUS_ICON: Record<StepStatus, string> = {
  pending: '○',
  running: '◌',
  done: '✓',
  failed: '✕',
  'awaiting-approval': '⏸',
  skipped: '–',
};

let nextId = 1000;

export function ChatPanel({ studio, messages, setMessages }: Props) {
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('execute');
  const [busy, setBusy] = useState(false);
  const listRef = useRef<HTMLOListElement>(null);

  const patch = (id: number, fn: (m: ChatMessage) => ChatMessage) =>
    setMessages((list) => list.map((m) => (m.id === id ? fn(m) : m)));

  const scroll = () => requestAnimationFrame(() => listRef.current?.lastElementChild?.scrollIntoView({ block: 'end' }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput('');
    setBusy(true);
    setMessages((m) => [...m, { id: nextId++, role: 'user', text }]);
    scroll();
    try {
      const plan = await sendChat({ message: text, mode, document: studio.doc, uploads: studio.uploads.map(stripUpload) });
      setMessages((m) => [
        ...m,
        { id: nextId++, role: 'maro', text: plan.reply, plan, run: plan.commands.length ? initialRun(plan.commands) : undefined },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { id: nextId++, role: 'system', text: err instanceof Error ? err.message : String(err) }]);
    } finally {
      setBusy(false);
      scroll();
    }
  }

  async function execute(msg: ChatMessage, approvedIndex: number | null) {
    if (!msg.plan || !msg.run || busy) return;
    setBusy(true);
    try {
      const final = await runPlan(studio, msg.plan.commands, msg.run, approvedIndex, (run) =>
        patch(msg.id, (m) => ({ ...m, run })),
      );
      if (final.finished) {
        void sendAudit({ requestId: msg.plan.requestId, results: final.results });
        const failed = final.results.find((r) => !r.ok);
        setMessages((m) => [
          ...m,
          {
            id: nextId++,
            role: 'maro',
            text: failed
              ? `وقفت عند خطوة: ${failed.message}${failed.error ? ` (${failed.error})` : ''}. تقدر تتراجع وتجرب تاني.`
              : `خلصت ✓ ${final.results.map((r) => r.message).join(' · ')}`,
          },
        ]);
        scroll();
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="chat" aria-label="Maro Assistant">
      <header className="chat-head">
        <div>
          <strong>مارو</strong>
          <span className="sub">مدربك ومساعدك في التصميم</span>
        </div>
        <button className="btn ghost" onClick={studio.undo} disabled={!studio.canUndo || busy} title="تراجع عن آخر خطة">
          ↶ تراجع
        </button>
      </header>

      <ol className="messages" ref={listRef}>
        {messages.map((m) => (
          <li key={m.id} className={`msg ${m.role}`}>
            <p>{m.text}</p>
            {m.plan && m.run && (
              <div className="plan">
                <ol>
                  {m.plan.steps.map((s, i) => (
                    <li key={s.commandId} className={`step ${m.run!.statuses[i]}`}>
                      <span className="icon" aria-hidden>
                        {STATUS_ICON[m.run!.statuses[i]!]}
                      </span>
                      {s.labelAr}
                      {m.plan!.commands[i]?.requiresApproval && <em> (يحتاج موافقتك)</em>}
                    </li>
                  ))}
                </ol>
                {m.plan.rejected.length > 0 && (
                  <p className="rejected">تم رفض {m.plan.rejected.length} أمر غير مسموح.</p>
                )}
                {!m.run.finished &&
                  (m.run.pausedAt === null ? (
                    m.run.statuses.every((s) => s === 'pending') && (
                      <button className="btn primary" disabled={busy} onClick={() => execute(m, null)}>
                        تنفيذ
                      </button>
                    )
                  ) : (
                    <button className="btn primary" disabled={busy} onClick={() => execute(m, m.run!.pausedAt)}>
                      موافقة: {m.plan.steps[m.run.pausedAt]?.labelAr}
                    </button>
                  ))}
              </div>
            )}
          </li>
        ))}
      </ol>

      <form className="composer" onSubmit={submit}>
        <div className="segmented small">
          <button type="button" aria-pressed={mode === 'explain'} onClick={() => setMode('explain')}>
            اشرح لي
          </button>
          <button type="button" aria-pressed={mode === 'execute'} onClick={() => setMode('execute')}>
            نفّذ
          </button>
        </div>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              e.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="اكتب لمارو… مثلًا: اعمل بوست وشيل الخلفية"
          rows={3}
          maxLength={2000}
        />
        <button className="btn primary" type="submit" disabled={busy || !input.trim()}>
          {busy ? '…' : 'إرسال'}
        </button>
      </form>
    </aside>
  );
}

function stripUpload({ uploadId, fileName, width, height }: { uploadId: string; fileName: string; width: number; height: number }) {
  return { uploadId, fileName, width, height };
}
