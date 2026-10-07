import { useEffect, useRef, useState, type ChangeEvent } from 'react';
import type { Studio } from './useStudio.ts';
import { renderDocument } from './render.ts';

const PHOTOCRAFT_URL = import.meta.env.VITE_PHOTOCRAFT_URL as string | undefined;

interface Props {
  studio: Studio;
  onUploaded: (upload: { uploadId: string; fileName: string }) => void;
  onError: (message: string) => void;
}

export function Workspace({ studio, onUploaded, onError }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [view, setView] = useState<'preview' | 'photocraft'>('preview');
  const { doc } = studio;

  useEffect(() => {
    if (canvasRef.current && doc.open) renderDocument(canvasRef.current, doc, studio.uploadById);
  }, [doc, studio.uploadById]);

  const onFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    try {
      const up = await studio.upload(file);
      onUploaded(up);
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="workspace">
      <div className="workspace-bar">
        <div className="segmented" role="tablist">
          <button role="tab" aria-selected={view === 'preview'} onClick={() => setView('preview')}>
            معاينة Maro
          </button>
          <button role="tab" aria-selected={view === 'photocraft'} onClick={() => setView('photocraft')}>
            PhotoCraft Web
          </button>
        </div>
        <label className="btn">
          رفع صورة
          <input type="file" accept="image/png,image/jpeg,image/webp" onChange={onFile} hidden />
        </label>
        <span className="doc-meta">
          {doc.open ? (
            <>
              <bdi dir="ltr">
                {doc.width}×{doc.height}
              </bdi>{' '}
              · {doc.layers.length} طبقة
            </>
          ) : (
            'لا يوجد ملف مفتوح'
          )}
        </span>
      </div>

      <div className="stage">
        {view === 'preview' ? (
          doc.open ? (
            <canvas ref={canvasRef} className="doc-canvas checker" aria-label="معاينة التصميم" />
          ) : (
            <div className="empty">
              <p>ارفع صورة، وبعدين اطلب من مارو اللي عايزه.</p>
              <p className="hint">مثال: «اعملي بوست 1080×1350، شيل الخلفية، حط المنتج في النص، وخلي الخلفية بيج.»</p>
            </div>
          )
        ) : PHOTOCRAFT_URL ? (
          <iframe className="photocraft-frame" src={PHOTOCRAFT_URL} title="PhotoCraft Web" />
        ) : (
          <div className="empty">
            <p>PhotoCraft Web غير مُعدّ.</p>
            <p className="hint">
              ابنِ PhotoCraft Web محليًا (انظر integrations/photocraft/README.md) ثم ضع رابطه في
              <code> apps/web/.env.local </code>
              كـ <code>VITE_PHOTOCRAFT_URL</code>. أوامر مارو في Sprint 1 تُنفَّذ على «معاينة Maro».
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
