import type { ActionName } from './actions.ts';

export type Risk = 'safe' | 'destructive' | 'exports-data';

export interface ActionPolicy {
  risk: Risk;
  /** Approval is decided here, never by the model or the client. */
  requiresApproval: boolean;
  /** Arabic label shown in the plan UI. */
  labelAr: string;
}

/** The allowlist. Adding an action means adding it here and to ACTION_PARAMS. */
export const ALLOWLIST: Record<ActionName, ActionPolicy> = {
  import_image: { risk: 'safe', requiresApproval: false, labelAr: 'فتح / استيراد صورة' },
  resize_canvas: { risk: 'safe', requiresApproval: false, labelAr: 'تغيير مقاس مساحة العمل' },
  remove_background: { risk: 'destructive', requiresApproval: false, labelAr: 'إزالة الخلفية' },
  position_layer: { risk: 'safe', requiresApproval: false, labelAr: 'تحريك / توسيط الطبقة' },
  export_image: { risk: 'exports-data', requiresApproval: true, labelAr: 'تصدير الصورة' },
};

export function isAllowedAction(action: string): action is ActionName {
  return Object.prototype.hasOwnProperty.call(ALLOWLIST, action);
}
