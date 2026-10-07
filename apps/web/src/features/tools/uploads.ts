import { LIMITS, type UploadRef } from '@maro/shared';

export interface LocalUpload extends UploadRef {
  image: HTMLImageElement;
  url: string;
}

/** Checks the real file type from its first bytes, not the extension or the browser's guess. */
export async function sniffImageType(file: Blob): Promise<string | null> {
  const b = new Uint8Array(await file.slice(0, 12).arrayBuffer());
  const at = (i: number, ...bytes: number[]) => bytes.every((v, k) => b[i + k] === v);
  if (at(0, 0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a)) return 'image/png';
  if (at(0, 0xff, 0xd8, 0xff)) return 'image/jpeg';
  if (at(0, 0x52, 0x49, 0x46, 0x46) && at(8, 0x57, 0x45, 0x42, 0x50)) return 'image/webp';
  return null;
}

export async function loadUpload(file: File, index: number): Promise<LocalUpload> {
  if (file.size > LIMITS.maxUploadBytes) {
    throw new Error(`الملف أكبر من ${Math.round(LIMITS.maxUploadBytes / 1024 / 1024)} ميجا`);
  }
  const type = await sniffImageType(file);
  if (!type || !(LIMITS.allowedImageMime as readonly string[]).includes(type)) {
    throw new Error('نوع الملف غير مدعوم. ارفع PNG أو JPG أو WebP.');
  }
  const url = URL.createObjectURL(file);
  const image = new Image();
  image.src = url;
  try {
    await image.decode();
  } catch {
    URL.revokeObjectURL(url);
    throw new Error('تعذّر قراءة الصورة');
  }
  if (image.naturalWidth > 8192 || image.naturalHeight > 8192) {
    URL.revokeObjectURL(url);
    throw new Error('أقصى مقاس 8192 بكسل لكل جانب');
  }
  return {
    uploadId: `up_${index}_${Date.now().toString(36)}`,
    fileName: file.name.slice(0, 255),
    width: image.naturalWidth,
    height: image.naturalHeight,
    image,
    url,
  };
}
