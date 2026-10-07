import { useCallback, useMemo, useRef, useState } from 'react';
import {
  emptyDocument,
  MockPhotoCraftAdapter,
  type CommandResult,
  type DocumentState,
  type ToolCommand,
} from '@maro/tool-protocol';
import { loadUpload, type LocalUpload } from '../tools/uploads.ts';
import { canvasToBlob, download, renderDocument } from './render.ts';

export interface Studio {
  doc: DocumentState;
  uploads: LocalUpload[];
  canUndo: boolean;
  upload(file: File): Promise<LocalUpload>;
  execute(command: ToolCommand): Promise<CommandResult>;
  /** Snapshot taken before a plan runs, so the whole plan can be undone in one step. */
  checkpoint(): Promise<void>;
  undo(): void;
  uploadById(id: string): LocalUpload | undefined;
  /** Renders the current document and downloads it with the settings of the last export_image. */
  downloadExport(): Promise<string>;
}

export function useStudio(): Studio {
  const [doc, setDoc] = useState<DocumentState>(emptyDocument);
  const [uploads, setUploads] = useState<LocalUpload[]>([]);
  const historyRef = useRef<DocumentState[]>([]);
  const [historySize, setHistorySize] = useState(0);
  const uploadsRef = useRef(new Map<string, LocalUpload>());
  const adapterRef = useRef<MockPhotoCraftAdapter | null>(null);

  const uploadById = useCallback((id: string) => uploadsRef.current.get(id), []);

  const adapter = () => {
    adapterRef.current ??= new MockPhotoCraftAdapter({ uploads: uploadById });
    return adapterRef.current;
  };

  const upload = useCallback(async (file: File) => {
    const up = await loadUpload(file, uploadsRef.current.size + 1);
    uploadsRef.current.set(up.uploadId, up);
    setUploads((list) => [...list, up]);
    return up;
  }, []);

  const execute = useCallback(async (command: ToolCommand) => {
    const result = await adapter().execute(command);
    setDoc(await adapter().inspect());
    return result;
  }, []);

  const checkpoint = useCallback(async () => {
    const snap = await adapter().inspect();
    historyRef.current = [...historyRef.current.slice(-19), snap];
    setHistorySize(historyRef.current.length);
  }, []);

  const undo = useCallback(() => {
    const prev = historyRef.current.at(-1);
    if (!prev) return;
    historyRef.current = historyRef.current.slice(0, -1);
    setHistorySize(historyRef.current.length);
    adapterRef.current = new MockPhotoCraftAdapter({ uploads: uploadById, initial: prev });
    setDoc(prev);
  }, [uploadById]);

  const downloadExport = useCallback(async () => {
    const state = await adapter().inspect();
    if (!state.lastExport) throw new Error('nothing to export');
    const canvas = document.createElement('canvas');
    renderDocument(canvas, state, uploadById);
    const { format, quality, fileName } = state.lastExport;
    download(await canvasToBlob(canvas, format, quality), fileName);
    return fileName;
  }, [uploadById]);

  return useMemo(
    () => ({ doc, uploads, canUndo: historySize > 0, upload, execute, checkpoint, undo, uploadById, downloadExport }),
    [doc, uploads, historySize, upload, execute, checkpoint, undo, uploadById, downloadExport],
  );
}
