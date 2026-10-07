import type { DocumentState } from '@maro/tool-protocol';
import type { LocalUpload } from '../tools/uploads.ts';

const cutouts = new WeakMap<HTMLImageElement, HTMLCanvasElement>();

/**
 * Sprint 1 simulation of Remove Background: keys out pixels close to the average
 * corner colour. Real subject selection comes from PhotoCraft (select.subject).
 */
function cutout(img: HTMLImageElement): HTMLCanvasElement {
  const cached = cutouts.get(img);
  if (cached) return cached;
  const c = document.createElement('canvas');
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  const ctx = c.getContext('2d', { willReadFrequently: true })!;
  ctx.drawImage(img, 0, 0);
  const data = ctx.getImageData(0, 0, c.width, c.height);
  const px = data.data;
  const corners = [0, c.width - 1, (c.height - 1) * c.width, c.height * c.width - 1];
  const ref = [0, 1, 2].map((ch) => corners.reduce((s, i) => s + px[i * 4 + ch]!, 0) / 4);
  for (let i = 0; i < px.length; i += 4) {
    const d = Math.abs(px[i]! - ref[0]!) + Math.abs(px[i + 1]! - ref[1]!) + Math.abs(px[i + 2]! - ref[2]!);
    if (d < 60) px[i + 3] = 0;
    else if (d < 110) px[i + 3] = Math.round((px[i + 3]! * (d - 60)) / 50);
  }
  ctx.putImageData(data, 0, 0);
  cutouts.set(img, c);
  return c;
}

export function renderDocument(
  canvas: HTMLCanvasElement,
  doc: DocumentState,
  uploadById: (uploadId: string) => LocalUpload | undefined,
): void {
  canvas.width = Math.max(1, doc.width);
  canvas.height = Math.max(1, doc.height);
  const ctx = canvas.getContext('2d')!;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (doc.background) {
    ctx.fillStyle = doc.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  for (const layer of doc.layers) {
    if (layer.kind !== 'image') continue;
    const up = layer.source ? uploadById(layer.source) : undefined;
    if (!up) continue;
    const source = layer.backgroundRemoved ? cutout(up.image) : up.image;
    ctx.drawImage(source, layer.x, layer.y, layer.width, layer.height);
  }
}

export function canvasToBlob(canvas: HTMLCanvasElement, format: 'png' | 'jpg', quality: number): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error('export failed'))),
      format === 'png' ? 'image/png' : 'image/jpeg',
      quality / 100,
    );
  });
}

export function download(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
