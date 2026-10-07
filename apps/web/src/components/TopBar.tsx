interface Props {
  canExport: boolean;
  onExport: () => void;
}

const TOOLS = [
  { id: 'photocraft', label: 'PhotoCraft', ready: true },
  { id: 'vectorcraft', label: 'VectorCraft', ready: false },
  { id: 'effectcraft', label: 'EffectCraft', ready: false },
];

export function TopBar({ canExport, onExport }: Props) {
  return (
    <header className="topbar">
      <div className="brand">
        <img src="/maro.svg" alt="" width={28} height={28} />
        <span>Maro Studio</span>
      </div>
      <nav className="tool-tabs" aria-label="الأدوات">
        {TOOLS.map((t) => (
          <button key={t.id} className={t.ready ? 'tab active' : 'tab'} disabled={!t.ready} title={t.ready ? '' : 'قريبًا'}>
            {t.label}
            {!t.ready && <small>قريبًا</small>}
          </button>
        ))}
      </nav>
      <button className="btn primary" disabled={!canExport} onClick={onExport}>
        تصدير PNG
      </button>
    </header>
  );
}
