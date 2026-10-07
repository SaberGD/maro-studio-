export const API_ROUTES = {
  health: '/api/health',
  chat: '/api/maro/chat',
  audit: '/api/audit',
} as const;

export const LIMITS = {
  maxMessageChars: 2000,
  maxUploadBytes: 15 * 1024 * 1024,
  allowedImageMime: ['image/png', 'image/jpeg', 'image/webp'] as const,
} as const;
