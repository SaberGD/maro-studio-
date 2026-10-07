import { useState } from 'react';
import { TopBar } from '../components/TopBar.tsx';
import { ChatPanel, type ChatMessage } from '../features/chat/ChatPanel.tsx';
import { Workspace } from '../features/studio/Workspace.tsx';
import { useStudio } from '../features/studio/useStudio.ts';

const WELCOME: ChatMessage = {
  id: 1,
  role: 'maro',
  text: 'أهلًا! أنا مارو 👋 ارفع صورة واكتبلي عايز تعمل إيه، وأنا هقترح خطة وأنفذها معاك خطوة بخطوة.',
};

export function App() {
  const studio = useStudio();
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const say = (role: ChatMessage['role'], text: string) =>
    setMessages((m) => [...m, { id: Date.now() + Math.random(), role, text }]);

  const manualExport = async () => {
    // The manual button counts as the student's approval; it still goes through the command schema.
    const result = await studio.execute({
      id: `manual_${Date.now()}`,
      tool: 'photocraft',
      action: 'export_image',
      params: { format: 'png', quality: 90 },
      requiresApproval: true,
    });
    if (!result.ok) return say('system', result.error ?? result.message);
    say('system', `تم تنزيل ${await studio.downloadExport()}`);
  };

  return (
    <div className="app">
      <TopBar canExport={studio.doc.open} onExport={manualExport} />
      <main className="main">
        <Workspace
          studio={studio}
          onUploaded={async ({ uploadId, fileName }) => {
            // Opening the upload is itself a schema-checked command, like everything Maro runs.
            const result = await studio.execute({
              id: `upload_${uploadId}`,
              tool: 'photocraft',
              action: 'import_image',
              params: { uploadId, fileName },
              requiresApproval: false,
            });
            say('system', result.ok ? `تم فتح «${fileName}».` : (result.error ?? result.message));
          }}
          onError={(text) => say('system', text)}
        />
        <ChatPanel studio={studio} messages={messages} setMessages={setMessages} />
      </main>
    </div>
  );
}
